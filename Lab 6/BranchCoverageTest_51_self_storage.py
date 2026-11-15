import pytest
from self_storage import rent_due, access_allowed, payment_status


# ----- rent_due branch coverage -----


def test_rent_due_invalid_unit_size():
    """Branch: line 5 - unit_size not in DEPOSIT_MONTHS (True)"""
    with pytest.raises(ValueError):
        rent_due("invalid", 1, False, False)


def test_rent_due_valid_unit_size():
    """Branch: line 5 - unit_size not in DEPOSIT_MONTHS (False/valid)"""
    assert rent_due("small", 1, False, False) == 0


def test_rent_due_negative_months():
    """Branch: line 7 - months < 0 (True)"""
    with pytest.raises(ValueError):
        rent_due("small", -1, False, False)


def test_rent_due_valid_months():
    """Branch: line 7 - months < 0 (False)"""
    assert rent_due("medium", 2, False, False) == 0


def test_rent_due_member_non_large():
    """Branch: line 10 - is_member and unit_size != "large" (True)"""
    # member with small/medium gets extra deposit month
    assert rent_due("small", 5, False, True) == 240


def test_rent_due_member_large():
    """Branch: line 10 - is_member and unit_size != "large" (False, large excluded)"""
    # member with large: benefit does not apply
    assert rent_due("large", 5, False, True) == 160


def test_rent_due_non_member():
    """Branch: line 10 - is_member and unit_size != "large" (False, no member)"""
    assert rent_due("small", 5, False, False) == 320


def test_rent_due_extra_zero():
    """Branch: line 13 - extra <= 0 (True, no charge)"""
    assert rent_due("small", 1, False, False) == 0


def test_rent_due_extra_positive():
    """Branch: line 13 - extra <= 0 (False, extra > 0, charged)"""
    assert rent_due("small", 5, False, False) == 320


def test_rent_due_climate_true():
    """Branch: line 15 - is_climate (True)"""
    assert rent_due("small", 5, True, False) == 480


def test_rent_due_climate_false():
    """Branch: line 15 - is_climate (False)"""
    assert rent_due("small", 5, False, False) == 320


def test_rent_due_extra_gt_6():
    """Branch: line 19 - extra > 6 (True)"""
    assert rent_due("small", 10, False, False) == 630


def test_rent_due_extra_6_or_less():
    """Branch: line 19 - extra > 6 (False, extra <= 6)"""
    assert rent_due("small", 7, False, False) == 480


def test_rent_due_extra_gt_6_climate():
    """Branch: line 19-21 - extra > 6 (True) with climate, nested is_climate check"""
    assert rent_due("small", 10, True, False) == 945


def test_rent_due_extra_6_climate():
    """Branch: line 19-21 - extra > 6 (False) with climate"""
    assert rent_due("small", 7, True, False) == 720


# ----- access_allowed branch coverage -----


def test_access_allowed_owner():
    """Branch: line 27 - is_owner (True)"""
    assert access_allowed(12, 3, True) is True


def test_access_allowed_non_owner():
    """Branch: line 27 - is_owner (False)"""
    assert access_allowed(12, 3, False) is False


def test_access_allowed_off_hours_early():
    """Branch: line 29 - hour < 6 or hour > 22 (True, early)"""
    assert access_allowed(1, 3, False) is False


def test_access_allowed_off_hours_late():
    """Branch: line 29 - hour < 6 or hour > 22 (True, late)"""
    assert access_allowed(23, 3, False) is False


def test_access_allowed_within_hours():
    """Branch: line 29 - hour < 6 or hour > 22 (False, within hours)"""
    assert access_allowed(12, 3, False) is False


def test_access_allowed_within_hours_visitors_2():
    """Branch: line 31 - visitors <= 2 (True, within allowed)"""
    assert access_allowed(12, 2, False) is True


def test_access_allowed_within_hours_visitors_3():
    """Branch: line 31 - visitors <= 2 (False, too many)"""
    assert access_allowed(12, 3, False) is False


# ----- payment_status branch coverage -----


def test_payment_status_autopay():
    """Branch: line 35 - is_autopay (True)"""
    assert payment_status(5, True, False) == "current"


def test_payment_status_not_autopay():
    """Branch: line 35 - is_autopay (False)"""
    assert payment_status(5, False, False) == "current"


def test_payment_status_has_prior_late():
    """Branch: line 39 - has_prior_late (True)"""
    assert payment_status(5, False, True) == "grace"


def test_payment_status_no_prior_late():
    """Branch: line 39 - has_prior_late (False)"""
    assert payment_status(5, False, False) == "current"


def test_payment_status_days_above_cutoff():
    """Branch: line 41 - days_to_due >= cutoff (True)"""
    assert payment_status(10, False, False) == "current"


def test_payment_status_days_below_cutoff():
    """Branch: line 41 - days_to_due >= cutoff (False)"""
    assert payment_status(3, False, False) == "grace"


def test_payment_status_days_grace_threshold():
    """Branch: line 43 - days_to_due >= cutoff - 15 (True, grace range)"""
    # cutoff=5, days=3 < 5 (line 41 False), then 3 >= 5-15=-10 (line 43 True) → "grace"
    assert payment_status(3, False, False) == "grace"


def test_payment_status_days_lien():
    """Branch: line 43 - days_to_due >= cutoff - 15 (False, lien)"""
    # cutoff=5, days=-20 < 5 (line 41 False), -20 >= 5-15=-10? No → "lien"
    assert payment_status(-20, False, False) == "lien"