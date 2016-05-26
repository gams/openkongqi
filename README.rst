#####################################
openkongqi - outdoor air quality data
#####################################

.. image:: https://travis-ci.org/gams/openkongqi.svg?branch=master
    :target: https://travis-ci.org/gams/openkongqi
    :alt: Testing Status

Fetch outdoor air quality data from multiple resources, the system is made of
the following components:

* fetching: fetches resources to create the raw material for air
  quality data. That material is saved to create a history and possibility to
  fix errors after the fact.
* data extraction: extract the data from the raw material to create data feeds.
* data reliability: determine which data source is the most reliable at any
  given time.

Architecture
============

The data flow from online resource to reliable data point is broken down as
follow:

* sources: online resources that provide the data, polled at regular interval
  and cached for archive purpose
* feeds: extracted data from sources, feeds are saved as time series in a
  database
* datapoint: extracted from feeds using an election algorithm to provide the
  most reliable data

Configuration
=============

The default local configuration file is ``okqconfig.py``, this can be changed
using the environment variable ``OKQ_CONFMODULE``. The ``okqconfig.py`` file
should define a dict called ``settings``, this dict can be used to overwrite
any configuration option defined in the ``global_settings`` of
``openkongqi.conf``.

Station UUID
============

Each station needs to be attached to a unique identier, a station identifier is
of the following formats::

    CC/STATION
    CC/CITY/STATION
    CC/STATE/CITY/STATION

The following fragments compose the UUID:

* ``CC``: country code - a two letter country code as defined by ISO 3166-1
  alpha-2, mandatory.
* ``STATE``: state name - state name
* ``CITY``: city name - city name
* ``STATION``: stations name - station name, mandatory.

All names have to be expressed in Uppercase or lowercase or numeric latin letters.

Install
=======

Make sure the `lxml` package is installed, on debian:

.. code:: sh

    $ apt-get install python-lxml

Install the code:

.. code:: sh

    $ pip install -U pip==8.1.1
    $ pip install pip-tools
    $ pip-sync requirements.txt

Development
===========

Install development environment:

.. code-block:: sh

    $ pip install -r dev_requirements.txt

Create necessary database & tables:

.. code-block:: sh

    (openkongqi)$ python -c "import openkongqi.bin; openkongqi.bin.okq_init()"

Run celery:

.. code-block:: sh

    (openkongqi)$ python openkongqi/bin.py worker --loglevel=debug --concurrency=1 --autoreload -B

Test
----

Test the package:

.. code-block:: sh


    $ python -m unittest discover

Automatic testing in various environments:

.. code-block:: sh

    $ tox

Versioning
----------

Openkongqi tries to follow the `PEP 440
<https://www.python.org/dev/peps/pep-0440/#public-version-identifiers>`_ /
`Semver <http://semver.org/>`_ conventions as defined by `PyPA
<https://packaging.python.org/en/latest/distributing/#choosing-a-versioning-scheme>`_

To update the version of the package, use the following command:

.. code-block:: sh

    $ bumpr -b -m

Packaging
---------

Create packages:

.. code-block:: sh

    $ python setup.py sdist bdist_wheel

Name origin
===========

Kōngqì (空气) is the Chinese word for air/atmosphere.

License
=======

This software is licensed under the Apache License 2.0. See the LICENSE file in the top distribution directory for the full license text.
