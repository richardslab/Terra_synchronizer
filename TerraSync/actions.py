import json
import os
from pprint import pprint
from google.cloud import storage
from NameFilter import NameFilter
from constants import *
import firecloud.api as fapi
from typing import List

from utils import filter_attributes, localize_possible_uri, transpose_double_dict
from os.path import exists


def process_query(query, data):
    pprint(query)
    if len(data) != 0:
        raise Exception(f"Input data has {len(data)} rows that will be over-written. Cowardly refusing to continue.")
    r = fapi.get_entities(namespace=query[NAMESPACE], workspace=query[WORKSPACE],
                          etype=query[ENTITY])

    data = json.loads(r.content)
    print(f"Found {len(data)} rows.")
    return data


def process_subset(subset, data: List[dict]):
    pprint(subset)
    values = subset[VALUES] if VALUES in subset else []
    regexps = subset[REGULAR_EXPRESSIONS] if REGULAR_EXPRESSIONS in subset else []

    filter_ = NameFilter(values=values, regexps=regexps)
    data = [datum for datum in data if filter_.filter(datum[NAME])]
    print(f"Found {len(data)} rows.")
    return data


def process_sample(sample, data):
    pprint(sample)
    if HEAD in sample:
        head = sample[HEAD]
        print(f"Taking first {head} rows from data")
        data = data[0:sample[HEAD]]
        print(f"Found {len(data)} rows.")

    else:
        raise Exception(f"Action '{SAMPLE}' needs field '{HEAD}':" + str(sample))
    return data


def process_select(select, data):
    pprint(select)

    values = select[VALUES] if VALUES in select else []
    regexps = select[REGULAR_EXPRESSIONS] if REGULAR_EXPRESSIONS in select else []

    filter_ = NameFilter(values=values, regexps=regexps)

    data = [filter_attributes(datum, filter_.filter) for datum in data]
    print(f"Found {len(data)} rows.")
    if data:
        print(f"Found {len(data[0][ATTRIBUTES])} attributes in the first row of the data.")
    return data


def process_write(write, data):
    target = write[OUTPUT]
    overwrite = OVERWRITE in write and bool(write[OVERWRITE])
    if exists(target) and not overwrite:
        raise Exception(f"Output file {target} already exists. Add 'overwrite: True' to the 'localize' action in the "
                        f"configuration or change the output location.")
    with open(target, 'wt') as file:
        print(f"writing {len(data)} rows to {target}.")
        file.write(json.dumps(data, indent=4))
    return data


def process_localize(localize, data: List[dict]):
    attributes = {k for datum in data for k in datum[ATTRIBUTES]}

    attribute_map = {k: k for k in attributes}
    if MAP in localize:
        print(f"The following attributes will be localized to different paths: {localize[MAP]}")
        attribute_map.update(localize[MAP])

    client = storage.Client()

    localize_files: bool = ACTUALLY_LOCALIZE not in localize or bool(localize[ACTUALLY_LOCALIZE])

    new_attributes = [
        {key: localize_possible_uri(client,
                                    value,
                                    os.path.join(localize[DIRECTORY], datum[NAME], attribute_map[key]),
                                    localize_files) for
         key, value in datum[ATTRIBUTES].items()}
        for
        datum in data]

    # remove Nones
    filtered_attributes = [{key: value for key, value in datum.items() if value is not None} for datum in
                           new_attributes]

    data_and_attributes = zip(data, filtered_attributes)
    data = [{**datum, **transpose_double_dict(new_attr)} for datum, new_attr in data_and_attributes]

    return data


def process_config(config_):
    data = []
    process_switch = {
        QUERY: process_query,
        SUBSET: process_subset,
        SAMPLE: process_sample,
        SELECT: process_select,
        WRITE: process_write,
        LOCALIZE: process_localize
    }

    for action in config_:
        if NAME in action:
            print(action[NAME])
        if ACTION not in action:
            raise Exception("expecting an 'action' element in each entry of the config:" + str(action))
        if action[ACTION] in process_switch:
            data = process_switch[action[ACTION]](action, data)
        else:
            raise Exception("Don't know how to deal with action: %s" % action[ACTION])

    # TODO: convert this to an action.
    pprint(data)
