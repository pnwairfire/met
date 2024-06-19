"""ArlProfile reads raw ARL data from text files produced by 'profile'
and bulk_profiler_csv, parses them into a complete dataset, fills in data,
and converts them to local time.

To aid clarity, here is an example of the first hour of the output
file ('profile.txt') produced for two locations:

     Meteorological Profile: wrfout_d2.2014052912.f00-11_12hr01.arl
     File start time : 14  5 29 12  0
     File ending time: 14  5 29 23  0

    ___________________________________________________
     Profile Time:  14  5 29 12  0
     Profile:       1   37.0000 -121.0000  (127,152)

              PRSS   SHGT   T02M   U10M   V10M   PBLH   TPPA
               hPa                                        mm
          0    979    272   13.7    2.1  -0.43      0      0

              PRES   UWND   VWND   WWND   TEMP   SPHU     TPOT   WDIR   WSPD
                      m/s    m/s   mb/h     oC   g/kg       oK    deg    m/s
        976    976    2.1  -0.35    3.5   14.7    4.3    289.9  279.4    2.1
        968    970    2.1  -0.42    3.5   14.7    4.2    290.4  281.5    2.1
        956    959    2.7   -3.3    3.5   16.0    3.9    292.7  320.5    4.3
        942    944    3.3   -7.9    3.5   17.1    3.5    295.0  337.1    8.6
        925    929    2.4  -10.0    3.5   16.8    3.1    296.1  346.7   10.3
        903    907    1.1   -9.7    3.5   15.7    2.3    297.0  353.8    9.8
        876    883   0.99   -8.1    1.8   14.4    1.5    298.0  353.0    8.2
        840    847    1.7   -5.1    1.8   12.7   0.89    299.7  341.6    5.4
        797    806    1.7   0.99    1.8   13.2   0.28    304.5  239.8    2.0
        754    766    3.8    1.4    1.8   10.2   0.16    305.8  250.5    4.1
        710    725    3.9    1.8   0.88    7.4   1E-1    307.6  245.7    4.3
        651    668    4.5    3.0   0.88    3.0   0.17    310.0  236.2    5.4
        578    599    5.2    1.9   0.88   -3.3   0.20    312.5  249.7    5.6
        511    535    8.1    3.9   0.44  -10.5   0.22    314.1  244.7    9.0
        451    477   13.7    5.7   0.44  -15.9   0.49    317.9  247.3   14.8
        395    425   17.5    8.3   0.22  -21.7   0.60    321.0  244.6   19.3
        345    377   17.8   11.6      0  -28.0   0.24    324.0  236.9   21.2
        299    334   18.1   14.0   0.11  -35.4   0.31    325.3  232.2   22.9
        258    295   21.0   14.3   1E-1  -41.6   0.15    328.4  235.8   25.3
        220    259   25.6   13.5   1E-1  -47.6   1E-1    331.9  242.3   29.0
        186    227   29.0   14.0   3E-2  -54.2   5E-2    334.8  244.3   32.2
        156    198   25.2   14.7   1E-2  -59.4   2E-2    339.8  239.6   29.2
        128    172   19.4   14.7   1E-2  -59.1   2E-2    354.2  232.9   24.4
        104    149   16.4   13.9   1E-2  -56.6   1E-2    373.6  229.6   21.5
         83    129   11.4   13.1   3E-3  -56.5   4E-3    389.6  221.0   17.4
         64    111    8.3   12.3   2E-3  -58.9   4E-3    401.8  213.9   14.8
         49   96.0    6.3   11.2   1E-3  -61.2   4E-3    414.2  209.6   12.8
         35   83.1    4.4    9.6      0  -61.7   3E-3    430.8  204.4   10.6
         23   71.9    2.2    8.1   1E-4  -61.5   3E-3    449.3  195.4    8.4
         13   62.2  -0.26    7.1      0  -61.3   3E-3    468.7  177.9    7.1
          4   53.9   -3.0    6.3      0  -60.8   3E-3    489.6  154.1    7.0
     Profile Time:  14  5 29 12  0
     Profile:       2   37.5000 -120.9000  (129,161)

              PRSS   SHGT   T02M   U10M   V10M   PBLH   TPPA
               hPa                                        mm
          0   1009   16.0   11.1    1.4   -1.1      0      0

              PRES   UWND   VWND   WWND   TEMP   SPHU     TPOT   WDIR   WSPD
                      m/s    m/s   mb/h     oC   g/kg       oK    deg    m/s
       1006   1006    1.5   -1.1      0   11.5    5.2    284.1  305.6    1.9
        997    998    1.8   -1.9      0   11.9    5.0    285.3  316.3    2.7
        986    987    3.6   -4.8      0   14.2    4.5    288.5  323.1    6.0
        971    972    5.5   -8.1      0   17.0    3.7    292.5  326.2    9.8
        953    955    5.0   -9.0      0   18.0    3.2    295.1  331.0   10.3
        930    935    3.2   -9.2      0   17.9    2.6    296.7  340.9    9.7
        903    909    1.9   -8.6      0   17.3    1.9    298.5  347.8    8.8
        866    873    1.3   -5.5      0   15.4   0.85    300.0  346.4    5.6
        821    830    2.2   -3.4      0   12.3   0.25    301.0  326.9    4.0
        777    788    1.7   0.11      0   11.4   0.16    304.7  266.4    1.7
        732    746    1.9    1.1      0    9.2   1E-1    307.1  238.3    2.2
        671    687    2.9    3.3      0    4.5   0.15    309.2  221.4    4.3
        596    616    4.1    1.9      0   -1.8   0.18    311.7  244.8    4.5
        527    550    6.2    4.0      0   -9.3   0.18    312.9  237.3    7.4
        464    491   10.9    6.3      0  -15.1   0.13    316.2  239.8   12.6
        407    437   15.5    7.9      0  -20.4   0.63    320.4  242.9   17.4
        355    388   17.2   10.3      0  -27.0   0.33    322.8  239.1   20.1
        308    343   18.7   13.6      0  -34.0   0.24    324.7  234.0   23.1
        266    302   20.9   15.1      0  -40.6   0.18    327.4  234.1   25.7
        227    266   24.5   15.0      0  -46.7   1E-1    330.8  238.6   28.7
        192    232   28.4   15.3      0  -53.1   4E-2    334.0  241.7   32.2
        160    203   25.5   16.0      0  -58.2   2E-2    339.3  237.9   30.1
        132    175   19.6   15.6      0  -58.7   2E-2    352.8  231.5   25.0
        107    152   16.2   14.4      0  -56.2   1E-2    372.2  228.3   21.7
         85    131   11.4   13.6      0  -55.9   4E-3    388.6  220.0   17.7
         66    113    8.1   12.9      0  -58.4   4E-3    400.8  212.3   15.2
         50   97.5    6.5   11.7      0  -61.0   4E-3    412.7  209.2   13.4
         36   84.1    5.1    9.6      0  -61.4   3E-3    429.9  207.7   10.9
         24   72.6    3.3    7.6      0  -61.0   3E-3    449.1  203.4    8.3
         13   62.6   0.65    6.5      0  -60.9   3E-3    468.9  185.8    6.5
          4   54.0   -2.7    5.8      0  -60.6   4E-3    489.8  155.4    6.4
    -----------next-------------

    ___________________________________________________
     Profile Time:  14  5 29 13  0
     Profile:       1   37.0000 -121.0000  (127,152)

     ...


Unfortunately, the set of fields is not consistent.

ArlProfile was copied from BlueSky Framework, and subsequently modified
TODO: acknoledge original authors (STI?)
"""

