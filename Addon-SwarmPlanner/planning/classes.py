import numpy as np


class FlightPath:
    def __init__(self, position_s, position_t, i_position_s, i_position_t):
        self.id = i_position_s
        self.start = position_s
        self.end = position_t
        self.length = -1
        self.start_position_index = i_position_s
        self.end_position_index = i_position_t
        self.collisions = []
        self.color = -1
        self.update_length()

    def update_length(self):
        self.length = np.linalg.norm(self.start - self.end)

class CrossingInfo:
    def __init__(self, valid, p1_point=None, p2_point=None, p1_distance=None, p2_distance=None, normal_separation=None, parallel_distance=None):
        self.valid = valid
        self.p1_point = p1_point
        self.p2_point = p2_point
        self.p1_distance = p1_distance
        self.p2_distance = p2_distance
        self.normal_separation = normal_separation
        self.parallel_distance = parallel_distance

        self.p1_distance_to_dz_s = None
        self.p1_distance_to_dz_e = None
        self.p2_distance_to_dz_s = None
        self.p2_distance_to_dz_e = None


class Collision:
    def __init__(self,
                 is_relevant: bool,
                 p1: FlightPath,
                 p2: FlightPath,
                 forbidden_delay_cnt = None,
                 p2_first: bool = False,
                 swap_required: bool = False):
        self.is_relevant = is_relevant
        self.p1: FlightPath = p1
        self.p2: FlightPath = p2
        self.forbidden_delay_cnt = forbidden_delay_cnt
        self.p2_first = p2_first
        self.swap_required = swap_required

