from ursina import Vec3, distance

def dist2d(a, b) -> float:
    return distance(Vec3(a.x, 0, a.z), Vec3(b.x, 0, b.z))
