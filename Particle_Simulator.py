# Importing necessary modules
# ----------------------------------------------------------------------------------------------------------------------

import sys
from datetime import datetime
import Particle_Class
from Functions import *

try:
    import pygame
    from pygame.locals import *

    pygame.init()

except ImportError:
    print("Import of pygame failed!")
    sys.exit()

# Constants
# ----------------------------------------------------------------------------------------------------------------------

FPS = 60
dT = 1 / FPS
background = (0, 0, 0)
resolution = pygame.display.Info()
x_offset = resolution.current_w / 2
y_offset = resolution.current_h / 2
trail_fade = 3
cam_pos = [0, 250, 0]
scroll_speed = 20
rotation_active = False


# Functions under construction
# ----------------------------------------------------------------------------------------------------------------------


def energy():
    grav_en = 0
    kin_en = 0
    elec_en = 0
    mag_en = 0
    for p in range(len(particles)):
        for o in range(p + 1, len(particles)):
            dist = ((particles[o].x - particles[p].x) ** 2 +
                    (particles[o].y - particles[p].y) ** 2 + (particles[o].z - particles[p].z) ** 2) ** 0.5

            grav_en += G * particles[o].mass * particles[p].mass / dist
            kin_en += 0.5 * particles[p].mass * ((particles[p].vx ** 2)
                                                 + (particles[p].vy ** 2) + (particles[p].vz ** 2))
            elec_en += k * particles[o].charge * particles[p].charge / dist

    print("Gravitational Potential Energy:", grav_en, "joules\n")
    print("Kinetic Energy:", kin_en, "joules\n")
    print("Electric Potential Energy:", elec_en, "joules\n")
    print("Magnetic Energy: I don't know how to calculate this\n")


# Draw_based functions
# ----------------------------------------------------------------------------------------------------------------------


def obj_draw(part, cam):
    for p in part:
        rotation = [(p.x - cam[0]) / p.dist, (p.y - cam[1]) / p.dist, (p.z - cam[2]) / p.dist]
        rotation = mult3_1(basis_conv, rotation)

        if rotation[2] <= 0:
            drawn_x = rotation[0] * 100 / rotation[2] + x_offset
            drawn_y = rotation[1] * 100 / rotation[2] + y_offset

            pygame.draw.circle(window, p.color, (drawn_x, drawn_y), 100 * p.radius / p.dist)


def trail_draw(part, cam):
    for p in part:
        for dot in p.trail:
            dot_dist = pyth(dot[0] - cam[0], dot[1] - cam[1], dot[2] - cam[2])

            rotation = [(dot[0] - cam[0]) / dot_dist, (dot[1] - cam[1]) / dot_dist, (dot[2] - cam[2]) / dot_dist]
            rotation = mult3_1(basis_conv, rotation)

            if rotation[2] <= 0:
                drawn_x = rotation[0] * 100 / rotation[2] + x_offset
                drawn_y = rotation[1] * 100 / rotation[2] + y_offset

                pygame.draw.circle(window, (int(p.color[0] / trail_fade), int(p.color[1] / trail_fade),
                                            int(p.color[2] / trail_fade)), (drawn_x, drawn_y), 1)


# Getting the program location and date, creating necessary directories
# ----------------------------------------------------------------------------------------------------------------------

date = datetime.now().strftime("%d\'%m\'%Y_%H\'%M\'%S")
base_directory = os.getcwd()
log_directory = base_directory + "\\Logs"
config_directory = base_directory + "\\Configs"

if not os.path.isdir(log_directory):
    try:
        os.mkdir(log_directory)
    except FileExistsError:
        pass

if not os.path.isdir(config_directory):
    try:
        os.mkdir(config_directory)
    except FileExistsError:
        pass

# Choosing the method of particle creation
# ----------------------------------------------------------------------------------------------------------------------

clear()

while True:
    print("Would you like to use the config file to generate particles? Y/N\n")
    config = input("Input: ").lower()
    if config == "y" or config == "yes":
        config = True
        break
    elif config == "n" or config == "no" or config == "":
        config = False
        break
    else:
        clear()
        print("Not a valid input!\n")

clear()

# Choosing realistic G
# ----------------------------------------------------------------------------------------------------------------------

while True:
    print("Would you like to use scaled gravity? Y/N\n    Scaled gravity allows for more engaging gravitational "
          "simulations, but will greatly interfere with the accuracy of electromagnetic simulations\n")
    scale = input("Input: ").lower()
    if scale == "y" or scale == "yes" or scale == "":
        use_scaling = True
        break
    elif scale == "n" or scale == "no":
        use_scaling = False
        break
    else:
        clear()
        print("Not a valid input!\n")

