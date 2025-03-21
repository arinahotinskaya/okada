import sys
import os

# Path to okada_wrapper
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "big", "okada_wrapper", "okada_wrapper"))
sys.path.append(parent_dir)

import init

# Reading parameters from eq_params
with open("eq_params", "r") as f:
    first_x = float(f.readline())
    first_y = float(f.readline())
    first_z = float(f.readline())
    eq_depths = float(f.readline())
    eq_dips1 = float(f.readline())
    eq_first_al1 = float(f.readline())
    eq_first_al2 = float(f.readline())
    eq_first_aw1 = float(f.readline())
    eq_first_aw2 = float(f.readline())
    eq_first_u1 = float(f.readline())
    eq_first_u2 = float(f.readline())
    eq_first_u3 = float(f.readline())

# Preparing data for calling dc3dwrapper
alpha = 2 / 3
xo = [first_x, first_y, first_z]
depth = eq_depths
dip = eq_dips1
strike_width = [eq_first_al1, eq_first_al2]
dip_width = [eq_first_aw1, eq_first_aw2]
dislocation = [eq_first_u1, eq_first_u2, eq_first_u3]

# Calling the function
success, u, grad_u = init.dc3dwrapper(alpha, xo, depth, dip, strike_width, dip_width, dislocation)

# Write ux, uy, uz to the eq_stn_disp file
with open("eq_stn_disp", "w") as f:
    f.write(f"{u[0]} {u[1]} {u[2]}\n")
