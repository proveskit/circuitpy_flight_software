from dataclasses import dataclass, asdict


@dataclass
class Gyroscope:
    x: float
    y: float
    z: float

    def __init__(self, data: tuple[float, float, float]):
        self.x = self.__zero_out_data(data[0])
        self.y = self.__zero_out_data(data[1])
        self.z = self.__zero_out_data(data[2])

    def __iter__(self):
        return iter(asdict(self).values())

    @staticmethod
    def __zero_out_data(ang_vel: float) -> float:
        return 0.0 if ang_vel < 0.01 else ang_vel
