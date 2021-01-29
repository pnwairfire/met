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
        'bin/arlquery',
        'bin/arlcleardb'
    ],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Programming Language :: Python :: 3.8",
        "Operating System :: POSIX",
        "Operating System :: MacOS"
    ],
    url='https://github.com/pnwairfire/met',
    description='Meteorological python utilities for the PNW AirFire team.',
    install_requires=[
        "pyairfire>=4.0.0,<5.0",
        "afscripting>=2.0.0,<3.0",
        "afdatetime>=2.0.0,<3.0",
        "pymongo>=3.11.2,<4"
    ],
    dependency_links=[
        "https://pypi.airfire.org/simple/pyairfire/",
        "https://pypi.airfire.org/simple/afscripting/"
    ],
    tests_require=test_requirements
)
