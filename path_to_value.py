import hashlib
import json
import os
import utils


class Leaf:
    def __init__(self, repo_type, repo_name, repo_item_name, path, value, stats, file_path):
        self.repo_type = repo_type
        self.repo_name = repo_name
        self.repo_item_name = repo_item_name
        self.path = path
        self.value = value
        self.stats = stats
        self.file_path = file_path


class AggLeaf:
    def __init__(self, path, leaves_path):
        self.path = path
        self.__leaves_path = leaves_path
        self.stats = {}

        serialized_tuple = json.dumps(self.path)
        hash_object = hashlib.sha256(serialized_tuple.encode())
        leaf_file_name = f'{hash_object.hexdigest()}.uniqueext'

        self.leaf_file_path = os.path.join(self.__leaves_path, leaf_file_name)
        self.leaf_file_path = os.path.normpath(self.leaf_file_path)

        self.__leaves = []

    def get_leaves_path(self):
        return self.__leaves_path

    def append_leaf(self, leaf):
        assert isinstance(leaf, Leaf)
        utils.accumulate_stats(self.stats, leaf.stats)
        self.__leaves.append(leaf)

    def get_leaves(self):
        for leaf in self.__leaves:
            yield leaf

    def clear_leaves(self):
        self.__leaves.clear()

    def get_leaves_len(self):
        return len(self.__leaves)


class Agg:
    def __init__(self, path, stats):
        self.path = path
        self.stats = stats
        self.leaves = {}
        self.values = {}


def convert_to_repository_types_paths_export(nodes, repo_type_to_all_repo_items, extract_non_leaves):
    result = []

    for n in nodes:
        assert 'repo_type' in n.stats
        for k in n.stats['repo_type'].keys():

            r = None
            repo_item_names = {dict(item)['repo_item_name'] for item in repo_type_to_all_repo_items.get(k, [])}

            if isinstance(n, Agg):
                if extract_non_leaves:

                    r = {
                        'repo_type': k,
                        'path': n.path,
                        'values_file_path': None,
                        'repo_type_total_values': n.stats['repo_type'][k],
                        'repo_type_missing_values': n.stats['repo_type_missing_values'][k],
                        'repo_type_total_items': len(repo_item_names),
                        'repo_type_items': len(repo_item_names.intersection(set(n.stats['repo_item'].keys()))),
                    }
            elif isinstance(n, AggLeaf):
                r = {
                    'repo_type': k,
                    'path': n.path,
                    'values_file_path': n.leaf_file_path,
                    'repo_type_total_values': n.stats['repo_type'][k],
                    'repo_type_missing_values': n.stats['repo_type_missing_values'][k],
                    'repo_type_total_items': len(repo_item_names),
                    'repo_type_items': len(repo_item_names.intersection(set(n.stats['repo_item'].keys()))),
                }
            else:
                assert False

            if r is not None:
                s = set(key for key in n.stats['repo_type'].keys())
                r['used_by_repo_types'] = sorted(s)
                result.append(r)

    return result


def convert_to_repository_paths_export(nodes, repo_to_all_repo_items, extract_non_leaves):
    result = []

    for n in nodes:
        assert 'repo' in n.stats
        for k in n.stats['repo'].keys():

            r = None
            repo_item_names = {dict(item)['repo_item_name'] for item in repo_to_all_repo_items.get(k, [])}

            if isinstance(n, Agg):
                if extract_non_leaves:
                    r = {
                        'repo': k,
                        'path': n.path,
                        'values_file_path': None,
                        'repo_total_values': n.stats['repo'][k],
                        'repo_missing_values': n.stats['repo_missing_values'][k],
                        'repo_total_items': len(repo_item_names),
                        'repo_items': len(repo_item_names.intersection(set(n.stats['repo_item'].keys()))),
                    }
            elif isinstance(n, AggLeaf):
                r = {
                    'repo': k,
                    'path': n.path,
                    'values_file_path': n.leaf_file_path,
                    'repo_total_values': n.stats['repo'][k],
                    'repo_missing_values': n.stats['repo_missing_values'][k],
                    'repo_total_items': len(repo_item_names),
                    'repo_items': len(repo_item_names.intersection(set(n.stats['repo_item'].keys()))),
                }
            else:
                assert False

            if r is not None:
                s = set(key for key in n.stats['repo'].keys())
                r['used_by_repos'] = sorted(s)
                result.append(r)

    return result


def add_missing_paths_to_leaves(nodes, repo_type_to_all_repo_items, max_value_size_to_flush, delimiter):
    processed_paths = set()

    for n in nodes:
        assert 'repo_type' in n.stats
        for k in n.stats['repo_type'].keys():
            if isinstance(n, AggLeaf):
                repo_item_names = {dict(item)['repo_item_name'] for item in repo_type_to_all_repo_items.get(k, [])}
                r = repo_item_names.difference(repo_item_names.intersection(set(n.stats['repo_item'].keys())))
                if len(r) > 0:
                    assert n.path not in processed_paths
                    agg_leaf_missing_data = None

                    for item_data in repo_type_to_all_repo_items[k]:
                        item_data = dict(item_data)
                        if item_data['repo_item_name'] in r:
                            leaf = Leaf(item_data['repo_type'], item_data['repo_name'], item_data['repo_item_name'], n.path, "<<$$complementDataFile$$>>", stats={}, file_path=item_data['repo_item_file_path'])

                            if agg_leaf_missing_data is None:
                                agg_leaf_missing_data = AggLeaf(n.path, n.get_leaves_path())

                            agg_leaf_missing_data.append_leaf(leaf)

                            if agg_leaf_missing_data.get_leaves_len() >= max_value_size_to_flush:
                                utils.flush_value_to_file(agg_leaf_missing_data, delimiter)
                                agg_leaf_missing_data.clear_leaves()

                    if agg_leaf_missing_data.get_leaves_len() > 0:
                        utils.flush_value_to_file(agg_leaf_missing_data, delimiter)
                        agg_leaf_missing_data.clear_leaves()

                    processed_paths.add(n.path)





