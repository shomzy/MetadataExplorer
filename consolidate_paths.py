from path_encodings import ROOT, DICT
from path_to_value import Agg, AggLeaf
from utils import merge_objects, copy_to_new_stats_instance, accumulate_stats, flush_value_to_file


def consolidated_items_with_same_prefix(repo_paths_to_keys_with_same_prefix):
    assert len(repo_paths_to_keys_with_same_prefix) > 0

    i = 0
    consolidated_items = None

    while i < len(repo_paths_to_keys_with_same_prefix):
        current_path = repo_paths_to_keys_with_same_prefix[i].path
        current_path_item = repo_paths_to_keys_with_same_prefix[i]
        current_prefix = current_path[:-1]

        # each json schema must contain at least a dictionary with 1 key
        assert len(current_path) >= 3
        assert current_path[0] == ROOT and current_path[1] == DICT and isinstance(current_path[2], str)

        if consolidated_items is None:
            stats = copy_to_new_stats_instance(current_path_item.stats)
            consolidated_items = Agg(current_prefix, stats)
            if isinstance(current_path_item, AggLeaf):
                consolidated_items.leaves[current_path] = current_path_item
            else:
                consolidated_items.values[current_path] = current_path_item
        else:
            accumulate_stats(consolidated_items.stats, current_path_item.stats)
            if isinstance(current_path_item, AggLeaf):
                if current_path in consolidated_items.leaves:
                    accumulate_stats(consolidated_items.leaves[current_path].stats, current_path_item.stats)
                else:
                    consolidated_items.leaves[current_path] = current_path_item
            else:
                if current_path in consolidated_items.values:
                    consolidated_items.values[current_path] = merge_objects(consolidated_items.values[current_path], current_path_item)
                else:
                    consolidated_items.values[current_path] = current_path_item

        i = i + 1

    return consolidated_items


def extract_full_tree(agg_leaves):
    while len(agg_leaves) > 0:
        agg_leaves = sorted(agg_leaves, key=lambda x: (-len(x.path[:-1]), x.path[:-1]))

        assert len(agg_leaves[0].path) >= 2
        if len(agg_leaves[0].path) == 2:
            break

        # get paths only with the same prefix
        i = 1
        current_prefix = agg_leaves[0].path[:-1]
        while i < len(agg_leaves):
            if agg_leaves[i].path[:-1] != current_prefix:
                break
            i = i + 1

        paths_with_same_prefix_to_values = agg_leaves[:i]
        agg_leaves = agg_leaves[i:]

        agg_paths = consolidated_items_with_same_prefix(paths_with_same_prefix_to_values)
        agg_leaves.append(agg_paths)

    result = agg_leaves[0]
    return result


def aggregate_leaves(agg_leaves, leaves, leaves_path, max_value_size_to_flush, delimiter):
    for lf in leaves:
        if lf.path in agg_leaves:
            agg_leaves[lf.path].append_leaf(lf)
        else:
            alf = AggLeaf(lf.path, leaves_path)
            alf.append_leaf(lf)
            agg_leaves[lf.path] = alf

        if agg_leaves[lf.path].get_leaves_len() >= max_value_size_to_flush:
            flush_value_to_file(agg_leaves[lf.path], delimiter)
            agg_leaves[lf.path].clear_leaves()











