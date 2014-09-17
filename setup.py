from distutils.core import setup
from setuptools.command.test import test as TestCommand
import sys


class Tox(TestCommand):
    user_options = [('tox-args=', 'a', "Arguments to pass to tox")]
    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.tox_args = None
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True
    def run_tests(self):
        #import here, cause outside the eggs aren't loaded
        import tox
        import shlex
        errno = tox.cmdline(args=shlex.split(self.tox_args))
        sys.exit(errno)

setup(
    name='cloudmanager',
    version='0.9.2dev',
    author='Hugo Peixoto',
    author_email='hugo.peixoto@gmail.com',
    packages=['cloudmanager'],
    scripts=[],
    package_data={'cloudmanager':['schema.sql', '../migrations/*.py']},
    url='https://github.com/super3/cloud-manager',
    license='LICENSE.txt',
    description='Manages a pool of files uploaded to "the cloud"',
    long_description=open('README.md').read(),
    install_requires=[
        'plowshare',
        'psycopg2 >= 2.5'
    ],
    dependency_links = ["https://github.com/Storj/plowshare-wrapper/tarball/master#egg=plowshare"],
    tests_require=['tox'],
    cmdclass = {'test': Tox},
)
