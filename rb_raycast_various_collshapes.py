import harfang as hg

def CreatePhysicCapsuleEx(scene, radius, height, mtx, model_ref, materials, rb_type=hg.RBT_Dynamic, mass=0):
    node = hg.CreateObject(scene, mtx, model_ref, materials)
    node.SetName("Physic Capsule")

    rb = scene.CreateRigidBody()
    rb.SetType(rb_type)
    node.SetRigidBody(rb)

    col = scene.CreateCollision()
    col.SetType(hg.CT_Capsule)
    col.SetRadius(radius)
    col.SetHeight(height)
    col.SetMass(mass)

    node.SetCollision(0, col)
    return node, rb

def CreatePhysicConeEx(scene, radius, height, mtx, model_ref, materials, rb_type=hg.RBT_Dynamic, mass=0):
    node = hg.CreateObject(scene, mtx, model_ref, materials)
    node.SetName("Physic Cone")

    rb = scene.CreateRigidBody()
    rb.SetType(rb_type)
    node.SetRigidBody(rb)

    col = scene.CreateCollision()
    col.SetType(hg.CT_Cone)
    col.SetRadius(radius)
    col.SetHeight(height)
    col.SetMass(mass)

    node.SetCollision(0, col)
    return node, rb

def CreatePhysicCylinderEx(scene, radius, height, mtx, model_ref, materials, rb_type=hg.RBT_Dynamic, mass=0):
    node = hg.CreateObject(scene, mtx, model_ref, materials)
    node.SetName("Physic Cylinder")

    rb = scene.CreateRigidBody()
    rb.SetType(rb_type)
    node.SetRigidBody(rb)

    col = scene.CreateCollision()
    col.SetType(hg.CT_Cylinder)
    col.SetRadius(radius)
    col.SetHeight(height)
    col.SetMass(mass)

    node.SetCollision(0, col)
    return node, rb

hg.AddAssetsFolder('assets_compiled')

hg.InputInit()
hg.WindowSystemInit()

res_x, res_y = 1280, 720
win = hg.RenderInit('Physics Test', res_x, res_y, hg.RF_VSync | hg.RF_MSAA4X)

pipeline = hg.CreateForwardPipeline()
res = hg.PipelineResources()

vtx_line_layout = hg.VertexLayoutPosFloatColorUInt8()
line_shader = hg.LoadProgramFromAssets("shaders/pos_rgb")

pbr_shader = hg.LoadPipelineProgramRefFromAssets('core/shader/pbr.hps', res, hg.GetForwardPipelineInfo())
mat_grey = hg.CreateMaterial(pbr_shader, 'uBaseOpacityColor', hg.Vec4(1, 1, 1), 'uOcclusionRoughnessMetalnessColor', hg.Vec4(1, 0.5, 0.05))

vtx_layout = hg.VertexLayoutPosFloatNormUInt8()

cube_size = hg.Vec3(1, 1, 1)
cube_ref = res.AddModel('cube', hg.CreateCubeModel(vtx_layout, cube_size.x, cube_size.y, cube_size.z))

sphere_radius = 0.5
sphere_ref = res.AddModel('sphere', hg.CreateSphereModel(vtx_layout, sphere_radius, 8, 8))

capsule_radius = 0.5
capsule_height = 1
capsule_ref = res.AddModel('capsule', hg.CreateCapsuleModel(vtx_layout, capsule_radius, capsule_height, 8, 8))

cone_radius = 0.5
cone_height = 1
cone_ref = res.AddModel('cone', hg.CreateConeModel(vtx_layout, cone_radius, cone_height, 16))

cylinder_radius = 0.5
cylinder_height = 1
cylinder_ref = res.AddModel("cylinder", hg.CreateCylinderModel(vtx_layout, cylinder_radius, cylinder_height, 16))

ground_size = hg.Vec3(15, 0.05, 15)
ground_ref = res.AddModel("ground", hg.CreateCubeModel(vtx_layout, ground_size.x, ground_size.y, ground_size.z))

scene = hg.Scene()

cam_mat = hg.TransformationMat4(hg.Vec3(-2, 6, -8.5), hg.Vec3(hg.Deg(25), 0, 0))
cam = hg.CreateCamera(scene, cam_mat, 0.01, 1000, hg.Deg(30))
view_matrix = hg.InverseFast(cam_mat)
c = cam.GetCamera()
projection_matrix = hg.ComputePerspectiveProjectionMatrix(
    c.GetZNear(),
    c.GetZFar(),
    hg.FovToZoomFactor(c.GetFov()),
    hg.Vec2(res_x / res_y, 1)
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
    hg.Vec4(2, 4, 10, 16)
)

