import harfang as hg

hg.AddAssetsFolder("assets_compiled")

# Initialisation de la fenêtre et des entrées
hg.InputInit()
hg.WindowSystemInit()

res_x, res_y = 1280, 720
win = hg.RenderInit("Physics Test", res_x, res_y, hg.RF_VSync | hg.RF_MSAA4X)

pipeline = hg.CreateForwardPipeline()
res = hg.PipelineResources()

# Débogage de la physique
vtx_line_layout = hg.VertexLayoutPosFloatColorUInt8()
line_shader = hg.LoadProgramFromAssets("shaders/pos_rgb")

# Création du matériau
test_shader = hg.LoadPipelineProgramRefFromAssets("core/shader/pbr.hps", res, hg.GetForwardPipelineInfo())
mat_grey = hg.CreateMaterial(test_shader, "uBaseOpacityColor", hg.Vec4(1, 1, 1), "uOcclusionRoughnessMetalnessColor", hg.Vec4(1, 0.5, 0.05))

# Création du sol
ground_size = hg.Vec3(4, 0.05, 4)
ground_ref = res.AddModel("ground", hg.CreateCubeModel(hg.VertexLayoutPosFloatNormUInt8(), ground_size.x, ground_size.y, ground_size.z))

# Configuration de la scène
scene = hg.Scene()

cam_mat = hg.TransformationMat4(hg.Vec3(0, 2.5, -10), hg.Vec3(hg.Deg(20), 0, 0))
cam = hg.CreateCamera(scene, cam_mat, 0.01, 1000)
view_matrix = hg.InverseFast(cam_mat)
c = cam.GetCamera()
projection_matrix = hg.ComputePerspectiveProjectionMatrix(c.GetZNear(), c.GetZFar(), hg.FovToZoomFactor(c.GetFov()), hg.Vec2(res_x / res_y, 1))
scene.SetCurrentCamera(cam)

lgt = hg.CreateLinearLight(scene, hg.TransformationMat4(hg.Vec3(0, 0, 0), hg.Vec3(hg.Deg(30), hg.Deg(30), 0)), hg.Color(1, 1, 1), hg.Color(1, 1, 1), 10, hg.LST_Map, 0.0001, hg.Vec4(2, 4, 10, 16))

cube_instance, _ = hg.CreateInstanceFromAssets(scene, hg.TranslationMat4(hg.Vec3(0, 0, 0)), "cube/cube.scn", res, hg.GetForwardPipelineInfo())

# Initialisation de la physique
physics = hg.SceneBullet3Physics()
physics.SceneCreatePhysicsFromAssets(scene)
physics_step = hg.time_from_sec_f(1 / 60)
dt_frame_step = hg.time_from_sec_f(1 / 60)

clocks = hg.SceneClocks()

print(">>> Description:\n>>> Set the position and rotation of an instantiated kinematic cube in the rendering loop. The cube shall move from left to right and rotate on its Y axis.")

keyboard = hg.Keyboard()
frame_count = 0

while not keyboard.Down(hg.K_Escape) and hg.IsWindowOpen(win):
    keyboard.Update()

    cube_instance.GetTransform().SetPos(hg.Vec3((frame_count % 200 - 100) / 100.0, 0.0, 0.0))
    cube_instance.GetTransform().SetRot(hg.Vec3(0.0, 3.14159 * frame_count / 360.0, 0.0))

    view_id = 0
    hg.SceneUpdateSystems(scene, clocks, dt_frame_step, physics, physics_step, 3)
    view_id, pass_id = hg.SubmitSceneToPipeline(view_id, scene, hg.IntRect(0, 0, res_x, res_y), True, pipeline, res)

    hg.SetViewClear(view_id, 0, 0, 1.0, 0)
    hg.SetViewRect(view_id, 0, 0, res_x, res_y)
    hg.SetViewTransform(view_id, view_matrix, projection_matrix)
    rs = hg.ComputeRenderState(hg.BM_Opaque, hg.DT_Disabled, hg.FC_Disabled)
    physics.RenderCollision(view_id, vtx_line_layout, line_shader, rs, 0)

    frame_count += 1

    hg.Frame()
    hg.UpdateWindow(win)

scene.Clear()
scene.GarbageCollect()

hg.RenderShutdown()
hg.DestroyWindow(win)

hg.WindowSystemShutdown()
hg.InputShutdown()

