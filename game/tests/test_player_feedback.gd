extends SceneTree
const Motion = preload("res://scripts/bus_motion.gd")
const Collision = preload("res://scripts/bus_collision.gd")
const Service = preload("res://scripts/practice_service.gd")
const CameraRig = preload("res://scripts/driving_camera.gd")
var failed := 0
func _initialize() -> void: _run.call_deferred()
func verify(ok: bool, description: String) -> void:
	if not ok:
		failed += 1
		push_error(description)
	else: print("PASS_FEEDBACK: ",description)
func barrier(world: Node3D, p: Vector3, size: Vector3) -> StaticBody3D:
	var body := StaticBody3D.new()
	body.position = p
	var shape := BoxShape3D.new()
	shape.size = size
	var collision := CollisionShape3D.new()
	collision.shape = shape
	body.add_child(collision)
	world.add_child(body)
	return body
func _run() -> void:
	var world := Node3D.new()
	root.add_child(world)
	var wall := barrier(world,Vector3(-1.7,1.7,-50),Vector3(.1,3.4,180))
	await physics_frame
	await physics_frame
	var collision = Collision.new(world.get_world_3d().direct_space_state)
	var m = Motion.new()
	m.reset(Vector2(.4,0),deg_to_rad(-4))
	m.speed = 4
	var sliding_frames := 0
	for i in 600:
		m.advance(1.0/60,collision.resolve)
		if m.sliding: sliding_frames += 1
	print("SLIDE_RESULT p=",m.position," speed=",m.speed," frames=",sliding_frames," block=",m.last_block)
	verify(m.position.y < -35 and m.speed > 3.9 and sliding_frames > 20,"roce lateral conserva avance durante diez segundos")
	var poses: Array[Transform3D] = collision.poses({"p":m.position,"h":m.heading,"t":m.trailer_heading})
	for i in poses.size():
		var query := PhysicsShapeQueryParameters3D.new()
		query.shape = collision.shapes[i]
		query.transform = poses[i]
		query.margin = 0
		verify(world.get_world_3d().direct_space_state.intersect_shape(query).is_empty(),"cuerpo %d no atraviesa el andén"%i)
	# Steering away must release the contact; it must not stick permanently.
	for i in 180:
		m.control(1.0/60,1,0,.4,false)
		m.advance(1.0/60,collision.resolve)
	verify(m.position.x > 1,"puede separarse del andén girando hacia fuera")
	wall.queue_free()
	await physics_frame
	barrier(world,Vector3(0,1.7,-20),Vector3(8,3.4,.05))
	await physics_frame
	await physics_frame
	m.reset(Vector2.ZERO)
	m.speed = 12
	m.advance(3,collision.resolve)
	verify(m.speed == 0 and m.position.y > -12.56,"el deslizamiento no permite atravesar un impacto frontal")
	var service = Service.new()
	m.reset(Service.STOP+Vector2(.45,.9))
	verify(service.aligned(m),"acepta separación de 82.5 cm y desfase de 90 cm")
	m.reset(Service.STOP+Vector2(.8,0))
	verify(not service.aligned(m),"rechaza una separación excesiva del andén")
	m.reset(Service.STOP+Vector2(-.5,0))
	verify(not service.aligned(m),"rechaza puertas dentro de la plataforma")
	var camera := CameraRig.new()
	world.add_child(camera)
	camera.set_mode(0)
	var yaw_before := camera.orbit_yaw
	camera.look(Vector2(200,-50))
	verify(absf(camera.orbit_yaw-yaw_before) > .5,"cámara exterior gira libremente con ratón")
	camera.set_mode(1)
	camera.look(Vector2(-250,0))
	verify(camera.cabin_look.x < -.6,"cabina puede mirar hacia puertas y andén")
	camera.recenter()
	verify(camera.cabin_look == Vector2.ZERO,"centrado recupera la vista de conducción")
	world.queue_free()
	await process_frame
	print("PLAYER_FEEDBACK_TEST ","PASS" if failed == 0 else "FAIL")
	quit(0 if failed == 0 else 1)
