"""Unit tests for bluesky.arlprofiler"""

__author__ = "Joel Dubowy"
__copyright__ = "Copyright 2016, AirFire, PNW, USFS"

import datetime
import os
import tempfile

from numpy.testing import assert_approx_equal
from pytest import raises
from pyairfire import sun

from met.arl import arlprofiler

from data import (
    profile_one_EXPECTED_OUTPUT as expected_profile_one,
    profile_nam12km_with_asterisks_EXPECTED_OUTPUT as expected_nam12km
)

##
## Tests for ArlProfileParser
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

class BaseTestArlProfileParser(object):

    def check_hourly_profiles(self, actual, expected):
        def check_vals(k, a, e):
            if isinstance(a, float):
                # assert_almost_equal(actual, desired, decimal=7, err_msg='', verbose=True)
                assert_approx_equal(a, e,
                    err_msg="Non-equal {} value: {} != {}".format(k, a, e))
            else:
                assert a == e, "Non-equal {} value: {} != {}".format(k, a, e)

        assert set(expected.keys()) == set(actual.keys())
        for idx in expected:
            assert set(expected[idx].keys()) == set(actual[idx].keys())
            for dt in expected[idx]:
                assert set(expected[idx][dt].keys()) == set(actual[idx][dt].keys())
                for k in expected[idx][dt]:
                    if isinstance(expected[idx][dt][k], list):
                        for i in range(len(expected[idx][dt][k])):
                            check_vals(k, actual[idx][dt][k][i], expected[idx][dt][k][i])
                    else:
                        check_vals(k, actual[idx][dt][k],   expected[idx][dt][k])

    def monkeypatch_sun(self, monkeypatch):
        monkeypatch.setattr(sun.Sun, "sunrise_hr", lambda *args: 13)
        monkeypatch.setattr(sun.Sun, "sunset_hr", lambda *args: 25)
        #monkeypatch.setattr(arlprofiler, "Sun", MockSun)

    # def test_split_hour_pressure_vals(self):
    #     line = '   799   799 -0.68   2.1   7.0  14.7   2.3    307.0 162.0   2.2               \n'
    #     assert [] == ...
    #     line = '   799   799-10.68   2.1   7.0  14.7   2.3    307.0 162.0   2.2               \n'
    #     assert [] == ...


class TestArlProfileParserOne(BaseTestArlProfileParser):

    def test_all_hours_with_offset(self, monkeypatch):
        self.monkeypatch_sun(monkeypatch)
        profiler = arlprofiler.ArlProfileParser(PROFILE_ONE_FILENAME,
            datetime.datetime(2014, 5, 30, 0, 0), # first
            datetime.datetime(2014, 5, 30, 0, 0), # start
            datetime.datetime(2014, 5, 30, 2, 0)) # end
        hourly_profiles = profiler.get_hourly_params()
        self.check_hourly_profiles(hourly_profiles,
            expected_profile_one.HOURLY_PROFILES_ALL_HOURS_WITH_OFFSET)

    def test_partial_with_offset(self, monkeypatch):
        self.monkeypatch_sun(monkeypatch)
        profiler = arlprofiler.ArlProfileParser(PROFILE_ONE_FILENAME,
            datetime.datetime(2014, 5, 30, 0, 0), # first
            datetime.datetime(2014, 5, 30, 1, 0), # start
            datetime.datetime(2014, 5, 30, 1, 0)) # end
        hourly_profiles = profiler.get_hourly_params()
        self.check_hourly_profiles(hourly_profiles,
            expected_profile_one.HOURLY_PROFILES_PARTIAL_WITH_OFFSET)

class TestArlProfileParserNam12kmWithAsterisks(BaseTestArlProfileParser):

    def test_four_hours_with_offset(self, monkeypatch):
        self.monkeypatch_sun(monkeypatch)
        profiler = arlprofiler.ArlProfileParser(PROFILE_WITH_ASTERISKS_FILENAME,
            datetime.datetime(2015, 8, 9, 0, 0), # first
            datetime.datetime(2015, 8, 9, 0, 0), # start
            datetime.datetime(2015, 8, 9, 3, 0)) # end
        hourly_profiles = profiler.get_hourly_params()
        self.check_hourly_profiles(hourly_profiles,
            expected_nam12km.HOURLY_PROFILES_ALL_HOURS_WITH_OFFSET)

    def test_partial_with_offset(self, monkeypatch):
        self.monkeypatch_sun(monkeypatch)
        profiler = arlprofiler.ArlProfileParser(PROFILE_WITH_ASTERISKS_FILENAME,
            datetime.datetime(2015, 8, 9, 0, 0), # first
            datetime.datetime(2015, 8, 9, 0, 0), # start
            datetime.datetime(2015, 8, 9, 0, 0)) # end
        hourly_profiles = profiler.get_hourly_params()
        self.check_hourly_profiles(hourly_profiles,
            expected_nam12km.HOURLY_PROFILES_PARTIAL_WITH_OFFSET)

