"""Unit tests for bluesky.arlprofiler"""

__author__ = "Joel Dubowy"
__copyright__ = "Copyright 2016, AirFire, PNW, USFS"

import datetime
import os
import tempfile

from numpy.testing import assert_approx_equal
from py.test import raises
from pyairfire import sun

from met.arl import arlprofiler

from data import (
    profile_one_EXPECTED_OUTPUT as expected_profile_one,
    profile_nam12km_with_asterisks_EXPECTED_OUTPUT as expected_nam12km
)

##
## Tests for ARLProfile
##

data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
PROFILE_ONE_FILENAME = os.path.join(data_dir, 'profile-one.txt')
PROFILE_WITH_ASTERISKS_FILENAME = os.path.join(data_dir, 'profile-nam12km-with-asterisks.txt')


# TODO: get example of profile.txt with different colums
# PROFILE_TWO = """ Meteorological Profile: wrfout_d2.2014053000.f00-11_12hr01.arl
#  File start time : 14  5 30  0  0
#  File ending time: 14  5 30  1  0
# ___________________________________________________
#  Profile Time:  13  1  2  0  0
#  Profile Location:    40.61 -100.56  ( 93, 65)
#        TPP3  T02M  RH2M  U10M  V10M  PRSS
#                                      hPa
#  1013     0     0     0     0     0     0
#        UWND  VWND  HGTS  TEMP  WWND  RELH     TPOT  WDIR  WSPD
#         m/s   m/s          oC  mb/h     %       oK   deg   m/s
#  1000   2.6  0.96   196 -0.50     0  66.0    272.7 247.6   2.8
#   975   2.6   1.2   397  -1.8     0  66.0    273.4 243.6   2.8
#   950   2.7   1.1   603  -3.1     0  66.0    274.1 244.6   2.9
#   925   2.5  0.91   813  -5.0     0  67.0    274.2 247.6   2.7
#   900   7.6  -1.9  1029  -3.1   6.2  40.0    278.3 282.0   7.8
#   875   6.8  -3.5  1252  -2.9   6.2  50.0    280.8 294.8   7.6
#   850   7.1  -3.2  1481  -4.5   6.0  60.0    281.4 291.8   7.7
#   800   7.6  -3.1  1955  -7.7   2.6  63.0    283.0 289.7   8.2
#   750   7.0  -3.8  2454 -11.1  0.58  59.0    284.5 295.8   8.0
#   700   6.9  -3.6  2980 -13.5     0  54.0    287.5 295.2   7.8
#   650   8.5  -3.1  3541 -16.3     0  42.0    290.6 287.4   9.1
#   600  10.7  -1.3  4138 -19.7  0.94  35.0    293.4 274.6  10.8
#   550   9.3  -1.3  4779 -23.3   1.6  29.0    296.5 275.9   9.4
#   500   6.4  -2.3  5470 -28.2   1.2  22.0    298.6 287.4   6.8
#   450   2.6  -4.0  6216 -33.7     0  22.0    300.9 324.3   4.8
#   400  -1.6  -5.3  7032 -39.2  -3.3  26.0    304.1  14.5   5.6
#   350  -2.4  -4.2  7933 -45.2 -0.85  26.0    307.8  27.7   4.9
#   300   4.8  -1.1  8955 -47.5     0  19.0    318.4 281.0   5.0
#   250  13.5   2.9 10154 -49.1  -1.1  11.0    333.1 255.5  13.8
#   200  19.4   4.3 11618 -48.5   1.1   4.0    356.0 255.2  19.9
#   150  28.1   6.9 13505 -51.9  0.52   9.0    380.7 253.8  29.0
#   100  18.0   4.8 16116 -55.3 -0.75   2.0    421.0 252.7  18.7
#    50   6.8 -0.15 20468 -60.8  0.54   2.0    500.2 268.9   6.8
# """
# class MockSun(object):
#     def __init__(self, *args, **kwargs):
#         pass

#     def sunrise_hr(self, *args, **kwargs):
#         return 6

#     def sunset_hr(self, *args, **kwargs):
#         return 18

