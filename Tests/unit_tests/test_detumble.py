import unittest
from Batt_Board import detumble


class TestDetumble(unittest.TestCase):

    def test_dot_product(self):
        # dot_product is only ever called to give the square of mag_field
        mag_field_vector = (30.0, -45.0, 60.0)
        result = detumble.dot_product(mag_field_vector, mag_field_vector)
        self.assertEqual(result, 6525.0)

        # testing with two different vectors
        vector1 = (1, 2, 3)
        vector2 = (4, 5, 6)
        result = detumble.dot_product(vector1, vector2)
        self.assertEqual(result, 32)  # 1*4 + 2*5 + 3*6 = 32

    def test_x_product(self):
        mag_field_vector = (30.0, -45.0, 60.0)
        ang_vel_vector = (0.0, 0.02, 0.015)
        expected_result = [-1.875, 0.45, 0.6]
        actual_result = detumble.x_product(
            mag_field_vector, ang_vel_vector
        )  # cross product
        self.assertAlmostEqual(actual_result[0], expected_result[0], places=5)
        self.assertAlmostEqual(actual_result[1], expected_result[1], places=5)
        self.assertAlmostEqual(actual_result[2], expected_result[2], places=5)
        # x_product takes in tuple arguments and returns a list value

    # magnetorquer_dipole is called by do_detumble() in (FC board) functions.py & (Batt Board) battery_functions.py
    # mag_field: mag. field strength at x, y, & z axis (tuple -> ex. (30.0, -45.0, 60.0)) (magnetometer reading)
    # ang_vel: ang. vel. at x, y, z axis (tuple -> ex. (0.0, 0.02, 0.015)) (gyroscope reading)
    def test_magnetorquer_dipole(self):
        mag_field = (30.0, -45.0, 60.0)
        ang_vel = (0.0, 0.02, 0.015)
        expected_result = [0.023211, -0.00557, -0.007426]
        actual_result = detumble.magnetorquer_dipole(mag_field, ang_vel)
        # allow for small margin of error w/ floating point arithmetic
        self.assertAlmostEqual(actual_result[0], expected_result[0], places=5)
        self.assertAlmostEqual(actual_result[1], expected_result[1], places=5)
        self.assertAlmostEqual(actual_result[2], expected_result[2], places=5)

        # testing handling of division by 0
        with self.assertRaises(ZeroDivisionError):
            detumble.magnetorquer_dipole((0.0, 0.0, 0.0), ang_vel)


# How to run: "cd Tests" > "cd unit_tests" > "python3 test_detumble.py"
# instead of having to use unittest module "python -m unittest test_detumble.py"
if __name__ == "__main__":
    unittest.main()
