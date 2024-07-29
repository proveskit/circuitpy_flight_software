from instrument import Gyroscope, Magnetometer


class Detumble:
    __gain = 1.0

    def magnetorquer_dipole(
        self, mag_field: Magnetometer, ang_vel: Gyroscope
    ) -> list[int]:
        dot_prod = pow(self.__dot_product(mag_field, mag_field), 0.5)
        # Prevent division by zero
        # TODO: should probably error here and catch it above
        if dot_prod == 0.0:
            return [0.0, 0.0, 0.0]

        scalar_coef = -self.__gain / dot_prod
        dipole_out = self.__x_product(mag_field, ang_vel)

        return [dipole_out[i] * scalar_coef for i in range(3)]

    @staticmethod
    def __dot_product(mag_field: Magnetometer, ang_vel: Gyroscope) -> float:
        return sum([a * b for a, b in zip(mag_field, ang_vel)])

    @staticmethod
    def __x_product(mag_field: Magnetometer, ang_vel: Gyroscope) -> list[float]:
        return [
            mag_field.y * ang_vel.z - mag_field.z * ang_vel.y,
            mag_field.x * ang_vel.z - mag_field.z * ang_vel.x,
            mag_field.x * ang_vel.y - mag_field.y * ang_vel.x,
        ]
