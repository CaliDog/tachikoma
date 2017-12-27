import json

import dictdiffer
import difflib
import deepdiff
import itertools

from tachikoma.util import TachikomaJSONEncoder


class BaseDiffer(object):
    def diff(self, old_data, new_data):
        raise NotImplementedError("You must implement a diff function in when subclassing {}".format(self.__class__.__name__))

class MultiDiffer(BaseDiffer):
    def diff(self, previous_results, new_results):
        all_keys = set(itertools.chain(previous_results.keys(), new_results.keys()))

        diff_payload = {}

        for key in all_keys:
            old_data = previous_results.get(key, {})
            new_data = new_results.get(key, {})

            unified_diff = "\n".join(list(difflib.unified_diff(
                json.dumps(old_data, indent=4, sort_keys=True, cls=TachikomaJSONEncoder).split("\n"),
                json.dumps(new_data, indent=4, sort_keys=True, cls=TachikomaJSONEncoder).split("\n"),
            )))

            dict_diff = list(dictdiffer.diff(old_data, new_data))

            deep_diff = deepdiff.DeepDiff(old_data, new_data, ignore_order=True, view="tree")

            diff_payload[key] = {
                "unified": unified_diff,
                "dict_diff": list(dict_diff),
                "deep_diff": deep_diff
            }

        return diff_payload