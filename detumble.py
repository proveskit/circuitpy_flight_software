def dot_product(vector1, vector2):
    return sum([a*b for a,b in zip(vector1, vector2)])

def x_product(vector1, vector2):
    return [vector1[1]*vector2[2]-vector1[2]*vector2[1],vector1[0]*vector2[2]-vector1[2]*vector2[0],vector1[0]*vector2[1]-vector1[1]*vector2[0]]

def gain_func():
    return 1.0

def magnetorquer_dipole(mag_field,ang_vel):
    gain=gain_func()
    scalar_coef=-gain/pow(dot_product(mag_field,mag_field),0.5)
    dipole_out=x_product(mag_field,ang_vel)
    for i in range(3):
        dipole_out[i]*=scalar_coef
    return dipole_out
