from commons.stringManipulation import split_string_after


class TestSplitStringAfter:
    def test_returns_substring_after_delimiter(self):
        assert split_string_after("header_country", "header_") == "country"

    def test_returns_empty_when_delimiter_not_found(self):
        assert split_string_after("country", "header_") == ""

    def test_returns_empty_when_delimiter_is_at_end(self):
        assert split_string_after("header_", "header_") == ""

    def test_uses_last_occurrence(self):
        assert split_string_after("header_x_header_y", "header_") == "y"

    def test_returns_empty_for_empty_string(self):
        assert split_string_after("", "_") == ""
