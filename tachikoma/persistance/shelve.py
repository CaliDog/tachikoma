import os
import shelve
import time

from tachikoma.persistance import BasePersistanceMechanism

from functools import lru_cache

class ShelveDB(BasePersistanceMechanism):
    def __init__(self, db_file='/tmp/tachikoma.db'):
        self.db_file = db_file

        if not os.path.exists(self.db_file):
            self.initialize_db()

    def initialize_db(self):
        with shelve.open(self.db_file) as db:
            db['latest-results'] = {}
            db['diffs'] = {}

    @lru_cache(1)
    def get_old_results(self):
        with shelve.open(self.db_file) as db:
            return db['latest-results']

    def store_diffs(self, diffs):
        with shelve.open(self.db_file, writeback=True) as db:
            db['diffs'][time.time()] = diffs

    def store_new_results(self, results):
        with shelve.open(self.db_file, writeback=True) as db:
            db['latest-results'] = results
        self.get_old_results.cache_clear()