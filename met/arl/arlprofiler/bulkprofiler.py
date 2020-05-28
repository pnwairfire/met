from .base import ArlProfilerBase

# From Rober re. fires that are outside grid:
#
# it doesn't die when the location is off the grid....what it does is
# in the line that starts each profile, like:
#
#  Profile:       1   41.4280 -121.1127  (154,495)
#
# it will look like this instead:
#
#  Profile:      -2   41.4554 -107.1011  (736,546)
#
# where the number is negative (and all the values are bs)...i might
# be trying to pull data from outside the array so that is likely a
# bad idea but it does flag them in a round-about-way.

class ArlBulkProfiler(ArlProfilerBase):
    pass
