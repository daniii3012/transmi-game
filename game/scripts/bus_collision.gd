extends RefCounted
## Conservative body boxes + articulation envelope. Ground uses a separate layer.
const Motion = preload("res://scripts/bus_motion.gd")
var space: PhysicsDirectSpaceState3D
var shapes: Array[Shape3D] = []

func _init(state: PhysicsDirectSpaceState3D) -> void:
	space = state
	for size in [Motion.FRONT_SIZE, Motion.REAR_SIZE]:
		var shape := BoxShape3D.new()
		shape.size = size
		shapes.append(shape)
	var joint := CylinderShape3D.new()
	joint.radius = 1.3
	joint.height = 3.2
	shapes.append(joint)

func poses(state: Dictionary) -> Array[Transform3D]:
	var p: Vector2 = state.p
	var h: float = state.h
	var t: float = state.t
	var hinge := p - Motion.forward(h) * Motion.HITCH_OFFSET
	var front := p - Motion.forward(h) * Motion.FRONT_CENTER
	var rear := hinge - Motion.forward(t) * Motion.REAR_CENTER
	return [Transform3D(Basis(Vector3.UP, -h), Vector3(front.x, 1.7, front.y)),
		Transform3D(Basis(Vector3.UP, -t), Vector3(rear.x, 1.7, rear.y)),
		Transform3D(Basis.IDENTITY, Vector3(hinge.x, 1.7, hinge.y))]

func check(old: Dictionary, proposed: Dictionary) -> String:
	var before := poses(old)
	var after := poses(proposed)
	for i in shapes.size():
		var query := PhysicsShapeQueryParameters3D.new()
		query.shape = shapes[i]
		query.collision_mask = 1
		query.margin = 0.025
		query.transform = before[i]
		query.motion = after[i].origin - before[i].origin
		var fractions := space.cast_motion(query)
		if fractions.size() == 2 and fractions[0] < 0.9999:
			return "front" if i == 0 else ("rear" if i == 1 else "joint")
		query.motion = Vector3.ZERO
		query.transform = after[i]
		if not space.intersect_shape(query, 1).is_empty():
			return "front" if i == 0 else ("rear" if i == 1 else "joint")
	return ""
