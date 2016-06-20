Installation
============

.. note:: It is highly recommended that the installation occurs within a virtual environment. We highly recommend `virtualenv <https://virtualenv.pypa.io/en/latest/>`_ to be used in unison with `virtualenvwrapper <https://virtualenvwrapper.readthedocs.org/en/latest/>`_.

To install the development environment, run the following::

    $ pip install requirements-dev.txt

To create the necessary database & tables::

    (openkongqi)$ python -c "import openkongqi.conf; openkongqi.conf.recsdb.init()"

To run `Celery <http://www.celeryproject.org/>`_::

    (openkongqi)$ python openkongqi/bin.py worker --loglevel=debug --concurrency=1 --autoreload -B

