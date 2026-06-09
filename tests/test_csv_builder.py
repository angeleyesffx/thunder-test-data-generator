import json
import os
import pytest

DATASOURCE_DIR = os.path.join(os.path.dirname(__file__), "..", "datasource")


class TestLoadCsv:
    def test_returns_list(self):
        from commons.csvBuilder import load_csv
        result = load_csv(os.path.join(DATASOURCE_DIR, "non_nested.csv"))
        assert isinstance(result, list)
        assert len(result) > 0

    def test_each_item_is_valid_json_string(self):
        from commons.csvBuilder import load_csv
        result = load_csv(os.path.join(DATASOURCE_DIR, "non_nested.csv"))
        for item in result:
            parsed = json.loads(item)
            assert isinstance(parsed, dict)

    def test_csv_contains_expected_columns(self):
        from commons.csvBuilder import load_csv
        result = load_csv(os.path.join(DATASOURCE_DIR, "non_nested.csv"))
        row = json.loads(result[0])
        assert "country" in row
        assert "product_id" in row


class TestGetScenarioDataCsv:
    def test_filters_by_valid_scenario(self):
        from commons.csvBuilder import get_scenario_data_csv
        result = get_scenario_data_csv(
            os.path.join(DATASOURCE_DIR, "scenario.csv"), "valid_data_multiple"
        )
        assert len(result) == 1
        assert json.loads(result[0])["test_scenario_id"] == "valid_data_multiple"

    def test_filters_invalid_scenario(self):
        from commons.csvBuilder import get_scenario_data_csv
        result = get_scenario_data_csv(
            os.path.join(DATASOURCE_DIR, "scenario.csv"), "invalid_data"
        )
        assert len(result) == 1
        assert json.loads(result[0])["test_scenario_id"] == "invalid_data"

    def test_returns_empty_list_for_nonexistent_scenario(self):
        from commons.csvBuilder import get_scenario_data_csv
        result = get_scenario_data_csv(
            os.path.join(DATASOURCE_DIR, "scenario.csv"), "scenario_that_does_not_exist"
        )
        assert result == []

    def test_each_result_is_valid_json(self):
        from commons.csvBuilder import get_scenario_data_csv
        result = get_scenario_data_csv(
            os.path.join(DATASOURCE_DIR, "scenario.csv"), "valid_data_multiple"
        )
        for item in result:
            assert isinstance(json.loads(item), dict)



class TestSelectCsvStrategy:
    def test_all_in_strategy_returns_list(self):
        from commons.csvBuilder import select_csv_strategy
        result = select_csv_strategy("br", "non_nested", "all_in")
        assert isinstance(result, list)
        assert len(result) > 0

    def test_single_line_strategy_returns_list(self):
        from commons.csvBuilder import select_csv_strategy
        result = select_csv_strategy("br", "non_nested", "single_line")
        assert isinstance(result, list)

    def test_scenario_line_strategy_filters_correctly(self):
        from commons.csvBuilder import select_csv_strategy
        result = select_csv_strategy(
            "br", "scenario", "scenario_line", scenario="valid_data_multiple"
        )
        assert len(result) == 1
        assert json.loads(result[0])["test_scenario_id"] == "valid_data_multiple"

    def test_unknown_strategy_defaults_to_all_in(self):
        from commons.csvBuilder import select_csv_strategy
        result = select_csv_strategy("br", "non_nested", "unknown_strategy")
        assert isinstance(result, list)
        assert len(result) > 0

    def test_raises_file_not_found_for_missing_csv(self):
        from commons.csvBuilder import select_csv_strategy
        with pytest.raises(FileNotFoundError):
            select_csv_strategy("br", "file_that_does_not_exist", "all_in")
