

def get_all_drones(context):
    drones = set()
    for obj in context.scene.objects:
        if not obj.name.startswith("Drone"):
            continue
        drones.add(obj)
    return drones


def update_from_property_group(operator, props):
    for prop, value in props.items():
        try:
            setattr(operator, prop, value)
        except AttributeError:
            pass
