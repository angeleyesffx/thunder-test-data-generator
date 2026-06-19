import os
import json
import jinja2
from commons.csvBuilder import select_csv_strategy
from commons.jsonBuilder import beautify_json
from commons.stringManipulation import split_string_after
from environment import get_execute_flag, get_data_param_keys


# ---------------------------------------------------------------------------------------------------------------------#
#                                        Functions to build body requests                                              #
# ---------------------------------------------------------------------------------------------------------------------#

# ----------------------------------------- Payload Builder Functions -------------------------------------------------#


def create_middleware_apipayload_body(json_template_name, edited_json, service, version):
    if not get_execute_flag():
        payload = get_beautified_payload(json_template_name, edited_json).decode('utf8')
    else:
        payload = str(json.dumps(edited_json.replace('\n', '')))
    template = get_template_from_folder(os.path.join(os.getcwd(), "templates/bodies"), "middleware.json")
    payload_data = {
        "service": service.upper(),
        "version": version,
        "payload": payload
    }
    return template.render(payload_data)


def create_middleware_apipayload(json_template_name, data, multiple_request, service, version):
    edited_json = template_editor(json_template_name, data, multiple_request)
    if multiple_request:
        return [create_middleware_apipayload_body(json_template_name, data, service, version) for data
                in edited_json]
    return create_middleware_apipayload_body(json_template_name, edited_json, service, version)


def create_standard_payload(template_name, data, multiple_request):
    edited_json = template_editor(template_name, data, multiple_request)
    body = get_beautified_payload(template_name, edited_json)
    return body


def create_payload(template_name, data, service, method, version, multiple_request=False, request_through_middleware_api=False):
    if request_through_middleware_api:
        payload = create_middleware_apipayload(template_name, data, multiple_request, service, version)
    elif not request_through_middleware_api and method == "get":
        payload = data
    else:
        payload = create_standard_payload(template_name, data, multiple_request)
    return payload


def get_template_from_folder(folder_path, template_name):
    file_folder = jinja2.FileSystemLoader(searchpath=folder_path)
    template_env = jinja2.Environment(loader=file_folder)
    template = template_env.get_template(template_name)
    return template


def template_editor(json_template_name, data, multiple_request):
    if json_template_name is not None and data is not None:
        json_template = json_template_name + ".json"
        template = get_template_from_folder(os.path.join(os.getcwd(), "templates"), json_template)
        if multiple_request and isinstance(data, list):
            return [template.render(dict_list=[d]) for d in data]
        else:
            return template.render(dict_list=data)
    else:
        return data


def data_and_header_creation(strategy=None, data_source=None, country=None, scenario=None, data_flow=None, param_keys=None, static_params=None, amount_data_mass=None, multiple_line_config=None):
    data = []
    header = []
    count = 1
    if data_source is None and data_flow is None and param_keys is None:
        raise ValueError(f"""
            Something goes wrong. Check in your yaml configuration!
            data_source and data_flow and param_keys can't be None at the same time
        """)
    if not data_source:
        while count <= amount_data_mass:
            # Convert to dict
            generated_params = get_data_param_keys(country, param_keys, static_params)
            if generated_params is not None:
                header.append({key: value for key, value in generated_params.items() if key.startswith('header_')})
                data.append({key: value for key, value in generated_params.items() if not key.startswith('header_')})
            elif generated_params is None and data_flow is not None:
                for index, item in enumerate(data_flow):
                    data_flow_line = data_flow[index]
                    header.append({split_string_after(key, 'header_'): value for key, value in data_flow_line.items() if
                                   key.startswith('header_')})
                    data.append({key: value for key, value in data_flow_line.items() if not key.startswith('header_')})
            else:
                raise ValueError(
                    "Check your config.yml: either 'param_keys' or a FLOW in config_flow.yml must be defined."
                )
            count = count + 1
        return data, header
    else:
        csv_data = select_csv_strategy(country, data_source, strategy, scenario, param_keys, static_params, multiple_line_config)
        for index, item in enumerate(csv_data):
            # Convert to dict
            csv_line = json.loads(csv_data[index])
            header.append({split_string_after(key, 'header_'): value for key, value in csv_line.items() if
                           key.startswith('header_')})
            data.append({key: value for key, value in csv_line.items() if not key.startswith('header_')})
        return data, header


def get_beautified_payload(json_template_name, payload):
    body_list = []
    if not isinstance(payload, list):
        body = payload.replace('\n', '').replace('"[', '[').replace(']"', ']').replace(
            '"{ ', '{').replace('}"', '}')
        if isinstance(payload, dict):
            body = json.dumps(payload)
        return beautify_json(json_template_name, body)
    else:
        for body in payload:
            if isinstance(body, dict):
                body_list.append(beautify_json(json_template_name, json.dumps(body)))
            else:
                body_list.append(beautify_json(json_template_name, body))
        return body_list


