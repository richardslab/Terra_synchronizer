# This is a sample Python script.

# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.
import firecloud.api as fapi
import yaml
import json
import re
from pprint import pprint


def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press ⌘F8 to toggle the breakpoint.


def get_config(where: str):
    with open(where, "tr") as file:
        config = yaml.safe_load(file)

    pprint(config)
    return (config)


def entity_filter(config):
    row_set: set = set(config["rows"]["values"])
    re_set = set([re.compile(re_text) for re_text in config["rows"]["regexps"]])

    def filter_name_(name):
        if name in row_set:
            return True
        for re_compiled in re_set:
            if re_compiled.match(name):
                return True
        return False

    return filter_name_


def get_entities(config_file, namespace, workspace):
    config = get_config("config.yml")

    r = fapi.get_entities(namespace=namespace, workspace=workspace, etype=config["rows"]["entity"])
    j = json.loads(r.content)

    entityFilter = entity_filter(config)

    output = [entity for entity in j if entityFilter(entity["name"])]
    pprint(output)
    return output


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print_hi('PyCharm')
    entities = get_entities("config.yml", "brent-billing-project", "covid_RNA_qtl_v2")
    pprint(entities)
# See PyCharm help at https://www.jetbrains.com/help/pycharm/
