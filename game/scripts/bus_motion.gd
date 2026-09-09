extends RefCounted
## Planar off-axle articulated vehicle. Units: metres, seconds, radians.
## Heading increases clockwise; the front module rear axle is the reference.

const WHEELBASE := 5.8
const HITCH_OFFSET := 2.7
const TRAILER_WHEELBASE := 5.4
const MAX_ARTICULATION := deg_to_rad(60.0)
const FRONT_CENTER := -2.6
const REAR_CENTER := 4.2
const FRONT_SIZE := Vector3(2.55, 3.2, 9.6)
const REAR_SIZE := Vector3(2.55, 3.2, 7.4)

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

static func forward(angle: float) -> Vector2:
	return Vector2(sin(angle), -cos(angle))

static func right(angle: float) -> Vector2:
	return Vector2(cos(angle), sin(angle))

func hinge() -> Vector2:
	return position - forward(heading) * HITCH_OFFSET

func trailer_axle() -> Vector2:
	return hinge() - forward(trailer_heading) * TRAILER_WHEELBASE

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
	doors_fraction = move_toward(doors_fraction, 1.0 if doors_target else 0.0, dt / 1.2)
	var steering_limit := lerpf(deg_to_rad(34.0), deg_to_rad(12.0), clampf(absf(speed) / 18.0, 0, 1))
	steering = move_toward(steering, steer * steering_limit, dt * deg_to_rad(48.0))
	if doors_target or doors_fraction > 0.001:
		speed = 0
		return
	var magnitude := absf(speed)
	var resistance := 0.13 + 0.0018 * magnitude * magnitude
	if handbrake:
		magnitude = move_toward(magnitude, 0.0, 8.0 * dt)
	elif brake > 0.0:
		magnitude = move_toward(magnitude, 0.0, (brake * 4.5 + resistance) * dt)
	elif throttle > 0:
		magnitude += (throttle * 1.5 - resistance) * dt
	else:
		magnitude = move_toward(magnitude, 0, resistance * dt)
	speed = clampf(magnitude, 0, 16.67 if gear > 0 else 2.22) * gear

func advance(dt: float, collision_check: Callable = Callable()) -> void:
	last_block = ""
	if absf(speed) < 0.00001:
		return
	# Bound translation AND corner rotation per substep. Translation is also swept.
	var yaw_rate := speed / WHEELBASE * tan(steering)
	var steps := maxi(1, ceili((absf(speed) + absf(yaw_rate) * 14.0) * dt / 0.04))
	var h := dt / float(steps)
	for _i in range(steps):
		var old := {"p": position, "h": heading, "t": trailer_heading}
		var old_hinge := hinge()
		var yaw_delta := speed / WHEELBASE * tan(steering) * h
		var next_position := position + forward(heading + yaw_delta * 0.5) * speed * h
		var next_heading := heading + yaw_delta
		var next_hinge := next_position - forward(next_heading) * HITCH_OFFSET
		var hitch_delta := next_hinge - old_hinge
		# Midpoint integration of the trailer axle's no-side-slip constraint.
		var half_angle := trailer_heading + hitch_delta.dot(right(trailer_heading)) / TRAILER_WHEELBASE * 0.5
		var next_trailer := trailer_heading + hitch_delta.dot(right(half_angle)) / TRAILER_WHEELBASE
		var next_articulation := absf(wrapf(next_heading - next_trailer, -PI, PI))
		if next_articulation > MAX_ARTICULATION and next_articulation > absf(articulation()):
			last_block = "articulation"
			speed = 0
			return
		var proposed := {"p": next_position, "h": next_heading, "t": next_trailer}
		if collision_check.is_valid():
			var hit: String = collision_check.call(old, proposed)
			if not hit.is_empty():
				last_block = hit
				speed = 0
				return
		position = next_position
		heading = wrapf(next_heading, -PI, PI)
		trailer_heading = wrapf(next_trailer, -PI, PI)
		distance_m += absf(speed * h)
