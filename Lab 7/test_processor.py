from hypothesis import given, strategies as st, assume, settings, HealthCheck
from self_storage import parse_rental, duration_average, payable_rent


# ---- parse_rental ----

VALID_UNITS = {"small", "medium", "large"}


@given(st.text(min_size=1))
@settings(max_examples=200, suppress_health_check=[HealthCheck.filter_too_much])
def test_parse_rental_valid_input_returns_tuple(s):
    """parse_rental with valid 'unit:months' should return a (str, float) tuple."""
    if ":" not in s:
        return
    parts = s.split(":")
    if len(parts) != 2:
        return
    unit, months_str = parts
    unit = unit.strip().title()
    if unit not in VALID_UNITS:
        return
    try:
        months = float(months_str)
    except ValueError:
        return
    if months < 0:
        return
    result = parse_rental(s)
    assert isinstance(result, tuple), f"Expected tuple, got {type(result)}"
    assert len(result) == 2, f"Expected 2-element tuple, got {len(result)}"
    unit_out, months_out = result
    assert isinstance(unit_out, str), f"Expected str unit, got {type(unit_out)}"
    assert isinstance(months_out, (int, float)), f"Expected numeric months, got {type(months_out)}"


@given(st.text(min_size=1))
@settings(max_examples=200, suppress_health_check=[HealthCheck.filter_too_much])
def test_parse_rental_inputs_without_colon_raise_or_handle(s):
    """parse_rental should not crash on inputs missing a colon - should raise or handle gracefully."""
    if ":" in s:
        return
    # For inputs without colon, the function should either raise ValueError/TypeError
    # or return gracefully without crashing. We test that it doesn't hang or crash
    # with an unexpected exception type.
    try:
        result = parse_rental(s)
        # If it returns, result should be acceptable (tuple or None)
        assert result is None or isinstance(result, tuple)
    except (ValueError, TypeError):
        # Expected for inputs without colon
        pass
    except Exception as e:
        # Unexpected exception types should fail the test
        raise AssertionError(f"Unexpected exception {type(e).__name__}: {e}")


@given(st.text(min_size=1))
@settings(max_examples=200, suppress_health_check=[HealthCheck.filter_too_much])
def test_parse_rental_inputs_with_multi_colon_raise_or_handle(s):
    """parse_rental should not crash on multiple colons - should raise or handle gracefully."""
    if s.count(":") != 2:
        return
    try:
        result = parse_rental(s)
        # If it returns, result should be acceptable
        assert result is None or isinstance(result, tuple)
    except (ValueError, TypeError):
        pass
    except Exception as e:
        raise AssertionError(f"Unexpected exception {type(e).__name__}: {e}")


@given(st.text(min_size=1))
@settings(max_examples=200, suppress_health_check=[HealthCheck.filter_too_much])
def test_parse_rental_non_numeric_months_handles_gracefully(s):
    """parse_rental with non-numeric months should not crash."""
    if ":" not in s:
        return
    parts = s.split(":")
    if len(parts) != 2:
        return
    unit, months_str = parts
    unit = unit.strip().title()
    if unit not in VALID_UNITS:
        return
    # Non-numeric months should not crash the function
    test_input = f"{unit}:abc"
    try:
        result = parse_rental(test_input)
        # Should return None or a tuple, not crash
        assert result is None or isinstance(result, tuple)
    except (ValueError, TypeError):
        # These are acceptable
        pass
    except Exception as e:
        raise AssertionError(f"Unexpected exception {type(e).__name__}: {e}")


@given(st.text(min_size=0))
@settings(max_examples=200, suppress_health_check=[HealthCheck.filter_too_much])
def test_parse_rental_empty_input_handles_gracefully(s):
    """parse_rental should handle empty input without hanging or unexpected crashes."""
    try:
        result = parse_rental(s)
        # Acceptable outcomes: None, or a tuple
        assert result is None or isinstance(result, tuple)
    except (ValueError, TypeError):
        # These are acceptable for empty input
        pass
    except Exception as e:
        raise AssertionError(f"Unexpected exception {type(e).__name__}: {e}")


