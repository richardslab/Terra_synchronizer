import google
import defopt

from actions import process_config
from utils import *


def process_configuration(filename: str = "config.yml"):
    """
        Examine a Terra workspace according to the instructions
        laid out in the provided configuration file

        :param filename: a YAML file containing actions to take with regards to a data table in Terra
        See README.md for more detail
    """
    _, project = google.auth.default()
    if project == "":
        raise Exception("you really need a default (google) project. If you cannot set one up with `gcloud auth "
                        "application-default login` please have the environment variable GOOGLE_CLOUD_PROJECT set to "
                        "your project.")
    config = get_config(filename)
    process_config(config)


if __name__ == '__main__':
    defopt.run(process_configuration)