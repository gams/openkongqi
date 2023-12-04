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

requirements = [
    "beautifulsoup4==4.9.3",
    "celery==4.4.7",
    "hiredis==2.0.0",
    "html5lib==1.1",
    "pytz>=2020.5",
    "redis==3.5.3",
    "requests>=2.28.1",
    "six>=1.13.0",
    "sqlalchemy>=1.3.23",
]

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
    include_package_data=True,
)