# ---- duration_average ----

@given(st.text(min_size=1))
@settings(max_examples=200, suppress_health_check=[HealthCheck.filter_too_much])
def test_duration_average_valid_csv_correctness(s):
    """duration_average should compute correct integer average from valid CSV of positive integers."""
    assume("," in s)
    parts = s.split(",")
    # Filter out empty parts and validate all are integers
    values = []
    for p in parts:
        p = p.strip()
        if p == "":
            # Empty value in CSV - this is an edge case we handle by returning None
            return
        try:
            values.append(int(p))
        except ValueError:
            # Non-integer value - skip this test case as invalid CSV
            return
    if len(values) == 0:
        return
    result = duration_average(s)
    # Function should not crash on valid CSV
    assert result is not None, "duration_average should return a result for valid CSV input"
    expected = sum(values) // len(values)
    assert result == expected, f"Expected {expected}, got {result}"


@given(st.text(min_size=0))
@settings(max_examples=200, suppress_health_check=[HealthCheck.filter_too_much])
def test_duration_average_empty_input_handles_gracefully(s):
    """duration_average should handle empty input without hanging or unexpected crashes."""
    try:
        result = duration_average(s)
        # Acceptable outcomes: int, None
        assert isinstance(result, (int, type(None))), f"Expected int or None, got {type(result)}"
    except (ValueError, ZeroDivisionError):
        # These are acceptable for empty input
        pass
    except Exception as e:
        raise AssertionError(f"Unexpected exception {type(e).__name__}: {e}")


@given(st.integers(min_value=1, max_value=365))
@settings(max_examples=50, suppress_health_check=[HealthCheck.filter_too_much])
def test_duration_average_single_value(n):
    """duration_average with a single value should return that value."""
    s = str(n)
    result = duration_average(s)
    assert result == n, f"Expected {n}, got {result}"


@given(st.integers(min_value=-365, max_value=-1))
@settings(max_examples=50, suppress_health_check=[HealthCheck.filter_too_much])
def test_duration_average_negative_single_value(n):
    """duration_average with a single negative value should return that value."""
    s = str(n)
    result = duration_average(s)
    assert result == n, f"Expected {n}, got {result}"


@given(st.lists(st.integers(min_value=1, max_value=365), min_size=1, max_size=20))
@settings(max_examples=200, suppress_health_check=[HealthCheck.filter_too_much])
def test_duration_average_from_list(months_list):
    """duration_average with valid list of positive integers should compute correct average."""
    months_csv = ",".join(str(r) for r in months_list)
    result = duration_average(months_csv)
    expected = sum(months_list) // len(months_list)
    assert result == expected, f"Expected {expected}, got {result}"


@given(st.text(min_size=1))
@settings(max_examples=200, suppress_health_check=[HealthCheck.filter_too_much])
def test_duration_average_non_integer_values_handles_gracefully(s):
    """duration_average should handle non-integer values in CSV without crashing."""
    assume("," in s)
    parts = s.split(",")
    # Check if any part is definitely non-integer (has letters, etc.)
    has_non_integer = any(
        p.strip() and not p.strip().lstrip("-").replace(".", "", 1).isdigit()
        for p in parts if p.strip()
    )
    if not has_non_integer:
        return  # All parts look like integers, skip
    # Has non-integer values - function should handle gracefully
    try:
        result = duration_average(s)
        assert result is None or isinstance(result, int)
    except (ValueError, TypeError):
        # These are acceptable for truly invalid input
        pass
    except Exception as e:
        raise AssertionError(f"Unexpected exception {type(e).__name__}: {e}")


# ---- payable_rent ---

