import cloudmanager

# This sample uploads a few sample files.
# 
# The limit is set to 20 MiB to force some
# files to be purged from cache.

readme = "5fb6fa809129cd4ad42e97b01463fdd9f1bb0c72ba9ac97a578211c8ac5bce0a"
rogues = "7d3dae3fd5ca0a4086983bf534f56705ff8a569d9d1c0c33c977f58ea3fa79cd"
crates = "f5a3f4e75ec2832ef3c9c485d91b5f880808cb8740d6d5b5386cd2ac40a0ac4b"

with cloudmanager.CloudManager("db/test.sqlite3", "storage", 20 * (2**20)) as cm:
    print cm.exists(readme)
    print cm.on_cache(readme)
    print cm.usage_ratio()

    print "uploading", cm.upload("README.md")
    print "uploading", cm.upload("RubyRogues20111116.mp3")
    print "uploading", cm.upload("supercrateboxosx.zip")

    print "warming", cm.warm_up(readme)
    print "warming", cm.warm_up(rogues)
    print "warming", cm.warm_up(crates)
