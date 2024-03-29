"""met.arl.arlindexer

This module indexes met data
"""

__author__ = "Joel Dubowy"
__copyright__ = "Copyright 2016, AirFire, PNW, USFS"

import datetime
import json
import logging
import os
import re
import socket
import ssl
import sys
import traceback
from collections import defaultdict

import pymongo

from pyairfire.data import utils as datautils

from .arlfinder import ArlFinder

__all__ = [
    'ArlIndexer',
    'MetFilesCollection',
    'MetDatesCollection'
]

class ArlIndexer(ArlFinder):

    def __init__(self, domain, met_root_dir, **config):
        """Constructor

        args:
         - domain -- domain identifier (ex. 'DRI2km')
         - met_root_dir -- root directory to search under

        config options:
         - mongodb_url -- format:
            'mongodb://[username:password@]host[:port][/[database][?options]]'"
         - output_file -- pathname (relative of absolute) of output file to
            save index data
        (see ArlIndexDB for its config options)
        (see ArlFinder for its config options)
        """
        # ArlFinder takes care of making sure met_root_dir exists
        super(ArlIndexer, self).__init__(met_root_dir, **config)
        self._domain = domain
        self._config = config
        # TODO: In case 'start' and/or 'end' are specified in index,
        #   set self._max_days_out to 0 to ignore directories timestamped
        #   before 'start'?  (prob not, since ultimately we're concerned
        #   with the dates represented in the met files, not what's indicated
        #   in the directory names.)
        #self._max_days_out = 0

    def index(self, start=None, end=None):
        """

        kwargs:
         - start -- only consider met data after this date
         - end -- only consider met data before this date
        """
        start, end = self._fill_in_start_end(start, end)
        date_matcher = self._create_date_matcher(start, end)
        index_files = self._find_index_files(date_matcher)
        arl_files = self._parse_index_files(index_files)
        files_per_hour = self._determine_files_per_hour(arl_files, start, end)
        files = self._determine_file_time_windows(files_per_hour)
        files_per_hour, files = self._filter(files_per_hour, files, start, end)
        index_data = self._analyse(index_files, files_per_hour, files)
        # TODO: if there's a way to get domain boundaries, do it here.
        #   (it can change, so would need to get boundaries for each set
        #   of met files....probably too much pain to be worth it)
        self._write(index_data)

    ##
    ## Filter
    ##

    def _filter(self, files_per_hour, files, start, end):
        if start and end:
            # need to filter files and files_per_hour separately
            # because some files may cross the start and/or end times
            #logging.debug("files (BEFORE): %s", files)
            #logging.debug("files_per_hour (BEFORE): %s", files_per_hour)

            # TODO: self._filter_files shouldn't be necessary; remove call,
            #   method, and unit test

            files = self._filter_files(files, start, end)
            files_per_hour = {k:v for k, v in files_per_hour.items()
                if k >= start and k <= end}
            #logging.debug("files (AFTER): %s", files)
            #logging.debug("files_per_hour (AFTER): %s", files_per_hour)
        return files_per_hour, files

    def _filter_files(self, files, start, end):
        # By this point start and end will either both be defined or not
        if not (start and end):
            return files

        def in_tw(t):
            return t >= start and t <= end

        return [
            f for f in files if in_tw(f['first_hour']) or in_tw(f['last_hour'])
        ]

    ##
    ## start/end validation and filling in
    ##

    # Error messages defined as constants in part for testing purposes
    END_WITHOUT_START_ERR_MSG = "End datetime can't be specified without start"
    START_AFTER_END_ERR_MSG = "Start datetime must be before end"
    def _fill_in_start_end(self, start, end):
        if start or end:
            # Start can be specified without end (which would default to
            # today), but not vice versa
            if not start:
                raise ValueError(self.END_WITHOUT_START_ERR_MSG)
            end = end or datetime.datetime.utcnow()
            if start > end:
                raise ValueError(self.START_AFTER_END_ERR_MSG)
            logging.debug('start: {}'.format(start.isoformat()))
            logging.debug('end: {}'.format(end.isoformat()))

        # else: both as undefined

        return start, end


    ##
    ## Reorganizing data for index
    ##

    # TODO: add '$' after date?
    ALL_DATE_MATCHER = re.compile('.*(\d{10})')

    def _parse_latest_forecast(self, index_files):
        if index_files:
            # index_files should aleady be sorted, but sort again just to be safe
            m = self.ALL_DATE_MATCHER.match(sorted(index_files)[-1])
            if m:
                return datetime.datetime.strptime(m.group(1), '%Y%m%d%H')
        # else return None

    def _analyse(self, index_files, files_per_hour, files):
        # Note: reduce will be removed from py 3.0 standard library; though it
        # will be available in functools, use explicit loop instead
        dates = defaultdict(lambda: [])
        sorted_hours = sorted(files_per_hour.keys())
        for dt in sorted_hours:
            dates[dt.date()].append(dt.hour)
        complete_dates = [d for d in dates if len(dates[d]) == 24]
        partial_dates = list(set(dates) - set(complete_dates))
        server_name = self._config.get('server_name') or socket.gethostname()
        availability = self._determine_availability_time_windows(files)
        data = {
            'server': server_name,
            'domain': self._domain,
            'latest_forecast': self._parse_latest_forecast(index_files),
            'start': sorted_hours[0] if sorted_hours else None,
            'end': sorted_hours[-1] if sorted_hours else None,
            'complete_dates': sorted(complete_dates),
            'partial_dates': sorted(partial_dates),
            'root_dir': self._met_root_dir,
            'files': files,
            'availability': availability
        }

        # TODO: slice and dice data in another way?
        return data

    ##
    ## Writing results to db, file, or stdout
    ##

    def _write(self, index_data):
        # Note: using datautils.format_datetimes instead of defining
        #  a datetime encoder for json.dumps because datautils.format_datetimes
        #  handles formating both keys and values
        index_data = datautils.format_datetimes(index_data)
        if (not self._config.get('mongodb_url')
                and not self._config.get('output_file')):
            sys.stdout.write(json.dumps(index_data, indent=self._config.get('indent')))
        else:
            succeeded = False

            for k in ('mongodb_url', 'output_file'):
                if self._config.get(k):
                    try:
                        m = getattr(self, '_write_to_{}'.format(k))
                        m(index_data)
                        succeeded = True
                    except Exception as e:
                        logging.debug(traceback.format_exc())
                        logging.error("Failed to write to {}: {}".format(
                            ' '.join(k.split('_')), e))
            if not succeeded:
                raise RuntimeError("Failed to record")

    def _write_to_mongodb_url(self, index_data):
        MetFilesCollection(**self._config).update(index_data)
        # TODO: instead of manually invoking update of dates collection
        #   here, use a trigger or have MetFilesCollection.update invoke it
        MetDatesCollection(**self._config).compute_and_save(
            domain=self._domain)
        # TODO: other hierarchies to be stored in mongodb (possibly
        #   maintained via triggers?):
        #   - met > server > date
        #   - met > date > server
        #   - server > met > date
        #   - server > date > met
        #   - date > met > server
        #   - date > server > met

    def _write_to_output_file(self, index_data):
        with open(self._config['output_file'], 'w') as f:
            f.write(json.dumps(index_data, indent=self._config.get('indent')))


