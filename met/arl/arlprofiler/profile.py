"""ArlProfile reads raw ARL data from text files produced by 'profile'
and bulk_profiler_csv, parses them into a complete dataset, fills in data,
and converts them local time.

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

HEre is another example, produced by the bulk_profiler_csv


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


ArlProfile was copied from BlueSky Framework, and subsequently modified
TODO: acknoledge original authors (STI?)
"""

import logging
import os
import re
from collections import defaultdict

from datetime import date, datetime, timedelta
from math import exp, log, pow

from pyairfire import osutils, sun
from afdatetime.parsing import parse_datetimes

class ArlProfileBase(object):
    def __init__(self, filename, first, start, end, utc_offset):
        self.raw_file = filename
        self.first = first
        self.start = start
        self.end = end
        self.utc_offset = utc_offset
        self.hourly_profile = defaultdict(lambda k: {})

    def get_hourly_params(self):
        """ Read a raw profile.txt into an hourly dictionary of parameters """
        read_data = False

        # The output file uses this text string to separate hours.
        hour_separator = "______"
        # The bulk profiler's output file additionall puts this text string
        # between hours.  It will be ignored, since hour_separator will
        # trigger hour switch
        next_separator =  "------next------"

        location_hour_first_line = "Profile Time:"
        location_hour_second_line = "Profile Location:"
        bulk_location_hour_second_line = "Profile:"

        # read raw text into a dictionary
        profile = []
        hour_step = []
        with open(self.raw_file, 'r') as f:
            for line in f.readlines():
                line = line.rstrip()
                if location_hour_first_line in line:
                    profile.append(dict(
                        ts=self._prase_ts(line)
                    ))

                elif location_hour_second_line in line:
                    profile[-1].update(location_idx=0)
                    profile[-1].update(self._parse_lat_lng(line))

                elif bulk_location_hour_second_line in line:
                    profile[-1].update(location_idx=self._parse_location_idx(line))
                    profile[-1].update(self._parse_lat_lng(line))

                elif hour_separator in line or next_separator in line:
                    continue

                elif profile:
                    profile[-1]['data'] = profile[-1].get('data', [])
                    profile[-1]['data'].append(line)

                # else, we haven't reached the first location-hour,
                # so ignore. (we're still in header lines)

        profile = [p for p in profile if p.get('data')]
        if not profile:
            return {}

        # process raw output into necessary data
        self.parse_hourly_text(profile)
        self.fix_first_hour()
        self.remove_below_ground_levels()
        self.spread_hourly_results()
        self.cast_strings_to_floats()
        self.fill_in_fields()
        self.utc_to_local()
        return self.hourly_profile

    def _prase_ts(self, line):
        # 'date' is of the form: ['12', '6', '22', '18', '0']
        date = line[line.find(":") + 1:].strip().split()
        year = int(date[0]) if int(date[0]) > 1980 else (2000 + int(date[0]))
        return datetime(year, int(date[1]), int(date[2]), int(date[3]))

    def _parse_location_idx(self, line):
        return int(s.split()[1])-1

    def _parse_lat_lng(self, line):
        parts = s.split()
        return {
            'lat': int(parts[-3]),
            'lng': int(parts[-2])
        }

    def parse_hourly_text(self, profile):
        """ Parse raw hourly text into a more useful dictionary """
        for p in profile:
            vars = {}

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
            for i in range(line_numbers[3], len(hour)):
                line = self._split_hour_pressure_vals(p['data'][i])
                if len(line) > 0:
                    for j in range(len(line)):
                        vars[main_vars[j]].append(line[j])

            self.hourly_profile[p['ts']][p['idx']] = vars

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
            for idx, param_dict in self.hourly_profile[dt].items():

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


    def get_sun_and_planet_into(self, lat, lng):
        s = sun.Sun(lat=self.lat, lng=self.lng)
        sunrise = s.sunrise_hr(d) + self.utc_offset
        sunset = s.sunset_hr(d) + self.utc_offset
        # default Planetary Boundary Layer (PBL) step function
        default_pbl = lambda hr,sunrise,sunset: 1000.0 if (sunrise + 1) < hr < sunset else 100.0
        return sunrise, sunset, default_pbl

    def fill_in_fields(self):
        # The following is from BSF
        d = self.first.date()

        for dt, hp in list(self.hourly_profile.items()):
            hr = (dt - self.first).total_seconds() / 3600.0
            for lp in hp.values():
                sunrise, sunset, default_pbl = get_sun_and_planet_into(
                    lp['lat'], lng['lng'])

                lp['lat'] = self.lat
                lp['lng'] = self.lng
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
