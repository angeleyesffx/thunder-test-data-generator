import pytest
from commons.payloadBuilder import data_and_header_creation


class TestDataAndHeaderCreation:
    def test_generates_correct_record_count(self):
        data, headers = data_and_header_creation(
            param_keys="name:name,email:email",
            country="br",
            amount_data_mass=3,
        )
        assert len(data) == 3
        assert len(headers) == 3

    def test_zero_amount_returns_empty_lists(self):
        data, headers = data_and_header_creation(
            param_keys="name:name",
            country="br",
            amount_data_mass=0,
        )
        assert data == []
        assert headers == []

    def test_single_record_boundary(self):
        data, headers = data_and_header_creation(
            param_keys="name:name",
            country="br",
            amount_data_mass=1,
        )
        assert len(data) == 1
        assert len(headers) == 1

    def test_data_contains_expected_keys(self):
        data, _ = data_and_header_creation(
            param_keys="name:name,email:email",
            country="br",
            amount_data_mass=1,
        )
        assert "name" in data[0]
        assert "email" in data[0]

    def test_header_prefix_keys_are_separated_from_body(self):
        data, headers = data_and_header_creation(
            param_keys="header_x_country:country_code,name:name",
            country="br",
            amount_data_mass=1,
        )
        assert "name" in data[0]
        assert "header_x_country" not in data[0]
        assert "header_x_country" in headers[0]

    def test_static_params_are_merged_into_body(self):
        data, _ = data_and_header_creation(
            param_keys="name:name",
            static_params="active=true,currency=BRL",
            country="br",
            amount_data_mass=1,
        )
        assert data[0]["active"] == "true"
        assert data[0]["currency"] == "BRL"

    def test_raises_when_all_sources_are_none(self):
        with pytest.raises(ValueError):
            data_and_header_creation(
                data_source=None,
                data_flow=None,
                param_keys=None,
                country="br",
                amount_data_mass=1,
            )

    def test_each_record_is_independently_generated(self):
        data, _ = data_and_header_creation(
            param_keys="email:email",
            country="br",
            amount_data_mass=5,
        )
        emails = [row["email"] for row in data]
        assert len(set(emails)) == 5, "Each generated email should be unique"
