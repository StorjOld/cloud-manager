cloud-manager
=============
[![Build Status](https://travis-ci.org/Storj/cloud-manager.svg?branch=master)](https://travis-ci.org/Storj/cloud-manager)
[![Coverage Status](https://coveralls.io/repos/Storj/cloud-manager/badge.png?branch=master)](https://coveralls.io/r/Storj/cloud-manager?branch=master)

"cloud-manager" manages a pool of files uploaded to "the cloud".  It keeps a
cache of the files uploaded, while uploading them using `plowshare-wrapper`.

It works by registering all uploaded files in a database, along with links of
hosts to where it has been uploaded. If there's enough space available locally,
some files are kept in local storage (but also uploaded) to make retrieval
faster.


#### Installation

Go to [INSTALL.md](INSTALL.md) for instructions regarding installation.


#### Module usage

`cloudmanager` requires a database to function properly. A SQL schema is available
in [cloudmanager/schema.sql](cloudmanager/schema.sql). There is also a helper tool,
`cm_setup_db`, to load this schema:

    ./cm_setup_db db/production.sqlite3


After creating the database, the module is ready to be used. One must provide
three parameters:

- File database location (sqlite3)
- Storage location (where to store the cached files)
- Storage capacity (in bytes)


Here's a usage example:

    import cloudmanager

    cm = cloudmanager.CloudManager(
      "/path/to/database.sqlite3",   # Database of the stored files' information
      "/path/to/storage/",           # Cached files will be stored here
      20 * (2**30))                  # 20 GiB capacity

    cm.upload("/path/to/file")       # returns hash of the uploaded file, or False

    cm.warm_up("6f7bed7...121b2")    # Puts the corresponding file in cache
    cm.download("6f7bed7...121b2")   # Same as warm_up

    cm.exists("6f7bed7...121b2")     # returns true if the file exists on the database
    cm.on_cache("6f7bed7...121b2")   # returns true if the file is on cache

    cm.usage_ratio()                 # Returns the storage usage percentage

    cm.close()                       # cleans up everything.


#### Serialization format

`cloudmanager` supports data export/import, through `data_load` and
`data_dump`, so that you can synchronize multiple nodes. Each of the uploaded
files exports the following information:

- version (if the json format changes, this will change too)
- file name (basename)
- file size (bytes)
- file hash (SHA-256)
- datetime (Unix timestamp)
- uploads (list of hosts and URLs)

Here's an example:

    {
      version: "0.2",
      datetime: "1391212800",
      filename: "README.md",
      filesize: "23124",
      filehash: "6e163442e29ec8d7538bc86fe2c4a48778e8ae2254632f0889da753b1c357b1b",
      "uploads": [
        { "host_name": "mediafire",  "url":"http://www.mediafire.com/?qorncpzfe74s9" },
        { "host_name": "rapidshare", "url":"http://rapidshare.com/files/130403982" },
        { "host_name": "anonfiles",  "error":true }
      ]
    }


#### Documentation

    import cloudmanager
    help(cloudmanager.CloudManager)


#### Tests

Install development dependencies by running:

    pip install -e '.[develop]'

Then run:

    tox

This will run the test suite on Python 2.7.


