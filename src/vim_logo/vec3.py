"""Vector functions for 3D vectors.

:author: Shay Hill
:created: 2023-12-31
"""

import math
from typing import Iterable

Vec3 = tuple[float, float, float]


def _get_magnitude(vector: Iterable[float]) -> float:
    """Return the euclidean norm of a vector.

    :param vector: the vector
    :return: the euclidean norm of the vector
    """
    return math.sqrt(sum(x**2 for x in vector))


def normalize(vector: Vec3) -> Vec3:
    """Return a normalized vector.

    :param vector: a three-component vector to normalize
    :return: the input vector with magnitude 1
    :raises ValueError: if the magnitude of the input vector is 0
    """
    magnitude = _get_magnitude(vector)
    if magnitude == 0:
        msg = f"Cannot normalize vector {vector} with magnitude 0"
        raise ValueError(msg)
    x, y, z = tuple(x / magnitude for x in vector)
    return x, y, z


def multiply(vector_a: Vec3, vector_b: Vec3) -> Vec3:
    """Return the component-wise product of two three-component vectors.

    :param vector_a: the first vector
    :param vector_b: the second vector
    :return: the component-wise product of the two vectors
    """
    ax, ay, az = vector_a
    bx, by, bz = vector_b
    return ax * bx, ay * by, az * bz


def scale(vector: Vec3, scalar: float) -> Vec3:
    """Scale a vector by a scalar.

    :param vector: the vector
    :param scalar: a scalar to be multiplied by each component of the vector
    :return: (x*scalar, y*scalar, z*scalar)
    """
    x, y, z = vector
    return (x * scalar, y * scalar, z * scalar)


def add(vector_a: Vec3, vector_b: Vec3) -> Vec3:
    """Return the component-wise sum of two three-component vectors.

    :param vector_a: the first vector
    :param vector_b: the second vector
    :return: the component-wise sum of the two vectors
    """
    ax, ay, az = vector_a
    bx, by, bz = vector_b
    return ax + bx, ay + by, az + bz

def vsum(*vectors: Vec3) -> Vec3:
    """Return the component-wise sum of an iterable of three-component vectors.

    :param vectors: an iterable of three-component vectors
    :return: the component-wise sum of the vectors
    """
    x, y, z = (sum(c) for c in zip(*vectors))
    return x, y, z


def subtract(vector_a: Vec3, vector_b: Vec3) -> Vec3:
    """Return the component-wise difference of two three-component vectors.

    :param vector_a: the first vector
    :param vector_b: the second vector
    :return: the component-wise difference of the two vectors
    """
    ax, ay, az = vector_a
    bx, by, bz = vector_b
    return ax - bx, ay - by, az - bz


def dot(vector_a: Vec3, vector_b: Vec3) -> float:
    """Return the dot product of two three-component vectors.

    :param vector_a: the first vector
    :param vector_b: the second vector
    :return: the dot product of the two vectors
    """
    return sum(multiply(vector_a, vector_b))

def clamp(vector_a: Vec3, min_val: float = 0, max_val: float = 1) -> Vec3:
    """Return a vector with each component clamped between two values.

    :param vector_a: the vector to clamp
    :param min_val: the minimum value to clamp to
    :param max_val: the maximum value to clamp to
    :return: a vector with each component clamped between min_val and max_val
    """
    x, y, z = vector_a
    return (min(max_val, max(min_val, x)),
            min(max_val, max(min_val, y)),
            min(max_val, max(min_val, z)))

def cross(vector_a: Vec3, vector_b: Vec3) -> Vec3:
    """Return the cross product of two three-component vectors.

    :param vector_a: the first vector
    :param vector_b: the second vector
    :return: the cross product of the two vectors
    """
    ax, ay, az = vector_a
    bx, by, bz = vector_b
    return ay * bz - az * by, az * bx - ax * bz, ax * by - ay * bx
