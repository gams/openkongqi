# -*- coding: utf-8 -*-
import os
from setuptools import setup, find_packages

import openkongqi as okq

# local path
here = os.path.abspath(os.path.dirname(__file__))

# Get the long description from the README file
with open(os.path.join(here, 'README.rst')) as fd:
    long_description = fd.read()

# list requirements for setuptools
requirements = [
    name.rstrip().split()[0]  # remove comments
    for name in open(os.path.join(here, 'requirements.txt')).readlines()
    if name[0] != '#'  # remove comments auto-generated from Sphinx
]

setup(
    name=okq.__name__,
    version=okq.__version__,
    author=okq.__author__,
    author_email=okq.__contact__,
    license="",  # TODO
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
        ]
    },
)
