import bpy
import mathutils


def is_drone_inside_mesh(drone_obj, color_obj):
    """Check if origin of given drone_obj is inside of color_obj."""
    is_inside = False

    if drone_obj.type != "MESH" or color_obj.type != "MESH":
        return is_inside

    # TODO any better solution for checking hit without applying original object transforms
    temp_color_obj = duplicate_obj(color_obj)
    origin = drone_obj.location
    x_axis = mathutils.Vector((1.0, 0.0, 0.0))
    direction = x_axis - origin
    hit, _, _, face_index = temp_color_obj.ray_cast(origin, direction.normalized())

    if hit:
        hitted_face = color_obj.data.polygons[face_index]
        world_space_normal = normal_to_world_space(color_obj, hitted_face.normal)
        is_inside = world_space_normal.dot(direction) > 0

    delete_obj(temp_color_obj)

    return is_inside


def duplicate_obj(obj):
    """Duplicate given object."""
    for selected_obj in bpy.context.selected_objects:
        selected_obj.select_set(False)
    
    obj.hide_set(False)
    obj.select_set(True)
    obj.display_type = 'WIRE'
    bpy.ops.object.duplicate(linked=False)
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    duplicated_obj = bpy.context.selected_objects[0]

    return duplicated_obj


def normal_to_world_space(obj, normal):
    """Returns normal converted from local space of given object to world space."""
    return obj.matrix_world.inverted_safe().transposed().to_3x3() @ normal


def delete_obj(obj):
    """Delete given object."""
    bpy.data.objects.remove(obj, do_unlink=True)
