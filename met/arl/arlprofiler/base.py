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

import abc
import logging
import os
import re
import subprocess
from datetime import date, datetime, timedelta
from math import exp, log, pow

from pyairfire import osutils, sun
from afdatetime.parsing import parse_datetimes

from .profile import ArlProfile

__all__ = [
    'ArlProfilerBase'
]

ONE_HOUR = timedelta(hours=1)


##
## Base Classes
##

class ArlProfilerBase(abc.ABC):
    # TODO: is there a way to tell 'profile' to write profile.txt and MESSAGE
    #  to an alternate dir (e.g. to a /tmp/ dir)
    PROFILE_OUTPUT_FILE = 'profile.txt'

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
        profile_exe = profile_exe or self.default_profile_exe
        try:
            # Use check_output so that output isn't sent to stdout
            output = subprocess.check_output([profile_exe])
        except OSError:
            raise ValueError(
                "{} is not an existing/valid profile executable".format(profile_exe))
        self._profile_exe = profile_exe

        self._time_step = time_step or 1

    ##
    ## Instantiation
    ##

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

    ##
    ## Profiling
    ##

    def profile(self, utc_start, utc_end, *location_args):
        """Returns local met profile for specific location and timewindow

        args:
         - start -- datetime object representing beginning of time window, in UTC
         - end -- datetime object representing end of time window, in UTC
        *args
         - location_args - either
        """
        self._set_location_info(*location_args)

        utc_start_hour, utc_end_hour = self._get_utc_start_and_end_hours(
            utc_start, utc_end)

        local_met_data = {}
        for met_file in self._met_files:
            if (met_file['first_hour'] > utc_end_hour or
                    met_file['last_hour'] < utc_start_hour):
                # met file has no data within given timewindow
                continue

            start = max(met_file['first_hour'], utc_start_hour)
            end = min(met_file['last_hour'], utc_end_hour)

            met_dir, met_file_name = os.path.split(met_file["file"])
            # split returns dir without trailing slash, which is required by profile
            met_dir = met_dir + '/'

            with osutils.create_working_dir() as wdir:
              output_filename = os.path.join(wdir, self.PROFILE_OUTPUT_FILE)
              cmd = self._get_command(met_dir, met_file_name, wdir, output_filename)
              self._call(cmd)
              lmd = self._load(output_filename, met_file['first_hour'],
                  start, end)
            local_met_data.update(lmd)
        return local_met_data


    def _get_utc_start_and_end_hours(self, utc_start, utc_end):
        if utc_start > utc_end:
            raise ValueError("Invalid localmet time window: start={}, end={}".format(
              utc_start, utc_end))

        utc_start_hour = datetime(utc_start.year, utc_start.month,
            utc_start.day, utc_start.hour)
        utc_end_hour = datetime(utc_end.year, utc_end.month, utc_end.day,
            utc_end.hour)
        # Don't include end hour if it's on the hour
        # TODO: should we indeed exclude it?
        if utc_end == utc_end_hour:
            utc_end_hour -= ONE_HOUR

        return utc_start_hour, utc_end_hour

    def _call(self, cmd):
        # TODO: cd into tmp dir before calling, or somehow specify
        # custom tmp file name for profile.txt
        # TODO: add another method for calling profile?
        # Note: there must be no space between each option and it's value
        # Note: '-w2' indicates wind direction, instead of components
        logging.debug("Calling '{}'".format(cmd))
        # Note: if we need the stdout/stderr output, we can use:
        #  > output = subprocess.check_output(cmd.split(' '),
        #        stderr=subprocess.STDOUT)
        # or do something like:
        #  > output = StringIO.StringIO()
        #  > status = subprocess.check_output(cmd.split(' '),
        #        stdout=output, stderr=subprocess.STDOUT)
        # TODO: if writing to '/dev/null' isn't portable, capture stdout/stderr
        # in tmp file or in StringIO.StringIO object, and just throw away
        status = subprocess.call(cmd.split(' '),
            stdout=open('/dev/null', 'w'), stderr=subprocess.STDOUT)
        if status:
            raise RuntimeError("profile failed with exit code {}".format(
                status))

    def _load(self, full_path_profile_txt, first, start, end):
        logging.debug("Loading {}".format(full_path_profile_txt))
        # data = {}
        # with open(full_path_profile_txt, 'w') as f:
        #     for line in f....
        profile = ArlProfile(full_path_profile_txt, first, start, end)
        local_hourly_profile = profile.get_hourly_params()

        # TDOO: manipulate local_hourly_profile[dt] at all (e.g. map keys to
        # more human readable ones...look in SEVPlumeRise for mappings, and remove
        # code from there if mapping is done here) ?

        return {k.isoformat(): v for k,v in local_hourly_profile.items()}

    ##
    ## to be implemented by base classes
    ##

    @abc.abstractmethod
    def _set_location_info(self, *location_args):
        pass

    @abc.abstractmethod
    def _get_command(self, met_dir, met_file_name, wdir, output_filename):
        pass

    @property
    @abc.abstractmethod
    def default_profile_exe(self):
        pass
