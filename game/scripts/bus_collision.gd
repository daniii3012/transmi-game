extends RefCounted
## Conservative body boxes + articulation envelope. Ground uses a separate layer.
const Motion = preload("res://scripts/bus_motion.gd")
const Definition = preload("res://scripts/vehicle_definition.gd")
var spec: Definition
var space: PhysicsDirectSpaceState3D
var shapes: Array[Shape3D] = []

func _init(state: PhysicsDirectSpaceState3D, definition = null) -> void:
	space = state
	spec = Motion.Definition.new() if definition == null else definition
	for size in [spec.module_size(spec.front), spec.module_size(spec.rear)]:
		var shape := BoxShape3D.new()
		shape.size = size
		shapes.append(shape)
	var joint := CylinderShape3D.new()
	joint.radius = spec.data.collision.joint_radius_m
	joint.height = spec.data.collision.height_m
	shapes.append(joint)

func poses(state: Dictionary) -> Array[Transform3D]:
	var p: Vector2 = state.p
	var h: float = state.h
	var t: float = state.t
	var hinge: Vector2 = p - Motion.forward(h) * spec.hitch_offset
	var front: Vector2 = p - Motion.forward(h) * spec.module_center(spec.front)
	var rear: Vector2 = hinge - Motion.forward(t) * spec.module_center(spec.rear)
	return [Transform3D(Basis(Vector3.UP, -h), Vector3(front.x, spec.data.collision.center_y_m, front.y)),
		Transform3D(Basis(Vector3.UP, -t), Vector3(rear.x, spec.data.collision.center_y_m, rear.y)),
		Transform3D(Basis.IDENTITY, Vector3(hinge.x, spec.data.collision.center_y_m, hinge.y))]

func check(old: Dictionary, proposed: Dictionary) -> String:
	return str(contact(old, proposed).get("body", ""))

func contact(old: Dictionary, proposed: Dictionary) -> Dictionary:
	var before := poses(old)
	var after := poses(proposed)
	for i in shapes.size():
		var query := PhysicsShapeQueryParameters3D.new()
		query.shape = shapes[i]
		query.collision_mask = 1
		query.margin = spec.data.collision.query_margin_m
		query.transform = before[i]
		query.motion = after[i].origin - before[i].origin
		var fractions := space.cast_motion(query)
		if fractions.size() == 2 and fractions[0] < 0.9999:
			query.transform.origin += query.motion * minf(1.0, fractions[1] + 0.005)
			query.motion = Vector3.ZERO
			return _contact_info(query, i)
		query.motion = Vector3.ZERO
		query.transform = after[i]
		if not space.intersect_shape(query, 1).is_empty():
			return _contact_info(query, i)
	return {}

func _contact_info(query: PhysicsShapeQueryParameters3D, body_index: int) -> Dictionary:
	var info := space.get_rest_info(query)
	var normal: Vector3 = info.get("normal", Vector3.ZERO)
	return {"body": ["front", "rear", "joint"][body_index],
		"normal": Vector2(normal.x, normal.z).normalized()}

func resolve(old: Dictionary, proposed: Dictionary) -> Dictionary:
	var hit := contact(old, proposed)
	if hit.is_empty(): return {"state": proposed, "sliding": false}
	var movement: Vector2 = proposed.p - old.p
	var normal: Vector2 = hit.normal
	# Keep tangential travel at a glancing contact, with no artificial friction.
	# A frontal impact still stops. Never accept an unchecked translated/rotated pose.
	if movement.length() > 0.000001 and normal.length() > 0.9:
		var incidence := absf(movement.normalized().dot(normal))
		if incidence < 0.75:
			var tangent := movement - normal * minf(movement.dot(normal), 0.0)
			var trailer: float = old.t + tangent.dot(Motion.right(old.t)) / spec.trailer_wheelbase
			var slide := {"p": old.p + tangent, "h": old.h, "t": trailer}
			if tangent.length() > movement.length() * 0.25 and check(old, slide).is_empty():
				return {"state": slide, "sliding": true}
			# Contact can temporarily constrain trailer rotation as well as front yaw.
			slide.t = old.t
			if tangent.length() > movement.length() * 0.25 and check(old, slide).is_empty():
				return {"state": slide, "sliding": true}
	return {"blocked": hit.body}
