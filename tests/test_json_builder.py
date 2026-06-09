import json
import pytest
from commons.jsonBuilder import beautify_json


class TestBeautifyJson:
    def test_returns_bytes(self):
        result = beautify_json("test", '{"key": "value"}')
        assert isinstance(result, bytes)

    def test_output_is_valid_json(self):
        result = beautify_json("test", '{"key": "value"}')
        parsed = json.loads(result.decode("utf-8"))
        assert parsed == {"key": "value"}

    def test_output_is_indented(self):
        result = beautify_json("test", '{"a":1,"b":2}')
        assert b"\n" in result

    def test_preserves_unicode_characters(self):
        result = beautify_json("test", '{"name": "Ângela"}')
        assert "Ângela" in result.decode("utf-8")

    def test_raises_exception_on_malformed_json(self):
        with pytest.raises(Exception) as exc_info:
            beautify_json("my_template", '{"key": invalid_value}')
        assert "my_template" in str(exc_info.value)

    def test_error_message_contains_template_name(self):
        with pytest.raises(Exception) as exc_info:
            beautify_json("orders_template", "{bad json}")
        assert "orders_template" in str(exc_info.value)

    def test_handles_nested_json(self):
        result = beautify_json("test", '{"outer": {"inner": "value"}}')
        parsed = json.loads(result.decode("utf-8"))
        assert parsed["outer"]["inner"] == "value"

    def test_handles_json_array(self):
        result = beautify_json("test", '[{"id": 1}, {"id": 2}]')
        parsed = json.loads(result.decode("utf-8"))
        assert len(parsed) == 2
