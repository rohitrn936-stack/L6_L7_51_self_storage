import pytest
from self_storage import rent_due, access_allowed, payment_status


def test_rent_due_invalid_unit_size():
    """Test line 6: invalid unit_size raises ValueError"""
    with pytest.raises(ValueError):
        rent_due("invalid", 1, False, False)


def test_rent_due_negative_months():
    """Test line 8: negative months raises ValueError"""
    with pytest.raises(ValueError):
        rent_due("small", -1, False, False)


def test_rent_due_small_within_deposit():
    """Test rent_due with small unit within deposit months"""
    assert rent_due("small", 1, False, False) == 0


def test_rent_due_medium_within_deposit():
    """Test medium unit within deposit months"""
    assert rent_due("medium", 2, False, False) == 0


def test_rent_due_large_within_deposit():
    """Test large unit within deposit months"""
    assert rent_due("large", 3, False, False) == 0


def test_rent_due_small_five_months_no_climate_no_member():
    """Test small unit, 5 months, no climate, no member - extra=4, rate=80 => 320"""
    assert rent_due("small", 5, False, False) == 320


def test_rent_due_small_seven_months_no_climate_no_member():
    """Test small unit, 7 months, no climate, no member - extra=6, rate=80 => 480"""
    assert rent_due("small", 7, False, False) == 480


def test_rent_due_small_ten_months_no_climate_no_member():
    """Test small unit, 10 months, no climate, no member - extra=9, rate=70 => 630"""
    assert rent_due("small", 10, False, False) == 630


def test_rent_due_small_five_months_climate_no_member():
    """Test small unit, 5 months, climate, no member - extra=4, rate=120 => 480"""
    assert rent_due("small", 5, True, False) == 480


def test_rent_due_small_seven_months_climate_no_member():
    """Test small unit, 7 months, climate, no member - extra=6, rate=120 => 720"""
    assert rent_due("small", 7, True, False) == 720


def test_rent_due_small_ten_months_climate_no_member():
    """Test small unit, 10 months, climate, no member - extra=9, rate=105 => 945"""
    assert rent_due("small", 10, True, False) == 945


def test_rent_due_member_small_five_months():
    """Test member with small unit: covered=2, extra=3, rate=80 => 240"""
    assert rent_due("small", 5, False, True) == 240


def test_rent_due_member_large_five_months():
    """Test member with large unit: member benefit doesn't apply to large, covered=3, extra=2, rate=80 => 160"""
    assert rent_due("large", 5, False, True) == 160


def test_rent_due_member_medium_five_months():
    """Test member with medium unit: covered=3 (2+1), extra=2, rate=80 => 160"""
    assert rent_due("medium", 5, False, True) == 160


def test_rent_due_member_medium_five_climate():
    """Test member with medium unit, climate: covered=3, extra=2, rate=120 => 240"""
    assert rent_due("medium", 5, True, True) == 240


def test_access_allowed_owner_visitors_4():
    """Test owner with visitors <= 4 - lines 27, 28"""
    assert access_allowed(12, 4, True) is True


def test_access_allowed_owner_visitors_5():
    """Test owner with visitors > 4 - line 27, not 28"""
    assert access_allowed(12, 5, True) is False


def test_access_allowed_off_hours_early_no_owner():
    """Test non-owner off-hours early - lines 27, 29, 30"""
    assert access_allowed(1, 3, False) is False


def test_access_allowed_off_hours_late_no_owner():
    """Test non-owner off-hours late - lines 27, 29, 30"""
    assert access_allowed(23, 3, False) is False


def test_access_allowed_within_hours_visitors_2():
    """Test non-owner within hours with 2 visitors - lines 27, 29, 31"""
    assert access_allowed(12, 2, False) is True


def test_access_allowed_within_hours_visitors_3():
    """Test non-owner within hours with 3 visitors - line 31"""
    assert access_allowed(12, 3, False) is False


def test_payment_status_autopay_current():
    """Test autopay with current days - lines 35, 36, 41, 42"""
    assert payment_status(5, True, False) == "current"


def test_payment_status_autopay_negative_grace():
    """Test autopay with negative days - lines 35, 36, 41, 42, 43-45"""
    assert payment_status(-5, True, False) == "grace"


def test_payment_status_normal_current():
    """Test non-autopay with sufficient days - lines 37, 38, 39(no), 41, 42"""
    assert payment_status(10, False, False) == "current"


def test_payment_status_normal_grace():
    """Test non-autopay with grace days - lines 37, 38, 39(yes), 43, 44"""
    assert payment_status(3, False, False) == "grace"


def test_payment_status_normal_lien():
    """Test non-autopay with insufficient days - lines 37, 38, 39(no), 45"""
    assert payment_status(-15, False, False) == "lien"


def test_payment_status_with_prior_late_current():
    """Test with prior late, sufficient days - lines 39, 40, 41, 42"""
    assert payment_status(20, False, True) == "current"


def test_payment_status_with_prior_late_grace():
    """Test with prior late, grace days - lines 39, 40, 41, 43, 44"""
    assert payment_status(10, False, True) == "grace"


def test_payment_status_with_prior_late_lien():
    """Test with prior late, insufficient days - lines 39, 40, 45"""
    assert payment_status(-5, False, True) == "lien"


def test_payment_status_autopay_with_prior_late():
    """Test autopay with prior late - lines 35, 36, 39, 40, 41, 42, 43-45"""
    assert payment_status(5, True, True) == "grace"
    assert payment_status(-10, True, True) == "lien"