cloud-manager
=============

"Cloud manager" manages a pool of files uploaded to "the cloud".  It keeps a
cache of uploaded files, while uploading them using `plowshare-wrapper`.

It works by registering all uploaded files in a database, along with links of
hosts to where it has been uploaded. If there's enough space available locally,
some files are kept in local storage (but also uploaded) to make retrieval
faster.


#### Installation

This module depends on the `plowshare` module. Please install that first, by
following the instructions in its
[repository](https://github.com/super3/plowshare-wrapper). It is preferable
that you use the pip installation method.

This module, due to its dependency on `plowshare-wrapper`, presumes
that you already have plowshare installed in your system correctly.

You can clone this repository and use its modules directly. Alternatively,
you can build a package and install it through pip (recommended):

    python setup.py sdist
    sudo pip install dist/cloudmanager-0.1.0.tar.gz


#### Module usage

To use this, one must create a database first. A schema file is available in
`db/schema.sql`. You can create a database by piping this file into sqlite3:

    sqlite3 db/production.sqlite3 < db/schema.sql


To use this, you need to provide three elements:

- File database location (sqlite3)
- Storage location (where to store the cached files)
- Storage capacity (in bytes)


Here's an usage example:

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


#### Documentation


Build a new cloudmanager instance.

    cm = cloudmanager.CloudManager(
        database_path,
        storage_path
        storage_size)


Upload a file to the cloud. Creates a copy in local cache.

    cm.upload(file_path)


Put a previously uploaded file in local cache.

    cm.warm_up(file_hash)
    cm.download(file_hash)

Check if a file matching the given hash has been uploaded previously.

    cm.exists(file_hash)


Check if a file matching the given hash is currently on local cache.

    cm.on_cache(file_hash)


Calculate the current usage ratio of the local cache.

    cm.usage_ratio()


Release all resources associated with the cloud manager instance.

    cm.close()

