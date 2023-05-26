import bpy
import json

class SwarmExporter(bpy.types.Operator):
    """Export flight paths for drone swarm"""
    bl_idname = "object.swarm_export"
    bl_label = "Swarm - Export flight paths"
    bl_options = {'REGISTER', 'UNDO'}

    filepath: bpy.props.StringProperty(subtype="FILE_PATH")

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

    def execute(self, context):
        content = {
            "fps": context.scene.render.fps,
            "data":{},
            "drone_count":0,
        }

        data = {}
        original_frame = context.scene.frame_current

        for frame in range(context.scene.frame_end+1):
            context.scene.frame_set(frame)
            for object in context.scene.objects:
                if not object.name.startswith("Drone"):
                    continue

                drone_id = int(object.name[-4:])
                position = list(object.location)
                color = list(object["custom_color"])

                if drone_id not in data.keys():
                    data[drone_id] = {"position":[position],"color":[color]}
                else:
                    data[drone_id]["position"].append(position)
                    data[drone_id]["color"].append(color)

        content["data"] = data
        content["drone_count"] = len(data)
        context.scene.frame_set(original_frame)
        with open(self.filepath, "w") as f:
            json.dump(content, f)

        return {'FINISHED'}

