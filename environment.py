from __future__ import annotations

import logging
import os
from collections import defaultdict
import yaml
import argparse
import random
import sys
from dotenv import load_dotenv

from commons.randomGenerator import create_param_dict, define_country_fake_data, random_data_generator

load_dotenv()

logger = logging.getLogger(__name__)


class Config(object):
    def __init__(self, environment, flow, config_yaml, countries, services, methods, versions, execute, ssl_verify):
        self.environment = environment
        self.flow = flow
        self.config_yaml = config_yaml
        self.countries = countries
        self.services = services
        self.methods = methods
        self.versions = versions
        self.execute = execute
        self.ssl_verify = ssl_verify


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-CONFIG_YAML', help='config yaml', dest='config_yaml')
    parser.add_argument('-ENV', help='environment', dest='environment')
    parser.add_argument('-COUNTRIES', help='countries', dest='countries')
    parser.add_argument('-services', help='services', dest='services')
    parser.add_argument('-METHODS', help='methods', dest='methods')
    parser.add_argument('-VERSIONS', help='versions', dest='versions')
    parser.add_argument('-FLOW', help='flow', dest='flow')
    parser.add_argument('-e', '--execute', action='store_true', help='enable the long listing format')
    parser.add_argument('--no-ssl-verify', action='store_true', dest='no_ssl_verify',
                        help='disable SSL certificate verification (use only for internal/self-signed environments)')
    parser.add_argument('-v', '--verbose', action='store_true', dest='verbose',
                        help='enable debug-level logging')
    return parser.parse_args(sys.argv[1:])


args = parse_args()


def read_yml_file(yml_file_name):
    file_path = os.path.dirname(__file__) + "/" + yml_file_name + ".yml"
    if os.path.exists(file_path):
        with open(file_path) as file:
            return yaml.full_load(file)
    else:
        raise FileNotFoundError("File does not exist in the path {0}".format(file_path))


def select_the_config_file(config_yaml):
    if config_yaml is None:
        config_file = read_yml_file("config")
        return config_file
    else:
        config_file = read_yml_file(config_yaml)
        return config_file


def select_the_environment(environment, config_yaml):
    environments = select_the_config_file(config_yaml)
    if environment is None:
        logger.info("Executing DataCreation in SIT environment...")
        return environments.get("sit")
    else:
        logger.info("Executing DataCreation in %s environment...", environment)
        return environments.get(environment)


def select_the_execution_flow(flow):
    if flow is not None:
        config_flow_file = read_yml_file("flow/config_flow")
        return config_flow_file
    else:
        return None


config = Config(select_the_environment(args.environment, args.config_yaml), select_the_execution_flow(args.flow),
                select_the_config_file(args.config_yaml), args.countries, args.services, args.methods, args.versions,
                args.execute, not args.no_ssl_verify)


def check_for_error_ir_order(execution_flows):
    flow_counter_list = defaultdict(list)
    for execution_flow in execution_flows:
        flow_counter_list[execution_flow[1]['execution_order']].append(execution_flow[0])

    for flow_order, flow_names in flow_counter_list.items():
        if len(flow_names) > 1:
            logger.warning(
                "Flows with same execution_order '%s': %s", flow_order, ', '.join(flow_names))


def get_countries():
    # Get a list of Countries
    countries_list = config.countries
    if countries_list is None:
        countries = set()
        countries.update(config.environment.get("countries"))
        return sorted(countries)
    else:
        countries = countries_list.split(",")
        return countries


def get_services(country):
    # Get a list of services
    services_list = config.services
    if services_list is None and config.flow is None:
        services = set()
        services.update(config.environment.get("countries").get(country).get("services"))
        return sorted(services)
    elif services_list is None and config.flow is not None:
        execution_flow = list(config.flow.get("execution_flows").get(args.flow).items())
        check_for_error_ir_order(execution_flow)
        execution_flow.sort(key=lambda e: e[1].get('execution_order', 0))
        return [value[0] for value in execution_flow]
    else:
        services = services_list.split(",")
        return services


