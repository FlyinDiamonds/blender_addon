import bpy
from mathutils import Color

from ..planning.classes import *
from ..planning.planner import plan, get_max_time, paths_to_keyframes


class SwarmInitBase:
    bl_options = {'REGISTER', 'UNDO'}

    cnt_x: bpy.props.IntProperty(name="X Count", default=2, min=1, max=100)
    cnt_y: bpy.props.IntProperty(name="Y Count", default=2, min=1, max=100)
    spacing: bpy.props.FloatProperty(name="Spacing", default=2.0, min=1.0, max=5.0)
    is_button: bpy.props.BoolProperty(default=False, options={'HIDDEN'})

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
        for y in range(self.cnt_y):
            for x in range(self.cnt_x):
                bpy.ops.mesh.primitive_uv_sphere_add(radius=0.15,segments=8,ring_count=8,location=(x*self.spacing, y*self.spacing, 0))
                drone_id = x + y*self.cnt_x

                mat = bpy.data.materials.new("Drone_color")
                mat.diffuse_color = list(Color([0,0,0]).hsv)+[1]
                context.active_object.data.materials.append(mat)

                mat.keyframe_insert(data_path="diffuse_color", frame=0)
                context.active_object["custom_color"] = [0,0,0]
                context.active_object.name = f"Drone{drone_id:04d}"

                context.active_object.keyframe_insert(data_path="location", frame=0)
                context.active_object.keyframe_insert(data_path='["custom_color"]', frame=0)

        return {'FINISHED'}
    
    def update_props_from_context(self, context):
        props = context.scene.fd_swarm_init_props
        self.cnt_x, self.cnt_y, self.spacing = props.cnt_x, props.cnt_y, props.spacing


class SwarmInit(bpy.types.Operator, SwarmInitBase):
    """Initialize drone swarm"""
    bl_idname = "object.swarm_init"
    bl_label = "Swarm - Initialize"


class SwarmLand(bpy.types.Operator, SwarmInitBase):
    """Land drone swarm"""
    bl_idname = "object.swarm_land"
    bl_label = "Swarm - Land"


    def execute(self, context):
        scene = context.scene
        FRAMERATE = scene.render.fps
        SPEED = 5.0

        all_drones = []
        positions_source = []
        positions_target = []
        my_flight_paths = []

        for object in scene.objects:
            if object.name.startswith("Drone"):
                all_drones.append(object)

        if self.cnt_x * self.cnt_y > len(all_drones):
            return {'FINISHED'}
        
        for i, drone in enumerate(all_drones):
            position_source = list(drone.location)
            drone_id = int(drone.name[5:])
            grid_x, grid_y = drone_id % self.cnt_x, drone_id // self.cnt_x
            position_target = list((self.spacing * grid_x, self.spacing * grid_y, 0))

            positions_source.append(position_source)
            positions_target.append(position_target)
            my_flight_paths.append(FlightPath(np.array(position_source), np.array(position_target), i, i))

        flight_paths = plan(
                positions_source,
                positions_target,
                self.spacing,
                my_flight_paths)
        
        frame_start = scene.frame_current
        last_frame = int(get_max_time(flight_paths, SPEED)*FRAMERATE) + frame_start
        paths_to_keyframes(scene, all_drones, flight_paths, frame_start, last_frame, SPEED, FRAMERATE)

        return {'FINISHED'}
