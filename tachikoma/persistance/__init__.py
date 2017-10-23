
class BasePersistanceMechanism(object):
    def initialize_db(self):
        raise NotImplementedError("Your persistance mechanism must create a initialize_db function!")

    def get_old_results(self):
        raise NotImplementedError("Your persistance mechanism must create a get_old_results function!")

    def store_diffs(self, diffs):
        raise NotImplementedError("Your persistance mechanism must create a store_diffs function!")

    def store_new_results(self, results):
        raise NotImplementedError("Your persistance mechanism must create a store_new_results function!")