def get_methods(country, service):
    # Get a list of Methods
    methods_list = config.methods
    if methods_list is None and config.flow is None:
        methods = set()
        methods.update(config.environment.get("countries").get(country).get("services").get(service))
        return sorted(methods)
    elif methods_list is None and config.flow is not None:
        service_methods = config.flow.get("execution_flows").get(args.flow).get(service).copy()
        service_methods.pop('execution_order')
        return sorted(service_methods.keys())
    else:
        methods = methods_list.split(",")
        return methods


def get_versions(country, service, method):
    # Get a list of Versions
    versions_list = config.versions
    if versions_list is None and config.flow is None:
        versions = set()
        versions.update(
            config.environment.get("countries").get(country).get("services").get(service).get(method).get("versions"))
        return sorted(versions)
    elif versions_list is None and config.flow is not None:
        versions = set()
        versions.update(config.flow.get("execution_flows").get(args.flow).get(service).get(method))
        return sorted(versions)
    else:
        versions = versions_list.split(",")
        return versions


def get_environment_basic_config(key):
    config_env = config.environment.get(key)
    return config_env


def get_execute_flag():
    return config.execute


def get_ssl_verify():
    return config.ssl_verify


def get_config_from_country(country, key):
    config_country = config.environment.get("countries").get(country).get(key)
    return config_country


def get_config_from_service(country, service, key):
    config_service = config.environment.get("countries").get(country).get("services").get(service).get(key)
    return config_service


def get_config_from_method(country, service, method, key):
    config_method = config.environment.get("countries").get(country).get("services").get(service).get(method).get(key)
    return config_method


def get_config_from_version(country, service, method, version, key):
    config_version = config.environment.get("countries").get(country).get("services").get(service).get(method).get(
        "versions").get(
        version).get(key)
    return config_version


def check_if_config_country_exist(country):
    return config.environment.get("countries").get(country) is not None


def check_if_config_service_exist(country, service):
    return config.environment.get("countries").get(country).get("services").get(service) is not None


def check_if_config_method_exist(country, service, method):
    return config.environment.get("countries").get(country).get("services").get(service).get(method) is not None


def check_if_config_version_exist(country, service, method, version):
    return config.environment.get("countries").get(country).get("services").get(service).get(method).get(
        "versions").get(version) is not None


def get_timezone(country):
    timezone = config.environment.get("countries").get(country).get("timezone")
    if timezone:
        return timezone
    return "America/Louisville"


def get_base_url(country, service, method, version):
    url = str(get_environment_basic_config("base_url")) + str(get_url(country, service, method, version))
    return url


def get_zip_payload(country, service, method, version):
    zip_payload = get_config_from_version(country, service, method, version, 'zip_payload')
    return zip_payload


def is_request_through_middleware_api(country, service, method):
    request_through_middleware_api = get_config_from_method(country, service, method, "request_through_middleware_api")
    return request_through_middleware_api


def _get_auth_field(country: str, service: str, method: str, field: str, method_key: str | None = None) -> str:
    if is_request_through_middleware_api(country, service, method):
        return str(get_config_from_country(country, f"middleware_api_{field}"))
    return str(get_config_from_method(country, service, method, method_key or field))


def get_auth_token(country, service, method):
    return _get_auth_field(country, service, method, "auth_token")


def get_auth_token_type(country, service, method):
    return _get_auth_field(country, service, method, "auth_token_type")


def get_vendor_id(country, service, method):
    return _get_auth_field(country, service, method, "vendor_id", method_key="auth_vendor_id")


def get_auth_type(country, service, method):
    return _get_auth_field(country, service, method, "auth_type")


def get_auth_method(country, service, method):
    return _get_auth_field(country, service, method, "auth_method")


def get_auth_url(country, service, method):
    return _get_auth_field(country, service, method, "auth_url")


def get_auth_scope(country, service, method):
    return _get_auth_field(country, service, method, "auth_scope")