import logging
import os
import re
from collections import defaultdict
from datetime import date, datetime, timedelta
from math import exp, log, pow

import pytz
from afdatetime.parsing import parse_datetimes
from pyairfire import osutils, sun
from timezonefinder import TimezoneFinder

__all__ = [
    'ArlProfileParser'
]

ONE_HOUR = timedelta(hours=1)

class memoize(object):

    def __init__(self, f):
        self.f = f
        self.mem = {}

    def __call__(self, *args, **kwargs):
        key = (args, tuple(kwargs.values()))
        if key not in self.mem:
            self.mem[key] = self.f(*args, **kwargs)
        return self.mem[key]

@memoize
def get_utc_offset(dt, lat, lng):
    # TODO: return already computed utc offset for lat,lng,
    #   despite different date, so we don't ahve double
    #   values for gaps when crossing DST <--> ST
    #   (update `memoize` to allows specifuing which args to
    #   include in key)
    tz_name = TimezoneFinder().timezone_at(lng=lng, lat=lat)
    tz = pytz.timezone(tz_name)
    return tz.utcoffset(dt).total_seconds() / 3600

@memoize
def get_sun_and_planet_into(dt, hr, lat, lng, utc_offset):
    s = sun.Sun(lat=lat, lng=lng)

    sunrise = s.sunrise_hr(dt) + utc_offset
    sunset = s.sunset_hr(dt) + utc_offset

    # default Planetary Boundary Layer (PBL) step function
    default_pbl = lambda hr,sunrise,sunset: 1000.0 if (sunrise + 1) < hr < sunset else 100.0

    return sunrise, sunset, default_pbl


