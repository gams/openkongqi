# -*- coding: utf-8 -*-
from codecs import open
from os import path
from setuptools import setup, find_packages

import openkongqi as okq


# local path
here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.rst')) as fd:
    long_description = fd.read()

# list requirements for setuptools
with open(path.join(here, 'requirements.txt'), encoding='utf-8') as f:
    requirements = []
    for name in f.readlines():
        if not name.startswith('--') and not name.startswith('#'):
            requirements.append(name.rstrip())

setup(
    name=okq.__name__,
    version=okq.__version__,
    author=okq.__author__,
    author_email=okq.__contact__,
    license="Apache License 2.0",
    packages=find_packages(exclude=['docs', 'test*']),
    url="https://github.com/gams/openkongqi",
    description="Outdoor air quality data",
    long_description=long_description,
    install_requires=requirements,
    classifiers=[
        'Development Status :: 1 - Planning',
        'Environment :: Console',
        'Framework :: Sphinx',
        'Intended Audience :: Developers',
        'Intended Audience :: Healthcare Industry',
        'Intended Audience :: Science/Research',
        'Natural Language :: Chinese (Simplified)',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
        'Topic :: Text Processing :: Markup :: HTML',
        'Topic :: Text Processing :: Markup :: XML',
    ],
    keywords="air quality",
    package_data={
        'openkongqi': [
            'data/user_agent_strings.json',
            'data/sources/pm25.in.json',
            'openkongqi/data/stations/cn/shanghai.json'
        ],
    },
    entry_points={
        'console_scripts': [
            "okq-server=openkongqi.bin:okq_server",
            "okq-init=openkongqi.bin:okq_init",
            "okq-source-test=utils.source_test:main",
        ]
    },
)
