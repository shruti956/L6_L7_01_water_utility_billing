import pytest
from water_utility_billing import calculate_water_bill, check_meter_tampering

# Example test case:
def test_single_active_residential():
    accounts = [
        {
            "is_active": True,
            "is_commercial": False,
            "has_leak_waiver": False,
            "usage_blocks": [30]
        }
    ]
    result = calculate_water_bill(accounts, 10.0)
    assert result["total_billed"] == 55.0
    assert result["status"] == "NORMAL"

# TODO: Add test cases to achieve 90-100% on both Line and Branch coverage!

# ==========================================
# ADDITIONAL BILLING TEST CASES
# ==========================================

def test_inactive_account():
    accounts = [{"is_active": False, "usage_blocks": [30]}]
    result = calculate_water_bill(accounts, 10.0)
    assert result["total_billed"] == 0.0
    assert result["status"] == "NO_ACTIVITY"


def test_empty_accounts():
    result = calculate_water_bill([], 0.0)
    assert result["status"] == "NO_ACTIVITY"


def test_empty_usage_blocks():
    accounts = [{"is_active": True, "usage_blocks": []}]
    result = calculate_water_bill(accounts, 10.0)
    assert result["total_billed"] == 10.0


def test_zero_and_negative_usage():
    accounts = [{
        "is_active": True,
        "usage_blocks": [0, -10]
    }]
    result = calculate_water_bill(accounts, 10.0)
    assert result["total_billed"] == 10.0


def test_usage_above_50():
    accounts = [{
        "is_active": True,
        "usage_blocks": [60]
    }]
    result = calculate_water_bill(accounts, 10.0)
    assert result["total_billed"] == 160.0


def test_commercial_usage_above_100():
    accounts = [{
        "is_active": True,
        "is_commercial": True,
        "usage_blocks": [120]
    }]
    result = calculate_water_bill(accounts, 10.0)
    assert result["total_billed"] == 430.0


def test_commercial_usage_continues_after_100():
    accounts = [{
        "is_active": True,
        "is_commercial": True,
        "usage_blocks": [120, 30]
    }]
    result = calculate_water_bill(accounts, 10.0)
    assert result["total_billed"] == 475.0


def test_residential_usage_above_100():
    accounts = [{
        "is_active": True,
        "is_commercial": False,
        "usage_blocks": [120, 30]
    }]
    result = calculate_water_bill(accounts, 10.0)
    assert result["total_billed"] == 550.0


def test_leak_waiver_applied():
    accounts = [{
        "is_active": True,
        "has_leak_waiver": True,
        "usage_blocks": [100]
    }]
    result = calculate_water_bill(accounts, 10.0)
    assert result["total_billed"] == 210.0


def test_leak_waiver_not_applied():
    accounts = [{
        "is_active": True,
        "has_leak_waiver": True,
        "usage_blocks": [50]
    }]
    result = calculate_water_bill(accounts, 10.0)
    assert result["total_billed"] == 85.0


def test_excessive_flags():
    accounts = [{
        "is_active": True,
        "usage_blocks": [-1, -2, -3, -4, -5, -6]
    }]
    result = calculate_water_bill(accounts, 10.0)
    assert result["status"] == "EXCESSIVE_FLAGS"


def test_five_flags_are_normal():
    accounts = [{
        "is_active": True,
        "usage_blocks": [-1, -2, -3, -4, -5]
    }]
    result = calculate_water_bill(accounts, 10.0)
    assert result["status"] == "NORMAL"


def test_invalid_accounts():
    with pytest.raises(ValueError):
        calculate_water_bill("invalid", 10.0)


def test_negative_base_fee():
    with pytest.raises(ValueError):
        calculate_water_bill([], -10.0)


# ==========================================
# METER TAMPERING TEST CASES
# ==========================================

def test_no_meter_data():
    assert check_meter_tampering([]) == "NO_DATA"


def test_empty_individual_meter():
    assert check_meter_tampering([[]]) == "CLEAR"


def test_normal_meter_readings():
    readings = [[10, 20, 30], [5, 10, 15]]
    assert check_meter_tampering(readings) == "CLEAR"


def test_single_backward_reading():
    readings = [[10, -5, 20]]
    assert check_meter_tampering(readings) == "CLEAR"


def test_two_consecutive_backward_readings():
    readings = [[10, -5, -10]]
    assert check_meter_tampering(readings) == "TAMPER_SUSPECTED"


def test_backward_counter_resets():
    readings = [[-5, 10, -10]]
    assert check_meter_tampering(readings) == "CLEAR"
