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

from .base import ArlProfilerBase, ARLProfileBase

__all__ = [
    'ArlProfiler'
]

##
## Single Location Profiler
##

class ArlProfiler(ArlProfilerBase):

    def _set_location_info(self, lat, lng):
        self._lat = lat
        self._lng = lng

    def _get_command(self, met_dir, met_file_name, wdir, output_filename):
        # Note: wdir and output_filename are ignored;
        #   they're used by bulk profiler
        return "{exe} -d{dir} -f{file} -y{lat} -x{lng} -w2 -t{time_step}".format(
            exe=self._profile_exe, dir=met_dir, file=met_file_name,
            lat=self._lat, lng=self._lng, time_step=self._time_step)

    def _load(self, full_path_profile_txt, first, start, end, utc_offset):
        logging.debug("Loading {}".format(full_path_profile_txt))
        # data = {}
        # with open(full_path_profile_txt, 'w') as f:
        #     for line in f....
        profile = ARLProfile(full_path_profile_txt, first, start, end,
            utc_offset, self._lat, self._lng)
        local_hourly_profile = profile.get_hourly_params()

        # TDOO: manipulate local_hourly_profile[dt] at all (e.g. map keys to
        # more human readable ones...look in SEVPlumeRise for mappings, and remove
        # code from there if mapping is done here) ?

        return {k.isoformat(): v for k,v in local_hourly_profile.items()}


