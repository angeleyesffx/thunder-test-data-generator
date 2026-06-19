from __future__ import annotations

import logging
from datetime import datetime, timedelta
import random
import uuid
from faker import Faker

logger = logging.getLogger(__name__)


def generate_random_number(number_of_digits: int) -> str:
    if not number_of_digits:
        number_of_digits = 1
    begin = int('1' + '0' * (number_of_digits - 1))
    end = int('9' * number_of_digits)
    return str(random.randrange(begin, end))


def define_country_fake_data(country: str) -> str:
    country_language_map = {
        "ar": "es_AR",
        "aq": "en",
        "bo": "es",
        "br": "pt_BR",
        "ca": "en_CA",
        "cl": "es_CL",
        "co": "es_CO",
        "de": "de_DE",
        "do": "es",
        "ec": "es",
        "fr": "fr_FR",
        "gb": "en_GB",
        "hn": "es",
        "jp": "ja_JP",
        "kr": "ko-KR",
        "mx": "es_MX",
        "pa": "es",
        "pe": "es",
        "pt": "pt_PT",
        "py": "es",
        "sv": "es",
        "tz": "en",
        "ug": "en",
        "uy": "es",
        "us": "en_US",
        "za": "en_ZA"
    }
    return country_language_map.get(country, "en")


def random_data_generator(param_dict: dict, language: str) -> dict:
    fake = Faker(language)

    def custom_id_generator(pattern):
        if pattern == "" or pattern is None:
            return ''.join(str(uuid.uuid4()))
        chars_number = int(pattern)
        return ''.join(str(generate_random_number(chars_number)))

    def custom_date_generator(days):
        if days == "" or days is None:
            days = "1"
        date = datetime.today() + timedelta(days=(int(days) - 1))
        return date.strftime("%Y-%m-%d")

    pattern_types = {
        'account_id': lambda prefix: "AC-" + prefix + str(generate_random_number(10)),
        'account_name': lambda _: fake.company() + "." + fake.company_suffix(),
        'address': lambda _: fake.street_suffix() + " " + fake.street_name(),
        'city': lambda _: fake.city(),
        'company_name': lambda _: fake.company() + "." + fake.company_suffix(),
        'country': lambda _: fake.country(),
        'country_code': lambda _: fake.country_code(),
        'cnpj': lambda _: fake.cnpj().replace(".", "").replace("/", "").replace("-", ""),
        'cpf': lambda _: fake.cpf().replace(".", "").replace("-", ""),
        'currency': lambda _: fake.currency_code(),
        'date': custom_date_generator,
        'dcc_id': lambda _: "DC-" + str(uuid.uuid4()),
        'deal_id': lambda prefix: "DEAL-" + prefix + str(generate_random_number(10)),
        'email': lambda _: 'test_email_' + str(uuid.uuid4().hex) + '@example.com',
        'first_name': lambda _: fake.first_name(),
        'float': lambda _: round(random.uniform(1.0, 999.9), 2),
        'id': custom_id_generator,
        'integer': lambda pattern: generate_random_number(int(pattern)),
        'last_name': lambda _: fake.last_name(),
        'name': lambda _: fake.first_name() + " " + fake.last_name(),
        'name_prefix': lambda _: fake.prefix(),
        'name_suffix': lambda _: fake.suffix(),
        'number': lambda pattern: generate_random_number(int(pattern)),
        'order_id': lambda prefix: "OR-" + prefix.upper() + "-" + str(uuid.uuid4().hex) + "-" + str(uuid.uuid4().hex),
        'phone': lambda _: fake.msisdn(),
        'state': lambda _: fake.state(),
        'state_abbr': lambda _: fake.state_abbr(),
        'startDate': custom_date_generator,
        'street': lambda _: fake.street_name(),
        'street_number': lambda _: fake.building_number(),
        'ssn': lambda _: fake.ssn(),
        'uuid': lambda _: str(uuid.uuid4()),
        'uuid_hex': lambda _: uuid.uuid4().hex,
        'vendor_account_id': custom_id_generator,
        'zipcode': lambda _: fake.postcode()
    }

    for key, value_type in param_dict.items():
        prefix, _, pattern = value_type.partition('|')
        generator = pattern_types.get(prefix)

        if generator is not None:
            param_dict[key] = generator(pattern)
        else:
            logger.warning('Unknown type "%s" for key "%s". Add it to random_data_generator.', value_type, key)

    return param_dict


def create_param_dict(params: str | None) -> dict | None:
    if params not in {None, ''}:
        return {key.strip(): value.strip() for key, value in (element.split(':', 1) for element in params.split(','))}
    return None
