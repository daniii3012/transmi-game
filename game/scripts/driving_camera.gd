extends Camera3D
## Mouse-look is independent from vehicle steering. All driving views are orientable.
var mode := 0
var orbit_yaw := 0.445
var orbit_pitch := 0.29
var orbit_distance := 23.8
var cabin_look := Vector2.ZERO
var dragging := false

func set_mode(value: int) -> void:
	mode = value % 3
	recenter()

func recenter() -> void:
	cabin_look = Vector2.ZERO
	orbit_yaw = -2.467 if mode == 2 else 0.445
	orbit_pitch = 0.235 if mode == 2 else 0.245
	orbit_distance = 19.8 if mode == 2 else 24.2
	fov = 65

func release_mouse() -> void:
	dragging = false
	Input.mouse_mode = Input.MOUSE_MODE_VISIBLE

func handle_input(event: InputEvent) -> bool:
	if event is InputEventMouseButton:
		if event.button_index == MOUSE_BUTTON_RIGHT:
			dragging = event.pressed
			Input.mouse_mode = Input.MOUSE_MODE_CAPTURED if dragging else Input.MOUSE_MODE_VISIBLE
			return true
		if event.pressed and event.button_index in [MOUSE_BUTTON_WHEEL_UP,MOUSE_BUTTON_WHEEL_DOWN]:
			var amount := -1.0 if event.button_index == MOUSE_BUTTON_WHEEL_UP else 1.0
			if mode == 1: fov = clampf(fov + amount * 3, 45, 85)
			else: orbit_distance = clampf(orbit_distance + amount * 1.5, 5, 45)
			return true
	if event is InputEventMouseMotion and dragging:
		look(event.relative)
		return true
	if event is InputEventKey and event.pressed and not event.echo and event.keycode == KEY_V:
		recenter()
		return true
	return false

func look(delta: Vector2) -> void:
	if mode == 1:
		cabin_look.x = clampf(cabin_look.x + delta.x * .003, -2.8, 2.8)
		cabin_look.y = clampf(cabin_look.y - delta.y * .003, -1.05, 1.05)
	else:
		orbit_yaw = wrapf(orbit_yaw - delta.x * .004, -PI, PI)
		orbit_pitch = clampf(orbit_pitch + delta.y * .003, .06, 1.35)

func follow(bus_front: Node3D, dt: float, space: PhysicsDirectSpaceState3D) -> void:
	if mode == 1:
		position = bus_front.to_global(Vector3(-.64,2.34,-6.05))
		var glance := 0.0
		if Input.is_physical_key_pressed(KEY_Q): glance -= 1.35
		if Input.is_physical_key_pressed(KEY_E): glance += 1.35
		var direction := Vector3(0,0,-1).rotated(Vector3.RIGHT,cabin_look.y).rotated(Vector3.UP,-cabin_look.x-glance)
		look_at(position + bus_front.global_basis * direction,Vector3.UP)
		return
	var target := bus_front.to_global(Vector3(0,1.8,-.2))
	var offset := Vector3(sin(orbit_yaw)*cos(orbit_pitch),sin(orbit_pitch),cos(orbit_yaw)*cos(orbit_pitch))*orbit_distance
	var desired := target + bus_front.global_basis * offset
	# Keep the exterior camera in front of opaque station walls/roofs.
	var ray := PhysicsRayQueryParameters3D.create(target,desired,1)
	var contact := space.intersect_ray(ray)
	if not contact.is_empty(): desired = contact.position + (target-contact.position).normalized()*.25
	position = position.lerp(desired,clampf(dt*12,0,1))
	look_at(target,Vector3.UP)