class ArlProfileParser(object):
    def __init__(self, filename, first, start, end):
        self.raw_file = filename
        self.first = first
        self.start = start
        self.end = end
        self.hourly_profile = defaultdict(lambda: {})

    def get_hourly_params(self):
        """ Read a raw profile.txt into an an array of location
        specific hourly dictionaries of parameters """

        profile = self.load_profile()
        if not profile:
            return {}

        # process raw output into necessary data
        self.parse_hourly_text(profile)
        self.fix_first_hour()
        self.remove_below_ground_levels()
        self.spread_hourly_results()
        self.cast_strings_to_floats()
        self.fill_in_fields()
        return self.utc_to_local()


    # The output file uses this text string to separate hours.
    HOUR_SEPARATOR = "______"
    # The bulk profiler's output file additionall puts this text string
    # between hours.  It will be ignored, since HOUR_SEPARATOR will
    # trigger hour switch
    NEXT_SEPARATOR =  "------next------"
    LOCATION_HOUR_FIRST_LINE = "Profile Time:"
    LOCATION_HOUR_SECOND_LINE = "Profile:"

    def load_profile(self):
        # read raw text into a dictionary
        profile = []
        hour_step = []
        with open(self.raw_file, 'r') as f:
            for line in f.readlines():
                line = line.rstrip()
                if self.LOCATION_HOUR_FIRST_LINE in line:
                    profile.append(dict(
                        ts=self.prase_ts(line)
                    ))

                elif line.lstrip().startswith(self.LOCATION_HOUR_SECOND_LINE):
                    profile[-1].update(self.parse_location_idx(line))
                    profile[-1].update(self.parse_lat_lng(line))
                    profile[-1].update(utc_offset=get_utc_offset(
                        profile[-1]['ts'], profile[-1]['lat'], profile[-1]['lng']))

                elif self.HOUR_SEPARATOR in line or self.NEXT_SEPARATOR in line:
                    continue

                elif profile:
                    profile[-1]['data'] = profile[-1].get('data', [])
                    profile[-1]['data'].append(line)

                # else, we haven't reached the first location-hour,
                # so ignore. (we're still in header lines)
        return [p for p in profile if p.get('data') and not p.get('out_of_bounds')]

    def prase_ts(self, line):
        # 'date' is of the form: ['12', '6', '22', '18', '0']
        date = line[line.find(":") + 1:].strip().split()
        year = int(date[0]) if int(date[0]) > 1980 else (2000 + int(date[0]))
        return datetime(year, int(date[1]), int(date[2]), int(date[3]))

    def parse_location_idx(self, line):
        # For fires that are outside the met grid, the index value is
        # negative.  For example, the following is within the grid:
        #
        #  Profile:       1   41.4280 -121.1127  (154,495)
        #
        # And the following is outside:
        #
        #  Profile:      -2   41.4554 -107.1011  (736,546)
        #
        # When negative, all of the houlry values are invalid

        val = int(line.split()[1])
        r = {
            'idx': abs(val) - 1
        }

        if val <= 0:
            r['out_of_bounds'] = True

        return r

    def parse_lat_lng(self, line):
        parts = line.split()
        return {
            'lat': float(parts[2]),
            'lng': float(parts[3])
        }

    def parse_hourly_text(self, profile):
        """ Parse raw hourly text into a more useful dictionary """
        for p in profile:
            vars = {
                'lat': p['lat'],
                'lng': p['lng'],
                'utc_offset': p['utc_offset']
            }

            # parameters appear on different line #s, for the two file types
            #line_numbers = [4, 6, 8, 10] if hour[5][2:6].split() == [] else [4, 8, 10, 12]
            line_numbers = [1, 3, 5, 7] if p['data'][2][2:6].split() == [] else [1, 5, 7, 9]
            # parse at-surface variables
            first_vars = []
            first_vars.append('pressure_at_surface')
            for var_str in p['data'][line_numbers[0]].split():
                first_vars.append(var_str)
            first_vals = self._split_hour_pressure_vals(p['data'][line_numbers[1]])
            for v in range(len(first_vars)):
                vars[first_vars[v]] = []
                vars[first_vars[v]].append(first_vals[v])

            # parse variables at pressure levels
            main_vars = []
            main_vars.append("pressure")

            for var_str in p['data'][line_numbers[2]].split():
                main_vars.append(var_str)
            for v in main_vars:
                vars[v] = []
            for i in range(line_numbers[3], len(p['data'])):
                line = self._split_hour_pressure_vals(p['data'][i])

                if len(line) > 0:
                    # only compare array lengths if line is non-empty
                    if len(line) != len(main_vars):
                        # Something went wrong with parsing the line. Set line to
                        # an array of None values (either None or 'None' will work)
                        line = [None] * len(main_vars)

                    for j in range(len(line)):
                        vars[main_vars[j]].append(line[j])

            self.hourly_profile[p['ts']][p['idx']] = vars


    NEGATIVE_NUMBER_MATCHER = re.compile('([^E])-')
    ONE_MISSING_VALUE_MATCHER = re.compile('([^*])\*{6,8}([^*])')
    TWO_MISSING_VALUE_MATCHER = re.compile('([^*])\*{12,16}([^*])')
    THREE_MISSING_VALUE_MATCHER = re.compile('([^*])\*{18,23}([^*])')
    REMAINING_MISSING_VALUE_MATCHER = re.compile('([^*])\*+([^*])')

    def _split_hour_pressure_vals(self, line):
        """Values occupy between 6 and 8 characters.  They are for the most
        part separated by spaces. One exception is when a negative number's
        '-' is right up against the value to it's left. For example:

           1000   1.9  0.15   129  20.2-125.3  71.1   1.2    293.4 253.2   1.9

        For these, we add an extra space before the '-', since we'll
        be splitting on spaces. Another exception is when there as asterisk
        strings in place of values. For example:

           1000    166   20.6      0      0   0.79   80.8   0.30    293.8*******    0.

        and
           959   488  1015     0     0 -0.16   1.0     0     0   959************  0.10   1.9     0******  15.6   291     0     0     0     0     0     0 24135

        We need to add extra space around these asterisk strings.  This is
        complicted by the fact that the strings are of variable length
        and by the posibility of multiple asterisk strings running into each
        other (as in the second example, above). The code, below, assumes
        that the substrings for each field are between 6 and 8 characters long.
        It only handles up to 23 continuous asterisks.  Beyond that, the
        number of fields represented by an asterisk string is ambigious.
        """
        # handle negative numbers
        new_line = self.NEGATIVE_NUMBER_MATCHER.sub('\\1 -', line)

        # handle asterisks (HACK: see docstring above)
        #new_line = self.MISSING_VALUE_MATCHER.sub(' None ', new_line).split()
        new_line = self.ONE_MISSING_VALUE_MATCHER.sub('\\1 None \\2', new_line)
        new_line = self.TWO_MISSING_VALUE_MATCHER.sub('\\1 None None \\2', new_line)
        new_line = self.THREE_MISSING_VALUE_MATCHER.sub('\\1 None None None \\2', new_line)
        # If there are other lengths of asterisks, just replace with single
        # 'None', which will likely trigger parse_hourly_text to abort use
        # the line and to use None values instead for this pressure leave
        new_line = self.REMAINING_MISSING_VALUE_MATCHER.sub('\\1 None \\2', new_line)

        return new_line.split()


    FIRST_HOUR_KEYS_TO_FIX = [
        'pressure_at_surface', 'TPP3', 'T02M', 'RH2M', 'U10M', 'V10M', 'PRSS'
    ]
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
        for loc in self.hourly_profile[self.first].values():
            if (self.to_float(loc["PRSS"][0]) == 0.0
                    and self.to_float(loc["T02M"][0]) == 0.0):
                loc.update(dict((k, self.hourly_profile[second_hr][loc['idx']][k])
                    for k in self.FIRST_HOUR_KEYS_TO_FIX))

    def remove_below_ground_levels(self):
        """
        Frequently, ARL files will include met variables at
        pressure levels that are below the surface of the Earth.
        This data is all nonsense, so it needs to be removed.
        """
        for dt in self.hourly_profile:
            for idx, param_dict in list(self.hourly_profile[dt].items()):
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
                    if hasattr(param_dict[k], 'count'):
                        if len(param_dict[k]) > 1:
                            new_array = []
                            for j in range(len(param_dict[k])):
                                if j >= surface_index:
                                    new_array.append(self.to_float(param_dict[k][j]))
                            new_dict[k] = new_array
                        elif len(param_dict[k]) == 1:
                            new_dict[k] = param_dict[k]
                    else:
                        new_dict[k] = param_dict[k]

                # replace old dict with new
                del self.hourly_profile[dt][idx]
                self.hourly_profile[dt][idx] = new_dict

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

        for hp in self.hourly_profile.values():
            for lp in hp.values():
                for k in lp:
                    if hasattr(lp[k], 'append'):
                        for i in range(len(lp[k])):
                            if hasattr(lp[k][i], 'strip'):
                                lp[k][i] = self.to_float(lp[k][i])
                    elif hasattr(lp[k], 'strip'):
                        lp[k] = self.to_float(lp[k])

    def to_float(self, val):
        if val != 'None' and val is not None:
            return float(val)
        # else returns None

    def fill_in_fields(self):
        # The following is from BSF
        d = self.first.date()

        for dt, hp in list(self.hourly_profile.items()):
            hr = (dt - self.first).total_seconds() / 3600.0
            for lp in hp.values():
                sunrise, sunset, default_pbl = get_sun_and_planet_into(
                    dt, hr, lp['lat'], lp['lng'], lp['utc_offset'])

                for k in ['pressure', 'TPOT', 'WSPD', 'WDIR', 'WWND', 'TEMP', 'SPHU']:
                    lp[k] = lp.get(k)
                if not lp.get('HGTS'):
                    lp['HGTS'] = self.calc_height(lp['pressure'])
                if not lp.get('RELH'):
                    lp['RELH'] = self.calc_rh(lp['pressure'], lp['SPHU'], lp['TEMP'])
                lp['dew_point'] = self.calc_dew_point(lp['RELH'], lp['TEMP'])
                lp['sunrise_hour'] = sunrise
                lp['sunset_hour'] = sunset
                # Note: Based on what they stand for and on looking at the SEV
                #  plumerise logic, it appears that 'PBLH' and 'HPBL' are aliases
                #  for one anohther. ('Planetary Boundary Layer Height' vs 'Height
                #  of Planetary Boundary Layer'.) If so, I don't see why the two
                #  values aren't consolidated into a single variable here, as opposed
                #  to storing them as separate values and only defaulting 'HPBL' to
                #  `default_pbl(hr, sunrise, sunset)` (which is the current logic
                #  that was taken from BSF).  The logic could be replace with
                #  something like:
                #    _pblh = self.list_to_scalar(lp, pblh, lambda: None)
                #    _hpbl = self.list_to_scalar(lp, hpbl, lambda: None)
                #    if _pblh is not None:
                #        lp['pblh'] = _pblh
                #    elif _hpbl is not None:
                #        lp['pblh'] = _pblh
                #    else:
                #        lp['pblh'] = default_pbl(hr, sunrise, sunset)
                for k in ['TO2M', 'RH2M', 'TPP3', 'TPP6', 'PBLH',
                        'T02M', 'U10M', 'V10M', 'PRSS', 'SHGT', 'TPPA',
                        'pressure_at_surface',]:
                    self.list_to_scalar(lp, k, lambda: None)
                self.list_to_scalar(lp, 'HPBL',
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
        # convert profiles to index by location idx and then local time
        local_hourly_profile = defaultdict(lambda: {})
        dt = self.start
        while dt <= self.end:
            logging.debug("Loading {}".format(dt.isoformat()))
            if dt not in self.hourly_profile:
                raise ValueError("{} not in arl file {}".format(dt.isoformat(),
                    self.raw_file))

            for idx, lp in self.hourly_profile[dt].items():
                local_time = dt + timedelta(hours=lp['utc_offset'])
                # TODO: deal with daylight savings time <-> standard time change
                #   one will result in overwriting hourly data, the other will
                #   result in a gap in the data
                #   one solution: compute utc_offset once per location, not
                #   once per location per hour
                local_hourly_profile[idx][local_time] = lp

            dt += ONE_HOUR

        return local_hourly_profile
