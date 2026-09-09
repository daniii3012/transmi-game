extends SceneTree
const Scene = preload("res://scenes/practice.tscn")
var failed := false
func _initialize() -> void:
	_run.call_deferred()
func verify(ok: bool, text: String) -> void:
	if not ok:
		failed = true
		push_error(text)
	else: print("PASS_SCENE: ", text)
func _run() -> void:
	var scene = Scene.instantiate()
	root.add_child(scene)
	await physics_frame
	await physics_frame
	scene.paused = true
	verify(scene.bus.front != null and scene.bus.rear != null and scene.bus.doors.size() == 8,"GLB: dos cuerpos y ocho hojas de puerta")
	var m = scene.motion
	m.reset(Vector2(0,35))
	# Approach on the actual practice geometry. A speed target provides repeatable braking.
	for i in 2400:
		var distance: float = -45.0-m.position.y
		var remaining := -distance
		var target := minf(7.0,sqrt(maxf(0,remaining-.18)*5.0))
		m.control(1.0/60,1.0 if m.speed < target-.12 else 0.0,1.0 if m.speed > target else 0.0,0,false)
		m.advance(1.0/60,scene.collision.resolve)
		if remaining < .65 and m.speed < .05: break
	verify(m.last_block.is_empty() and scene.service.aligned(m),"aproximación a plataforma real de ensayo, sin colisión")
	m.toggle_doors()
	for i in 360:
		m.control(1.0/60,0,0,0,false)
		scene.service.update(1.0/60,m)
	scene.bus.sync(m,0)
	verify(scene.service.served,"atención de parada integrada en escena")
	for door in scene.bus.doors:
		verify(absf(door.node.position.z-door.base) > .58,"hoja de puerta abierta en el modelo")
	scene.queue_free()
	await process_frame
	print("PRACTICE_SCENE_TEST ","FAIL" if failed else "PASS")
	quit(1 if failed else 0)