class ArlIndexDB(object):

    def __init__(self, mongodb_url=None, **config):
        """Constructor:

        kwargs
         - mongodb_url -- mongodb url
            format 'mongodb://[username:password@]host[:port][/[database][?options]]'"

        config options:
         - mongo_ssl_certfile -- if specified, mongo_ssl_keyfile must be specified too
         - mongo_ssl_keyfile -- if specified, mongo_ssl_certfile must be specified too
         - mongo_ssl_ca_certs -- can be specified instead of mongo_ssl_certfile and
            mongo_ssl_keyfile
        """
        # TODO: raise exception if self.__class__.__name__ == 'ArlIndexDB' ???

        mongodb_url, db_name = self._parse_mongodb_url(mongodb_url)
        ssl_config = self._get_ssl_config(config)
        self.client = pymongo.MongoClient(mongodb_url, **ssl_config)
        self.db = self.client[db_name]

        # 'met_files' collection list available met files
        # per server per domain
        self.met_files = self.client[db_name]['met_files']
        # 'dates' collection lists dates available per domain
        # across  all servers
        self.dates = self.client[db_name]['dates']

        # TODO: is this the appropriate place to call _ensure_indices
        self._ensure_indices(self.met_files)
        self._ensure_indices(self.dates)

    SSL_KEY_AND_CERT_MUST_BOTH_BE_SPECIFIED = (
        "SSL key and cert files must both be specified or neither specified")
    def _get_ssl_config(self, config):
        if bool(config.get('mongo_ssl_certfile')) ^ bool(config.get('mongo_ssl_keyfile')):
            raise ValueError(self.SSL_KEY_AND_CERT_MUST_BOTH_BE_SPECIFIED)

        if config.get('mongo_tls_cafile'):
            return {
                'ssl': True,
                #'tlsAllowInvalidHostnames': True, # Note: makes vulnerable to man-in-the-middle attacks
                'tlsAllowInvalidCertificates': True,
                # 'tlsCertificateKeyFile': config['mongo_tls_certfile'],
                'tlsCAFile': config['mongo_tls_cafile']
            }

        elif config.get('mongo_ssl_certfile') and config.get('mongo_ssl_keyfile'):
            return {
                'ssl': True,
                'ssl_cert_reqs': ssl.CERT_NONE,
                'ssl_certfile': config['mongo_ssl_certfile'],
                'ssl_keyfile': config['mongo_ssl_keyfile']
            }

        elif config.get('mongo_ssl_ca_certs'):
            return {
                'ssl': True,
                'ssl_cert_reqs': ssl.CERT_NONE,
                'ssl_ca_certs': config['mongo_ssl_ca_certs']
            }

        else:
            return {}

    DEFAULT_DB_NAME = 'arlindex'
    DEFAULT_DB_URL = 'mongodb://localhost/{}'.format(DEFAULT_DB_NAME)
    MONGODB_URL_MATCHER = re.compile(
        "^mongodb://((?P<username>[^:/]+):(?P<password>[^:/]+)@)?"
        "(?P<host>[^/@]+)(:(?P<port>[0-9]+))?(/(?P<db_name>[^?/]+)?)?"
        "/?(\?(?P<query_string>.+)?)?$")
    INVALID_MONGODB_URL_ERR_MSG = "Invalid mongodb url"
    @classmethod
    def _parse_mongodb_url(cls, mongodb_url):
        """Parses db name out of mongodb url and sets db name if not defined
        in the url.

        Implemented as a classmethod in part for testability
        TODO: implement at module level function?  maybe move to pyairfire?
        """
        if not mongodb_url:
            mongodb_url = cls.DEFAULT_DB_URL
            db_name = cls.DEFAULT_DB_NAME

        else:
            # insert default database name to url if not already defined
            m = cls.MONGODB_URL_MATCHER.match(mongodb_url)
            if not m:
                raise ValueError(cls.INVALID_MONGODB_URL_ERR_MSG)

            db_name = m.group('db_name')
            if not db_name:
                db_name = cls.DEFAULT_DB_NAME
                # Hacky but simple way to insert db_name
                parts = mongodb_url.split('?')
                mongodb_url = os.path.join(parts[0], db_name)
                if len(parts) > 1:
                    mongodb_url = '?'.join([mongodb_url] + parts[1:])
            logging.debug('mongodb url: %s', mongodb_url)
            logging.debug('db name: %s', db_name)

        return mongodb_url, db_name

    def _ensure_indices(self, collection):
        # handle 'INDEXED_FIELDS' not being defined for a collection
        fields = getattr(self, 'INDEXED_FIELDS', [])
        for f in fields:
            collection.create_index(f)

