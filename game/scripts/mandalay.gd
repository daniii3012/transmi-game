extends "res://scripts/practice.gd"
## Two-direction local practice. No official route is claimed.
const MandalayWorld = preload("res://scripts/mandalay_world.gd")
const StationService = preload("res://scripts/station_service.gd")
var stop_index := 0
var mandalay_capture := false
var photo_stage := 0
var photo_seconds := 0.0
var direction_label: Label

func _create_world():
	return MandalayWorld.new()

func _create_service():
	world.set_stop(stop_index)
	return StationService.new(world.data.stops[stop_index])

func _spawn_pose() -> Dictionary:
	var stop: Dictionary = world.data.stops[stop_index]
	return {"p":Vector2(stop.spawn[0],stop.spawn[1]),"h":float(stop.heading)}

func _outside_sample() -> bool:
	return absf(motion.position.x) > 88 or absf(motion.position.y) > 180

func _session_text() -> Dictionary:
	return {"title":"Mandalay · Troncal Américas","subtitle":"Práctica local · Articulado 18 m","exercise":"MANDALAY   /   APROXIMACIÓN Y PUERTAS","pause":"Elige el sentido de la práctica.\\nCompleta la parada y avanza 25 m.".replace("\\n","\n")}

func _extra_pause_buttons(stack: VBoxContainer) -> void:
	for i in world.data.stops.size():
		var button := Button.new()
		button.text = "Practicar · "+world.data.stops[i].direction
		button.custom_minimum_size.y = 36
		button.pressed.connect(_choose_stop.bind(i))
		stack.add_child(button)
	var button := Button.new()
	button.text = "Volver a la pista de conducción"
	button.custom_minimum_size.y = 36
	button.pressed.connect(func(): get_tree().change_scene_to_file("res://scenes/practice.tscn"))
	stack.add_child(button)
	pause_panel.position.y = 170

func _choose_stop(index: int) -> void:
	stop_index = index
	_restart_from_menu()
	bus.sync(motion,0)
	camera.recenter()
	_update_camera(1)

func _ready() -> void:
	super._ready()
	if bus == null or not bus.ready_ok: return
	ui.get_child(0).custom_minimum_size.y = 155
	direction_label = label(ui,"",16,"e8c989")
	direction_label.position = Vector2(47,137)
	mandalay_capture = "--capture-mandalay" in OS.get_cmdline_user_args()
	if mandalay_capture:
		capture_mode = true
		capture_step = -1
		motion.reset(service.target,service.heading)
		bus.sync(motion,0)
		service.update(0,motion)
		_update_camera(1)
	print("MANDALAY_READY modules=",world.data.modules.size()," stops=",world.data.stops.size()," layout=",world.data.summary.layout_version)

func _process(dt: float) -> void:
	super._process(dt)
	if direction_label != null:
		direction_label.text = world.data.stops[stop_index].direction+" · Esc cambia de sentido"
	if not mandalay_capture or photo_stage < 0: return
	photo_seconds += dt
	if photo_seconds < 2.5: return
	var stage := photo_stage
	photo_stage = -1
	await RenderingServer.frame_post_draw
	var names := ["preview_mandalay.png","preview_mandalay_cabina.png","preview_mandalay_parada.png"]
	get_viewport().get_texture().get_image().save_png(ProjectSettings.globalize_path("res://../docs/"+names[stage]))
	if stage == 2:
		print("MANDALAY_CAPTURE_COMPLETE")
		get_tree().quit()
		return
	photo_stage = stage+1
	photo_seconds = 0
	if photo_stage == 1:
		motion.reset(service.target-service.forward*28,service.heading)
		camera_mode = 1
		camera.set_mode(1)
	else:
		motion.reset(service.target,service.heading)
		motion.doors_target = true
		motion.doors_fraction = 1
		service.update(4,motion)
		service.update(0,motion)
		camera_mode = 2
	service.update(0,motion)
	bus.sync(motion,0)
	_update_camera(1)

func _update_camera(dt: float) -> void:
	if mandalay_capture:
		if photo_stage == 0:
			camera.position = Vector3(74,65,112)
			camera.look_at(Vector3(0,0,5),Vector3.UP)
			return
		if photo_stage == 2:
			var p: Vector2 = service.target-service.right*6+service.forward*16
			camera.position = Vector3(p.x,3.6,p.y)
			camera.look_at(Vector3(service.target.x,2,service.target.y),Vector3.UP)
			return
	super._update_camera(dt)
