from dataclasses import dataclass, asdict


@dataclass
class Magnetometer:
    x: float
    y: float
    z: float

    def __init__(self, data: tuple[float, float, float]):
        self.x = data[0]
        self.y = data[1]
        self.z = data[2]

    def __iter__(self):
        return iter(asdict(self).values())
