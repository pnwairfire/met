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
import re
import subprocess

from .base import ArlProfilerBase

__all__ = [
    'ArlProfiler'
]

##
## Single Location Profiler
##

class ArlProfiler(ArlProfilerBase):

    def _set_location_info(self, lat, lng):
        # need to set self._locations, an aray of dicts, to be used in ArlProfile
        self._locations = [
            {"latitude": lat, "longitude": lng}
        ]
        # cone
        self._lat = lat
        self._lng = lng

    def _get_command(self, met_dir, met_file_name, wdir, output_filename):
        # Note: wdir and output_filename are ignored;
        #   they're used by bulk profiler
        return "{exe} -d{dir} -f{file} -y{lat} -x{lng} -w2 -t{time_step}".format(
            exe=self._profile_exe, dir=met_dir, file=met_file_name,
            lat=self._lat, lng=self._lng, time_step=self._time_step)

    @property
    def default_profile_exe(self):
        return 'profile'
