from __future__ import annotations

import json
import os
import datetime
from commons.utils import create_folder

# ---------------------------------------------------------------------------------------------------------------------#
#                    Functions to manipulate JSON files information and responses                                      #
# ---------------------------------------------------------------------------------------------------------------------#

# ------------------------------------------------- JSON Functions ----------------------------------------------------#



def load_json_as_dict(json_file_path: str) -> dict:
    with open(json_file_path, 'r') as file:
        return json.load(file)


def read_scenario_from_json(scenario: str, key: str, json_file_path: str):
    with open(json_file_path, 'r') as file:
        json_data = json.load(file)
        if json_data.get(scenario).get(key):
            return json_data.get(scenario).get(key)
        return None


def get_json_keys(json_file_path: str):
    return load_json_as_dict(json_file_path).keys()


def get_json_values(json_file_path: str):
    return load_json_as_dict(json_file_path).values()


def write_json_file(json_object: str, request_name: str) -> None:
    folder_path = os.path.join(os.getcwd(), "json_generated")
    date_time = str(datetime.date.today())
    create_folder(folder_path)
    create_folder(folder_path + "/" + date_time)
    file_path = os.path.join(os.getcwd(), folder_path + "/" + date_time, request_name + ".json")
    with open(file_path, "w") as outfile:
        json.dump(
            json_object.replace('"[', '[').replace(']"', ']').replace(
                '"{ ', '{').replace('}"', '}').replace(' ', '').replace('\n', '').replace('\"', '"'),
            outfile, indent=1, ensure_ascii=False,
        )


def beautify_json(json_template_name: str, json_string: str) -> bytes:
    try:
        return json.dumps(json.loads(json_string), indent=4, ensure_ascii=False).encode('utf8')
    except json.decoder.JSONDecodeError as err:
        body = json_string.replace('"[', '[').replace(']"', ']').replace(
            '"{ ', '{').replace('}"', '}').replace(' ', '').replace('\n', '')
        raise Exception(
            f"Check if the template '{json_template_name}' is malformed and try again."
            f"\nError: {err}"
            f"\nBODY: {body}"
        )