def get_auth_grant_type(country, service, method):
    return _get_auth_field(country, service, method, "auth_grant_type")


def get_auth_client_id(country, service, method):
    return _get_auth_field(country, service, method, "auth_client_id")


def get_auth_client_secret(country, service, method):
    return _get_auth_field(country, service, method, "auth_client_secret")


def get_auth_username(country, service, method):
    return _get_auth_field(country, service, method, "auth_username")


def get_auth_password(country, service, method):
    return _get_auth_field(country, service, method, "auth_password")


def get_auth_response_type(country, service, method):
    return _get_auth_field(country, service, method, "auth_response_type")


def get_auth_payload(country, service, method):
    auth_token_type = get_auth_token_type(country, service, method)
    payload = (
        f"grant_type={get_auth_grant_type(country, service, method)}"
        f"&client_id={get_auth_client_id(country, service, method)}"
        f"&scope={get_auth_scope(country, service, method)}"
        f"&client_secret={get_auth_client_secret(country, service, method)}"
    )
    if str(auth_token_type).upper() != "B2B":
        payload += (
            f"&username={get_auth_username(country, service, method)}"
            f"&password={get_auth_password(country, service, method)}"
            f"&response_type={get_auth_response_type(country, service, method)}"
        )
    return payload


def get_url(country, service, method, version):
    if is_request_through_middleware_api(country, service, method):
        url = get_config_from_version(country, service, method, version, "url")
        return url
    else:
        url = get_config_from_version(country, service, method, version, "value_stream_url")
        return url


def get_supported_languages(country):
    supported_languages = get_config_from_country(country, "supported_languages")
    languages = supported_languages.replace(' ', '').split(",")
    language = random.choice(languages)
    return language


def get_id_prefix(country, service, method, version):
    id_prefix = get_config_from_version(country, service, method, version, "id_prefix")
    return id_prefix



def get_param_keys(country, service, method, version):
    param_keys = get_config_from_version(country, service, method, version, "param_keys")
    if param_keys is not None:
        params = param_keys.replace(" ", "")
        return params


def get_static_params(country, service, method, version):
    static_params = get_config_from_version(country, service, method, version, "static_params")
    if static_params is not None:
        params = static_params.replace(" ", "")
        return params


def create_static_params_dict(static_params):
    # using strip() and split()  methods
    if static_params not in {None, ''}:
        result = dict((key.strip(), value.strip())
                      for key, value in (element.split('=')
                                         for element in static_params.split(',')))
        return result



def get_data_param_keys(country, params, static_params=None):
    language = define_country_fake_data(country)
    new_static_params = create_static_params_dict(static_params)
    param_dict = create_param_dict(params)
    data = None
    if new_static_params is not None:
        for key, value in new_static_params.items():
            param_dict[key] = value
    if param_dict is not None:
        data = random_data_generator(param_dict, language)
    return data


def get_encoding_type(country, service, method, version):
    encoding_type = get_config_from_version(country, service, method, version, "encoding_type")
    return encoding_type


def get_template_name(country, service, method, version):
    template_name = get_config_from_version(country, service, method, version, "template_name")
    return template_name


def get_data_source(country, service, method, version):
    data_name = get_config_from_version(country, service, method, version, "csv_data_source")
    return data_name


def get_csv_strategy(country, service, method, version):
    csv_strategy = get_config_from_version(country, service, method, version, "csv_strategy")
    return csv_strategy


def get_csv_scenario(country, service, method, version):
    csv_scenario = get_config_from_version(country, service, method, version, "csv_scenario")
    if not csv_scenario:
        return None
    scenarios_list = csv_scenario.replace(' ', '').split(",")
    return scenarios_list


def get_amount_data_mass(country, service, method, version):
    amount_data_mass = get_config_from_version(country, service, method, version, "amount_data_mass")
    return amount_data_mass


def get_multiple_line_config(country, service, method, version):
    return get_config_from_version(country, service, method, version, "multiple_line_config")
