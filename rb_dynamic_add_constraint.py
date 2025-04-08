import harfang as hg

def  create_physic_cube_ex(scene, size, mtx, model_ref, materials, rb_type=hg.RBT_Dynamic, mass=0):
    node = hg.CreateObject(scene, mtx, model_ref, materials)
    node.SetName("Physic Cube")
    rb = scene.CreateRigidBody()
    rb.SetType(rb_type)
    node.SetRigidBody(rb)
    col = scene.CreateCollision()
    col.SetType(hg.CT_Cube)
    col.SetSize(size)
    col.SetMass(mass)
    node.SetCollision(0, col)
    return node, rb

def get_nodes(scene, paths):
    nodes = {}
    for path in paths:
        key = path.split("/")[-1]
        nodes[key] = scene.GetNodeEx(path)
    return nodes


def create_anchors(nodes, joint_paths):
    anchors = {}
    for joint_path in joint_paths:
        anchor_key = f"{joint_path}_anchor" 
        anchors[anchor_key] = hg.TransformationMat4(nodes[joint_path].GetTransform().GetPos(), nodes[joint_path].GetTransform().GetRot())
    return anchors

node_paths = [
    "chest",
    "chest/chest_bone",
    "chest/chest_joint_to_head",
    "chest/chest_joint_to_right_arm_2",
    "chest/chest_joint_to_right_arm_3",
    "chest/chest_joint_to_left_arm_2",
    "chest/chest_joint_to_left_arm_3",
    "chest/chest_joint_to_right_leg",
    "chest/chest_joint_to_right_leg_2",
    "chest/chest_joint_to_right_leg_3",
    "chest/chest_joint_to_right_leg_4",
    "chest/chest_joint_to_left_leg",
    "chest/chest_joint_to_left_leg_2",
    "chest/chest_joint_to_left_leg_3",
    "chest/chest_joint_to_left_leg_4",
    "left_leg/left_leg_joint_to_chest",
    "left_leg/left_leg_joint_to_chest_2",
    "left_leg/left_leg_joint_to_chest_3",
    "left_leg/left_leg_joint_to_chest_4",
    "right_leg/right_leg_joint_to_chest",
    "right_leg/right_leg_joint_to_chest_2",
    "right_leg/right_leg_joint_to_chest_3",
    "right_leg/right_leg_joint_to_chest_4",
    "right_arm/right_arm_joint_to_chest",
    "right_arm/right_arm_joint_to_chest_2",
    "left_arm/left_arm_joint_to_chest",
    "left_arm/left_arm_joint_to_chest_2",
    "head/head_joint_to_chest",
    "left_leg/left_leg_joint_to_ground",
    "left_leg/left_leg_joint_to_ground_2",
    "left_leg/left_leg_joint_to_ground_3",
    "right_leg/right_leg_joint_to_ground",
    "right_leg/right_leg_joint_to_ground_2",
    "right_leg/right_leg_joint_to_ground_3",
    "ground/ground_joint_to_left_leg",
    "ground/ground_joint_to_left_leg_2",
    "ground/ground_joint_to_left_leg_3",
    "ground/ground_joint_to_right_leg",
    "ground/ground_joint_to_right_leg_2",
    "ground/ground_joint_to_right_leg_3",
    "right_arm",
    "right_arm/right_arm_bone",
    "left_arm",
    "left_arm/left_arm_bone",
    "right_leg",
    "right_leg/right_leg_bone",
    "left_leg",
    "left_leg/left_leg_bone",
    "head",
    "head/head_bone",
    "ground"
]

joint_paths = [
    "right_arm_joint_to_chest",
    "right_arm_joint_to_chest_2",
    "left_arm_joint_to_chest",
    "left_arm_joint_to_chest_2",
    "right_leg_joint_to_chest",
    "right_leg_joint_to_chest_2",
    "right_leg_joint_to_chest_3",
    "right_leg_joint_to_chest_4",
    "left_leg_joint_to_chest",
    "left_leg_joint_to_chest_2",
    "left_leg_joint_to_chest_3",
    "left_leg_joint_to_chest_4",
    "head_joint_to_chest",
    "chest_joint_to_head",
    "chest_joint_to_right_arm_2",
    "chest_joint_to_right_arm_3",
    "chest_joint_to_left_arm_2",
    "chest_joint_to_left_arm_3",
    "chest_joint_to_right_leg",
    "chest_joint_to_right_leg_2",
    "chest_joint_to_right_leg_3",
    "chest_joint_to_right_leg_4",
    "chest_joint_to_left_leg",
    "chest_joint_to_left_leg_2",
    "chest_joint_to_left_leg_3",
    "chest_joint_to_left_leg_4",
    "left_leg_joint_to_ground",
    "left_leg_joint_to_ground_2",
    "left_leg_joint_to_ground_3",
    "right_leg_joint_to_ground",
    "right_leg_joint_to_ground_2",
    "right_leg_joint_to_ground_3",
    "ground_joint_to_left_leg",
    "ground_joint_to_left_leg_2",
    "ground_joint_to_left_leg_3",
    "ground_joint_to_right_leg",
    "ground_joint_to_right_leg_2",
    "ground_joint_to_right_leg_3"
]

hg.AddAssetsFolder('assets_compiled')

hg.InputInit()
hg.WindowSystemInit()

res_x, res_y = 1280, 720
win = hg.RenderInit('Physics Test', res_x, res_y, hg.RF_VSync | hg.RF_MSAA4X)

pipeline = hg.CreateForwardPipeline()
res = hg.PipelineResources()

line_shader = hg.LoadProgramFromAssets("shaders/pos_rgb")

