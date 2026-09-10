extends SceneTree
const Definition = preload("res://scripts/vehicle_definition.gd")
const Motion = preload("res://scripts/bus_motion.gd")
const Collision = preload("res://scripts/bus_collision.gd")
const Visual = preload("res://scripts/bus_visual.gd")
const Service = preload("res://scripts/station_service.gd")
var failures := 0
func _initialize() -> void: run.call_deferred()
func verify(ok: bool, description: String) -> void:
	print("PASS_SPEC: " if ok else "FAIL_SPEC: ",description)
	if not ok: failures += 1
func run() -> void:
	var spec := Definition.new()
	verify(spec.asset_error().is_empty(),"el GLB corresponde a la ficha y al manifiesto")
	var sector := Node3D.new()
	sector.position = Vector3(310,0,-180)
	sector.rotation.y = .65
	root.add_child(sector)
	var bus = Visual.new(spec)
	sector.add_child(bus)
	var motion := Motion.new(spec)
	motion.reset(Vector2(8,25),.43)
	motion.trailer_heading = .25
	bus.sync(motion,0)
	var anchors: Array[Vector2] = motion.door_positions()
	var definitions: Array[Dictionary] = spec.straight_doors()
	var geometry_matches := true
	for i in definitions.size():
		var sum := Vector3.ZERO
		var count := 0
		for leaf in bus.doors:
			if leaf.id == definitions[i].id:
				# The leaf pivots sit at body X=0; the actual doorway uses the body side.
				sum += sector.to_local(leaf.node.to_global(Vector3(-spec.width*.5,0,0)))
				count += 1
		if count != 2:
			geometry_matches = false
			continue
		var center := sum*.5
		geometry_matches = geometry_matches and Vector2(center.x,center.z).distance_to(anchors[i]) < .001
	verify(geometry_matches,"las cuatro puertas del GLB coinciden con la cinemática aun articulado y bajo un sector colocado")
	var a: Vector3 = bus.front.to_global(Vector3(0,0,spec.front.z_max_m-.03))
	var b: Vector3 = bus.rear.to_global(Vector3(0,0,spec.rear.z_min_m+.03))
	var joint_ok := true
	var vertices: PackedVector3Array = bus.joint_mesh.mesh.surface_get_arrays(0)[Mesh.ARRAY_VERTEX]
	for vertex in vertices:
		var world: Vector3 = bus.joint_mesh.to_global(vertex)
		if minf(world.distance_to(a),world.distance_to(b)) > 5: joint_ok = false
	verify(joint_ok,"el fuelle conserva su posición al colocar el vehículo dentro de un sector")
	var changed_data := spec.data.duplicate(true)
	changed_data.hitch_offset_m = 3.2
	var scratch := "user://vehicle_definition_test_fixture.json"
	var file := FileAccess.open(scratch,FileAccess.WRITE)
	file.store_string(JSON.stringify(changed_data))
	file.close()
	var changed := Definition.new(scratch)
	DirAccess.remove_absolute(ProjectSettings.globalize_path(scratch))
	var other := Motion.new(changed)
	other.reset(Vector2.ZERO)
	verify(absf(other.hinge().y-3.2) < .0001 and absf(other.door_positions()[2].y-5.2) < .0001,"cambiar el enganche en la ficha cambia cinemática y puertas")
	var collision := Collision.new(sector.get_world_3d().direct_space_state,changed)
	var poses := collision.poses({"p":Vector2.ZERO,"h":0.0,"t":0.0})
	verify(absf(poses[1].origin.z-7.4) < .0001,"la envolvente trasera sigue el enganche configurado")
	verify(not changed.asset_error().is_empty(),"se detecta el modelo desactualizado al cambiar la ficha")
	var stops: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://data/mandalay.json"))
	var service := Service.new(stops.stops[0])
	other.reset(service.target,service.heading)
	verify(not service.aligned(other),"Mandalay rechaza anclajes generados para otra revisión del vehículo")
	sector.queue_free()
	await process_frame
	print("VEHICLE_DEFINITION_TEST ","PASS" if failures == 0 else "FAIL")
	quit(0 if failures == 0 else 1)
