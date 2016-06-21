import bpy, random, argparse, sys, time, pickle, os
from random import randint
import numpy as np
from math import pi
from tqdm import *

#Short hands for common calls
scene = bpy.context.scene
selected = bpy.context.selected_objects
mesh = bpy.ops.mesh
context = bpy.context
object = bpy.ops.object
ops = bpy.ops
selected_object = bpy.context.active_object
obj = scene.objects.active
layers_tfff=(True, False, False, False, False, False, False, False, False, False,
                False, False, False, False, False, False, False, False, False, False)

def makeMaterial(name, diffuse, specular, alpha):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = diffuse
    mat.diffuse_shader = 'LAMBERT'
    mat.diffuse_intensity = 1.0
    mat.specular_color = specular
    mat.specular_shader = 'COOKTORR'
    mat.specular_intensity = 0.5
    mat.alpha = alpha
    mat.ambient = 1
    return mat

#Color Paremeters
blue = makeMaterial('BlueSemi', (0,0,1), (0.5,0.5,0), 0.5)

def setMaterial(obj, mat):
    obj.data.materials.append(mat)
    return

def clearScene():
    # Clears the current scene
    for obj in scene.objects:
        scene.objects.unlink(obj)
        bpy.data.objects.remove(obj)
    return

def earthSetup():
    # TODO: Add Earth texture
    mesh.primitive_plane_add(radius = 5, view_align = False, enter_editmode = False, location = (0, 0, -1), layers = layers_tfff)
    setMaterial(context.object, blue)
    context.object.active_material.use_raytrace = False
    context.object.active_material.use_mist = False
    context.object.active_material.use_cast_shadows = False
    context.object.active_material.use_cast_buffer_shadows = False
    context.object.active_material.use_cast_approximate = False
    bpy.ops.texture.new()
    bpy.data.textures["Texture.001"].type = 'CLOUDS'

clearScene()
earthSetup()
