import bpy
import gpu
from gpu_extras.batch import batch_for_shader


def draw_cube():
    p1 = None
    p2 = None

    for obj in bpy.context.scene.objects:
        if obj.name == f"Swarm Area p0":
            p1 = obj.location
        elif obj.name == f"Swarm Area p1":
            p2 = obj.location

    if p1 is None or p2 is None:
        return

    points = [
        (p1[0], p1[1], p1[2]), (p2[0], p1[1], p1[2]),
        (p1[0], p2[1], p1[2]), (p2[0], p2[1], p1[2]),
        (p1[0], p1[1], p2[2]), (p2[0], p1[1], p2[2]),
        (p1[0], p2[1], p2[2]), (p2[0], p2[1], p2[2])
    ]
    indices = [
        (0, 1), (0, 2), (1, 3), (2, 3),
        (4, 5), (4, 6), (5, 7), (6, 7),
        (0, 4), (1, 5), (2, 6), (3, 7)
    ]

    positions_ok = True
    for obj in bpy.context.scene.objects:
        if not obj.name.startswith("Drone"):
            continue

        for i in range(3):
            pos = list(obj.location)
            if pos[i] > max(p1[i],p2[i]) or pos[i] < min(p1[i],p2[i]):
                points.append(tuple(pos))
                pos[2] = 0
                points.append(tuple(pos))
                indices.append( (len(points)-2, len(points)-1) )
                positions_ok = False
                break

    shader = gpu.shader.from_builtin('3D_UNIFORM_COLOR')
    batch = batch_for_shader(shader, 'LINES', {"pos": points}, indices=indices)

    shader.bind()
    shader.uniform_float("color", (0,1,0,1) if positions_ok else (1,0,0,1))
    batch.draw(shader)


class SwarmArea(bpy.types.Operator):
    """Set area for drone swarm"""
    bl_idname = "view3d.swarm_area"
    bl_label = "Swarm - Set area"
    point0: bpy.props.FloatVectorProperty(name="Point 0", default=[-5,-5,0])
    point1: bpy.props.FloatVectorProperty(name="Point 1", default=[20,20,20])
    is_button: bpy.props.BoolProperty(default=False)

    def invoke(self, context, event):
        if self.is_button:
            self.update_props_from_context(context)
            self.is_button = False
            return self.execute(context)
        else:
            self.update_props_from_context(context)
            wm = context.window_manager
            return wm.invoke_props_dialog(self)

    def execute(self, context):
        handler_present = False
        for i, point in enumerate([self.point0, self.point1]):
            point_exists = False
            for obj in context.scene.objects:
                if obj.name == f"Swarm Area p{i}":
                    handler_present = True
                    point_exists = True
                    obj.location = point
                    break

            if not point_exists:
                bpy.ops.object.empty_add(location=point)
                context.active_object.name = f"Swarm Area p{i}"

        if not handler_present:
            bpy.types.SpaceView3D.draw_handler_add(draw_cube, (), 'WINDOW', 'POST_VIEW')

        return {"FINISHED"}
    
    def update_props_from_context(self, context):
        props = context.scene.fd_swarm_area_props
        self.point0, self.point1 = props.point0, props.point1
