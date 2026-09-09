extends SceneTree
var failures := 0
func _initialize() -> void: run.call_deferred()
func check(ok: bool, message: String) -> void:
	if ok: print("PASS_SCALE: ",message)
	else:
		failures += 1
		push_error(message)
func body_bounds(node: Node3D, relative_to: Node3D) -> AABB:
	var points: Array[Vector3] = []
	for child in node.find_children("*","MeshInstance3D",true,false):
		var box: AABB = child.get_aabb()
		for i in 8: points.append(relative_to.to_local(child.to_global(box.get_endpoint(i))))
	var result := AABB(points[0],Vector3.ZERO)
	for p in points: result = result.expand(p)
	return result
func run() -> void:
	var scene = load("res://scenes/scale_study.tscn").instantiate()
	root.add_child(scene)
	await process_frame
	check(scene.bus_instances.size() == 2,"ambas versiones cargan el modelo articulado")
	var a: Node3D = scene.bus_instances[0]
	var b: Node3D = scene.bus_instances[1]
	var front_a := body_bounds(a.front,a.front)
	var front_b := body_bounds(b.front,b.front)
	var rear_a := body_bounds(a.rear,a.rear)
	var rear_b := body_bounds(b.rear,b.rear)
	print("MESH_DIMENSIONS front=",front_a.size," / ",front_b.size," rear=",rear_a.size," / ",rear_b.size)
	check(front_a.size.distance_to(front_b.size) < .001 and rear_a.size.distance_to(rear_b.size) < .001,"las mallas del bus conservan dimensiones en ambas disposiciones")
	check(a.global_basis.get_scale().is_equal_approx(Vector3.ONE) and b.global_basis.get_scale().is_equal_approx(Vector3.ONE),"los vehículos no heredan una reducción de escala")
	check(a.front.global_position.distance_to(a.rear.global_position) > 2.69 and b.front.global_position.distance_to(b.rear.global_position) > 2.69,"la separación de cuerpos conserva el enganche de 2,7 m")
	check(a.doors.size() == 8 and b.doors.size() == 8,"ambos buses conservan ocho hojas de puerta")
	scene.queue_free()
	await process_frame
	print("SCALE_STUDY_TEST ","PASS" if failures == 0 else "FAIL")
	quit(0 if failures == 0 else 1)
