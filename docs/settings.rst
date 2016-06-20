Settings
========

Default Settings
----------------

The openkongqi settings file doesn't have to define any settings if it doesn't need to. Each setting has a sensible default value. These defaults live in the ``global_settings`` variable from the module ``openkongqi.conf``.


Configuration Variables
-----------------------

``CACHE``
^^^^^^^^^

Default: ``_cache``

Path to cache the sources content. The default path is relative to running path.

Each source content is saved on each instance after fetching to allow for data history processing.


``DATABASES``
^^^^^^^^^^^^^

.. TODO


``LOGGING``
^^^^^^^^^^^

Default: See ``DEFAULT_LOGGING`` in ``openkongqi.conf``

.. TODO


``LOFGILE``
^^^^^^^^^^^

Default: ``openkongqi.log``

The name of the file containing the logs.


``DEBUG``
^^^^^^^^^

Default: ``False``

Whether to print out logging debug messages onto console.


``SOURCES``
^^^^^^^^^^^

Default: ``{}`` (Empty dictionary)

A dictionary containing all the air quality monitoring sources. It is a nested dictionary whose contents provide the following metadata:

- ``target``: the html link where the content is fetched from
- ``uuid``: the unique identifier id that provides the station maps when fed into ``get_station_map``.
- ``modname``: the module name in ``openkongqi.source`` containing the extraction method for scrapping
- ``tz``: the local timezone of the source

An example of a key-value in ``SOURCES``:

.. code-block:: python

    SOURCES = {
        "pm25.in/beijing": {
            "target": "http://pm25.in/beijing",
            "uuid": "cn/beijing",
            "modname": "pm25in",
            "tz": "Asia/Shanghai"
        },
        ...  # omitted for brevity
    }


``SOURCES_DIR``
^^^^^^^^^^^^^^^

Default: ``openkongqi/data/sources``

The path where the JSON files for sources are located.


``STATIONS_MAP_DIR``
^^^^^^^^^^^^^^^^^^^^

Default: ``data/stations``

The path where the JSON files for the station maps are located.


``UA_FILE``
^^^^^^^^^^^

Default: ``data/user_agent_strings.json``

The path containing a list of strings that are valid user agents for web crawling. The default JSON file contains user agents selected from http://useragentstring.com/pages/useragentstring.php.

