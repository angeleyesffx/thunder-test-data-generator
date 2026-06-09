def split_string_after(string_value, slice_a):
    """Returns the substring after the last occurrence of slice_a, or '' if not found."""
    pos_a = string_value.rfind(slice_a)
    if pos_a == -1:
        return ""
    adjusted_pos_a = pos_a + len(slice_a)
    if adjusted_pos_a >= len(string_value):
        return ""
    return string_value[adjusted_pos_a:]
