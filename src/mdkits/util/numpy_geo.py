"""
filename: numpy_geo.py
function: some vector calculation with numpy
"""


from numpy import array, dot, abs, cross
from numpy.linalg import norm
import numpy as np



def point_plane_distance(plane):
# distance of point with a plane(a list with [normal_voctor, a_point_in_plane])
    def point(point):
        return abs(dot(plane[0], point - plane[1])) / norm(plane[0])
    return point


def point_point_distance(point1, point2):
# distance of point with a point
    return norm(point1 - point2)


def point(frame):
# return a point of atom, from .xyz file
    def point_index(index):
        return array(frame[index].split()[1:]).astype(float)
    return point_index

def plane(frame, index1, index2, index3):
# return a normal voctor of a plane with three point(index and group)
    get_point = point(frame)
    base1 = get_point(index1)
    base2 = get_point(index2)
    base3 = get_point(index3)
    return [cross(base2 - base1, base3 - base1), base3]


def vector_between_two_vector(vector1, vector2):
    vector1_unit = vector1 / np.linalg.norm(vector1)
    vector2_unit = vector2 / np.linalg.norm(vector2)
    vector = vector1_unit + vector2_unit
    return vector


def vector_vector_angle(vector, surface_vector):
    cos = np.dot(vector, surface_vector) / (np.linalg.norm(vector) * np.linalg.norm(surface_vector))
    vector_vector_angle = np.arccos(np.clip(cos, -1.0, 1.0))
    vector_vector_angle = np.degrees(vector_vector_angle)
    return vector_vector_angle


def cell_to_wrap_coefficients(cell, z=False):
    angle = np.radians(180-cell[-1])
    dangle = [np.cos(angle), np.sin(angle)]
    xyz = cell[0:3]
    if z:
        coefficients = np.array([
            [(kx * xyz[0] + ky * dangle[0] * xyz[1]), (ky * dangle[1] * xyz[1]), kz * xyz[2]]
            for kx in range(-1, 2)
            for ky in range(-1, 2)
            for kz in range(-1, 2)
        ])
    else:
        coefficients = np.array([
            [(kx * xyz[0] + ky * dangle[0] * xyz[1]), (ky * dangle[1] * xyz[1]), 0]
            for kx in range(-1, 2)
            for ky in range(-1, 2)
        ])

    return coefficients


def unwrap(atom1, atom2, coefficients, max=0, total=False):
    init_dist = point_point_distance(atom1, atom2)
    if total:
        atoms = atom2 + coefficients
        distance = np.linalg.norm(atoms-atom1, axis=1)

        return distance, atoms
    else:
        if init_dist > max:
            min_dist = float('inf')
            closest_point = None
            atoms = atom2 + coefficients
            distance = np.linalg.norm(atoms-atom1, axis=1)
            min_index = np.argmin(distance)
            min_dist = distance[min_index]
            closest_point = atoms[min_index]

        else:
            closest_point = atom2
            min_dist = init_dist

        return min_dist, closest_point


def find_surface(surface_group:np.ndarray, layer_tolerance=1, surface_tolerance=5):
    sort_group = np.sort(surface_group)
    layer_mean = []
    current_layer = [sort_group[0]]
    for i in range(1, len(sort_group)):
        if abs(sort_group[i] - sort_group[i-1]) < layer_tolerance:
            current_layer.append(sort_group[i])
        else:
            layer_mean.append(np.mean(current_layer))
            current_layer = [sort_group[i]]
        layer_mean.append(np.mean(current_layer))
    
    if len(current_layer) == 1:
        return layer_mean[0]

    diff = np.diff(layer_mean)
    if np.any(diff > surface_tolerance):
        index = np.argmax(diff > 5)
        return (layer_mean[index], layer_mean[index + 1])
    else:
        return (layer_mean[-1], layer_mean[0])
