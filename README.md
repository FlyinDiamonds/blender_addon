# FlyinDiamonds

## First installation
- Add-on requires python module `scipy` installed in Blender's python interpreter, not the PC's one so follow these steps:
    1. Turn on Blender with Admin rights
    2. Make sure you are connected to the internet and you have enabled internet connection in Blender `Edit -> Preferences -> System -> Network`
    3. Go to `Scripting` screen preset and add a new file
    4. Paste this:
    ```
    import subprocess
    import sys

    py_exec = sys.executable
    # ensure pip is installed & update
    subprocess.call([str(py_exec), "-m", "ensurepip", "--user"])
    subprocess.call([str(py_exec), "-m", "pip", "install", "--upgrade", "pip"])
    # install dependencies using pip
    # dependencies such as 'numpy' could be added to the end of this command's list
    subprocess.call([str(py_exec),"-m", "pip", "install", "--user", "scipy"])
    ```
    5. (OPTIONAL) Turn on Blender System Console to see what is happening by `Blender -> Window -> Toggle system console`
    6. Pres `Run Script (big white arrow)` and wait few moments, until Blender "unfreezes", than restart Blender
    7. Install add-on as any other by `Blender -> Preferences -> Add-ons -> Install from Disk (right top arrow)`, locate .zip file and install, than enable

## Planning

### Swarm area
- define and check area for swarm

![Swarm area](gifs/swarm_area.gif)

### Swarm initialize
- initialize drones

![Swarm initialize](gifs/swarm_init.gif)

### Swarm distance
- check minimal distance between drones

![Swarm distance](gifs/swarm_distance.gif)

### Swarm speed
- check maximal horizontal and vertical drones speed

![Swarm speed](gifs/swarm_speed.gif)

## Swarm plan
- plan transition of drones to object vertices/faces

### Selection
- select which drones to plan for from all drones, selected drones in scene, drones from group
- more about groups <https://github.com/FlyinDiamonds/blender_addon#groups>

### Check collisions
- keeps minimal distance between drones

![Swarm planner collisions](gifs/planner_collisions.gif)

### Same mesh
- plans on same object
- does not check distance between drones

![Swarm planner same mesh](gifs/planner_same_mesh.gif)

### Plan to target
- plan to vertices/faces of selected object

![Swarm planner target](gifs/planner_target.gif)


## Frames

### Frame duration
- calculates given number of frames starting with your current frame

![Frame duration](gifs/frame_duration.gif)

### Frame range
- calculates frames in selected range

![Frame range](gifs/frame_range.gif)

### Frame step
- number of frames to step over during calculation
- can be used to control intensity of blinking with selecting random drones or for better performance with selecting by mesh

![Frame step](gifs/frame_step.gif)

## Colors

### Color pallete
- color pallete for quick access to often used colors

![Color pallete](gifs/color_pallete.gif)

### Color picker
- color picker for ather colors

![Color picker](gifs/color_picker.gif)

### Color transition
- two pickers to calculate color transition on

![Color transition](gifs/color_transition.gif)

### Override background
- if checked colors on drones which are not selected are overriden with selected color

![Override background checked](gifs/override_background_checked.gif)
- if unchecked colors on drones which are not selected will stay as they are

![Override background unchecked](gifs/override_background_unchecked.gif)

## Select

### Select mouse
- drones selected in viewport are used

![Select mouse](gifs/select_mouse.gif)

### Select by mesh
- drones which are in picked mesh are used

![Select by mesh](gifs/select_by_mesh.gif)

### Select random
- select random drones on each step

![Select random](gifs/select_random.gif)

### Select group
- select items in active group
- more about groups <https://github.com/FlyinDiamonds/blender_addon#groups>

![Select group](gifs/select_group.gif)

### Invert selection
- drones which are not selected are used

![Select invert](gifs/select_invert.gif)

## Groups

### Create group
- create empty drone group
- group can be named

![Create group](gifs/create_group.gif)

### Remove group
- remove group

![Remove group](gifs/remove_group.gif)


### Move group
- move group by arrows fro better organization

![Move group](gifs/move_group.gif)

## Group items

### Add
- adds empty item with object picker
![Group item add](gifs/group_item_add.gif)

### Remove
- remove item from group
![Group item remove](gifs/group_item_remove.gif)

### Move
- move item in group
![Group item move](gifs/group_item_move.gif)

### Add selected
- adds items for selected drones
![Group item add](gifs/group_item_add_selected.gif)

### Remove selected
- remove selected drones from group
![Group item remove](gifs/group_item_remove_selected.gif)

### Select
- selects drones in group
![Group select](gifs/group_item_select.gif)

### Deselect
- deselects drones in group
![Group deselect](gifs/group_item_deselect.gif)


## Dev doc

### Reloading addon
- currently best for me is adding a symlink into Blender addons folder, that refers to `Addon-SwarmPlanner` folder in git repo, restart Blender if it is first time

- example `mklink /d "C:\Users\vk\AppData\Roaming\Blender Foundation\Blender\4.2\scripts\addons\Addon-SwarmPlanner" "C:\Work\FlyinDiamonds\blender_addon\Addon-SwarmPlanner"`

- thanks to symlink and `reload()` in the most inner `__init__.py` now works `Blender (left top corner icon) -> System -> Reload Scripts`

- You can add it to `Quick favorites` and then just pres `Q`.