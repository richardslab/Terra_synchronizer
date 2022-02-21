import os
from re import Pattern
from tqdm.std import tqdm
import firecloud.api as fapi
import yaml
import json
from pprint import pprint
from constants import *
from pathlib import Path

from google.cloud import storage


def transpose_double_dict(double_dictionary: dict[str, dict]):
    temp = {innerKey: {k: double_dictionary[k][innerKey] for k in double_dictionary if innerKey in double_dictionary[k]}
            for
            outerKey, outerDict in double_dictionary.items() for
            innerKey, innerValue in outerDict.items()}
    return temp


def split_gs_uri(uri: str):
    if not GCS_GS_SCHEMA.match(uri):
        raise Exception(f"Not a gcs schema: {uri}")
    bucket = GCS_GS_BUCKET.match(uri).group(1)
    blob = GCS_GS_BLOB.match(uri).group(1)
    return bucket, blob


class NameFilter:
    def __init__(self, values: list[str], regexps: list[str]):
        self.values = values
        self.regexps = regexps

        self.values_set: set[str] = set(values)
        self.re_set: set[Pattern] = set([re.compile(regexp) for regexp in regexps])

    def filter(self, name):
        if name in self.values_set:
            return True
        for re_compiled in self.re_set:
            if re_compiled.match(name):
                return True
        return False


def get_config(where: str):
    with open(where, "tr") as file:
        config_ = yaml.safe_load(file)
    pprint(config_)
    return config_


def process_query(query, data):
    pprint(query)
    if len(data) != 0:
        raise Exception(f"Input data has {len(data)} rows that will be over-written. Cowardly refusing to continue.")
    r = fapi.get_entities(namespace=query[NAMESPACE], workspace=query[WORKSPACE],
                          etype=query[ENTITY])

    data = json.loads(r.content)
    print(f"Found {len(data)} rows.")
    return data


def process_subset(subset, data: list):
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


def filter_attributes(datum: dict, filter_):
    if ATTRIBUTES not in datum:
        raise Exception(f"Cannot find key '{ATTRIBUTES}' in datum: {datum}")
    datum[ATTRIBUTES] = {k: v for k, v in datum[ATTRIBUTES].items() if filter_(k)}
    return datum


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
    with open(target, 'wt') as file:
        print(f"writing {len(data)} rows to {target}.")
        file.write(json.dumps(data, indent=4))
    return data


def localize_blob(blob, path):
    print(f"going to write blob to {path}")
    Path(os.path.dirname(path)).mkdir(parents=True, exist_ok=True)

    with open(path, 'wb') as f:
        with tqdm.wrapattr(f, "write", total=blob.size) as file_obj:
            # blob.download_to_file is deprecated
            blob.download_to_file(file_obj)
    return blob.crc32c


def localize_possible_uri(client, datum, key, value, local_path):
    if type(value) == str:
        try:
            bucket, blob = split_gs_uri(value)
        except Exception:
            return None
        blob = client.get_bucket(bucket).get_blob(blob)

        print(f"found blob {blob.name} in bucket {blob.bucket.name} with crc32 = '{blob.crc32c}'")
        local_path = os.path.join(os.path.join(local_path, datum[NAME], key), os.path.basename(blob.name))
        crc32 = localize_blob(blob, local_path)
        assert crc32 == blob.crc32c
        return {CRC32: crc32, LOCAL_PATH: local_path}


def process_localize(localize, data: list[dict]):
    local_path = localize[DIRECTORY]
    client = storage.Client()

    new_attributes = [
        {key: localize_possible_uri(client, datum, key, value, local_path) for key, value in datum[ATTRIBUTES].items()}
        for
        datum in data]

    # remove Nones
    filtered_attributes = [{key: value for key, value in datum.items() if value is not None} for datum in
                           new_attributes]

    data_and_attributes = zip(data, filtered_attributes)
    data = [datum | transpose_double_dict(new_attr) for datum, new_attr in data_and_attributes]

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
    pprint(data)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    config = get_config("config.yml")

    process_config(config)
