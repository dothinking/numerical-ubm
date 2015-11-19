# encoding: utf8
import numpy as np
import math
import re
from sympy import *
from scipy import integrate
# a = np.array([[5,0,0],[1,2,3],[1,5,6],[7,5,1],[3,4,5],[2,4,6]])
# b = np.array([2,3,4])
# c = np.array([2,3,4])
# c.shape = -1,1

def velocity_field(stream_function,z,r):
    vz = -diff(stream_function,r) / r
    vr = diff(stream_function,z) / r
    return vz,vr

def plastic_strain(vz,vr,z,r):
    strain_rate_r = diff(vr,r)
    strain_rate_z = diff(vz,z)
    strain_rate_sita = -(strain_rate_r+strain_rate_z)
    strain_rate_rz = 0.5 * (diff(vr,z)+diff(vz,r))
    strain_rate = sqrt(2.0/3.0*(strain_rate_r**2 + strain_rate_z**2 + strain_rate_sita**2 + 2.0*strain_rate_rz**2))
    return strain_rate

r,z,zn,apha = symbols('r,z,zn,apha',positive=True)
stream_function = -0.5 / apha*(1-zn**2/z**2)*r**2
vz,vr = velocity_field(stream_function,z,r)
ps = plastic_strain(vz,vr,z,r)

x = np.array([z,r])
y = np.array([0.5*z,r*2])
print np.dot(x,y)

expr = sin(r)/r + z + zn
f = lambdify((r,z), expr,'numpy')
print f(np.array([[1],[2]]),np.array([[1],[2]])),math.sin(1)+2

print np.arange(1,3)