clear()

# Creating the particles from config file
# ----------------------------------------------------------------------------------------------------------------------

particles = []

if config:
    try:
        configfile = open("config.csv", "r")
        config_list = configfile.readlines()

        index = -1
        for line in config_list:
            if index == -1:
                if line == "Mass, Charge, X, Y, Z, X_Velocity, Y_Velocity, Z_Velocity, Density, Color":
                    print("Read Error\nConfig file has no data")
                    sys.exit()
                elif line != "Mass, Charge, X, Y, Z, X_Velocity, Y_Velocity, Z_Velocity, Density, Color\n":
                    print("Read Error\nConfig file is missing header")
                    sys.exit()
                index += 1
            else:
                line_list = line.strip().replace(" ", "").split(",")
                if len(line_list) == 1 and line_list[0] == "":
                    pass
                elif len(line_list) != 12:
                    print("Read Error\nConfig file is missing data or formatted incorrectly0")
                    sys.exit()
                else:
                    line_list[9] = line_list[9] + "," + line_list[10] + "," + line_list[11]
                    line_list.pop()
                    line_list.pop()

                    for x in range(len(line_list)):
                        if x == 9:
                            try:
                                if line_list[9][0] == "(" and line_list[9][-1] == ")":
                                    config_color = line_list[9][1:len(line_list[9]) - 1].replace(" ", "").split(",")
                                    try:
                                        for y in range(len(config_color)):
                                            config_color[y] = int(config_color[y])
                                        if len(config_color) != 3:
                                            print("Read Error\nConfig file is missing data or formatted incorrectly1")
                                            sys.exit()
                                        else:
                                            line_list[9] = tuple(config_color)
                                    except ValueError:
                                        print("Read Error\nConfig file is missing data or formatted incorrectly2")
                                        sys.exit()
                                else:
                                    print("Read Error\nConfig file is missing data or formatted incorrectly3")
                                    sys.exit()
                            except (ValueError, IndexError):
                                print("Read Error\nConfig file is missing data or formatted incorrectly4")
                                sys.exit()
                        else:
                            try:
                                line_list[x] = float(line_list[x])
                            except ValueError:
                                print("Read Error\nConfig file is missing data or formatted incorrectly5")
                                sys.exit()
                particles.append(Particle_Class.Particle(index, line_list[0], line_list[1], line_list[2], line_list[3],
                                                         line_list[4], line_list[5], line_list[6], line_list[7],
                                                         line_list[8], line_list[9]))
                index += 1
        configfile.close()

    except FileNotFoundError:
        print("Read Error\nFile \"config.csv\" does not exist.\nFile \"config.csv\" has been created")
        configfile = open("config.csv", "w")
        configfile.write("Mass, Charge, X, Y, Z, X_Velocity, Y_Velocity, Z_Velocity, Density, Color\n")
        configfile.close()
        sys.exit()

# Creating the particles from random
# ----------------------------------------------------------------------------------------------------------------------

if not config:
    while True:
        print("How many particles do you want to simulate?\n")
        try:
            num_par = int(input("Number of particles: "))
            break
        except ValueError:
            clear()
            print("Not a valid input!\n")

    for x in range(num_par):
        particles.append(
            Particle_Class.Particle(x, rand_param()[0], rand_param()[1], rand_param()[2], rand_param()[3],
                                    rand_param()[4], rand_param()[5], rand_param()[6], rand_param()[7], rand_param()[8],
                                    rand_param()[9]))

clear()

# Editing the particles
# ----------------------------------------------------------------------------------------------------------------------

