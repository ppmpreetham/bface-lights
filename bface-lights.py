bl_info = {
    "name": "bFace lights",
    "blender": (3, 5, 0),
    "category": "Object",
    "description": "Adds lights to each selected face of the active mesh object with customizable options.",
    "author": "Preetham",
}

import bpy
import bmesh

class LIGHT_PT_add_to_faces_panel(bpy.types.Panel):
    bl_label = "Add Lights to Faces"
    bl_idname = "LIGHT_PT_add_to_faces"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Tool'
    
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        layout.prop(scene, "light_type")
        layout.prop(scene, "light_color")
        layout.prop(scene, "light_strength")
        if scene.light_type == 'SPOT':
            layout.prop(scene, "spot_size")
            layout.prop(scene, "spot_blend")
        if scene.light_type == 'AREA':
            layout.prop(scene, "area_shape")
            if scene.area_shape in {'RECTANGLE', 'ELLIPSE'}:
                layout.prop(scene, "area_size_x")
                layout.prop(scene, "area_size_y")
            else:
                layout.prop(scene, "area_size")
            layout.prop(scene, "area_spread")
        layout.operator("object.add_lights_to_faces", text="Add Lights to Faces")

class LIGHT_OT_add_to_faces(bpy.types.Operator):
    bl_idname = "object.add_lights_to_faces"
    bl_label = "Add Lights to Selected Faces"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        light_type = context.scene.light_type
        color = context.scene.light_color
        strength = context.scene.light_strength
        spot_size = context.scene.spot_size
        spot_blend = context.scene.spot_blend
        area_shape = context.scene.area_shape
        area_size_x = context.scene.area_size_x
        area_size_y = context.scene.area_size_y
        area_size = context.scene.area_size
        area_spread = context.scene.area_spread

        if context.active_object and context.active_object.type == 'MESH':
            obj = context.active_object
            bpy.ops.object.mode_set(mode='OBJECT')
            mesh = obj.data
            bm = bmesh.new()
            bm.from_mesh(mesh)
            bm.faces.ensure_lookup_table()
            collection_name = "Face Lights"
            if collection_name in bpy.data.collections:
                light_collection = bpy.data.collections[collection_name]
            else:
                light_collection = bpy.data.collections.new(collection_name)
                context.scene.collection.children.link(light_collection)
            for face in bm.faces:
                if face.select:
                    face_center = obj.matrix_world @ face.calc_center_median()
                    bpy.ops.object.light_add(type=light_type, location=face_center)
                    light = context.object
                    if light is not None and light.type == 'LIGHT':
                        light.data.color = color
                        light.data.energy = strength
                        if light_type == 'SPOT':
                            light.data.spot_size = spot_size
                            light.data.spot_blend = spot_blend
                        if light_type == 'AREA':
                            light.data.shape = area_shape
                            if area_shape in {'RECTANGLE', 'ELLIPSE'}:
                                light.data.size = area_size_x
                                light.data.size_y = area_size_y
                            else:
                                light.data.size = area_size
                            light.data.spread = area_spread
                        normal = obj.matrix_world.to_3x3() @ face.normal
                        light.location += normal * 0.2
                        if light.name not in light_collection.objects:
                            light_collection.objects.link(light)
                        if light.name in context.scene.collection.objects:
                            context.scene.collection.objects.unlink(light)
            bm.free()
            context.view_layer.update()
            return {'FINISHED'}
        else:
            self.report({'WARNING'}, "No mesh object selected.")
            return {'CANCELLED'}

def register():
    bpy.utils.register_class(LIGHT_PT_add_to_faces_panel)
    bpy.utils.register_class(LIGHT_OT_add_to_faces)
    bpy.types.Scene.light_type = bpy.props.EnumProperty(
        name="Light Type",
        items=[
            ('POINT', "Point", "Add a Point Light"),
            ('SPOT', "Spot", "Add a Spot Light"),
            ('SUN', "Sun", "Add a Sun Light"),
            ('AREA', "Area", "Add an Area Light"),
        ],
        default='SPOT'
    )
    bpy.types.Scene.light_color = bpy.props.FloatVectorProperty(
        name="Color",
        subtype='COLOR',
        default=(1.0, 1.0, 1.0),
        min=0.0, max=1.0
    )
    bpy.types.Scene.light_strength = bpy.props.FloatProperty(
        name="Strength",
        default=1000.0,
        min=0.0
    )
    bpy.types.Scene.spot_size = bpy.props.FloatProperty(
        name="Spot Size",
        default=1.0,
        min=0.0,
        max=6.28
    )
    bpy.types.Scene.spot_blend = bpy.props.FloatProperty(
        name="Spot Blend",
        default=0.1,
        min=0.0,
        max=1.0
    )
    bpy.types.Scene.area_shape = bpy.props.EnumProperty(
        name="Area Shape",
        items=[
            ('SQUARE', "Square", "Square shaped Area Light"),
            ('RECTANGLE', "Rectangle", "Rectangle shaped Area Light"),
            ('DISK', "Disk", "Disk shaped Area Light"),
            ('ELLIPSE', "Ellipse", "Ellipse shaped Area Light"),
        ],
        default='SQUARE'
    )
    bpy.types.Scene.area_size_x = bpy.props.FloatProperty(
        name="Area Size X",
        default=1.0,
        min=0.0
    )
    bpy.types.Scene.area_size_y = bpy.props.FloatProperty(
        name="Area Size Y",
        default=1.0,
        min=0.0
    )
    bpy.types.Scene.area_size = bpy.props.FloatProperty(
        name="Size",
        default=1.0,
        min=0.0
    )
    bpy.types.Scene.area_spread = bpy.props.FloatProperty(
        name="Area Spread",
        default=1.0,
        min=0.0,
        max=3.14
    )

def unregister():
    bpy.utils.unregister_class(LIGHT_PT_add_to_faces_panel)
    bpy.utils.unregister_class(LIGHT_OT_add_to_faces)
    del bpy.types.Scene.light_type
    del bpy.types.Scene.light_color
    del bpy.types.Scene.light_strength
    del bpy.types.Scene.spot_size
    del bpy.types.Scene.spot_blend
    del bpy.types.Scene.area_shape
    del bpy.types.Scene.area_size_x
    del bpy.types.Scene.area_size_y
    del bpy.types.Scene.area_size
    del bpy.types.Scene.area_spread

if __name__ == "__main__":
    register()