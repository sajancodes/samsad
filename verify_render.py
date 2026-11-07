import bpy
import math
import os
import sys

def render_model_view(glb_path, output_png, camera_angle="front"):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    
    # Import model
    bpy.ops.import_scene.gltf(filepath=glb_path)
    
    # Add Camera
    cam_data = bpy.data.cameras.new("TestCam")
    cam_obj = bpy.data.objects.new("TestCam", cam_data)
    bpy.context.scene.collection.objects.link(cam_obj)
    bpy.context.scene.camera = cam_obj
    
    # Focus on head (~Z=1.52m)
    # Head local center is approximately (0, 0, 1.55)
    if camera_angle == "front":
        cam_obj.location = (0.0, -0.62, 1.52)
        cam_obj.rotation_euler = (math.radians(90), 0, 0)
    elif camera_angle == "side":
        # Right profile view (looking at character's right side)
        cam_obj.location = (-0.62, 0.0, 1.52)
        cam_obj.rotation_euler = (math.radians(90), 0, math.radians(-90))
    elif camera_angle == "back":
        # Direct back view
        cam_obj.location = (0.0, 0.62, 1.52)
        cam_obj.rotation_euler = (math.radians(90), 0, math.radians(180))
    elif camera_angle == "three_quarter":
        # 3/4 angle
        cam_obj.location = (-0.45, -0.45, 1.52)
        cam_obj.rotation_euler = (math.radians(90), 0, math.radians(-45))

    # Add Multi-Directional Studio Lighting
    # Front Light
    light_f = bpy.data.lights.new("FrontLight", type='POINT')
    light_f.energy = 55.0
    obj_f = bpy.data.objects.new("FrontLight", light_f)
    obj_f.location = (0.0, -0.65, 1.55)
    bpy.context.scene.collection.objects.link(obj_f)

    # Back Light (illuminates back of head and hair)
    light_b = bpy.data.lights.new("BackLight", type='POINT')
    light_b.energy = 55.0
    obj_b = bpy.data.objects.new("BackLight", light_b)
    obj_b.location = (0.0, 0.65, 1.55)
    bpy.context.scene.collection.objects.link(obj_b)

    # Side Light
    light_s = bpy.data.lights.new("SideLight", type='POINT')
    light_s.energy = 45.0
    obj_s = bpy.data.objects.new("SideLight", light_s)
    obj_s.location = (-0.65, 0.0, 1.55)
    bpy.context.scene.collection.objects.link(obj_s)

    # Ambient Fill Light
    light_fill = bpy.data.lights.new("FillLight", type='SUN')
    light_fill.energy = 1.5
    obj_fill = bpy.data.objects.new("FillLight", light_fill)
    obj_fill.location = (1.5, -1.0, 2.0)
    bpy.context.scene.collection.objects.link(obj_fill)
    
    bpy.context.scene.render.resolution_x = 512
    bpy.context.scene.render.resolution_y = 512
    bpy.context.scene.render.filepath = os.path.abspath(output_png)
    
    bpy.context.scene.render.engine = 'BLENDER_EEVEE'
    bpy.ops.render.render(write_still=True)
    print(f"Rendered view '{camera_angle}' to: {output_png}")

if __name__ == "__main__":
    args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    glb = args[0] if len(args) > 0 else "public/models/kpoli.glb"
    out = args[1] if len(args) > 1 else "verify_output.png"
    angle = args[2] if len(args) > 2 else "front"
    render_model_view(glb, out, angle)
