# met

This package contains meteorological python utilities used by the PNW AirFire team.

***This software is provided for research purposes only. Use at own risk.***

## Non-python Dependencies

### ```profile```

The met package relies on the fortran arl profile utility. It is
expected to reside in a directory in the search path. To obtain `profile`,
contact NOAA.

## Development

### Clone Repo

Via ssh:

    git clone git@github.com:pnwairfire/met.git

or http:

    git clone https://github.com/pnwairfire/met.git

### Install Dependencies

After installing the non-python dependencies (mentioned above), run the
following to install required python packages:

    pip install --trusted-host pypi.smoke.airfire.org --extra-index http://pypi.smoke.airfire.org/simple -r requirements.txt
    pip install -r requirements-dev.txt
    pip install -r requirements-test.txt

## Running tests

You can run tests with pytest:

    py.test
    py.test ./test/unit/met/arl/test_arlfinder.py

You can also use the ```--collect-only``` option to see a list of all tests.

    py.test --collect-only

Use the '-s' option to see output:

    py.test -s

## Installation

### Installing With pip

First, install pip (with sudo if necessary):

    apt-get install python-pip

Then, to install, for example, v1.1.2, use the following (with sudo if
necessary):

    pip install --trusted-host pypi.smoke.airfire.org -i http://pypi.smoke.airfire.org/simple met==1.1.2

If you get an error like    ```AttributeError: 'NoneType' object has no attribute 'skip_requirements_regex```, it means you need in upgrade pip.  One way to do so is with the following:

    pip install --upgrade pip
