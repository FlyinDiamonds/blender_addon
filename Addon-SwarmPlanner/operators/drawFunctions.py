import gpu
from gpu_extras.batch import batch_for_shader
import bpy

def draw_distance():
    if "shader_draw_distance" not in dict(bpy.context.scene).keys():
        return
    if not bpy.context.scene["shader_draw_distance"]:
        return
    points = []
    indices = []

    current_frame = bpy.context.scene.frame_current
    for obj in bpy.context.scene.objects:
        if not obj.name.startswith("Drone"):
            continue

        if "collision_intervals" not in obj.keys():
            continue

        intervals = []
        for interval in obj["collision_intervals"].values():
            intervals += interval

        names = []
        for interval in intervals:
            if interval[0] > current_frame:
                continue
            if interval[1] == -1 or interval[1] > current_frame:
                names.append(f"Drone{interval[2]:04d}")

        if not names:
            continue

        objects = [candidate for candidate in bpy.context.scene.objects if candidate.name in names]
        objects.insert(0, obj)

        org_p_len = len(points)
        for i,target in enumerate(objects):
            pos = list(target.location)
            points.append(tuple(pos))
            pos[2] = 0
            points.append(tuple(pos))
            indices.append((len(points) - 2, len(points) - 1))
            if i > 0:
                indices.append((org_p_len, len(points) - 2))

    shader = gpu.shader.from_builtin('3D_UNIFORM_COLOR')
    batch = batch_for_shader(shader, 'LINES', {"pos": points}, indices=indices)

    shader.bind()
    shader.uniform_float("color", (1, 0, 0, 1))
    batch.draw(shader)



def draw_speed():
    if "shader_draw_speed" not in dict(bpy.context.scene).keys():
        return
    if not bpy.context.scene["shader_draw_speed"]:
        return
    points = []
    indices = []

    current_frame = bpy.context.scene.frame_current
    for obj in bpy.context.scene.objects:
        if not obj.name.startswith("Drone"):
            continue

        if "speed_intervals" not in obj.keys():
            continue

        active = False
        for interval in obj["speed_intervals"]:
            if interval[0] > current_frame:
                break
            if interval[1] == -1 or interval[1] > current_frame:
                active = True
                break

        if not active:
            continue

        pos = list(obj.location)
        points.append(tuple(pos))
        pos[2] = 0
        points.append(tuple(pos))
        indices.append((len(points) - 2, len(points) - 1))

    shader = gpu.shader.from_builtin('3D_UNIFORM_COLOR')
    batch = batch_for_shader(shader, 'LINES', {"pos": points}, indices=indices)

    shader.bind()
    shader.uniform_float("color", (1,0,0,1))
    batch.draw(shader)

def enable_draw_speed():
    if "shader_draw_speed" not in dict(bpy.context.scene).keys():
        bpy.types.SpaceView3D.draw_handler_add(draw_speed, (), 'WINDOW', 'POST_VIEW')
    bpy.context.scene["shader_draw_speed"] = True

    if "shader_draw_distance" in dict(bpy.context.scene).keys():
        bpy.context.scene["shader_draw_distance"] = False

def enable_draw_distance():
    if "shader_draw_distance" not in dict(bpy.context.scene).keys():
        bpy.types.SpaceView3D.draw_handler_add(draw_distance, (), 'WINDOW', 'POST_VIEW')
    bpy.context.scene["shader_draw_distance"] = True

    if "shader_draw_speed" in dict(bpy.context.scene).keys():
        bpy.context.scene["shader_draw_speed"] = False
