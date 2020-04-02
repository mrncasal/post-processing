import glob
import pandas as pd
import numpy as np
import argparse
from numpy import cross
from numpy.linalg import norm

## Instructions

# 1. Use a .xyz type file generated by molden 
# 2. file_name_without_.xyz > atom_origin > atom_normal_1 > atom_normal_2 > increment > num_of_increments > last_atom_fixed-1


# Possibilita a passagem de argumentos pelo terminal
parser = argparse.ArgumentParser(description='Create N geometries of homodimers, displaced along the normal vector orientation')

parser.add_argument('file')
parser.add_argument('atom_origin')
parser.add_argument('atom_normal_1')
parser.add_argument('atom_normal_2')
parser.add_argument('increment')
parser.add_argument('num_of_increments')
parser.add_argument('last_atom_fixed')

args = parser.parse_args()

FILE = args.file+".xyz"

## MOLECULA FIXA

# Definicao de atomo para a origem
ATOM_0 =int(args.atom_origin)
#ATOM_0 = 0

# Definicao de atomos para o calculo do vetor normal
ATOM_NORMAL_1_IDX = int(args.atom_normal_1)
ATOM_NORMAL_2_IDX = int(args.atom_normal_2)

# Definições do incremento
INCREMENT = float(args.increment)
NUM_OF_INCREMENTS = int(args.num_of_increments)

# Definicao da fronteira entre molecula fixa e a deslocada no arquivo .xyz
LAST_ATOM_FROM_FIXED_MOLECULE_IDX = int(args.last_atom_fixed)
#LAST_ATOM_FROM_FIXED_MOLECULE_IDX = 30

## REDEFINICAO DA ORIGEM

with open(FILE) as file:
    geometry_txt = file.readlines()

geometry = geometry_txt[2:]
geometry = [geo.lstrip(" ").rstrip("\n").split("   ") for geo in geometry]
geometry_df = pd.DataFrame(geometry)
geometry_df.columns = ["Atom", "x", "y", "z"]
geometry_df["x"] = geometry_df["x"].astype(float)
geometry_df["y"] = geometry_df["y"].astype(float)
geometry_df["z"] = geometry_df["z"].astype(float)

atom_0_df = geometry_df.loc[ATOM_0]

x = atom_0_df["x"]
y = atom_0_df["y"]
z = atom_0_df["z"]

geometry_df["x"] = geometry_df["x"] - x
geometry_df["y"] = geometry_df["y"] - y
geometry_df["z"] = geometry_df["z"] - z

## VETOR NORMAL

atom_normal_1 = np.array(geometry_df.loc[ATOM_NORMAL_1_IDX].tolist()[1:])
atom_normal_2 = np.array(geometry_df.loc[ATOM_NORMAL_2_IDX].tolist()[1:])

normal_vector = cross(atom_normal_1, atom_normal_2)
normal_vector = normal_vector/norm(normal_vector)
increment_vector = normal_vector*INCREMENT

x_incr = increment_vector[0]
y_incr = increment_vector[1]
z_incr = increment_vector[2]

## INCREMENTO NA MOLECULA DESLOCADA

ATOM_TO_INCREMENT = LAST_ATOM_FROM_FIXED_MOLECULE_IDX + 1

FIXED_MOLECULE = geometry_df.loc[:LAST_ATOM_FROM_FIXED_MOLECULE_IDX].reset_index()
DISPLACED_MOLECULE = geometry_df.loc[LAST_ATOM_FROM_FIXED_MOLECULE_IDX+1:].reset_index()

for x in (range(NUM_OF_INCREMENTS+1)):
    NEW_DISPLACED_MOLECULE = DISPLACED_MOLECULE.copy()
    NEW_DISPLACED_MOLECULE.loc[:, "x"] = NEW_DISPLACED_MOLECULE.loc[:, "x"] + x_incr*(x)
    NEW_DISPLACED_MOLECULE.loc[:, "y"] = NEW_DISPLACED_MOLECULE.loc[:, "y"] + y_incr*(x)
    NEW_DISPLACED_MOLECULE.loc[:, "z"] = NEW_DISPLACED_MOLECULE.loc[:, "z"] + z_incr*(x)
    
    x_centroid = NEW_DISPLACED_MOLECULE["x"].mean()
    y_centroid = NEW_DISPLACED_MOLECULE["y"].mean()
    z_centroid = NEW_DISPLACED_MOLECULE["z"].mean()    
    centroid = np.array((x_centroid, y_centroid, z_centroid))
    
    print('Step {step}'.format(step=x))
    print("Centroid: ", centroid)
    print("Distance: ", np.dot(normal_vector, centroid))
    
    lista = geometry_txt[0:2]
    for row in FIXED_MOLECULE.iterrows():
        lista.append(' {}    {}   {}   {} \n'.format(row[1][1], row[1][2], row[1][3], row[1][4]))

    for row in NEW_DISPLACED_MOLECULE.iterrows():
        lista.append(' {}    {}   {}   {} \n'.format(row[1][1], row[1][2], row[1][3], row[1][4]))
    
    with open("{}-step{}.xyz".format(args.file , x), "w") as file:
        file.writelines(lista)
