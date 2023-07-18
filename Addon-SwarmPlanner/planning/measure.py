from itertools import product
import numpy as np


def get_min_distance(positions, voxel_size):
    hashed = {}
    min_distance = 9999999
    for pos in positions:
        offsets = list(product([-1, 0, 1], repeat=3))
        for offset in offsets:
            section = (pos // voxel_size) + np.array(offset)
            voxel_hash = f"x{section[0]}y{section[1]}z{section[2]}"
            if voxel_hash not in hashed.keys():
                continue
            for candidate in hashed[voxel_hash]:
                distance = np.linalg.norm(candidate - pos)
                min_distance = min(min_distance, distance)

        section = pos // voxel_size
        hash = f"x{section[0]}y{section[1]}z{section[2]}"
        if hash not in hashed.keys():
            hashed[hash] = [pos]
        else:
            hashed[hash].append(pos)

    return min_distance


