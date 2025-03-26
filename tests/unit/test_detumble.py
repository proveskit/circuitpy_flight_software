# After following the necessary steps in README.md, you can use "make test" to run all tests in the unit_tests folder
# To run this file specifically: cd Tests > cd unit_tests > pytest test_detumble.py
# pytest test_detumble.py -v displays which tests ran and their respective results (fail or pass)
# Note: If you encounter a ModuleNotFoundError, try: export PYTHONPATH=<path to this repo>

import pytest

import pysquared.detumble as detumble


def test_dot_product():
    # dot_product is only ever called to give the square of mag_field
    mag_field_vector = (30.0, 45.0, 60.0)
    result = detumble.dot_product(mag_field_vector, mag_field_vector)
    assert result == 6525.0  # 30.0*30.0 + 45.0*45.0 + 60.0*60.0 = 6525.0


def test_dot_product_negatives():
    # testing with negative vectors
    vector1 = (-1, -2, -3)
    vector2 = (-4, -5, -6)
    result = detumble.dot_product(vector1, vector2)
    assert result == 32  # -1*-4 + -2*-5 + -3*-6


def test_dot_product_large_val():
    # testing with large value vectors
    vector1 = (1e6, 1e6, 1e6)
    vector2 = (1e6, 1e6, 1e6)
    result = detumble.dot_product(vector1, vector2)
    assert result == 3e12  # 1e6*1e6 + 1e6*1e6 + 1e6*1e6 = 3e12


def test_dot_product_zero():
    # testing with zero values
    vector = (0.0, 0.0, 0.0)
    result = detumble.dot_product(vector, vector)
    assert result == 0.0


def test_x_product():
    mag_field_vector = (30.0, 45.0, 60.0)
    ang_vel_vector = (0.0, 0.02, 0.015)
    expected_result = [-0.525, 0.45, 0.6]
    # x_product takes in tuple arguments and returns a list value
    actual_result = detumble.x_product(
        mag_field_vector, ang_vel_vector
    )  # cross product
    assert pytest.approx(actual_result[0], 0.001) == expected_result[0]
    assert pytest.approx(actual_result[1], 0.001) == expected_result[1]
    assert pytest.approx(actual_result[2], 0.001) == expected_result[2]
    # due to floating point arithmetic, accept answer within 5 places


def test_x_product_negatives():
    mag_field_vector = (-30.0, -45.0, -60.0)
    ang_vel_vector = (-0.02, -0.02, -0.015)
    expected_result = [-0.525, -0.75, -0.3]
    actual_result = detumble.x_product(mag_field_vector, ang_vel_vector)
    assert pytest.approx(actual_result[0], 0.001) == expected_result[0]
    assert pytest.approx(actual_result[1], 0.001) == expected_result[1]
    assert pytest.approx(actual_result[2], 0.001) == expected_result[2]


def test_x_product_large_val():
    mag_field_vector = (1e6, 1e6, 1e6)
    ang_vel_vector = (1e6, 1e6, 1e6)  # cross product of parallel vector equals 0
    result = detumble.x_product(mag_field_vector, ang_vel_vector)
    assert result == [0.0, 0.0, 0.0]


def test_x_product_zero():
    mag_field_vector = (0.0, 0.0, 0.0)
    ang_vel_vector = (0.0, 0.02, 0.015)
    result = detumble.x_product(mag_field_vector, ang_vel_vector)
    assert result == [0.0, 0.0, 0.0]


# Bigger context: magnetorquer_dipole() is called by do_detumble() in (FC board) functions.py & (Batt Board) battery_functions.py
# mag_field: mag. field strength at x, y, & z axis (tuple) (magnetometer reading)
# ang_vel: ang. vel. at x, y, z axis (tuple) (gyroscope reading)
def test_magnetorquer_dipole():
    mag_field = (30.0, -45.0, 60.0)
    ang_vel = (0.0, 0.02, 0.015)
    expected_result = [0.023211, -0.00557, -0.007426]
    actual_result = detumble.magnetorquer_dipole(mag_field, ang_vel)
    assert pytest.approx(actual_result[0], 0.001) == expected_result[0]
    assert pytest.approx(actual_result[1], 0.001) == expected_result[1]
    assert pytest.approx(actual_result[2], 0.001) == expected_result[2]


def test_magnetorquer_dipole_zero_mag_field():
    # testing throwing of exception when mag_field = 0 (division by 0)
    mag_field = (0.0, 0.0, 0.0)
    ang_vel = (0.0, 0.02, 0.015)
    with pytest.raises(ZeroDivisionError):
        detumble.magnetorquer_dipole(mag_field, ang_vel)


def test_magnetorquer_dipole_zero_ang_vel():
    # testing ang_vel with zero value
    mag_field = (30.0, -45.0, 60.0)
    ang_vel = (0.0, 0.0, 0.0)
    result = detumble.magnetorquer_dipole(mag_field, ang_vel)
    assert result == [0.0, 0.0, 0.0]
