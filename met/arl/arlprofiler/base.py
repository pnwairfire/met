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

__all__ = [
    'ArlProfilerBase',
    'ARLProfileBase'
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
        profile_exe = profile_exe or 'profile'
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

    def profile(self, local_start, local_end, utc_offset, *location_args):
        """Returns local met profile for specific location and timewindow

        args:
         - lat -- latitude of location
         - lng -- longitude of location
         - local_start -- local datetime object representing beginning of time window
         - local_end -- local datetime object representing end of time window
         - utc_offset -- hours ahead of or behind UTC
        """
        self._set_location_info(*location_args)

        utc_start_hour, utc_end_hour = self._get_utc_start_and_end_hours(
            local_start, local_end, utc_offset)

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
                  start, end, utc_offset)
            local_met_data.update(lmd)
        return local_met_data


    def _get_utc_start_and_end_hours(self, local_start, local_end, utc_offset):
        # TODO: validate utc_offset?
        if local_start > local_end:
            raise ValueError("Invalid localmet time window: start={}, end={}".format(
              local_start, local_end))

        utc_start = local_start - timedelta(hours=utc_offset)
        utc_start_hour = datetime(utc_start.year, utc_start.month,
            utc_start.day, utc_start.hour)
        utc_end = local_end - timedelta(hours=utc_offset)
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

    ##
    ## to be implemented by base classes
    ##

    @abc.abstractmethod
    def _set_location_info(self, *location_args):
        pass

    @abc.abstractmethod
    def _get_command(self, met_dir, met_file_name, wdir, output_filename):
        pass

    @abc.abstractmethod
    def _load(self, output_filename, first, start, end, utc_offset):
        pass


