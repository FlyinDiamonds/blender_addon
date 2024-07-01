

def get_all_drones(context):
    drones = set()
    for obj in context.scene.objects:
        if not obj.name.startswith("Drone"):
            continue
        drones.add(obj)
    return drones
