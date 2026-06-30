import json
import datetime
import pytest
from commons.jsonBuilder import (
    beautify_json,
    load_json_as_dict,
    read_scenario_from_json,
    get_json_keys,
    get_json_values,
    write_json_file,
)


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


class TestLoadJsonAsDict:
    def test_returns_dict(self, tmp_path):
        f = tmp_path / "data.json"
        f.write_text('{"key": "value"}')
        result = load_json_as_dict(str(f))
        assert result == {"key": "value"}

    def test_returns_nested_dict(self, tmp_path):
        f = tmp_path / "nested.json"
        f.write_text('{"outer": {"inner": 42}}')
        result = load_json_as_dict(str(f))
        assert result["outer"]["inner"] == 42


class TestGetJsonKeys:
    def test_returns_top_level_keys(self, tmp_path):
        f = tmp_path / "keys.json"
        f.write_text('{"a": 1, "b": 2}')
        keys = list(get_json_keys(str(f)))
        assert "a" in keys
        assert "b" in keys


class TestGetJsonValues:
    def test_returns_top_level_values(self, tmp_path):
        f = tmp_path / "values.json"
        f.write_text('{"x": 10, "y": 20}')
        values = list(get_json_values(str(f)))
        assert 10 in values
        assert 20 in values


class TestReadScenarioFromJson:
    def test_returns_value_for_existing_key(self, tmp_path):
        f = tmp_path / "scenario.json"
        f.write_text('{"happy_path": {"payload": "data"}}')
        result = read_scenario_from_json("happy_path", "payload", str(f))
        assert result == "data"

    def test_returns_none_for_missing_key(self, tmp_path):
        f = tmp_path / "scenario.json"
        f.write_text('{"happy_path": {"payload": "data"}}')
        result = read_scenario_from_json("happy_path", "nonexistent", str(f))
        assert result is None


class TestWriteJsonFile:
    def test_creates_file_in_output_folder(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        write_json_file('{"key": "value"}', "test_request")
        date_str = str(datetime.date.today())
        expected = tmp_path / "json_generated" / date_str / "test_request.json"
        assert expected.exists()