class MetFilesCollection(ArlIndexDB):

    INDEXED_FIELDS = ['server', 'domain']

    def update(self, index_data):
        """Updates the set of arl files on record **for a particular
        domain on a specific server**.
        """
        if not index_data.get('server') or not index_data.get('domain'):
            raise ValueError("Index data must define 'server' and 'domain'")

        # we want to update or insert
        query = {'server': index_data['server'], 'domain': index_data['domain']}
        self.met_files.update_one(query, {'$set': index_data}, upsert=True)

    def find(self, **query):
        """Find available files, by server and domain
        """
        r = self.met_files.find(filter=query)
        return [e.pop('_id') and e for e in r]

    def clear(self):
        self.met_files.delete_many({})

class MetDatesCollection(ArlIndexDB):

    INDEXED_FIELDS = ['domain']

    # TODO: build aggregation into the db as a trigger
    def compute(self, domain=None):
        date_info_by_domain = {}
        query = {'domain': domain} if domain else {}
        for d in self.met_files.find(query):
            if d['domain'] not in date_info_by_domain:
                date_info_by_domain[d['domain']] = {
                    'latest_forecast': d['latest_forecast'],
                    'complete_dates': set(d['complete_dates']),
                    'partial_dates': set(d['partial_dates']),
                    'start': d['start'],
                    'end': d['end']
                }

            else:
                date_info = date_info_by_domain[d['domain']]
                for k in ('complete_dates', 'partial_dates'):
                    date_info[k].update(d[k])
                for k, f in (('start', min), ('end', max), ('latest_forecast', max)):
                    if date_info[k] and d[k]:
                        date_info[k] = f(date_info[k], d[k])
                    elif d[k]:
                        date_info[k] = d[k]
                    # else leave date_info[k] as is

        # iterate through domains, removing from partial_dates any dates
        # that are in complete_dates, and create record for domain
        to_save = []
        for domain, date_info in date_info_by_domain.items():
            partial_dates = sorted(list(date_info['partial_dates']
                - date_info['complete_dates']))
            complete_dates = sorted(list(date_info['complete_dates']))
            to_save.append({
                'domain': domain,
                'complete_dates': complete_dates,
                'partial_dates': partial_dates,
                'start': date_info['start'],
                'end': date_info['end'],
                'latest_forecast': date_info['latest_forecast']
            })
        return to_save

    def compute_and_save(self, domain=None):
        """Updates the dates information across all servers
        """
        to_save = self.compute(domain=None)

        # TODO: is there a way to do a bulk write, opting for upsert
        #  on each item in to_save?
        for d in to_save:
            self.dates.update_one({'domain': d['domain']}, {'$set': d}, upsert=True)
        return to_save

    def find(self, domain=None):
        """Find available dates, by domain or across all dates
        """
        query = {'domain': domain} if domain else {}
        r = self.dates.find(filter=query)
        return [e.pop('_id') and e for e in r]

    def clear(self):
        self.dates.delete_many({})