class ARLProfile(ARLProfileBase):
    """Reads raw ARL data from text file produced by 'profile', parses it
    into a complete dataset, fills in data, and converts to local time.

    To aid clarity, here is an example of one hour of the output
    file ('profile.txt') that we are parsing:

        ___________________________________________________
         Profile Time:  13  1  2  0  0
         Profile Location:    40.61 -100.56  ( 93, 65)

               TPP3  T02M  RH2M  U10M  V10M  PRSS
                                             hPa
         1013     0     0     0     0     0     0

               UWND  VWND  HGTS  TEMP  WWND  RELH     TPOT  WDIR  WSPD
                m/s   m/s          oC  mb/h     %       oK   deg   m/s
         1000   2.6  0.96   196 -0.50     0  66.0    272.7 247.6   2.8
          975   2.6   1.2   397  -1.8     0  66.0    273.4 243.6   2.8
          950   2.7   1.1   603  -3.1     0  66.0    274.1 244.6   2.9
          925   2.5  0.91   813  -5.0     0  67.0    274.2 247.6   2.7
          900   7.6  -1.9  1029  -3.1   6.2  40.0    278.3 282.0   7.8
          875   6.8  -3.5  1252  -2.9   6.2  50.0    280.8 294.8   7.6
          850   7.1  -3.2  1481  -4.5   6.0  60.0    281.4 291.8   7.7
          800   7.6  -3.1  1955  -7.7   2.6  63.0    283.0 289.7   8.2
          750   7.0  -3.8  2454 -11.1  0.58  59.0    284.5 295.8   8.0
          700   6.9  -3.6  2980 -13.5     0  54.0    287.5 295.2   7.8
          650   8.5  -3.1  3541 -16.3     0  42.0    290.6 287.4   9.1
          600  10.7  -1.3  4138 -19.7  0.94  35.0    293.4 274.6  10.8
          550   9.3  -1.3  4779 -23.3   1.6  29.0    296.5 275.9   9.4
          500   6.4  -2.3  5470 -28.2   1.2  22.0    298.6 287.4   6.8
          450   2.6  -4.0  6216 -33.7     0  22.0    300.9 324.3   4.8
          400  -1.6  -5.3  7032 -39.2  -3.3  26.0    304.1  14.5   5.6
          350  -2.4  -4.2  7933 -45.2 -0.85  26.0    307.8  27.7   4.9
          300   4.8  -1.1  8955 -47.5     0  19.0    318.4 281.0   5.0
          250  13.5   2.9 10154 -49.1  -1.1  11.0    333.1 255.5  13.8
          200  19.4   4.3 11618 -48.5   1.1   4.0    356.0 255.2  19.9
          150  28.1   6.9 13505 -51.9  0.52   9.0    380.7 253.8  29.0
          100  18.0   4.8 16116 -55.3 -0.75   2.0    421.0 252.7  18.7
           50   6.8 -0.15 20468 -60.8  0.54   2.0    500.2 268.9   6.8


    Unfortunately, the set of fields is not consistent.  Here's another
    example, from another profile.txt file:

        ___________________________________________________
         Profile Time:  14  5 30  0  0
         Profile Location:    37.43 -120.40  (136,160)

                PRSS  SHGT  T02M  U10M  V10M  PBLH  TPPA
                 hPa                                  mm
             0   996   112  31.5   2.6  -1.8     0     0

                PRES  UWND  VWND  WWND  TEMP  SPHU     TPOT  WDIR  WSPD
                       m/s   m/s  mb/h    oC  g/kg       oK   deg   m/s
           993   993   2.5  -1.9  -7.0  31.0   3.2    304.8 307.1   3.1
           984   984   2.5  -1.8  -7.0  29.5   3.0    304.0 305.4   3.1
           973   975   2.3  -1.7  -7.0  27.0   2.8    302.3 307.2   2.9
           958   961   2.4  -1.7  -7.0  25.5   2.5    302.1 305.5   3.0
           940   943   2.5  -1.7  -3.5  24.0   2.4    302.1 304.0   3.0
           918   922   2.6  -1.4  -5.3  22.1   2.4    302.2 299.0   2.9
           891   896   2.6 -0.80  -5.3  19.9   2.4    302.3 287.6   2.7
           855   862   2.3 -1E-1  -3.5  16.7   2.5    302.5 272.7   2.3
           811   820  0.75   1.5  -3.5  13.4   1.3    303.3 206.4   1.7
           766   778  -2.1   4.5  -3.5  11.8  0.24    306.2 155.5   5.0
           722   736  -2.3   3.8  -2.6   9.3  0.37    308.3 149.6   4.4
           662   678  -1.2   3.1  -1.8   4.8  0.33    310.6 158.9   3.4
           588   608   2.7   4.9  -1.3  -1.9  0.31    312.7 209.2   5.7
           520   544   6.5   7.8 -0.88  -8.7  0.85    314.8 219.8  10.2
           458   486   6.3  10.6 -0.66 -15.7  0.45    316.5 211.1  12.3
           402   432   8.8  13.1 -0.44 -22.1  0.75    319.3 214.0  15.8
           351   383  11.8  13.7 -0.33 -28.1  0.50    322.5 221.0  18.1
           304   339  16.4  14.5 -0.22 -34.3  0.46    325.6 228.9  21.9
           262   299  19.0  17.7 -0.11 -40.5  0.26    328.7 227.4  26.0
           224   263  17.5  20.1 -0.11 -47.7  0.11    330.5 221.4  26.6
           189   230  15.4  19.5 -1E-1 -54.5  5E-2    333.0 218.6  24.8
           158   200  16.2  18.3 -3E-2 -59.0  2E-2    339.1 221.9  24.4
           130   174  19.8  17.5 -2E-2 -57.7  2E-2    355.4 228.8  26.4
           106   150  19.6  15.6 -1E-2 -55.9  1E-2    373.6 231.8  25.1
            84   130  15.9  13.3 -1E-2 -57.1  1E-2    387.4 230.4  20.7
            65   112  11.6  10.6 -3E-3 -59.0  1E-2    400.4 228.0  15.7
            49  96.9   7.6   8.9 -2E-3 -60.7  1E-2    414.3 221.1  11.7
            35  83.6   3.8   9.1 -4E-4 -61.6  3E-3    430.2 202.8   9.8
            23  72.3  0.20   9.2 -2E-4 -62.0  1E-3    447.6 181.5   9.2
            13  62.4  -2.8   7.6 -3E-5 -61.9  1E-3    466.9 160.3   8.1
             4  53.9  -5.3   5.1     0 -61.3  2E-3    488.2 134.4   7.3


    ARLProfile was copied from BlueSky Framework, and subsequently modified
    TODO: acknoledge original authors (STI?)
    """

    def __init__(self, filename, first, start, end, utc_offset, lat, lng):
        super().__init__(filename, first, start, end, utc_offset)
        self.lat = lat
        self.lng = lng
        self.hourly_profile = {}

    def get_hourly_params(self):
        """ Read a raw profile.txt into an hourly dictionary of parameters """
        read_data = False
        hour_separator = "______"  # The output file uses this text string to separate hours.

        # read raw text into a dictionary
        profile = []
        hour_step = []
        with open(self.raw_file, 'r') as f:
            for line in f.readlines():
                if hour_separator in line:
                    read_data = True
                    profile.append(hour_step)
                    hour_step = []
                if read_data:
                    hour_step.append(line)
        if read_data:
            profile.append(hour_step)

        if [] in profile: profile.remove([])

        if profile == []: return {}

        # process raw output into necessary data
        self.parse_hourly_text(profile)
        self.fix_first_hour()
        self.remove_below_ground_levels()
        self.spread_hourly_results()
        self.cast_strings_to_floats()
        self.fill_in_fields()
        self.utc_to_local()
        return self.hourly_profile

    NEGATIVE_NUMBER_MATCHER = re.compile('([^E])-')
    MISSING_VALUE_MATCHER = re.compile('\*{6}')
    def _split_hour_pressure_vals(self, line):
        # Some values occupy 6 characters, and some 8.  They are for
        # the most part separated by spaces. The one exception I've
        # found is when a negative number's '-' is right up against
        # the value to it's left; so, add an extra space before any
        # '-' and then split on space
        new_line = self.NEGATIVE_NUMBER_MATCHER.sub('\\1 -', line)
        return self.MISSING_VALUE_MATCHER.sub(' None ', new_line).split()

    def parse_hourly_text(self, profile):
        """ Parse raw hourly text into a more useful dictionary """

        for hour in profile:
            # 'date' is of the form: ['12', '6', '22', '18', '0']
            date = hour[1][hour[1].find(":") + 1:].strip().split()
            year = int(date[0]) if int(date[0]) > 1980 else (2000 + int(date[0]))
            t = datetime(year, int(date[1]), int(date[2]), int(date[3]))
            vars = {}

            # parameters appear on different line #s, for the two file types
            line_numbers = [4, 6, 8, 10] if hour[5][2:6].split() == [] else [4, 8, 10, 12]
            # parse at-surface variables
            first_vars = []
            first_vars.append('pressure_at_surface')
            for var_str in hour[line_numbers[0]].split():
                first_vars.append(var_str)
            first_vals = self._split_hour_pressure_vals(hour[line_numbers[1]])
            for v in range(len(first_vars)):
                vars[first_vars[v]] = []
                vars[first_vars[v]].append(first_vals[v])

            # parse variables at pressure levels
            main_vars = []
            main_vars.append("pressure")
            for var_str in hour[line_numbers[2]].split():
                main_vars.append(var_str)
            for v in main_vars:
                vars[v] = []
            for i in range(line_numbers[3], len(hour)):
                line = self._split_hour_pressure_vals(hour[i])
                if len(line) > 0:
                    for j in range(len(line)):
                        vars[main_vars[j]].append(line[j])

            self.hourly_profile[t] = vars
