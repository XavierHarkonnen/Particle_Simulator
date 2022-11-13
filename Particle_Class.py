class Particle:
    def __init__(self, index, mass, charge, x, y, z, vx, vy, vz, density, color):
        self.index = index + 1

        self.mass = mass
        self.charge = charge

        self.x = x
        self.y = y
        self.z = z

        self.vx = vx
        self.vy = vy
        self.vz = vz

        self.ax = 0.0
        self.ay = 0.0
        self.az = 0.0

        self.density = density
        self.radius = pow((3 * mass) / (4 * 3.1415927 * density), (1 / 3))
        self.color = color

        self.ignore = False

        self.trail = []

        self.dist = 0

    def __str__(self):
        return "{:<2} {:<19} {:<19} {:<19} {:<19} {:<19} {:<19} {:<19} {:<19} {:<19} {:<15}".format(self.index,
                                                                                                    self.mass,
                                                                                                    self.charge,
                                                                                                    self.x, self.y,
                                                                                                    self.z, self.vx,
                                                                                                    self.vy, self.vz,
                                                                                                    self.density,
                                                                                                    str(self.color))

    def update_radius(self):
        self.radius = pow((3 * self.mass) / (4 * 3.1415927 * self.density), (1 / 3))
