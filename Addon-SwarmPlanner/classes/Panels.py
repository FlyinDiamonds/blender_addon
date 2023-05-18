import bpy


class EditPanel(bpy.types.Panel):
    """Creates Edit panel."""
    bl_label = "Swarm"
    bl_idname = "OBJECT_PT_edit"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'FlyingDiamonds'

    def draw(self, context):
        layout = self.layout

        row = layout.row()
        row.operator("view3d.swarm_area")
        row = layout.row()
        row.operator("object.swarm_init")
        row = layout.row()
        row.operator("object.swarm_plan")
        row = layout.row()
        row.operator("object.swarm_speed")
        row = layout.row()
        row.operator("object.swarm_distance")
        row = layout.row()
        row.operator("object.swarm_paint")
        row = layout.row()
        row.operator("object.swarm_export")

        row = layout.row()
        row.operator("wm.url_open", text="Documentation", icon='URL'
                     ).url = "https://github.com/FlyinDiamonds/blender_addon/tree/main/Addon-SwarmPlanner"


classes = (
    EditPanel,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
