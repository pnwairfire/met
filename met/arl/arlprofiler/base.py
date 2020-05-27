"""met.arl.arlprofiler

This module wraps the fortran arl profile utility.  Unless an absolute or
relative path to profile is provided on ArlProfile instantiation, profile
is expected to be in a directory in the search path. (This module prevents
configuring relative or absolute paths to hysplit, to eliminiate security
vulnerabilities when invoked by web service request.) To obtain profile,
contact NOAA.

TODO: move this to pyairfire or into it's own repo (arl-profile[r]) ?
"""

__author__ = "Joel Dubowy and others (unknown)"
__copyright__ = "Copyright 2016, AirFire, PNW, USFS"

import logging
import os
import re
import subprocess
from datetime import date, datetime, timedelta
from math import exp, log, pow

from pyairfire import osutils, sun
from afdatetime.parsing import parse_datetimes

__all__ = [
    'ArlProfilerBase'
]

ONE_HOUR = timedelta(hours=1)


##
## Base Classes
##

class ArlProfilerBase(object):

    def __init__(self, met_files, profile_exe=None, time_step=None):
        """Constructor

        Carries out initialization and validation

        args:
         - met_files
        kwargs:
         - profile_exe
         - time_step -- time step of arl file; defaults to 1

        met_files is expected to be a list of dicts, each dict specifying an
        arl met file along with a 'first', 'start', and 'end' datetimes. For
        example:
           [
              {"file": "...", "first_hour": "...", "last_hour": "..."}
           ]
        'first' is the first hour in the arl file. 'start' and 'end' define
        the time window for which local met data is desired.  Though fire
        growth windows don't have to start or end on the hour, 'first',
        'start', and 'end' do.

        'first', 'start', and 'end' are all assumed to be UTC.
        """
        # _parse_met_files validates information in met_files
        self._met_files = self._parse_met_files(met_files)

        # make sure profile_exe is a valid fully qualified pathname to the
        # profile exe or that it's
        profile_exe = profile_exe or 'profile'
        try:
            # Use check_output so that output isn't sent to stdout
            output = subprocess.check_output([profile_exe])
        except OSError:
            raise ValueError(
                "{} is not an existing/valid profile executable".format(profile_exe))
        self._profile_exe = profile_exe

        self._time_step = time_step or 1

    def _parse_met_files(self, met_files):
        logging.debug("Parsing met file specifications")
        if not met_files:
            raise ValueError(
                "ArlProfiler can't be instantiated without met files defined")

        # TODO: make sure ranges in met_files don't overlap

        # don't override values in original
        _met_files = []
        for met_file in met_files:
            # parse datetimes, and make sure they're valid
            _met_file = parse_datetimes(met_file, 'first_hour', 'last_hour')
            for k in 'first_hour', 'last_hour':
                d = _met_file[k]
                if datetime(d.year, d.month, d.day, d.hour) != d:
                    raise ValueError("ARL file's first_hour and last_hour times must be round hours")
            if _met_file['first_hour'] > _met_file['last_hour']:
                raise ValueError("ARL file's last hour can't be before ARL file's first first")

            # make sure file exists
            if not met_file.get("file"):
                raise ValueError("Arl met file not defined")
            _met_file["file"] = os.path.abspath(met_file.get("file"))
            if not os.path.isfile(_met_file["file"]):
                raise ValueError("{} is not an existing file".format(
                    _met_file["file"]))
            _met_files.append(_met_file)
        return _met_files
