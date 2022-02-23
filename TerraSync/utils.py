import base64
import os
from pathlib import Path
from pprint import pprint

import google_crc32c
import yaml
from tqdm.auto import tqdm

from constants import *
from typing import Dict


def transpose_double_dict(double_dictionary: Dict[str,Dict]):
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


def get_config(where: str):
    with open(where, "tr") as file:
        config_ = yaml.safe_load(file)
    pprint(config_)
    return config_


def get_google_crc32(path):
    crc_read = google_crc32c.Checksum()
    with open(path, "rb") as file:
        f_crc = crc_read.consume(stream=file, chunksize=CRC_CHUNCKSIZE)
        for _ in f_crc:
            pass
    return base64.b64encode(crc_read.digest()).decode("utf-8")


def possibly_localize_blob(blob, path):
    if os.path.isfile(path) and os.path.exists(path):
        print(f"checking crc for {path}")
        crc32_string = get_google_crc32(path)
        if crc32_string == blob.crc32c:
            print(f"Not downloading since crc32 values match.")
            return crc32_string
        else:
            print(f"crc32 mismatch ({crc32_string} != {blob.crc32c})")

    print(f"Going to write blob to {path}")
    Path(os.path.dirname(path)).mkdir(parents=True, exist_ok=True)

    with open(path, 'wb') as f:
        with tqdm.wrapattr(f, "write", total=blob.size) as file_obj:
            blob.download_to_file(file_obj)
    crc32_string = get_google_crc32(path)
    if crc32_string != blob.crc32c:
        raise Exception(f"file written crc {crc32_string} doesn't match blob's {blob.crc32c}")
    return crc32_string


def localize_possible_uri(client, datum, key, value, local_path):
    if type(value) == str:
        try:
            bucket, blob = split_gs_uri(value)
        except Exception:
            return None
        blob = client.get_bucket(bucket).get_blob(blob)

        print(f"found blob {blob.name} in bucket {blob.bucket.name} with crc32 = '{blob.crc32c}'")
        local_path = os.path.join(os.path.join(local_path, datum[NAME], key), os.path.basename(blob.name))
        crc32 = possibly_localize_blob(blob, local_path)
        assert crc32 == blob.crc32c
        return {CRC32: crc32, LOCAL_PATH: local_path}


def filter_attributes(datum: dict, filter_):
    if ATTRIBUTES not in datum:
        raise Exception(f"Cannot find key '{ATTRIBUTES}' in datum: {datum}")
    datum[ATTRIBUTES] = {k: v for k, v in datum[ATTRIBUTES].items() if filter_(k)}
    return datum
