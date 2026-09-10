extends RefCounted
## Planar off-axle articulated vehicle. Units: metres, seconds, radians.
## Heading increases clockwise; the front module rear axle is the reference.

const Definition = preload("res://scripts/vehicle_definition.gd")
var spec: Definition

func _init(definition = null) -> void:
	spec = Definition.new() if definition == null else definition

var position := Vector2.ZERO
var heading := 0.0
var trailer_heading := 0.0
var speed := 0.0
var steering := 0.0
var gear := 1
var doors_target := false
var doors_fraction := 0.0
var distance_m := 0.0
var last_block := ""
var sliding := false

static func forward(angle: float) -> Vector2:
	return Vector2(sin(angle), -cos(angle))

static func right(angle: float) -> Vector2:
	return Vector2(cos(angle), sin(angle))

func hinge() -> Vector2:
	return position - forward(heading) * spec.hitch_offset

func trailer_axle() -> Vector2:
	return hinge() - forward(trailer_heading) * spec.trailer_wheelbase

func articulation() -> float:
	return wrapf(heading - trailer_heading, -PI, PI)

func reset(p: Vector2, angle := 0.0) -> void:
	position = p
	heading = angle
	trailer_heading = angle
	speed = 0
	steering = 0
	gear = 1
	doors_target = false
	doors_fraction = 0
	last_block = ""
	sliding = false
	distance_m = 0

func toggle_gear() -> bool:
	if absf(speed) > 0.05:
		return false
	gear *= -1
	return true

func toggle_doors() -> bool:
	if absf(speed) > 0.05:
		return false
	doors_target = not doors_target
	return true

func control(dt: float, throttle: float, brake: float, steer: float, handbrake: bool) -> void:
	doors_fraction = move_toward(doors_fraction, 1.0 if doors_target else 0.0, dt / float(spec.data.door_motion.duration_s))
	var steering_limit := lerpf(deg_to_rad(spec.dynamics.steering_low_speed_deg), deg_to_rad(spec.dynamics.steering_high_speed_deg), clampf(absf(speed) / float(spec.dynamics.steering_blend_speed_mps), 0, 1))
	steering = move_toward(steering, steer * steering_limit, dt * deg_to_rad(spec.dynamics.steering_rate_deg_s))
	if doors_target or doors_fraction > 0.001:
		speed = 0
		return
	var magnitude := absf(speed)
	var resistance := float(spec.dynamics.coast_constant_mps2) + float(spec.dynamics.coast_speed_factor) * magnitude * magnitude
	if handbrake:
		magnitude = move_toward(magnitude, 0.0, float(spec.dynamics.handbrake_mps2) * dt)
	elif brake > 0.0:
		magnitude = move_toward(magnitude, 0.0, (brake * float(spec.dynamics.braking_mps2) + resistance) * dt)
	elif throttle > 0:
		magnitude += (throttle * float(spec.dynamics.acceleration_mps2) - resistance) * dt
	else:
		magnitude = move_toward(magnitude, 0, resistance * dt)
	speed = clampf(magnitude, 0, float(spec.dynamics.forward_speed_mps) if gear > 0 else float(spec.dynamics.reverse_speed_mps)) * gear

func advance(dt: float, collision_check: Callable = Callable()) -> void:
	last_block = ""
	sliding = false
	if absf(speed) < 0.00001:
		return
	# Bound translation AND corner rotation per substep. Translation is also swept.
	var yaw_rate := speed / spec.wheelbase * tan(steering)
	var steps := maxi(1, ceili((absf(speed) + absf(yaw_rate) * float(spec.data.collision.corner_motion_bound_m)) * dt / 0.04))
	var h := dt / float(steps)
	for _i in range(steps):
		var old := {"p": position, "h": heading, "t": trailer_heading}
		var old_hinge := hinge()
		var yaw_delta := speed / spec.wheelbase * tan(steering) * h
		var next_position := position + forward(heading + yaw_delta * 0.5) * speed * h
		var next_heading := heading + yaw_delta
		var next_hinge := next_position - forward(next_heading) * spec.hitch_offset
		var hitch_delta := next_hinge - old_hinge
		# Midpoint integration of the trailer axle's no-side-slip constraint.
		var half_angle := trailer_heading + hitch_delta.dot(right(trailer_heading)) / spec.trailer_wheelbase * 0.5
		var next_trailer := trailer_heading + hitch_delta.dot(right(half_angle)) / spec.trailer_wheelbase
		var next_articulation := absf(wrapf(next_heading - next_trailer, -PI, PI))
		if next_articulation > spec.max_articulation and next_articulation > absf(articulation()):
			last_block = "articulation"
			speed = 0
			return
		var proposed := {"p": next_position, "h": next_heading, "t": next_trailer}
		if collision_check.is_valid():
			var result = collision_check.call(old, proposed)
			# The simple check callback remains useful for strict obstacle tests.
			if result is String: result = {"state": proposed} if result.is_empty() else {"blocked": result}
			if result.has("blocked"):
				last_block = result.blocked
				speed = 0
				return
			proposed = result.state
			sliding = sliding or result.get("sliding", false)
		if absf(wrapf(proposed.h-proposed.t, -PI, PI)) > spec.max_articulation:
			last_block = "articulation"
			speed = 0
			return
		distance_m += position.distance_to(proposed.p)
		position = proposed.p
		heading = wrapf(proposed.h, -PI, PI)
		trailer_heading = wrapf(proposed.t, -PI, PI)

func door_positions() -> Array[Vector2]:
	var result: Array[Vector2] = []
	for module in [spec.front,spec.rear]:
		var origin: Vector2 = position if module.id == "front" else hinge()
		var angle: float = heading if module.id == "front" else trailer_heading
		for door in module.doors:
			result.append(origin-forward(angle)*float(door.z_m)-right(angle)*spec.width*.5)
	return result