while True:
    print("{:<2} {:<19} {:<19} {:<19} {:<19} {:<19} {:<19} {:<19} {:<19} {:<19} {:<15}".format("#", "Mass", "Charge",
                                                                                               "X", "Y", "Z",
                                                                                               "X_Velocity",
                                                                                               "Y_Velocity",
                                                                                               "Z_Velocity",
                                                                                               "Density", "Color"))

    for x in particles:
        print(x)
    print("\nChoose a parameter to edit")
    print("    For example, enter \"1-X_Velocity-12.3\" to change the X_Velocity of Particle 1 to 12.3")
    print("    Entering \"all\" or \"a\" for the first field will change that parameter for all particles")
    print("    Radius must be a tuple")
    print("    Entering an empty field will move to the simulation stage")

    change = input("\nInput: ").lower()

    valid_parameters_0 = []
    for x in particles:
        valid_parameters_0.append(x.index)
    valid_parameters_0.append("a")
    valid_parameters_0.append("all")

    valid_parameters_1 = ["#", "mass", "charge", "x", "y", "z", "x_velocity", "y_velocity", "z_velocity", "density",
                          "radius", "color"]
    allow = False

    if change == "":
        break
    else:
        changelist = change.split("-")

        try:
            changelist[0] = int(changelist[0])
        except ValueError:
            clear()
            print("Not a valid input!\n")

        try:
            if changelist[1] == "color":
                try:
                    if changelist[2][0] == "(" and changelist[2][-1] == ")":
                        color_change = changelist[2][1:len(changelist[2]) - 1].replace(" ", "").split(",")

                        try:
                            for x in range(len(color_change)):
                                color_change[x] = bound(int(color_change[x]), 0, 255)
                            if len(color_change) != 3:
                                clear()
                                print("Not a valid input!\n")
                            else:
                                changelist[2] = tuple(color_change)
                                allow = True
                        except ValueError:
                            clear()
                            print("Not a valid input!\n")
                    else:
                        clear()
                        print("Not a valid input!\n")
                except (ValueError, IndexError):
                    clear()
                    print("Not a valid input!\n")
            else:
                try:
                    changelist[2] = float(changelist[2])
                    allow = True
                except (ValueError, IndexError):
                    clear()
                    print("Not a valid input!\n")
        except IndexError:
            clear()
            print("Not a valid input!\n")

        if len(changelist) != 3:
            clear()
            print("Not a valid input!\n")
        elif changelist[0] not in valid_parameters_0:
            clear()
            print("Not a valid input!\n")
        elif changelist[1] not in valid_parameters_1:
            clear()
            print("Not a valid input!\n")
        elif changelist[2] == "":
            clear()
            print("Not a valid input!\n")
        elif allow:
            if changelist[1] == "#":
                clear()
                print("Particle number cannot be changed")
            elif changelist[1] == "mass":
                if changelist[0] == "a" or changelist[0] == "all":
                    for x in range(len(particles)):
                        particles[x].mass = changelist[2]
                        particles[x].update_radius()
                else:
                    particles[changelist[0] - 1].mass = changelist[2]
                    particles[changelist[0] - 1].update_radius()
                clear()
            elif changelist[1] == "charge":
                if changelist[0] == "a" or changelist[0] == "all":
                    for x in range(len(particles)):
                        particles[x].charge = changelist[2]
                else:
                    particles[changelist[0] - 1].charge = changelist[2]
                clear()
            elif changelist[1] == "x":
                if changelist[0] == "a" or changelist[0] == "all":
                    for x in range(len(particles)):
                        particles[x].x = changelist[2]
                else:
                    particles[changelist[0] - 1].x = int(changelist[2])
                clear()
            elif changelist[1] == "y":
                if changelist[0] == "a" or changelist[0] == "all":
                    for x in range(len(particles)):
                        particles[x].y = changelist[2]
                else:
                    particles[changelist[0] - 1].y = int(changelist[2])
                clear()
            elif changelist[1] == "z":
                if changelist[0] == "a" or changelist[0] == "all":
                    for x in range(len(particles)):
                        particles[x].z = changelist[2]
                else:
                    particles[changelist[0] - 1].z = int(changelist[2])
                clear()
            elif changelist[1] == "x_velocity":
                if changelist[0] == "a" or changelist[0] == "all":
                    for x in range(len(particles)):
                        particles[x].vx = changelist[2]
                else:
                    particles[changelist[0] - 1].vx = changelist[2]
                clear()
            elif changelist[1] == "y_velocity":
                if changelist[0] == "a" or changelist[0] == "all":
                    for x in range(len(particles)):
                        particles[x].vy = changelist[2]
                else:
                    particles[changelist[0] - 1].vy = changelist[2]
                clear()
            elif changelist[1] == "z_velocity":
                if changelist[0] == "a" or changelist[0] == "all":
                    for x in range(len(particles)):
                        particles[x].vz = changelist[2]
                else:
                    particles[changelist[0] - 1].vz = changelist[2]
                clear()
            elif changelist[1] == "density":
                if changelist[0] == "a" or changelist[0] == "all":
                    for x in range(len(particles)):
                        particles[x].density = changelist[2]
                        particles[x].update_radius()
                else:
                    particles[changelist[0] - 1].density = changelist[2]
                    particles[changelist[0] - 1].update_radius()
                clear()
            elif changelist[1] == "radius":
                clear()
                print("Radius cannot be changed")
            elif changelist[1] == "color":
                if changelist[0] == "a" or changelist[0] == "all":
                    for x in range(len(particles)):
                        particles[x].color = changelist[2]
                else:
                    particles[changelist[0] - 1].color = changelist[2]
                clear()

