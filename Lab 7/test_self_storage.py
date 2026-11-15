from hypothesis import given, strategies as st, assume, settings
from self_storage import parse_rental, duration_average, payable_rent


# --- parse_rental tests ---

@given(st.text())
@settings(max_examples=200)
def test_parse_rental_no_crash(s):
    """Test that parse_rental does not crash on various text inputs."""
    try:
        result = parse_rental(s)
        # If it returns, result should be a tuple of (str, float)
        assert isinstance(result, tuple), f"Expected tuple, got {type(result)}"
        assert len(result) == 2, f"Expected 2-element tuple, got {len(result)}"
        unit, months = result
        assert isinstance(unit, str), f"Expected str unit, got {type(unit)}"
        # months should be a number (int or float)
        assert isinstance(months, (int, float)), f"Expected numeric months, got {type(months)}"
    except (ValueError, TypeError):
        # These are acceptable failures for invalid inputs
        pass


@given(st.text(min_size=1).filter(lambda s: ':' in s))
def test_parse_rental_returns_unit_and_months(s):
    """Test that parse_rental returns a unit and months for inputs with a colon."""
    assume(s.count(':') == 1)  # Only one colon
    unit, months = parse_rental(s)
    assert unit == s.split(':')[0].strip().title()
    assert months == float(s.split(':')[1].strip())


# --- duration_average tests ---

@given(st.lists(st.integers(min_value=1, max_value=365), min_size=1, max_size=20))
@settings(max_examples=200)
def test_duration_average_valid_csv(months_list):
    """Test duration_average with valid CSV of positive integers."""
    months_csv = ','.join(str(r) for r in months_list)
    result = duration_average(months_csv)
    expected = sum(months_list) // len(months_list)
    assert result == expected, f"Expected {expected}, got {result}"


@given(st.text(min_size=1))
@settings(max_examples=200)
def test_duration_average_no_crash(s):
    """Test that duration_average does not crash on various text inputs."""
    try:
        result = duration_average(s)
        assert isinstance(result, int), f"Expected int, got {type(result)}"
    except (ValueError, TypeError):
        pass


# --- payable_rent tests ---

@given(st.text(min_size=1).filter(lambda s: '|' in s))
def test_payable_rent_valid_format(s):
    """Test payable_rent with valid 'rent|discount' format."""
    parts = s.split('|')
    assume(len(parts) == 2)
    assume(all(p.strip() for p in parts))
    total = float(parts[0]) * 1.18 - float(parts[1])
    expected = max(total, 0)
    result = payable_rent(s)
    assert result == expected, f"Expected {expected}, got {result}"


@given(st.text(min_size=1))
@settings(max_examples=200)
def test_payable_rent_no_crash(s):
    """Test that payable_rent does not crash on various text inputs."""
    try:
        result = payable_rent(s)
        assert isinstance(result, (int, float)), f"Expected numeric, got {type(result)}"
        assert result >= 0, f"Expected non-negative, got {result}"
    except (ValueError, TypeError):
        pass