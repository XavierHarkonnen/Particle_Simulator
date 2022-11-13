# Importing necessary modules
# ----------------------------------------------------------------------------------------------------------------------

import os
import platform
import random

# Constants
# ----------------------------------------------------------------------------------------------------------------------

G = 0.000000000066743
k = 8987551792.3

# Non-returning functions
# ----------------------------------------------------------------------------------------------------------------------

if platform.system() == "Windows":
    def clear():
        os.system("cls")
else:
    def clear():
        os.system("clear")


def use_scaling(a):
    if not a:
        scale_factor = 1


def acc_calc(part, scaling):
    if scaling:
        scale_factor = 100000000000
    else:
        scale_factor = 1

    for p in part:
        for o in part:
            if o != p:
                dist = pyth((o.x - p.x), (o.y - p.y), (o.z - p.z))
                unit_vec = [(o.x - p.x) / dist, (o.y - p.y) / dist, (o.z - p.z) / dist]

                p.ax += unit_vec[0] * G * scale_factor * o.mass / (dist ** 2)
                p.ay += unit_vec[1] * G * scale_factor * o.mass / (dist ** 2)
                p.az += unit_vec[2] * G * scale_factor * o.mass / (dist ** 2)

                p.ax += p.charge * ((-k * o.charge * unit_vec[0]) / (dist ** 2)
                                    + (o.vy - p.vy) * (
                                            (10 ** -7) * o.charge * ((o.vx - p.vx) * unit_vec[1] - (o.vy - p.vy)
                                                                     * unit_vec[0])) / (dist ** 2)
                                    - (o.vz - p.vz) * (
                                            (10 ** -7) * o.charge * ((o.vz - p.vz) * unit_vec[0] - (o.vx - p.vx)
                                                                     * unit_vec[2])) / (dist ** 2)) / p.mass
                p.ay += p.charge * ((-k * o.charge * unit_vec[1]) / (dist ** 2)
                                    + (o.vz - p.vz) * (
                                            (10 ** -7) * o.charge * ((o.vy - p.vy) * unit_vec[2] - (o.vz - p.vz)
                                                                     * unit_vec[1])) / (dist ** 2)
                                    - (o.vx - p.vx) * (
                                            (10 ** -7) * o.charge * ((o.vx - p.vx) * unit_vec[1] - (o.vy - p.vy)
                                                                     * unit_vec[0])) / (dist ** 2)) / p.mass
                p.az += p.charge * ((-k * o.charge * unit_vec[2]) / (dist ** 2)
                                    + (o.vx - p.vx) * (
                                            (10 ** -7) * o.charge * ((o.vz - p.vz) * unit_vec[0] - (o.vx - p.vx)
                                                                     * unit_vec[2])) / (dist ** 2)
                                    - (o.vy - p.vy) * (
                                            (10 ** -7) * o.charge * ((o.vy - p.vy) * unit_vec[2] - (o.vz - p.vz)
                                                                     * unit_vec[1])) / (dist ** 2)) / p.mass


def pos_upd(part, delta):
    for p in part:
        p.vx += p.ax * delta
        p.vy += p.ay * delta
        p.vz += p.az * delta

        p.x += p.vx * delta
        p.y += p.vy * delta
        p.z += p.vz * delta

        p.ax = 0
        p.ay = 0
        p.az = 0


def obj_dist(part, cam):
    for p in part:
        p.dist = pyth(p.x - cam[0], p.y - cam[1], p.z - cam[2])


def init_sort(part):
    part.sort(key=lambda p: p.dist)


def post_sort(part):
    n = len(part)
    for i in range(n):
        for j in range(0, n - i - 1):
            if part[j].dist < part[j + 1].dist:
                part[j], part[j + 1] = part[j + 1], part[j]


def trail_write(part):
    for p in part:
        p.trail.append([p.x, p.y, p.z])
        if len(p.trail) > 1000:
            p.trail.pop(0)


def config_write(directory, time, part):
    new_config = open(directory + f"\\config_{time}.csv", "w")
    new_config.write("Mass, Charge, X, Y, Z, X_Velocity, Y_Velocity, Z_Velocity, Density, Color\n")
    for p in part:
        new_config.write(f"{p.mass}, {p.charge}, {p.x}, {p.y}, {p.z}, {p.vx}, {p.vy}, {p.vz}, {p.density}, {p.color}\n")
    new_config.close()


def log(log_name, part):
    for p in part:
        log_name.write(f"{p.index}, {p.x}, {p.y}, {p.z}")
        log_name.write("\n")
    log_name.write("\n")


# Returning functions
# ----------------------------------------------------------------------------------------------------------------------


def rand_param():
    mass = random.uniform(1000, 1000000)
    charge = random.uniform(-1, 1)
    x = random.uniform(-500, 500)
    y = random.uniform(-500, 500)
    z = random.uniform(-500, 500)
    vx = random.uniform(-10, 10)
    vy = random.uniform(-10, 10)
    vz = random.uniform(-10, 10)
    density = random.uniform(1, 10)
    color = (random.randrange(0, 255), random.randrange(0, 255), random.randrange(0, 255))
    return [mass, charge, x, y, z, vx, vy, vz, density, color]


def bound(a, b, c):
    d = max(a, b)
    return min(c, d)


def pyth(a, b, c=0):
    return (a ** 2 + b ** 2 + c ** 2) ** 0.5


# Matrix functions
# ----------------------------------------------------------------------------------------------------------------------


def det2(a, b, c, d):
    return a * d - c * b


def det3(m):
    result = m[0][0] * det2(m[1][1], m[2][1], m[1][2], m[2][2])
    result -= m[0][1] * det2(m[1][0], m[2][0], m[1][2], m[2][2])
    result += m[0][2] * det2(m[1][0], m[2][0], m[1][1], m[2][1])

    return result


def inv3(m):
    result = [[None, None, None], [None, None, None], [None, None, None]]

    result[0][0] = det2(m[1][1], m[2][1], m[1][2], m[2][2]) / det3(m)
    result[1][0] = det2(m[1][2], m[2][2], m[1][0], m[2][0]) / det3(m)
    result[2][0] = det2(m[1][0], m[2][0], m[1][1], m[2][1]) / det3(m)
    result[0][1] = det2(m[0][2], m[2][2], m[0][1], m[2][1]) / det3(m)
    result[1][1] = det2(m[0][0], m[2][0], m[0][2], m[2][2]) / det3(m)
    result[2][1] = det2(m[0][1], m[2][1], m[0][0], m[2][0]) / det3(m)
    result[0][2] = det2(m[0][1], m[0][2], m[1][1], m[1][2]) / det3(m)
    result[1][2] = det2(m[0][2], m[1][2], m[0][0], m[1][0]) / det3(m)
    result[2][2] = det2(m[0][0], m[1][0], m[0][1], m[1][1]) / det3(m)

    return result


def mult3_1(m, n):
    result = [None, None, None]

    result[0] = m[0][0] * n[0] + m[1][0] * n[1] + m[2][0] * n[2]
    result[1] = m[0][1] * n[0] + m[1][1] * n[1] + m[2][1] * n[2]
    result[2] = m[0][2] * n[0] + m[1][2] * n[1] + m[2][2] * n[2]

    return result
