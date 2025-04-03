import harfang as hg

def create_physic_cube_ex(scene, size, mtx, model_ref, materials, rb_type=None, mass=0):
    rb_type = rb_type if rb_type is not None else hg.RBT_Dynamic
    mass = mass if mass is not None else 0

    node = hg.CreateObject(scene, mtx, model_ref, materials)
    node.SetName("Physic Cube")

    rb = scene.CreateRigidBody()
    rb.SetType(rb_type)
    node.SetRigidBody(rb)

    # Create custom cube collision
    col = scene.CreateCollision()
    col.SetType(hg.CT_Cube)
    col.SetSize(size)
    col.SetMass(mass)

    # Set cube as collision shape
    node.SetCollision(0, col)

    return node, rb

hg.AddAssetsFolder("assets_compiled")

# Main window
hg.InputInit()
hg.WindowSystemInit()

res_x, res_y = 1280, 720
win = hg.RenderInit("Physics Test", res_x, res_y, hg.RF_VSync | hg.RF_MSAA4X)

pipeline = hg.CreateForwardPipeline()
res = hg.PipelineResources()

# Physics debug
vtx_line_layout = hg.VertexLayoutPosFloatColorUInt8()
line_shader = hg.LoadProgramFromAssets("shaders/pos_rgb")

# Create material
pbr_shader = hg.LoadPipelineProgramRefFromAssets("core/shader/pbr.hps", res, hg.GetForwardPipelineInfo())
mat_grey = hg.CreateMaterial(
    pbr_shader,
    "uBaseOpacityColor",
    hg.Vec4(1, 1, 1),
    "uOcclusionRoughnessMetalnessColor",
    hg.Vec4(1, 0.5, 0.05),
)

# Create models
vtx_layout = hg.VertexLayoutPosFloatNormUInt8()

# Cube
cube_size = hg.Vec3(1, 1, 1)
cube_ref = res.AddModel("cube", hg.CreateCubeModel(vtx_layout, cube_size.x, cube_size.y, cube_size.z))

# Ground
ground_size = hg.Vec3(15, 0.05, 15)
ground_ref = res.AddModel("ground", hg.CreateCubeModel(vtx_layout, ground_size.x, ground_size.y, ground_size.z))

# Setup the scene
scene = hg.Scene()

cam_mat = hg.TransformationMat4(hg.Vec3(-2, 6, -8.5), hg.Vec3(hg.Deg(15), 0, 0))
cam = hg.CreateCamera(scene, cam_mat, 0.01, 1000, hg.Deg(35))
view_matrix = hg.InverseFast(cam_mat)
c = cam.GetCamera()
projection_matrix = hg.ComputePerspectiveProjectionMatrix(
    c.GetZNear(), c.GetZFar(), hg.FovToZoomFactor(c.GetFov()), hg.Vec2(res_x / res_y, 1)
)

scene.SetCurrentCamera(cam)

lgt = hg.CreateLinearLight(
    scene,
    hg.TransformationMat4(hg.Vec3(0, 0, 0), hg.Vec3(hg.Deg(30), hg.Deg(30), 0)),
    hg.Color(1, 1, 1),
    hg.Color(1, 1, 1),
    10,
    hg.LST_Map,
    0.00025,
    hg.Vec4(10, 15, 20, 25),
)

cube_node, cube_rb = create_physic_cube_ex(
    scene, cube_size, hg.TranslationMat4(hg.Vec3(-6, 5.0, 2.5)), cube_ref, [mat_grey], hg.RBT_Dynamic, 1.0
)

floor, rb_floor = create_physic_cube_ex(
    scene, ground_size, hg.TranslationMat4(hg.Vec3(-2, -0.005, 0)), ground_ref, [mat_grey], hg.RBT_Static, 0
)
rb_floor.SetRestitution(1)

# Scene physics
physics = hg.SceneBullet3Physics()
physics.SceneCreatePhysicsFromAssets(scene)

physics_step = hg.time_from_sec_f(1 / 60)
dt_frame_step = hg.time_from_sec_f(1 / 60)

clocks = hg.SceneClocks()

# Description
print(">>> Description:\n>>> Drop a cube and print out the amount of collisions.")

# Main loop
keyboard = hg.Keyboard()
physics.NodeStartTrackingCollisionEvents(cube_node)

while not keyboard.Down(hg.K_Escape) and hg.IsWindowOpen(win):
    keyboard.Update()

    physics.NodeWake(cube_node)

    view_id = 0
    hg.SceneUpdateSystems(scene, clocks, dt_frame_step, physics, physics_step, 3)
    view_id, pass_id = hg.SubmitSceneToPipeline(
        view_id, scene, hg.IntRect(0, 0, res_x, res_y), True, pipeline, res
    )

    paircontacts = physics.CollectCollisionEvents(scene)
    nodes_in_contact = hg.GetNodePairContacts(cube_node, floor, paircontacts)
    print(f"nodes_in_contact: {nodes_in_contact.size()}")

    # Debug physics display
    hg.SetViewClear(view_id, 0, 0, 1.0, 0)
    hg.SetViewRect(view_id, 0, 0, res_x, res_y)
    hg.SetViewTransform(view_id, view_matrix, projection_matrix)
    rs = hg.ComputeRenderState(hg.BM_Opaque, hg.DT_Disabled, hg.FC_Disabled)
    physics.RenderCollision(view_id, vtx_line_layout, line_shader, rs, 0)

    hg.Frame()
    hg.UpdateWindow(win)

scene.Clear()
scene.GarbageCollect()

hg.RenderShutdown()
hg.DestroyWindow(win)

hg.WindowSystemShutdown()
hg.InputShutdown()
