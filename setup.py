from setuptools import setup, find_packages

from met import __version__

test_requirements = []
with open('requirements-test.txt') as f:
    test_requirements = [r for r in f.read().splitlines()]

setup(
    name='met',
    version=__version__,
    license='GPLv3+',
    author='Joel Dubowy',
    author_email='jdubowy@gmail.com',
    packages=find_packages(),
    scripts=[
        'bin/arlfinder',
        'bin/arlindexer',
        'bin/arlprofiler',
        'bin/arlquery'
    ],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Programming Language :: Python :: 2",
        "Operating System :: POSIX",
        "Operating System :: MacOS"
    ],
    url='https://github.com/pnwairfire/met',
    description='Meteorological python utilities for the PNW AirFire team.',
    install_requires=[
        "pyairfire==2.*",
        "afscripting==1.*",
        "afdatetime==1.*",
        "pymongo==3.2.2"
    ],
    dependency_links=[
        "https://pypi.smoke.airfire.org/simple/pyairfire/",
        "https://pypi.smoke.airfire.org/simple/afscripting/"
    ],
    tests_require=test_requirements
)