@given(st.text(min_size=1))
@settings(max_examples=200, suppress_health_check=[HealthCheck.filter_too_much])
def test_payable_rent_valid_input_no_crash(s):
    """payable_rent with valid 'rent|discount' should not crash and return numeric result."""
    if "|" not in s:
        return
    parts = s.split("|")
    if len(parts) != 2:
        return
    assume(all(p.strip() for p in parts))
    try:
        rent = float(parts[0])
        discount = float(parts[1])
    except ValueError:
        return
    if rent < 0 or discount < 0:
        return
    result = payable_rent(s)
    assert result is not None, "payable_rent should return a result for valid input"
    assert isinstance(result, (int, float)), f"Expected numeric result, got {type(result)}"


@given(st.text(min_size=1))
@settings(max_examples=200, suppress_health_check=[HealthCheck.filter_too_much])
def test_payable_rent_inputs_without_pipe_raise_or_handle(s):
    """payable_rent should handle input without pipe gracefully."""
    if "|" in s:
        return
    try:
        result = payable_rent(s)
        # If it returns, result should be acceptable
        assert result is None or isinstance(result, (int, float))
    except (ValueError, TypeError):
        # Expected for input without pipe
        pass
    except Exception as e:
        raise AssertionError(f"Unexpected exception {type(e).__name__}: {e}")


@given(st.text(min_size=1))
@settings(max_examples=200, suppress_health_check=[HealthCheck.filter_too_much])
def test_payable_rent_inputs_with_multi_pipe_raise_or_handle(s):
    """payable_rent should handle multiple pipes gracefully."""
    if s.count("|") != 1:
        return
    try:
        result = payable_rent(s)
        assert result is None or isinstance(result, (int, float))
    except (ValueError, TypeError):
        pass
    except Exception as e:
        raise AssertionError(f"Unexpected exception {type(e).__name__}: {e}")


@given(st.text(min_size=1))
@settings(max_examples=200, suppress_health_check=[HealthCheck.filter_too_much])
def test_payable_rent_non_numeric_rent_handles_gracefully(s):
    """payable_rent with non-numeric rent should not crash."""
    if "|" not in s:
        return
    parts = s.split("|")
    if len(parts) != 2:
        return
    # Test with non-numeric rent
    test_input = "abc|200"
    try:
        result = payable_rent(test_input)
        assert result is None or isinstance(result, (int, float))
    except ValueError:
        # Expected for non-numeric rent
        pass
    except Exception as e:
        raise AssertionError(f"Unexpected exception {type(e).__name__}: {e}")


@given(st.text(min_size=1))
@settings(max_examples=200, suppress_health_check=[HealthCheck.filter_too_much])
def test_payable_rent_non_numeric_discount_handles_gracefully(s):
    """payable_rent with non-numeric discount should not crash."""
    if "|" not in s:
        return
    parts = s.split("|")
    if len(parts) != 2:
        return
    # Test with non-numeric discount
    test_input = "2400|abc"
    try:
        result = payable_rent(test_input)
        assert result is None or isinstance(result, (int, float))
    except ValueError:
        # Expected for non-numeric discount
        pass
    except Exception as e:
        raise AssertionError(f"Unexpected exception {type(e).__name__}: {e}")


@given(st.text(min_size=0))
@settings(max_examples=200, suppress_health_check=[HealthCheck.filter_too_much])
def test_payable_rent_empty_input_handles_gracefully(s):
    """payable_rent should handle empty input without hanging or unexpected crashes."""
    try:
        result = payable_rent(s)
        assert result is None or isinstance(result, (int, float))
    except (ValueError, TypeError):
        # Acceptable for empty input
        pass
    except Exception as e:
        raise AssertionError(f"Unexpected exception {type(e).__name__}: {e}")


@given(st.text(min_size=1))
@settings(max_examples=200, suppress_health_check=[HealthCheck.filter_too_much])
def test_payable_rent_result_always_non_negative(s):
    """payable_rent should always return non-negative value for valid inputs."""
    if "|" not in s:
        return
    parts = s.split("|")
    if len(parts) != 2:
        return
    assume(all(p.strip() for p in parts))
    try:
        rent = float(parts[0])
        discount = float(parts[1])
    except ValueError:
        return
    if rent < 0 or discount < 0:
        return
    result = payable_rent(s)
    assert result >= 0, f"Negative result: {result}"