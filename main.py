import json
import os
from pathlib import Path

import utils
from consolidate_paths import extract_full_tree, aggregate_leaves
from path_encodings import DICT, LIST, LIST_KEY, ROOT
from path_to_value import Leaf, convert_to_repository_types_paths_export, Agg, AggLeaf, \
    convert_to_repository_paths_export, add_missing_paths_to_leaves


def extract_paths_to_values(file_path, leaves, repo_type, repo_name, repo_item_name, data, running_path):
    if isinstance(data, dict):
        for k, v in data.items():
            next_path = (*running_path, DICT, str(k))
            extract_paths_to_values(file_path, leaves, repo_type, repo_name, repo_item_name, v, next_path)
    elif isinstance(data, list):
        for item in data:
            next_path = (*running_path, LIST, LIST_KEY)
            extract_paths_to_values(file_path, leaves, repo_type, repo_name, repo_item_name, item, next_path)
    else:
        stats = {}

        missing_value = 0
        if utils.is_value_missing(data):
            missing_value = 1

        stats['repo_item'] = {repo_item_name: 1}
        stats['repo_item_missing_values'] = {repo_item_name: missing_value}

        stats['repo_type'] = {repo_type: 1}
        stats['repo_type_missing_values'] = {repo_type: missing_value}

        stats['repo'] = {repo_name: 1}
        stats['repo_missing_values'] = {repo_name: missing_value}

        leaves.append(
            Leaf(repo_type, repo_name, repo_item_name, running_path, str(data), stats, file_path)
        )


def get_all_nodes(n, result):
    if isinstance(n, Agg):
        result.append(n)

        for lf in n.leaves.values():
            get_all_nodes(lf, result)
        for lf in n.values.values():
            get_all_nodes(lf, result)
    elif isinstance(n, AggLeaf):
        result.append(n)

    else:
        assert False

directory_path = 'C:/PythonProjects/Lunaris/metadataExplorer/data'

max_value_size_to_flush = 1000
delimiter = ";"


# clear leaves directory
repo_leaves_path = os.path.join(directory_path, 'leaves')
os.makedirs(repo_leaves_path, exist_ok=True)
utils.delete_all_files(repo_leaves_path)

repo_type_to_all_repo_items = {}
repo_to_all_repo_items = {}
all_repos_all_agg_leaves = {}
for repo_type_and_repo_name in os.listdir(directory_path):
    repo_path = os.path.join(directory_path, repo_type_and_repo_name)
    if os.path.isdir(repo_path):
        if repo_type_and_repo_name == 'leaves':
            continue

        for repo_item_name in os.listdir(repo_path):
            file_path = os.path.join(repo_path, repo_item_name)
            file_path = os.path.normpath(file_path)

            if not os.path.isfile(file_path):
                continue
            if 'merged' in repo_item_name:
                continue

            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    d = json.load(file)
            except Exception as e:
                print(f"An error occurred: {e}")

            repo_type, repo_name = utils.extract_repo_name_parts(repo_type_and_repo_name)
            repo_item_name = Path(repo_item_name).stem

            leaves = []
            extract_paths_to_values(file_path, leaves, repo_type, repo_name, repo_item_name, d, running_path=(ROOT,))
            aggregate_leaves(all_repos_all_agg_leaves, leaves, repo_leaves_path, max_value_size_to_flush, delimiter)

            repo_item_data = frozenset({
                'repo_item_file_path': file_path,
                'repo_item_name': repo_item_name,
                'repo_type': repo_type,
                'repo_name': repo_name,
            }.items())

            if repo_type not in repo_type_to_all_repo_items:
                repo_type_to_all_repo_items[repo_type] = {repo_item_data}
            else:
                repo_type_to_all_repo_items[repo_type].add(repo_item_data)

            if repo_name not in repo_to_all_repo_items:
                repo_to_all_repo_items[repo_name] = {repo_item_data}
            else:
                repo_to_all_repo_items[repo_name].add(repo_item_data)

        for alf in all_repos_all_agg_leaves.values():
            if alf.get_leaves_len() > 0:
                utils.flush_value_to_file(alf, delimiter)
                alf.clear_leaves()


full_tree_root = extract_full_tree(all_repos_all_agg_leaves.values())

agg_nodes = []
get_all_nodes(full_tree_root, agg_nodes)

add_missing_paths_to_leaves(agg_nodes, repo_type_to_all_repo_items, max_value_size_to_flush, delimiter)

r = convert_to_repository_types_paths_export(agg_nodes, repo_type_to_all_repo_items, extract_non_leaves=False)
fn = 'repository_types_paths_merged'
# utils.write_json(os.path.join(directory_path, f'{fn}.json'), r)
utils.write_repository_paths_data_to_excel(r, os.path.join(directory_path, f'{fn}.xlsx'), delimiter)

r = convert_to_repository_paths_export(agg_nodes, repo_to_all_repo_items, extract_non_leaves=False)
fn = 'repository_paths_merged'
# utils.write_json(os.path.join(directory_path, f'{fn}.json'), r)
utils.write_repository_paths_data_to_excel(r, os.path.join(directory_path, f'{fn}.xlsx'), delimiter)