class ARLProfileBase(object):
    def __init__(self, filename, first, start, end, utc_offset):
        self.raw_file = filename
        self.first = first
        self.start = start
        self.end = end
        self.utc_offset = utc_offset

    def fix_first_hour(self):
        """
        Some ARL file keep a special place for at-surface met variables. However, sometimes these variables are not
        populated correctly at the zero hour (they will all be zero), and that needs to be fixed.
        """
        t = datetime(self.first.year, self.first.month, self.first.day)
        second_hr = t
        # find second hour in file
        for hr in range(1, 23):
            second_hr = datetime(int(t.year), int(t.month), int(t.day), int(hr))
            if second_hr in self.hourly_profile:
                break

        # back-fill first hour's values, if they are empty
        # These opaque variable names are defined by the ARL standard, and are described in types.ini
        if (self.to_float(self.hourly_profile[self.first]["PRSS"][0]) == 0.0
                and self.to_float(self.hourly_profile[self.first]["T02M"][0]) == 0.0):
            keys = [
                'pressure_at_surface', 'TPP3', 'T02M', 'RH2M', 'U10M', 'V10M', 'PRSS'
            ]
            self.hourly_profile[self.first].update(dict((k, self.hourly_profile[second_hr][k]) for k in keys))

    def remove_below_ground_levels(self):
        """
        Frequently, ARL files will include met variables at
        pressure levels that are below the surface of the Earth.
        This data is all nonsense, so it needs to be removed.
        """
        for dt, param_dict in list(self.hourly_profile.items()):
            surface_p = self.to_float(param_dict['pressure_at_surface'][0])
            if surface_p > self.to_float(param_dict['pressure'][0]) or surface_p < self.to_float(param_dict['pressure'][-1]):
                continue
            new_dict = {}
            for i in range(len(param_dict['pressure'])):
                if self.to_float(param_dict['pressure'][i]) < surface_p:
                    surface_index = i
                    break
            for k in list(param_dict.keys()):
                # loop through each array, and append to new one
                if len(param_dict[k]) > 1:
                    new_array = []
                    for j in range(len(param_dict[k])):
                        if j >= surface_index:
                            new_array.append(self.to_float(param_dict[k][j]))
                    new_dict[k] = new_array
                elif len(param_dict[k]) == 1:
                    new_dict[k] = param_dict[k]

            # replace old dict with new
            del self.hourly_profile[dt]
            self.hourly_profile[dt] = new_dict

    def spread_hourly_results(self):
        """
        Frequently, ARL files will only have data every 3 or 6 hours.
        If so, we need to spread those values out to become hourly data.
        """
        # clean up unwanted hours of information
        for k in list(self.hourly_profile.keys()):
            if k < self.start or k > (self.end):
                del self.hourly_profile[k]

        times = sorted(self.hourly_profile.keys())

        # spread values if the data is not hourly
        new_datetime = self.start
        while new_datetime <= self.end:
            if new_datetime not in times:
                closest_date = sorted(times, key=lambda d:abs(new_datetime - d))[0]
                self.hourly_profile[new_datetime] = self.hourly_profile[closest_date]
            new_datetime += ONE_HOUR

    def cast_strings_to_floats(self):
        # TODO: distinguish between floats and ints; use '<string>.isdigit()'
        # (which returns true if integer); can assume that, if string and not int,
        # then it's a float (?)

        for dt, hp in list(self.hourly_profile.items()):
            for k in hp:
                if hasattr(hp[k], 'append'):
                    for i in range(len(hp[k])):
                        if hasattr(hp[k][i], 'strip'):
                            hp[k][i] = self.to_float(hp[k][i])
                elif hasattr(hp[k], 'strip'):
                    hp[k] = self.to_float(hp[k])

    def to_float(self, val):
        if val != 'None' and val is not None:
            return float(val)
        # else returns None

    def fill_in_fields(self):
        # The following is from BSF
        d = self.first.date()
        s = sun.Sun(lat=self.lat, lng=self.lng)
        sunrise = s.sunrise_hr(d) + self.utc_offset
        sunset = s.sunset_hr(d) + self.utc_offset
        # default Planetary Boundary Layer (PBL) step function
        default_pbl = lambda hr,sunrise,sunset: 1000.0 if (sunrise + 1) < hr < sunset else 100.0

        for dt, hp in list(self.hourly_profile.items()):
            hr = (dt - self.first).total_seconds() / 3600.0
            hp['lat'] = self.lat
            hp['lng'] = self.lng
            for k in ['pressure', 'TPOT', 'WSPD', 'WDIR', 'WWND', 'TEMP', 'SPHU']:
                hp[k] = hp.get(k)
            if not hp.get('HGTS'):
                hp['HGTS'] = self.calc_height(hp['pressure'])
            if not hp.get('RELH'):
                hp['RELH'] = self.calc_rh(hp['pressure'], hp['SPHU'], hp['TEMP'])
            hp['dew_point'] = self.calc_dew_point(hp['RELH'], hp['TEMP'])
            hp['sunrise_hour'] = sunrise
            hp['sunset_hour'] = sunset
            # Note: Based on what they stand for and on looking at the SEV
            #  plumerise logic, it appears that 'PBLH' and 'HPBL' are aliases
            #  for one anohther. ('Planetary Boundary Layer Height' vs 'Height
            #  of Planetary Boundary Layer'.) If so, I don't see why the two
            #  values aren't consolidated into a single variable here, as opposed
            #  to storing them as separate values and only defaulting 'HPBL' to
            #  `default_pbl(hr, sunrise, sunset)` (which is the current logic
            #  that was taken from BSF).  The logic could be replace with
            #  something like:
            #    _pblh = self.list_to_scalar(hp, pblh, lambda: None)
            #    _hpbl = self.list_to_scalar(hp, hpbl, lambda: None)
            #    if _pblh is not None:
            #        hp['pblh'] = _pblh
            #    elif _hpbl is not None:
            #        hp['pblh'] = _pblh
            #    else:
            #        hp['pblh'] = default_pbl(hr, sunrise, sunset)
            for k in ['TO2M', 'RH2M', 'TPP3', 'TPP6', 'PBLH',
                    'T02M', 'U10M', 'V10M', 'PRSS', 'SHGT', 'TPPA',
                    'pressure_at_surface',]:
                self.list_to_scalar(hp, k, lambda: None)
            self.list_to_scalar(hp, 'HPBL',
                lambda: default_pbl(hr, sunrise, sunset))

    def list_to_scalar(self, hourly_profile, k, default):
        a = hourly_profile.get(k)
        if a is not None:
            if hasattr(a, 'append'):
                hourly_profile[k] = self.to_float(a[0])
            elif hasattr(a, 'strip'):
                hourly_profile[k] = self.to_float(a)
            # else, leave as is
        else:
            hourly_profile[k] = default()

    def calc_dew_point(self, rh, temp):
        """ dew_point_temp = (-5321/((ln(RH/100))-(5321/(273+T))))-273 """
        if not rh or not temp:
            return None

        dp = []
        for i in range(len(rh)):
            if self.to_float(rh[i]) < 1.0:
                dp.append((-5321.0 / ((-5.0) - (5321.0 / (273.0 + self.to_float(temp[i]))))) - 273.0)
            else:
                dp.append((-5321.0 / ((log(self.to_float(rh[i])/100.0)) - (5321.0 / (273.0 + self.to_float(temp[i]))))) - 273.0)

        return dp

    def calc_rh(self, pressure, sphu, temp):
        """
        SPHU=0.622*EVAP/PRES         ! specific humidity
        EVAP=RELH*ESAT               ! vapor pressure
        ESAT=EXP(21.4-(5351.0/TEMP)) ! saturation vapor pressure

        rh = EVAP / ESAT = (SPHU * PRES / 0.622) / (EXP(21.4-(5351.0/TEMP)))
        """
        if not pressure or not sphu or not temp:
            return None

        rh = list(map(lambda s,p,t: (self.to_float(s) * self.to_float(p) / 0.622) / (exp(21.4 - (5351.0 /(self.to_float(t) + 273.15)))), sphu,pressure,temp))
        # The above calculation is off by a factor of 10. Divide all values by 10
        return [h / 10.0 for h in rh]

    P_SURFACE = 1000  # Psfc (mb)
    T_REF = 288.15    # Tref (K)
    LAPSE_RATE = 6.5  # Lapse Rate (K/km)
    G = 9.80665       # Gravitational Constant (m/s*s)
    Rd = 287.04       # Gas Constant

    def calc_height(self, pressure):
        """
        height =(Tref/(lapse_rate*0.001))*(1-(pressure/Psfc)^(gas_constant*lapse_rate*0.001/G))
        """
        if not pressure:
            return None

        return [(self.T_REF/(self.LAPSE_RATE*0.001))*(1.0 - pow(self.to_float(p)/self.P_SURFACE, self.Rd*self.LAPSE_RATE*0.001/self.G)) for p in pressure]

    def utc_to_local(self):
        # profile dict will contain local met data index by *local* time
        local_hourly_profile = {}
        dt = self.start
        while dt <= self.end:
            logging.debug("Loading {}".format(dt.isoformat()))
            if dt not in self.hourly_profile:
                raise ValueError("{} not in arl file {}".format(dt.isoformat(),
                    self.raw_file))

            local_hourly_profile[dt + timedelta(hours=self.utc_offset)] = self.hourly_profile[dt]
            dt += ONE_HOUR
        self.hourly_profile = local_hourly_profile
