import harfang as hg

hg.AddAssetsFolder("assets_compiled")

# Initialisation des entrées et de la fenêtre
hg.InputInit()
hg.WindowSystemInit()

res_x, res_y = 1280, 720
win = hg.RenderInit("Physics Test", res_x, res_y, hg.RF_VSync | hg.RF_MSAA4X)

pipeline = hg.CreateForwardPipeline()
res = hg.PipelineResources()

# Débogage physique
vtx_line_layout = hg.VertexLayoutPosFloatColorUInt8()
line_shader = hg.LoadProgramFromAssets("shaders/pos_rgb")

# Configuration de la scène
scene = hg.Scene()

cam_mat = hg.TransformationMat4(hg.Vec3(0, 1, -3), hg.Vec3(hg.Deg(20), 0, 0))
cam = hg.CreateCamera(scene, cam_mat, 0.01, 1000)
view_matrix = hg.InverseFast(cam_mat)
c = cam.GetCamera()
projection_matrix = hg.ComputePerspectiveProjectionMatrix(
    c.GetZNear(), c.GetZFar(), hg.FovToZoomFactor(c.GetFov()), hg.Vec2(res_x / res_y, 1)
)

scene.SetCurrentCamera(cam)

lgt = hg.CreateLinearLight(
    scene, hg.TransformationMat4(hg.Vec3(0, 0, 0), hg.Vec3(hg.Deg(30), hg.Deg(30), 0)),
    hg.Color(1, 1, 1), hg.Color(1, 1, 1), 10, hg.LST_Map, 0.0001, hg.Vec4(2, 4, 10, 16)
)

octogone_instance, _ = hg.CreateInstanceFromAssets(
    scene, hg.TranslationMat4(hg.Vec3(0, 0, 0)), "octogone/octogone.scn", res, hg.GetForwardPipelineInfo()
)

# Physique de la scène
physics = hg.SceneBullet3Physics()
physics.SceneCreatePhysicsFromAssets(scene)
physics_step = hg.time_from_sec_f(1 / 60)
dt_frame_step = hg.time_from_sec_f(1 / 60)

clocks = hg.SceneClocks()

# Description
hg.SetLogLevel(hg.LL_Normal)
print(
    ">>> Description:\n>>> Create a mesh collider with octogon surface from .physics_bullet file "
    "from the plane geometry and test the collisions with raycasts."
)

# Initialisation de la physique du maillage
octogone_node = scene.GetNode("Cercle")
mesh_col = scene.CreateCollision()
mesh_col.SetType(hg.CT_Mesh)
mesh_col.SetCollisionResource("octogone/Cercle_38.physics_bullet")
mesh_col.SetMass(0)
octogone_node.SetCollision(0, mesh_col)

# Création d'un corps rigide
rb = scene.CreateRigidBody()
rb.SetType(hg.RBT_Static)
rb.SetFriction(0.498)
rb.SetRollingFriction(0)
octogone_node.SetRigidBody(rb)
physics.NodeCreatePhysicsFromAssets(octogone_node)

# Boucle principale
keyboard = hg.Keyboard()
mouse = hg.Mouse()
cam_pos = cam.GetTransform().GetPos()
cam_rot = cam.GetTransform().GetRot()
vtx = hg.Vertices(vtx_line_layout, 2)
vid_scene_opaque = 0
frame_count = 0

while not keyboard.Down(hg.K_Escape) and hg.IsWindowOpen(win):
    keyboard.Update()
    mouse.Update()

    dt = hg.TickClock()
    s = 20 if keyboard.Down(hg.K_LShift) else 8
    hg.FpsController(keyboard, mouse, cam_pos, cam_rot, s, dt)

    cam.GetTransform().SetPos(cam_pos)
    cam.GetTransform().SetRot(cam_rot)

    for i in range(-20, 21):
        for o in range(-20, 21):
            start_pos = hg.Vec3(i * 0.05, 0.1, o * 0.05)
            end_pos = hg.Vec3(i * 0.05, -0.1, o * 0.05)
            raycast_out = physics.RaycastFirstHit(scene, start_pos, end_pos)

            vtx.Clear()
            if raycast_out.node.IsValid():
                vtx.Begin(0).SetPos(start_pos).SetColor0(hg.Color.Yellow).End()
                vtx.Begin(1).SetPos(raycast_out.P).SetColor0(hg.Color.Yellow).End()
            else:
                vtx.Begin(0).SetPos(start_pos).SetColor0(hg.Color.Red).End()
                vtx.Begin(1).SetPos(end_pos).SetColor0(hg.Color.Red).End()

            hg.DrawLines(vid_scene_opaque, vtx, line_shader)

    view_id = 0
    hg.SceneUpdateSystems(scene, clocks, dt_frame_step, physics, physics_step, 3)
    view_id, pass_id = hg.SubmitSceneToPipeline(view_id, scene, hg.IntRect(0, 0, res_x, res_y), True, pipeline, res)
    vid_scene_opaque = hg.GetSceneForwardPipelinePassViewId(pass_id, hg.SFPP_Opaque)

    # Affichage du débogage physique
    hg.SetViewClear(view_id, 0, 0, 1.0, 0)
    hg.SetViewRect(view_id, 0, 0, res_x, res_y)
    cam_mat = cam.GetTransform().GetWorld()
    view_matrix = hg.InverseFast(cam_mat)
    c = cam.GetCamera()
    projection_matrix = hg.ComputePerspectiveProjectionMatrix(
        c.GetZNear(), c.GetZFar(), hg.FovToZoomFactor(c.GetFov()), hg.Vec2(res_x / res_y, 1)
    )
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