sphere_node = hg.CreatePhysicSphere(scene, sphere_radius, hg.TranslationMat4(hg.Vec3(2, 1, 2.5)), sphere_ref, [mat_grey], 0)
cube_node = hg.CreatePhysicCube(scene, cube_size, hg.TranslationMat4(hg.Vec3(0, 1, 2.5)), cube_ref, [mat_grey], 0)
capsule_node, capsule_rb = CreatePhysicCapsuleEx(scene, capsule_radius, capsule_height, hg.TranslationMat4(hg.Vec3(-2, 1, 2.5)), capsule_ref, [mat_grey], hg.RBT_Dynamic, 0)
cone_node, cone_rb = CreatePhysicConeEx(scene, cone_radius, cone_height, hg.TranslationMat4(hg.Vec3(-4, 1, 2.5)), cone_ref, [mat_grey], hg.RBT_Dynamic, 0)
cylinder_node, cylinder_rb = CreatePhysicCylinderEx(scene, cylinder_radius, cylinder_height, hg.TranslationMat4(hg.Vec3(-6, 1, 2.5)), cylinder_ref, [mat_grey], hg.RBT_Dynamic, 0)

physics = hg.SceneBullet3Physics()
physics.SceneCreatePhysicsFromAssets(scene)
physics_step = hg.time_from_sec_f(1 / 60)
dt_frame_step = hg.time_from_sec_f(1 / 60)

clocks = hg.SceneClocks()

hg.SetLogLevel(hg.LL_Normal)
print(">>> Description:\n>>> Shoot N raycast toward a collection of Node + Rigid bodies + Collision shapes of various types.\n>>> Red if the raycast hit nothing.\n>>> Green if the raycast hit a node.")

keyboard = hg.Keyboard()
mouse = hg.Mouse()

vtx = hg.Vertices(vtx_line_layout, 2)
vid_scene_opaque = 0

while not keyboard.Down(hg.K_Escape) and hg.IsWindowOpen(win):
    keyboard.Update()
    mouse.Update()
    
    for i in range(1, 61):
        start_pos = hg.Vec3(-8 + 0.2 * i, 0.75, -5)
        end_pos = hg.Vec3(-8 + 0.2 * i, 0.75, 10)
        raycast_out = physics.RaycastFirstHit(scene, start_pos, end_pos)

        vtx.Clear()
        if raycast_out.node.IsValid():
            vtx.Begin(0).SetPos(start_pos).SetColor0(hg.Color.Green).End()
            vtx.Begin(1).SetPos(raycast_out.P).SetColor0(hg.Color.Green).End()
        else:
            vtx.Begin(0).SetPos(start_pos).SetColor0(hg.Color.Red).End()
            vtx.Begin(1).SetPos(end_pos).SetColor0(hg.Color.Red).End()
            hg.DrawLines(vid_scene_opaque, vtx, line_shader)

    view_id = 0
    hg.SceneUpdateSystems(scene, clocks, dt_frame_step, physics, physics_step, 3)
    view_id, pass_id = hg.SubmitSceneToPipeline(view_id, scene, hg.IntRect(0, 0, res_x, res_y), True, pipeline, res)
    vid_scene_opaque = hg.GetSceneForwardPipelinePassViewId(pass_id, hg.SFPP_Opaque)
    
    hg.SetViewClear(view_id, 0, 0, 1.0, 0)
    hg.SetViewRect(view_id, 0, 0, res_x, res_y)
    hg.SetViewTransform(view_id, hg.InverseFast(cam.GetTransform().GetWorld()), hg.ComputePerspectiveProjectionMatrix(c.GetZNear(), c.GetZFar(), hg.FovToZoomFactor(c.GetFov()), hg.Vec2(res_x / res_y, 1)))
    rs = hg.ComputeRenderState(hg.BM_Opaque, hg.DT_Disabled, hg.FC_Disabled)
    physics.RenderCollision(view_id, vtx_line_layout, line_shader, rs, 0)
    
    hg.Frame()
    hg.UpdateWindow(win)
    
scene.Clear()
scene.GarbageCollect()

hg.RenderShutdown()
hg.DestoryWindow(win)

hg.WindowSystemShutdown()
hg.InputShutdown()