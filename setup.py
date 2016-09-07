#!/usr/bin/env python

from setuptools import setup
DESCRIPTION = ("FileSystemStorage class to save uploaded files on server "
               "filesystem.")

with open('README.rst') as f:
    LONG_DESCRIPTION = f.read()

with open('LICENSE') as f:
    LICENSE = f.read()

install_requires = ['Eve']

setup(
    name='Eve-FSMediaStorage',
    version='0.1.dev0',
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    author='Juan M Barrios',
    author_email='j.m.barrios@gmail.com',
    url='https://github.com/jmbarrios/eve-fsmediastorage',
    license=LICENSE,
    platforms=['any'],
    packages=['eve_fsstorage'],
    install_requires=install_requires,
    test_suite="eve_fsstorage.tests"
)
