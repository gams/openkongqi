# vim: set noexpandtab:
GIT:=/usr/bin/git

NAME=openkongqi
PACKAGE_NAME:=$(NAME)
PACKAGE_VERSION:="0.1.8"

pipreq:
	pip-compile requirements.in
	pip-compile requirements-dev.in

bump:
	$(GIT) checkout master
	$(GIT) merge dev
	bumpr -b -p
	$(GIT) checkout dev
	$(GIT) merge master

pushcode:
	$(GIT) push upstream master dev --tags

pushbump: bump pushcode

pydistclean:
	python setup.py clean
	rm -rf *egg-info build dist

pydist: pydistclean test
	python setup.py sdist bdist_wheel

pypipush: dist
	twine upload dist/*

test: unittest

unittest:
	python -m unittest discover

.PHONY: pipreq bump pushcode pushbump pydistclean pydist pypipush test unittest
