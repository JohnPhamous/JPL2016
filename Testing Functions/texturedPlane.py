import bpy

bpy.ops.mesh.primitive_plane_add(radius=1, view_align=False, enter_editmode=False, location=(0, 0, 0), layers=(True, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False))
mat = bpy.data.materials.new(name="Ocean10")
mat.diffuse_color = (0, 0.461457, 0.8)


tex = bpy.data.textures.new('BumpTex', type = 'CLOUDS')
#tex.color = (0, 0.2333, 0 ,1)


bpy.context.object.data.materials.append(mat)
