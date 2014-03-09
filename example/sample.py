import cloudmanager

# This sample uploads a few sample files.
#
# The limit is set to 20 MiB to force some
# files to be purged from cache.

readme = "5ad70c0c7cc50a73600df290e545cd9d2c83a815ce63c8bce400b867f1b4f5b5"
nostro = "dc28c33939823340bdb7a5826d09eca991d6274a3cd4411e280c2a65bcc684cc"

with cloudmanager.CloudManager("db/files.db", "storage", 20 * (2**20)) as cm:
    print cm.exists(readme)
    print cm.on_cache(readme)
    print cm.usage_ratio()

    print "uploading", cm.upload("README.md")
    print "uploading", cm.upload("nostromo.mp3")

    print "warming", cm.warm_up(readme)
    print "warming", cm.warm_up(nostro)

    data = cm.data_dump(128000)
    print data

    print cm.data_load(data, "blockchain-hash")
