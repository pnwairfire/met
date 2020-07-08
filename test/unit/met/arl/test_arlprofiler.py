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
## Tests for ArlProfile
##

data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
PROFILE_ONE_FILENAME = os.path.join(data_dir, 'profile-one.txt')
PROFILE_WITH_ASTERISKS_FILENAME = os.path.join(data_dir, 'profile-nam12km-with-asterisks.txt')


# class MockSun(object):
#     def __init__(self, *args, **kwargs):
#         pass

#     def sunrise_hr(self, *args, **kwargs):
#         return 6

#     def sunset_hr(self, *args, **kwargs):
#         return 18

class BaseTestArlProfile(object):

    def check_hourly_profiles(self, actual, expected):
        def check_vals(k, a, e):
            if isinstance(a, float):
                # assert_almost_equal(actual, desired, decimal=7, err_msg='', verbose=True)
                assert_approx_equal(a, e,
                    err_msg="Non-equal {} value: {} != {}".format(k, a, e))
            else:
                assert a == e, "Non-equal {} value: {} != {}".format(k, a, e)

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


class TestArlProfileOne(BaseTestArlProfile):

    def test_all_hours_with_offset(self, monkeypatch):
        self.monkeypatch_sun(monkeypatch)
        profiler = arlprofiler.ArlProfile(PROFILE_ONE_FILENAME,
            datetime.datetime(2014, 5, 30, 0, 0), # first
            datetime.datetime(2014, 5, 30, 0, 0), # start
            datetime.datetime(2014, 5, 30, 2, 0), # end
            -7, # utc offset
            37, # lat
            -122) # lng
        hourly_profiles = profiler.get_hourly_params()
        self.check_hourly_profiles(hourly_profiles,
            expected_profile_one.HOURLY_PROFILES_ALL_HOURS_WITH_OFFSET)

    def test_all_hours_no_offset(self, monkeypatch):
        self.monkeypatch_sun(monkeypatch)
        profiler = arlprofiler.ArlProfile(PROFILE_ONE_FILENAME,
            datetime.datetime(2014, 5, 30, 0, 0), # first
            datetime.datetime(2014, 5, 30, 0, 0), # start
            datetime.datetime(2014, 5, 30, 2, 0), # end
            0, # utc offset
            37, # lat
            -122) # lng
        hourly_profiles = profiler.get_hourly_params()
        self.check_hourly_profiles(hourly_profiles,
            expected_profile_one.HOURLY_PROFILES_ALL_HOURS_NO_OFFSET)

    def test_partial_with_offset(self, monkeypatch):
        self.monkeypatch_sun(monkeypatch)
        profiler = arlprofiler.ArlProfile(PROFILE_ONE_FILENAME,
            datetime.datetime(2014, 5, 30, 0, 0), # first
            datetime.datetime(2014, 5, 30, 1, 0), # start
            datetime.datetime(2014, 5, 30, 1, 0), # end
            -7, # utc offset
            37, # lat
            -122) # lng
        hourly_profiles = profiler.get_hourly_params()
        self.check_hourly_profiles(hourly_profiles,
            expected_profile_one.HOURLY_PROFILES_PARTIAL_WITH_OFFSET)

    def test_partial_no_offset(self, monkeypatch):
        self.monkeypatch_sun(monkeypatch)
        profiler = arlprofiler.ArlProfile(PROFILE_ONE_FILENAME,
            datetime.datetime(2014, 5, 30, 0, 0), # first
            datetime.datetime(2014, 5, 30, 1, 0), # start
            datetime.datetime(2014, 5, 30, 1, 0), # end
            0, # utc offset
            37, # lat
            -122) # lng
        hourly_profiles = profiler.get_hourly_params()
        self.check_hourly_profiles(hourly_profiles,
            expected_profile_one.HOURLY_PROFILES_PARTIAL_NO_OFFSET)


class TestArlProfileNam12kmWithAsterisks(BaseTestArlProfile):

    def test_four_hours_with_offset(self, monkeypatch):
        self.monkeypatch_sun(monkeypatch)
        profiler = arlprofiler.ArlProfile(PROFILE_WITH_ASTERISKS_FILENAME,
            datetime.datetime(2015, 8, 9, 0, 0), # first
            datetime.datetime(2015, 8, 9, 0, 0), # start
            datetime.datetime(2015, 8, 9, 3, 0), # end
            -7, # utc offset
            41.77, # lat
            -123.97) # lng
        hourly_profiles = profiler.get_hourly_params()
        self.check_hourly_profiles(hourly_profiles,
            expected_nam12km.HOURLY_PROFILES_ALL_HOURS_WITH_OFFSET)

    def test_four_hours_no_offset(self, monkeypatch):
        self.monkeypatch_sun(monkeypatch)
        profiler = arlprofiler.ArlProfile(PROFILE_WITH_ASTERISKS_FILENAME,
            datetime.datetime(2015, 8, 9, 0, 0), # first
            datetime.datetime(2015, 8, 9, 0, 0), # start
            datetime.datetime(2015, 8, 9, 3, 0), # end
            0, # utc offset
            41.77, # lat
            -123.97) # lng
        hourly_profiles = profiler.get_hourly_params()
        self.check_hourly_profiles(hourly_profiles,
            expected_nam12km.HOURLY_PROFILES_ALL_HOURS_NO_OFFSET)

    def test_partial_with_offset(self, monkeypatch):
        self.monkeypatch_sun(monkeypatch)
        profiler = arlprofiler.ArlProfile(PROFILE_WITH_ASTERISKS_FILENAME,
            datetime.datetime(2015, 8, 9, 0, 0), # first
            datetime.datetime(2015, 8, 9, 0, 0), # start
            datetime.datetime(2015, 8, 9, 0, 0), # end
            -7, # utc offset
            41.77, # lat
            -123.97) # lng
        hourly_profiles = profiler.get_hourly_params()
        self.check_hourly_profiles(hourly_profiles,
            expected_nam12km.HOURLY_PROFILES_PARTIAL_WITH_OFFSET)

    def test_partial_no_offset(self, monkeypatch):
        self.monkeypatch_sun(monkeypatch)
        profiler = arlprofiler.ArlProfile(PROFILE_WITH_ASTERISKS_FILENAME,
            datetime.datetime(2015, 8, 9, 0, 0), # first
            datetime.datetime(2015, 8, 9, 0, 0), # start
            datetime.datetime(2015, 8, 9, 0, 0), # end
            0, # utc offset
            41.77, # lat
            -123.97) # lng
        hourly_profiles = profiler.get_hourly_params()
        self.check_hourly_profiles(hourly_profiles,
            expected_nam12km.HOURLY_PROFILES_PARTIAL_NO_OFFSET)