pbr_shader = hg.LoadPipelineProgramRefFromAssets('core/shader/pbr.hps', res, hg.GetForwardPipelineInfo())
mat_grey = hg.CreateMaterial(pbr_shader, 'uBaseOpacityColor', hg.Vec4(1, 1, 1), 'uOcclusionRoughnessMetalnessColor',
                             hg.Vec4(1, 0.5, 0.05))

scene = hg.Scene()
hg.LoadSceneFromAssets("cube/cube_remastered.scn", scene, res, hg.GetForwardPipelineInfo())

cam_mat = hg.TransformationMat4(hg.Vec3(0, 7, -15), hg.Vec3(hg.Deg(10), 0, 0))
cam = hg.CreateCamera(scene, cam_mat, 0.01, 1000)
c = cam.GetCamera()
projection_matrix = hg.ComputePerspectiveProjectionMatrix(c.GetZNear(), c.GetZFar(), hg.FovToZoomFactor(c.GetFov()),
                                                          hg.Vec2(res_x / res_y, 1))

scene.SetCurrentCamera(cam)

physics = hg.SceneBullet3Physics()
physics.SceneCreatePhysicsFromAssets(scene)
physics_step = hg.time_from_sec_f(1 / 60)
dt_frame_step = hg.time_from_sec_f(1 / 60)

clocks = hg.SceneClocks()

nodes = get_nodes(scene, node_paths)
anchors = create_anchors(nodes, joint_paths)

print(nodes['chest_joint_to_right_arm_2'].HasRigidBody())


physics.Add6DofConstraint(nodes['chest'], nodes['right_arm'], anchors['chest_joint_to_right_arm_2_anchor'], anchors['right_arm_joint_to_chest_anchor'])
physics.Add6DofConstraint(nodes['chest'], nodes['right_arm'], anchors['chest_joint_to_right_arm_3_anchor'], anchors['right_arm_joint_to_chest_2_anchor'])
physics.Add6DofConstraint(nodes['chest'], nodes['left_arm'], anchors['chest_joint_to_left_arm_2_anchor'], anchors['left_arm_joint_to_chest_anchor'])
physics.Add6DofConstraint(nodes['chest'], nodes['left_arm'], anchors['chest_joint_to_left_arm_3_anchor'], anchors['left_arm_joint_to_chest_2_anchor'])
physics.Add6DofConstraint(nodes['chest'], nodes['right_leg'], anchors['chest_joint_to_right_leg_anchor'], anchors['right_leg_joint_to_chest_anchor'])
physics.Add6DofConstraint(nodes['chest'], nodes['right_leg'], anchors['chest_joint_to_right_leg_2_anchor'], anchors['right_leg_joint_to_chest_2_anchor'])
physics.Add6DofConstraint(nodes['chest'], nodes['right_leg'], anchors['chest_joint_to_right_leg_3_anchor'], anchors['right_leg_joint_to_chest_3_anchor'])
physics.Add6DofConstraint(nodes['chest'], nodes['left_leg'], anchors['chest_joint_to_left_leg_anchor'], anchors['left_leg_joint_to_chest_anchor'])
physics.Add6DofConstraint(nodes['chest'], nodes['left_leg'], anchors['chest_joint_to_left_leg_2_anchor'], anchors['left_leg_joint_to_chest_2_anchor'])
physics.Add6DofConstraint(nodes['chest'], nodes['left_leg'], anchors['chest_joint_to_left_leg_3_anchor'], anchors['left_leg_joint_to_chest_3_anchor'])
physics.Add6DofConstraint(nodes['chest'], nodes['head'], anchors['chest_joint_to_head_anchor'], anchors['head_joint_to_chest_anchor'])

physics.Add6DofConstraint(nodes['left_leg'], nodes['ground'], anchors['left_leg_joint_to_ground_anchor'], anchors['ground_joint_to_left_leg_anchor'])
physics.Add6DofConstraint(nodes['left_leg'], nodes['ground'], anchors['left_leg_joint_to_ground_2_anchor'], anchors['ground_joint_to_left_leg_2_anchor'])
physics.Add6DofConstraint(nodes['left_leg'], nodes['ground'], anchors['left_leg_joint_to_ground_3_anchor'], anchors['ground_joint_to_left_leg_3_anchor'])
physics.Add6DofConstraint(nodes['right_leg'], nodes['ground'], anchors['right_leg_joint_to_ground_anchor'], anchors['ground_joint_to_right_leg_anchor'])
physics.Add6DofConstraint(nodes['right_leg'], nodes['ground'], anchors['right_leg_joint_to_ground_2_anchor'], anchors['ground_joint_to_right_leg_2_anchor'])
physics.Add6DofConstraint(nodes['right_leg'], nodes['ground'], anchors['right_leg_joint_to_ground_3_anchor'], anchors['ground_joint_to_right_leg_3_anchor'])

keyboard = hg.Keyboard()

while not keyboard.Down(hg.K_Escape) and hg.IsWindowOpen(win):
    keyboard.Update()
    physics.NodeWake(nodes['chest'])

    view_id = 0
    hg.SceneUpdateSystems(scene, clocks, dt_frame_step, physics, physics_step, 3)
    view_id, pass_id = hg.SubmitSceneToPipeline(view_id, scene, hg.IntRect(0, 0, res_x, res_y), True, pipeline, res)

    hg.Frame()
    hg.UpdateWindow(win)

scene.Clear()
scene.GarbageCollect()

hg.RenderShutdown()
hg.DestroyWindow(win)

hg.WindowSystemShutdown()
hg.InputShutdown()