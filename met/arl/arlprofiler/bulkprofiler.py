import csv
import logging
import os
import uuid

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

    LOCATIONS_INPUT_FILE = 'locations.csv'

    def _set_location_info(self, locations):
        self._locations = locations
        for l in self._locations:
            if not l.get('id'):
                l['id'] = uuid.uuid4()
            if not l.get('latitude') and l.get('lat'):
                l['latitude'] = l['lat']
            if not l.get('longitude') and l.get('lng'):
                l['longitude'] = l['lng']

    def _get_command(self, met_dir, met_file_name, wdir, output_file_name):
        input_file_name = self._write_input_file(wdir)

        # Note: there must be no space between each option and it's value
        # Note: '-w2' indicates wind direction, instead of components
        return "{exe} -d{dir} -f{file} -w2 -t{time_step} -i{input} -p{output}".format(
            exe=self._profile_exe, dir=met_dir, file=met_file_name,
            time_step=self._time_step, input=input_file_name,
            output=output_file_name)

    def _write_input_file(self, wdir):
        """Writes locations file with the following format:
        id,latitude,longitude
        fire1,39.7594327122312,-121.79589795303
        fire2,39.7031935450582,-121.777010952899
        fire3,39.8120322635477,-121.769338567569
        ...
        """
        filename = os.path.join(wdir, self.LOCATIONS_INPUT_FILE)
        with open(filename, 'w') as f:
            csv_writer = csv.DictWriter(f,
                fieldnames=['id', 'latitude', 'longitude'])
            csv_writer.writeheader()

            for l in self._locations:
                if not l.get('latitude') or not l.get('longitude'):
                    logging.warn("location missing latitude or longitude")
                    # TODO: fail?
                else:
                    csv_writer.writerow(l)
        return filename

    def _load(self, full_path_profile_txt, first, start, end, utc_offset):
        pass
