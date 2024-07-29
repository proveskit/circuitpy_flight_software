import pytest

from detumble import Detumble
from instrument import Gyroscope, Magnetometer
import pytest
import itertools
from detumble import Detumble
from instrument import Gyroscope, Magnetometer


@pytest.mark.parametrize(
    "mag_field, ang_vel, expected_dipole",
    [
        ((0.1, 0.2, 0.3), (0.1, 0.2, 0.3), [0.0, 0.0, 0.0]),
        ((0.0, 0.0, 0.0), (0.0, 0.0, 0.0), [0.0, 0.0, 0.0]),
        (
            (0.001, 0.3, 0.01),
            (0.001, 0.3, 0.01),
            [0.0, pytest.approx(-3.331464535720607e-05), -0.000999439360716182],
        ),
    ],
)
def test_magnetorquer_dipole(mag_field, ang_vel, expected_dipole):
    d = Detumble()
    dipole = d.magnetorquer_dipole(Magnetometer(mag_field), Gyroscope(ang_vel))
    assert dipole == expected_dipole