class BaseTestARLProfile(object):

    def check_hourly_profiles(self, actual, expected):
        def check_vals(k, a, e):
            if isinstance(a, float):
                # assert_almost_equal(actual, desired, decimal=7, err_msg='', verbose=True)
                assert_approx_equal(a, e,
                    err_msg="Non-equal {} value - {} != {}".format(k, a, e))
            else:
                assert a == e

        assert set(expected.keys()) == set(actual.keys())
        for dt in expected:
            assert set(expected[dt].keys()) == set(actual[dt].keys())
            for k in expected[dt]:
                if isinstance(expected[dt][k], list):
                    for i in range(len(expected[dt][k])):
                        check_vals(k, actual[dt][k][i], expected[dt][k][i])
                else:
                    check_vals(k, actual[dt][k],   expected[dt][k])

    def monkeypatch_sun(self, monkeypatch):
        monkeypatch.setattr(sun.Sun, "sunrise_hr", lambda *args: 13)
        monkeypatch.setattr(sun.Sun, "sunset_hr", lambda *args: 25)
        #monkeypatch.setattr(arlprofiler, "Sun", MockSun)

    # def test_split_hour_pressure_vals(self):
    #     line = '   799   799 -0.68   2.1   7.0  14.7   2.3    307.0 162.0   2.2               \n'
    #     assert [] == ...
    #     line = '   799   799-10.68   2.1   7.0  14.7   2.3    307.0 162.0   2.2               \n'
    #     assert [] == ...


class TestARLProfileOne(BaseTestARLProfile):

    def test_all_hours_with_offset(self, monkeypatch):
        self.monkeypatch_sun(monkeypatch)
        profiler = arlprofiler.ARLProfile(PROFILE_ONE_FILENAME,
            datetime.datetime(2014, 5, 30, 0, 0), # first
            datetime.datetime(2014, 5, 30, 0, 0), # start
            datetime.datetime(2014, 5, 30, 2, 0), # end
            -7, # utc offset
            37, # lat
            -122) # lng
        hourly_profiles = profiler.get_hourly_params()
        self.check_hourly_profiles(hourly_profiles,
            expected_profile_one.HOURLY_PROFILES_ONE_ALL_HOURS_WITH_OFFSET)

    def test_all_hours_no_offset(self, monkeypatch):
        self.monkeypatch_sun(monkeypatch)
        profiler = arlprofiler.ARLProfile(PROFILE_ONE_FILENAME,
            datetime.datetime(2014, 5, 30, 0, 0), # first
            datetime.datetime(2014, 5, 30, 0, 0), # start
            datetime.datetime(2014, 5, 30, 2, 0), # end
            0, # utc offset
            37, # lat
            -122) # lng
        hourly_profiles = profiler.get_hourly_params()
        self.check_hourly_profiles(hourly_profiles,
            expected_profile_one.HOURLY_PROFILES_ONE_ALL_HOURS_NO_OFFSET)

    def test_partial_with_offset(self, monkeypatch):
        self.monkeypatch_sun(monkeypatch)
        profiler = arlprofiler.ARLProfile(PROFILE_ONE_FILENAME,
            datetime.datetime(2014, 5, 30, 0, 0), # first
            datetime.datetime(2014, 5, 30, 1, 0), # start
            datetime.datetime(2014, 5, 30, 1, 0), # end
            -7, # utc offset
            37, # lat
            -122) # lng
        hourly_profiles = profiler.get_hourly_params()
        self.check_hourly_profiles(hourly_profiles,
            expected_profile_one.HOURLY_PROFILES_ONE_PARTIAL_WITH_OFFSET)

    def test_partial_no_offset(self, monkeypatch):
        self.monkeypatch_sun(monkeypatch)
        profiler = arlprofiler.ARLProfile(PROFILE_ONE_FILENAME,
            datetime.datetime(2014, 5, 30, 0, 0), # first
            datetime.datetime(2014, 5, 30, 1, 0), # start
            datetime.datetime(2014, 5, 30, 1, 0), # end
            0, # utc offset
            37, # lat
            -122) # lng
        hourly_profiles = profiler.get_hourly_params()
        self.check_hourly_profiles(hourly_profiles,
            expected_profile_one.HOURLY_PROFILES_ONE_PARTIAL_NO_OFFSET)


