import argparse
import pytest
from api_sender import get_execution_list


def _args(**kwargs):
    defaults = dict(countries=None, services=None, methods=None, versions=None, flow=None)
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


class TestGetExecutionList:
    def test_returns_valid_combination_from_config(self):
        # config_test.yml has br / test-service / post / v1
        flow_toggle, execution_list, failure_report = get_execution_list(_args())
        assert execution_list == [["br", "test-service", "post", "v1"]]
        assert failure_report == []

    def test_flow_toggle_is_false_without_flow_arg(self):
        flow_toggle, _, _ = get_execution_list(_args())
        assert flow_toggle is False

    def test_flow_toggle_is_true_with_flow_arg(self):
        flow_toggle, _, _ = get_execution_list(_args(flow="some_flow"))
        assert flow_toggle is True

    def test_invalid_country_goes_to_failure_report(self):
        _, execution_list, failure_report = get_execution_list(_args(countries="xx"))
        assert execution_list == []
        assert len(failure_report) == 1
        assert "XX" in failure_report[0]

    def test_invalid_service_goes_to_failure_report(self):
        _, execution_list, failure_report = get_execution_list(
            _args(countries="br", services="nonexistent-service")
        )
        assert execution_list == []
        assert len(failure_report) == 1
        assert "NONEXISTENT-SERVICE" in failure_report[0]

    def test_invalid_method_goes_to_failure_report(self):
        _, execution_list, failure_report = get_execution_list(
            _args(countries="br", services="test-service", methods="delete")
        )
        assert execution_list == []
        assert len(failure_report) == 1
        assert "DELETE" in failure_report[0]

    def test_invalid_version_goes_to_failure_report(self):
        _, execution_list, failure_report = get_execution_list(
            _args(countries="br", services="test-service", methods="post", versions="v99")
        )
        assert execution_list == []
        assert len(failure_report) == 1
        assert "V99" in failure_report[0]

    def test_multiple_countries_accumulates_failures(self):
        _, execution_list, failure_report = get_execution_list(_args(countries="br,ar,xx"))
        assert ["br", "test-service", "post", "v1"] in execution_list
        assert any("AR" in msg for msg in failure_report)
        assert any("XX" in msg for msg in failure_report)

    def test_explicit_valid_args_produce_execution_list(self):
        _, execution_list, failure_report = get_execution_list(
            _args(countries="br", services="test-service", methods="post", versions="v1")
        )
        assert execution_list == [["br", "test-service", "post", "v1"]]
        assert failure_report == []
