import harfang as hg
import random
import time

# Initialisation
hg.InputInit()
hg.WindowSystemInit()

res_x, res_y = 1280, 720
win = hg.RenderInit('LEFT CUBE = impulse via renderloop | RIGHT CUBE = impulse via callback', res_x, res_y, hg.RF_VSync | hg.RF_MSAA4X)

pipeline = hg.CreateForwardPipeline()
res = hg.PipelineResources()

# Debug physique
vtx_line_layout = hg.VertexLayoutPosFloatColorUInt8()
line_shader = hg.LoadProgramFromFile("assets_compiled/shaders/pos_rgb")

# Création des modèles
vtx_layout = hg.VertexLayoutPosFloatNormUInt8()

cube_mdl = hg.CreateCubeModel(vtx_layout, 1, 1, 1)
cube_ref = res.AddModel('cube', cube_mdl)

ground_mdl = hg.CreateCubeModel(vtx_layout, 50, 0.01, 50)
ground_ref = res.AddModel('ground', ground_mdl)

# Création du matériau
prg_ref = hg.LoadPipelineProgramRefFromFile('assets_compiled/core/shader/pbr.hps', res, hg.GetForwardPipelineInfo())
mat = hg.CreateMaterial(prg_ref, 'uBaseOpacityColor', hg.Vec4(1, 1, 1), 'uOcclusionRoughnessMetalnessColor', hg.Vec4(1, 0.5, 0.05))

# Configuration de la scène
scene = hg.Scene()

cam_mat = hg.TransformationMat4(hg.Vec3(0, 4.0, -8), hg.Vec3(hg.Deg(10), 0, 0))
cam = hg.CreateCamera(scene, cam_mat, 0.01, 1000)
scene.SetCurrentCamera(cam)
view_matrix = hg.InverseFast(cam_mat)
c = cam.GetCamera()
projection_matrix = hg.ComputePerspectiveProjectionMatrix(c.GetZNear(), c.GetZFar(), hg.FovToZoomFactor(c.GetFov()), hg.Vec2(res_x / res_y, 1))

lgt = hg.CreateLinearLight(scene, hg.TransformationMat4(hg.Vec3(0, 0, 0), hg.Vec3(hg.Deg(30), hg.Deg(59), 0)), hg.Color(1, 1, 1), hg.Color(1, 1, 1), 10, hg.LST_Map, 0.002, hg.Vec4(2, 4, 10, 16))

cube_node_render_pos = hg.Vec3(-1, 2.0, 0)
cube_node_callback_pos = hg.Vec3(1, 2.0, 0)

cube_node_render = hg.CreatePhysicCube(scene, hg.Vec3(1, 1, 1), hg.TranslationMat4(cube_node_render_pos), cube_ref, [mat], 2)
cube_node_callback = hg.CreatePhysicCube(scene, hg.Vec3(1, 1, 1), hg.TranslationMat4(cube_node_callback_pos), cube_ref, [mat], 2)
ground_node = hg.CreatePhysicCube(scene, hg.Vec3(100, 0.02, 100), hg.TranslationMat4(hg.Vec3(0, -0.005, 0)), ground_ref, [mat], 0)

clocks = hg.SceneClocks()

# Physique de la scène
physics = hg.SceneBullet3Physics()
physics.SceneCreatePhysicsFromAssets(scene)
physics_step = hg.time_from_sec_f(1 / 60)

# Boucle principale
keyboard = hg.Keyboard()

def random_float(lower, greater):
    return lower + random.random() * (greater - lower)

def draw_line(pos_a, pos_b, line_color, vid, vtx_line_layout, line_shader):
    vtx = hg.Vertices(vtx_line_layout, 2)
    vtx.Begin(0).SetPos(pos_a).SetColor0(line_color).End()
    vtx.Begin(1).SetPos(pos_b).SetColor0(line_color).End()
    hg.DrawLines(vid, vtx, line_shader)

def impulse(ph, node, dt, target_pos):
    cur_velocity = ph.NodeGetLinearVelocity(node)
    vel_to_target = target_pos - hg.GetT(node.GetTransform().GetWorld())
    vel_to_target = vel_to_target - cur_velocity
    ph.NodeAddImpulse(node, vel_to_target)
    ph.NodeWake(node)

def foo(ph, dt):
    impulse(ph, cube_node_callback, dt, cube_node_callback_pos)

physics.SetPreTickCallback(foo)

_ofs = 0.75
pos_timer = hg.time_from_sec_f(0.0)

while not keyboard.Down(hg.K_Escape) and hg.IsWindowOpen(win):
    keyboard.Update()

    dt = hg.TickClock()
    view_id = 0
    lines = []

    pos_timer += dt

    if pos_timer > hg.time_from_sec_f(5.0):
        pos_timer = hg.time_from_sec_f(0.0)
        cube_node_render_pos.y = random_float(1.0, 5.0)
        cube_node_callback_pos.y = cube_node_render_pos.y

    lines.append([cube_node_render_pos + hg.Vec3(_ofs, 0, 0), cube_node_render_pos - hg.Vec3(_ofs, 0, 0), hg.Color.Red])
    lines.append([cube_node_render_pos + hg.Vec3(0, _ofs, 0), cube_node_render_pos - hg.Vec3(0, _ofs, 0), hg.Color.Red])
    lines.append([cube_node_render_pos + hg.Vec3(0, 0, _ofs), cube_node_render_pos - hg.Vec3(0, 0, _ofs), hg.Color.Red])

    lines.append([cube_node_callback_pos + hg.Vec3(_ofs, 0, 0), cube_node_callback_pos - hg.Vec3(_ofs, 0, 0), hg.Color.Red])
    lines.append([cube_node_callback_pos + hg.Vec3(0, _ofs, 0), cube_node_callback_pos - hg.Vec3(0, _ofs, 0), hg.Color.Red])
    lines.append([cube_node_callback_pos + hg.Vec3(0, 0, _ofs), cube_node_callback_pos - hg.Vec3(0, 0, _ofs), hg.Color.Red])

    impulse(physics, cube_node_render, dt, cube_node_render_pos)

    hg.SceneUpdateSystems(scene, clocks, dt, physics, physics_step, 8)
    view_id, pass_id = hg.SubmitSceneToPipeline(view_id, scene, hg.IntRect(0, 0, res_x, res_y), True, pipeline, res)

    # Dessin des lignes de débogage
    opaque_view_id = hg.GetSceneForwardPipelinePassViewId(pass_id, hg.SFPP_Opaque)
    for line in lines:
        draw_line(line[0], line[1], line[2], opaque_view_id, vtx_line_layout, line_shader)

    # Affichage de la physique de débogage
    hg.SetViewClear(view_id, 0, 0, 1.0, 0)
    hg.SetViewRect(view_id, 0, 0, res_x, res_y)
    hg.SetViewTransform(view_id, view_matrix, projection_matrix)
    rs = hg.ComputeRenderState(hg.BM_Opaque, hg.DT_Disabled, hg.FC_Disabled)
    physics.RenderCollision(view_id, vtx_line_layout, line_shader, rs, 0)

    hg.Frame()
    hg.UpdateWindow(win)

    time.sleep(random_float(0.0, 0.05))

hg.RenderShutdown()
hg.DestroyWindow(win)

hg.WindowSystemShutdown()
hg.InputShutdown()
