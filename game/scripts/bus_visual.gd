extends Node3D
const MODEL = preload("res://assets/vehicles/articulado_prototipo.glb")
const Motion = preload("res://scripts/bus_motion.gd")
var front: Node3D
var rear: Node3D
var doors: Array[Dictionary] = []
var wheels: Array[Node3D] = []
var joint_mesh: MeshInstance3D
var rubber := StandardMaterial3D.new()
var model: Node3D
var wheel_angle := 0.0

func _ready() -> void:
	model = MODEL.instantiate()
	add_child(model)
	front = model.find_child("Front", true, false)
	rear = model.find_child("Rear", true, false)
	_collect(model)
	rubber.albedo_color = Color("444c51")
	rubber.roughness = 0.95
	rubber.cull_mode = BaseMaterial3D.CULL_DISABLED
	joint_mesh = MeshInstance3D.new()
	joint_mesh.material_override = rubber
	add_child(joint_mesh)
	var sign_label := Label3D.new()
	sign_label.text = "PRÁCTICA"
	sign_label.font_size = 40
	sign_label.pixel_size = 0.0025
	sign_label.position = Vector3(0, 2.87, -7.385)
	sign_label.rotation.y = PI
	sign_label.modulate = Color("ffca62")
	front.add_child(sign_label)

func _collect(node: Node) -> void:
	if node is MeshInstance3D:
		for i in node.mesh.get_surface_count():
			var original = node.get_active_material(i)
			if original is StandardMaterial3D and original.transparency != BaseMaterial3D.TRANSPARENCY_DISABLED:
				var window_mat = original.duplicate()
				window_mat.albedo_color.a = 0.18
				node.set_surface_override_material(i,window_mat)
	if node.name.begins_with("Door_"):
		doors.append({"node":node, "base":node.position.z, "sign":-1 if "minus" in str(node.name) else 1})
	if node.name.begins_with("SteerWheel") or node.name.begins_with("Wheel"):
		wheels.append(node)
	for child in node.get_children(): _collect(child)

func sync(motion, dt: float) -> void:
	front.position = Vector3(motion.position.x, 0, motion.position.y)
	front.rotation.y = -motion.heading
	var hinge: Vector2 = motion.hinge()
	rear.position = Vector3(hinge.x, 0, hinge.y)
	rear.rotation.y = -motion.trailer_heading
	for door in doors:
		door.node.position.z = door.base + door.sign * 0.59 * motion.doors_fraction
	wheel_angle += motion.speed * dt / 0.51
	for wheel in wheels:
		wheel.rotation.y = -motion.steering if wheel.name.begins_with("SteerWheel") else 0.0
		# The wheel pivots own the tire and hub; rotate children without changing axle position.
		for part in wheel.get_children():
			if part is MeshInstance3D: part.rotation.x = -wheel_angle
	_update_joint()

func _update_joint() -> void:
	var a := front.to_global(Vector3(0, 0, 2.17))
	var b := rear.to_global(Vector3(0, 0, 0.53))
	var surface := SurfaceTool.new()
	surface.begin(Mesh.PRIMITIVE_TRIANGLES)
	var rings: Array[PackedVector3Array] = []
	for i in range(13):
		var t := float(i) / 12.0
		var center := a.lerp(b, t)
		var basis := front.global_basis.slerp(rear.global_basis, t)
		var w := 1.22 + (0.055 if i % 2 == 0 else -0.02)
		var top := 3.05 + (0.035 if i % 2 == 0 else -0.01)
		var ring := PackedVector3Array()
		for corner in [Vector3(-w, 1.02, 0), Vector3(-w, top, 0), Vector3(w, top, 0), Vector3(w, 1.02, 0)]:
			ring.append(center + basis * corner)
		rings.append(ring)
	for i in range(12):
		for j in range(4):
			var k := (j + 1) % 4
			for vertex in [rings[i][j], rings[i+1][j], rings[i+1][k], rings[i][j], rings[i+1][k], rings[i][k]]:
				surface.add_vertex(vertex)
	surface.generate_normals()
	joint_mesh.mesh = surface.commit()
