import pytest

from instrument import Gyroscope, Magnetometer


@pytest.mark.parametrize(
    "data, expected_x, expected_y, expected_z",
    [
        ((0.1, 0.2, 0.3), 0.1, 0.2, 0.3),
        ((0.0, 0.0, 0.0), 0.0, 0.0, 0.0),
        ((0.001, 0.3, 0.01), 0.0, 0.3, 0.01),
    ],
)
def test_gyroscope(data, expected_x, expected_y, expected_z):
    gyro = Gyroscope(data)
    assert gyro.x == expected_x
    assert gyro.y == expected_y
    assert gyro.z == expected_z


def test_magnetometer():
    mag = Magnetometer((0.1, 0.2, 0.3))
    assert mag.x == 0.1
    assert mag.y == 0.2
    assert mag.z == 0.3
