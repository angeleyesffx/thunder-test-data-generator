import pytest
from datetime import datetime
from commons.randomGenerator import (
    create_param_dict,
    define_country_fake_data,
    generate_random_number,
    random_data_generator,
)


class TestCreateParamDict:
    def test_parses_multiple_params(self):
        result = create_param_dict("name:name,email:email")
        assert result == {"name": "name", "email": "email"}

    def test_parses_single_param(self):
        result = create_param_dict("key:value")
        assert result == {"key": "value"}

    def test_strips_whitespace(self):
        result = create_param_dict(" name : name , email : email ")
        assert result == {"name": "name", "email": "email"}

    def test_returns_none_for_empty_string(self):
        assert create_param_dict("") is None

    def test_returns_none_for_none_value(self):
        assert create_param_dict(None) is None

    def test_preserves_pipe_pattern_in_value(self):
        result = create_param_dict("account:account_id|TEST")
        assert result == {"account": "account_id|TEST"}


class TestGenerateRandomNumber:
    @pytest.mark.parametrize("digits", [1, 3, 5, 8, 10])
    def test_generates_correct_digit_count(self, digits):
        result = generate_random_number(digits)
        assert len(result) == digits, f"Expected {digits} digits, got {len(result)}"
        assert result.isdigit()

    def test_result_is_string(self):
        assert isinstance(generate_random_number(5), str)

    @pytest.mark.parametrize("boundary", [0, None])
    def test_falsy_value_defaults_to_single_digit(self, boundary):
        result = generate_random_number(boundary)
        assert len(result) == 1
        assert result.isdigit()


class TestDefineCountryFakeData:
    def test_brazil_returns_pt_br(self):
        assert define_country_fake_data("br") == "pt_BR"

    def test_us_returns_en_us(self):
        assert define_country_fake_data("us") == "en_US"

    def test_mexico_returns_es_mx(self):
        assert define_country_fake_data("mx") == "es_MX"

    def test_germany_returns_de_de(self):
        assert define_country_fake_data("de") == "de_DE"

    def test_unknown_country_returns_en(self):
        assert define_country_fake_data("xx") == "en"


class TestRandomDataGenerator:
    def test_generates_valid_email(self):
        result = random_data_generator({"email": "email"}, "en_US")
        assert "@example.com" in result["email"]

    def test_email_is_unique_per_call(self):
        r1 = random_data_generator({"email": "email"}, "en_US")
        r2 = random_data_generator({"email": "email"}, "en_US")
        assert r1["email"] != r2["email"]

    def test_generates_name_as_string(self):
        result = random_data_generator({"full_name": "name"}, "en_US")
        assert isinstance(result["full_name"], str)
        assert len(result["full_name"]) > 0

    def test_generates_uuid_format(self):
        result = random_data_generator({"id": "uuid"}, "en_US")
        assert len(result["id"]) == 36
        assert result["id"].count("-") == 4

    def test_generates_uuid_hex_format(self):
        result = random_data_generator({"id": "uuid_hex"}, "en_US")
        assert len(result["id"]) == 32
        assert all(c in "0123456789abcdef" for c in result["id"])

    def test_generates_float_in_range(self):
        result = random_data_generator({"price": "float"}, "en_US")
        assert isinstance(result["price"], float)
        assert 1.0 <= result["price"] <= 999.9

    def test_generates_integer_with_digit_count(self):
        result = random_data_generator({"qty": "integer|5"}, "en_US")
        assert len(str(result["qty"])) == 5
        assert str(result["qty"]).isdigit()

    def test_generates_cpf_digits_only(self):
        result = random_data_generator({"cpf": "cpf"}, "pt_BR")
        assert result["cpf"].isdigit()
        assert len(result["cpf"]) == 11

    def test_generates_cnpj_digits_only(self):
        result = random_data_generator({"cnpj": "cnpj"}, "pt_BR")
        assert result["cnpj"].isdigit()
        assert len(result["cnpj"]) == 14

    def test_account_id_contains_prefix(self):
        result = random_data_generator({"account": "account_id|TEST"}, "en_US")
        assert result["account"].startswith("AC-TEST")

    def test_dcc_id_starts_with_dc(self):
        result = random_data_generator({"dcc": "dcc_id"}, "en_US")
        assert result["dcc"].startswith("DC-")

    def test_order_id_starts_with_or(self):
        result = random_data_generator({"order": "order_id|TEST"}, "en_US")
        assert result["order"].startswith("OR-TEST")

    def test_generates_valid_date(self):
        result = random_data_generator({"start": "startDate|0"}, "en_US")
        datetime.strptime(result["start"], "%Y-%m-%d")

    def test_id_with_digit_count_generates_number_of_correct_length(self):
        result = random_data_generator({"my_id": "id|8"}, "en_US")
        assert len(str(result["my_id"])) == 8
        assert str(result["my_id"]).isdigit()

    def test_id_without_pattern_generates_uuid(self):
        result = random_data_generator({"my_id": "id"}, "en_US")
        val = str(result["my_id"])
        assert len(val) == 36
        assert val.count("-") == 4

    def test_startdate_with_empty_pattern_defaults_to_today(self):
        from datetime import date
        result = random_data_generator({"d": "startDate|"}, "en_US")
        parsed = datetime.strptime(result["d"], "%Y-%m-%d").date()
        assert parsed == date.today()

    def test_generates_multiple_fields(self):
        params = {"name": "name", "email": "email", "id": "uuid"}
        result = random_data_generator(params, "en_US")
        assert set(result.keys()) == {"name", "email", "id"}

    def test_unknown_type_does_not_raise(self):
        params = {"field": "unknown_type_xyz"}
        result = random_data_generator(params, "en_US")
        assert "field" in result

    def test_returns_dict(self):
        result = random_data_generator({"name": "name"}, "en_US")
        assert isinstance(result, dict)