# Save setup as a config file and start logging position
# ----------------------------------------------------------------------------------------------------------------------

config_write(config_directory, date, particles)

new_log = open(log_directory + f"\\position_log_{date}.csv", "w")
new_log.write("#, X, Y, Z")
new_log.write("\n\n")
log(new_log, particles)

# Energy Calculation
# ----------------------------------------------------------------------------------------------------------------------

clear()

energy()

# Display and simulation
# ----------------------------------------------------------------------------------------------------------------------

window = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
pygame.display.set_caption("Particle Simulation")
fpsClock = pygame.time.Clock()

obj_dist(particles, cam_pos)
init_sort(particles)

i = 0

while True:
    # Updating the camera basis
    # ------------------------------------------------------------------------------------------------------------------

    cam_dist = pyth(cam_pos[0], cam_pos[1], cam_pos[2])

    cam_basis = [None, None, None]

    cam_basis[2] = [cam_pos[0] / cam_dist, cam_pos[1] / cam_dist, cam_pos[2] / cam_dist]
    bas0_dist = pyth(cam_basis[2][1], cam_basis[2][0])
    cam_basis[0] = [cam_basis[2][1] / bas0_dist, -cam_basis[2][0] / bas0_dist, 0]
    cam_basis[1] = [-cam_basis[2][2] * cam_basis[0][1], cam_basis[2][2] * cam_basis[0][0],
                    cam_basis[2][0] * cam_basis[0][1] - cam_basis[2][1] * cam_basis[0][0]]

    basis_conv = inv3(cam_basis)

    # ------------------------------------------------------------------------------------------------------------------

    window.fill(background)
    fpsClock.tick(FPS)

    acc_calc(particles, use_scaling)
    pos_upd(particles, dT)

    obj_dist(particles, cam_pos)
    post_sort(particles)

    trail_draw(particles, cam_pos)
    obj_draw(particles, cam_pos)

    if i == 10:
        trail_write(particles)

    if i == 20:
        i = 0
        log(new_log, particles)
        trail_write(particles)

    i += 1

    pygame.display.update()

    for event in pygame.event.get():
        if event.type == MOUSEBUTTONDOWN and not rotation_active:
            if pygame.mouse.get_pressed()[0] or pygame.mouse.get_pressed()[2]:
                rotation_active = True

        if event.type == MOUSEBUTTONUP and rotation_active:
            if not pygame.mouse.get_pressed()[0] and not pygame.mouse.get_pressed()[2]:
                rotation_active = False

        if event.type == pygame.MOUSEMOTION and rotation_active:
            pos_change = pygame.mouse.get_rel()

            cam_pos[1] += bound(pos_change[0], -10, 10) * cam_basis[0][1] * cam_dist / 250
            cam_pos[0] += bound(pos_change[0], -10, 10) * cam_basis[0][0] * cam_dist / 250

            tent_pos = [0, 0, 0]

            tent_pos[0] = cam_pos[0] + bound(pos_change[1], -10, 10) * cam_basis[1][0] * cam_dist / 250
            tent_pos[1] = cam_pos[1] + bound(pos_change[1], -10, 10) * cam_basis[1][1] * cam_dist / 250
            tent_pos[2] = cam_pos[2] + bound(pos_change[1], -10, 10) * cam_basis[1][2] * cam_dist / 250

            tent_len = pyth(tent_pos[0], tent_pos[1], tent_pos[2])

            if -0.99 < dot(tent_pos, [0, 0, 1]) / tent_len < 0.99:
                cam_pos = tent_pos

        if event.type == pygame.MOUSEWHEEL:
            cam_dist = pyth(cam_pos[0], cam_pos[1], cam_pos[2])
            if cam_dist > 50 or event.y == -1:
                cam_pos[0] -= event.y * cam_basis[2][0] * scroll_speed * cam_dist / 250
                cam_pos[1] -= event.y * cam_basis[2][1] * scroll_speed * cam_dist / 250
                cam_pos[2] -= event.y * cam_basis[2][2] * scroll_speed * cam_dist / 250

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                new_log.close()
                print("Remember to clean out your config and log folders!")
                sys.exit()
        if event.type == QUIT:
            pygame.quit()
            new_log.close()
            print("Remember to clean out your config and log folders!")
            sys.exit()
