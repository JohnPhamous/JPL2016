import bpy

number = 5

def clearScene():
    #Clears the current scene
    for obj in bpy.context.scene.objects:
        bpy.context.scene.objects.unlink(obj)
        bpy.data.objects.remove(obj)
    return
    
def create():
    bpy.ops.object.camera_add()
    for x in range(number):
        bpy.ops.mesh.primitive_cube_add(location = (x - 5, 0, 0))
    return
    
def joinObjects():
    for ob in bpy.context.scene.objects:
        if ob.type == 'MESH':
            ob.select = True
            bpy.context.scene.objects.active = ob
        else:
            ob.select = False
        bpy.ops.object.join()
    
clearScene()
create()
joinObjects()