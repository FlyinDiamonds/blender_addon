from .classes import *


def saturate(val, _up=1, _low=0):
    return min(_up, max(_low, val))


def calculate_danger_zone_distance(p1:FlightPath, p2:FlightPath, crossing_info:CrossingInfo, min_separation):
    #here there be dragons
    if not crossing_info.valid:
        return

    normal_separation = crossing_info.normal_separation
    if normal_separation >= min_separation:
        crossing_info.valid = False
        return

    u = p1.end - p1.start
    v = p2.end - p2.start

    if (u == [0, 0, 0]).all() or (v == [0, 0, 0]).all():
        crossing_info.valid = False
        return

    horizontal_separation = np.sqrt(min_separation*min_separation - normal_separation*normal_separation)

    cos_a = np.dot(u, v)/np.linalg.norm(u)/np.linalg.norm(v)

    if 1-cos_a*cos_a <= 0.01:
        #parallel
        if crossing_info.p1_distance > p1.length or -crossing_info.p1_distance > p2.length:
            return
        if cos_a < 0:
            # 180
            return

        if crossing_info.p1_distance > crossing_info.p2_distance:
            crossing_info.p1_distance_to_dz_s = crossing_info.p1_distance - crossing_info.p2_distance
            crossing_info.p1_distance_to_dz_e = p1.length
            crossing_info.p2_distance_to_dz_s = 0
            crossing_info.p2_distance_to_dz_e = p1.length - (crossing_info.p1_distance - crossing_info.p2_distance)
        else:
            crossing_info.p1_distance_to_dz_s = 0
            crossing_info.p1_distance_to_dz_e = p2.length - (crossing_info.p2_distance - crossing_info.p1_distance)
            crossing_info.p2_distance_to_dz_s = crossing_info.p2_distance - crossing_info.p1_distance
            crossing_info.p2_distance_to_dz_e = p2.length
        return

    sin_a = np.sqrt(1-cos_a*cos_a)

    max_influence = horizontal_separation * cos_a / sin_a
    if cos_a / sin_a < 0.01:
        max_influence = 0.01
    projected_max_influence = horizontal_separation / sin_a


    p1_influence_start = min(crossing_info.p1_distance + horizontal_separation, max_influence)
    p1_influence_start_projected = projected_max_influence * p1_influence_start / max_influence
    crossing_info.p2_distance_to_dz_s = crossing_info.p2_distance - p1_influence_start_projected

    p1_influence_end = min(p1.length - crossing_info.p1_distance + horizontal_separation, max_influence)
    p1_influence_end_projected = projected_max_influence * p1_influence_end / max_influence
    crossing_info.p2_distance_to_dz_e = crossing_info.p2_distance + p1_influence_end_projected

    p2_influence_start = min(crossing_info.p2_distance + horizontal_separation, max_influence)
    p2_influence_start_projected = projected_max_influence * p2_influence_start / max_influence
    crossing_info.p1_distance_to_dz_s = crossing_info.p1_distance - p2_influence_start_projected

    p2_influence_end = min(p2.length - crossing_info.p2_distance + horizontal_separation, max_influence)
    p2_influence_end_projected = projected_max_influence * p2_influence_end / max_influence
    crossing_info.p1_distance_to_dz_e = crossing_info.p1_distance + p2_influence_end_projected

    return


def calculate_crossing(p1: FlightPath, p2:FlightPath) -> CrossingInfo:
    if p1.id == p2.id:
        return CrossingInfo(False)

    u = p1.end - p1.start
    v = p2.end - p2.start
    n = np.cross(u, v)
    t = p2.start - p1.start

    if (u == [0, 0, 0]).all() or (v == [0, 0, 0]).all():
        # fp is point
        return CrossingInfo(False)

    if (n == [0,0,0]).all():
        # parallel, project p2start onto u
        t1 = np.dot(p2.start - p1.start, u) / np.dot(u, u)
        t2 = 0

    else:
        R = np.cross(n/np.dot(n,n), t)
        t1 = np.dot(R, v)
        t2 = np.dot(R, u)

    p1_point = p1.start + t1*u
    p2_point = p2.start + t2*v

    p1_distance = p1.length*t1
    p2_distance = p2.length*t2

    normal_separation = np.linalg.norm(p1_point - p2_point)
    return CrossingInfo(True, p1_point, p2_point, p1_distance, p2_distance, normal_separation)


def evaluate_danger(
        p1:FlightPath,
        p2:FlightPath,
        crossing_info:CrossingInfo) -> Collision:

    if not crossing_info.valid:
        return Collision(False, p1, p2)

    if crossing_info.p1_distance_to_dz_s is None:
        return Collision(False, p1, p2)

    if crossing_info.p1_distance_to_dz_e <= 0 or crossing_info.p1_distance_to_dz_s >= p1.length:
        return Collision(False, p1, p2)

    forbidden_delay_cnt = max(0, crossing_info.p2_distance_to_dz_s) - max(0, crossing_info.p1_distance_to_dz_s)

    p1_starts_in_dz = crossing_info.p1_distance_to_dz_e > 0 and crossing_info.p1_distance_to_dz_s <= 0
    p1_ends_in_dz = crossing_info.p1_distance_to_dz_e >= p1.length and crossing_info.p1_distance_to_dz_s < p1.length

    p2_starts_in_dz = crossing_info.p2_distance_to_dz_e > 0 and crossing_info.p2_distance_to_dz_s <= 0
    p2_ends_in_dz = crossing_info.p2_distance_to_dz_e >= p2.length and crossing_info.p2_distance_to_dz_s < p2.length

    p1_inside_dz = p1_starts_in_dz and p1_ends_in_dz
    p2_inside_dz = p2_starts_in_dz and p2_ends_in_dz

    if p1_inside_dz or p2_inside_dz:
        return Collision(True, p1, p2, forbidden_delay_cnt,
                         p2_first=crossing_info.p2_distance < crossing_info.p1_distance)

    if p1_starts_in_dz and p2_starts_in_dz:
        return Collision(True, p1, p2, forbidden_delay_cnt,
                         p2_first=crossing_info.p2_distance < crossing_info.p1_distance)

    if p1_ends_in_dz and p2_ends_in_dz:
        return Collision(True, p1, p2, forbidden_delay_cnt,
                         p2_first=p2.length - crossing_info.p2_distance > p1.length - crossing_info.p1_distance)

    return Collision(True, p1, p2, forbidden_delay_cnt, p2_first=p1_ends_in_dz or p2_starts_in_dz)


def detect_collisions(flight_paths, DANGER_ZONE):
    for current_flight_path in flight_paths:
        collisions = []
        for tested_flight_path in flight_paths:
            if current_flight_path.start_position_index == tested_flight_path.start_position_index:
                continue
            crossing_info = calculate_crossing(current_flight_path, tested_flight_path)
            calculate_danger_zone_distance(
                            current_flight_path,
                            tested_flight_path,
                            crossing_info,
                            DANGER_ZONE)
            collision = evaluate_danger(
                            current_flight_path,
                            tested_flight_path,
                            crossing_info)
            if collision.is_relevant:
                collisions.append(collision)
        flight_paths[current_flight_path.id].collisions = collisions
