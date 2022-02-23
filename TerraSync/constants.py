# parts of a workspace
import re

NAMESPACE = "namespace"
WORKSPACE = "workspace"
ENTITY = "entity"

# parts of a filter
VALUES = "values"
REGULAR_EXPRESSIONS = "regexps"
HEAD = "head"

# parts of a write
OUTPUT = "output"
DIRECTORY = "directory"

# parts of a localize
CRC32 = "crc32"
LOCAL_PATH = "local_path"
CRC_CHUNCKSIZE = 65536

# parts of the data
ATTRIBUTES = "attributes"

# actions
ACTION = "action"
NAME = "name"
SAMPLE = "sample"
QUERY = "query"
SUBSET = "subset"
SELECT = "select"
WRITE = "write"
LOCALIZE = "localize"

# REs
# TODO: tighten these greatly (spaces etc...)
GCS_GS_SCHEMA = re.compile("gs://.*")
GCS_GS_BUCKET = re.compile("gs://([^/]*)/.*")
GCS_GS_BLOB = re.compile("gs://[^/]*/(.*)")
