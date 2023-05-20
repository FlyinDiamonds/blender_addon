from .classes import *

from scipy.optimize import linear_sum_assignment
from .collision_detection import detect_collisions
from typing import List
import time
import numpy as np

def create_cost_matrix(source, target):
    #   t0 t1
    # s0
    # s1
    cost_matrix = []
    for s in source:
        cost_row = []
        for t in target:
            delta = t - s
            distance = np.sqrt((delta * delta).sum())
            distance *= distance
            cost_row.append(distance)
        cost_matrix.append(cost_row)
    return np.array(cost_matrix)


def color_analog(_collisions:List[Collision], safe_delay):
    collisions = [collision for collision in _collisions if collision.p2.color != -1]
    collisions.sort(key=lambda collision: collision.forbidden_delay_cnt)

    delay = 0
    for collision in collisions:
        if not collision.p2_first:
            continue
        min_delay = collision.forbidden_delay_cnt + collision.p2.color + safe_delay
        delay = max(delay, min_delay)

    while collisions:
        collision = collisions.pop(0)
        if delay < collision.forbidden_delay_cnt + collision.p2.color - safe_delay:
            break
        else:
            min_delay = collision.forbidden_delay_cnt + collision.p2.color + safe_delay
            delay = max(delay, min_delay)

    return delay


def plan(sg, tg, DANGER_ZONE):
    formation_s = np.array(sg)
    formation_t = np.array(tg)
    # do linear assignment
    print("LINEAR ASSIGNMENT STARTED")
    cm = create_cost_matrix(formation_s, formation_t)
    rows, cols = linear_sum_assignment(cm)
    flight_paths = [FlightPath(formation_s[s], formation_t[t], s, t) for s, t in zip(rows, cols)]
    print("LINEAR ASSIGNMENT FINISHED\n")


    print("COLLISION EVALUATION STARTED")
    detect_collisions(flight_paths, DANGER_ZONE)
    print("COLLISION EVALUATION FINISHED\n")

    print("GRAPH COLORING STARTED")
    # construct graph
    for path in flight_paths:
        if len(path.collisions) == 0:
            path.color = 0
    graph = [path for path in flight_paths if len(path.collisions) > 0]
    graph.sort(key=lambda path: path.length, reverse=True)
    graph.sort(key=lambda path: any([c.p2_first for c in path.collisions]))

    move_streak = 0
    streak_start_id = -1

    while graph:
        override_prerequisite_check = False

        current_flight_path = graph.pop(0)

        if move_streak >= len(graph) or streak_start_id == current_flight_path.id:
            override_prerequisite_check = True
            # break

        # check if has uncolored prerequisite
        unfulfilled_prerequisite_ids = []
        for collision in current_flight_path.collisions:
            if collision.p2_first and collision.p2.color == -1:
                unfulfilled_prerequisite_ids.append(collision.p2.id)

        if override_prerequisite_check or (not unfulfilled_prerequisite_ids):
            current_flight_path.color = color_analog(current_flight_path.collisions, DANGER_ZONE*1.44)
            move_streak = 0
            streak_start_id = -1
            continue

        new_index = 0
        while unfulfilled_prerequisite_ids:
            if graph[new_index].id in unfulfilled_prerequisite_ids:
                unfulfilled_prerequisite_ids.remove(graph[new_index].id)
            new_index += 1

        graph.insert(new_index, current_flight_path)
        if move_streak == 0:
            streak_start_id = current_flight_path.id
        move_streak += 1
    print("GRAPH COLORING FINISHED\n")
    return flight_paths


def get_max_time(flight_paths, SPEED):
    return max([(p.length + p.color) / SPEED for p in flight_paths])


def reverse_paths(_paths, SPEED):
    time_max = get_max_time(_paths, SPEED)
    for path in _paths:
        path.start, path.end = path.end, path.start
        path.start_position_index, path.end_position_index = path.end_position_index, path.start_position_index

        path_time = (path.length + path.color) / SPEED
        dt = time_max - path_time
        path.color = dt * SPEED


def plan_fastest(_source_points, _target_points, SPEED, DANGER_ZONE):
    tstart = time.time()
    og_paths = plan(_source_points, _target_points, DANGER_ZONE)
    og_time = get_max_time(og_paths, SPEED)

    reversed_paths = plan(_target_points, _source_points, DANGER_ZONE)
    reverse_paths(reversed_paths, SPEED)
    reversed_time = get_max_time(reversed_paths, SPEED)

    print(f"PLANNING TOOK: {time.time()-tstart}")
    print(f"OG TIME: {og_time}, REV TIME: {reversed_time}")
    if reversed_time < og_time:
        print("using reversed paths")
        return reversed_paths
    print("using og paths")
    return og_paths
