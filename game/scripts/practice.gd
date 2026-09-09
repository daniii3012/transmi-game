extends Node3D
const Motion = preload("res://scripts/bus_motion.gd")
const Collision = preload("res://scripts/bus_collision.gd")
const Visual = preload("res://scripts/bus_visual.gd")
const World = preload("res://scripts/practice_world.gd")
const CameraRig = preload("res://scripts/driving_camera.gd")
const Service = preload("res://scripts/practice_service.gd")
var motion = Motion.new()
var service = Service.new()
var collision
var bus
var camera
var camera_mode := 0
var paused := false
var ui: CanvasLayer
var speed_label: Label
var vehicle_label: Label
var instruction_label: Label
var operation_label: Label
var notice_label: Label
var pause_panel: PanelContainer
var pause_title: Label
var feedback := ""
var feedback_seconds := 0.0
var capture_mode := false
var capture_step := 0
var capture_seconds := 0.0

func _ready() -> void:
	capture_mode = "--capture-practice" in OS.get_cmdline_user_args()
	var world := World.new()
	add_child(world)
	bus = Visual.new()
	add_child(bus)
	camera = CameraRig.new()
	camera.far = 900
	camera.near = 0.06
	camera.fov = 65
	add_child(camera)
	camera.make_current()
	collision = Collision.new(get_world_3d().direct_space_state)
	_reset()
	_make_ui()
	if capture_mode:
		motion.reset(Vector2(0,0))
		camera_mode = 2
		camera.set_mode(camera_mode)
	bus.sync(motion, 0)
	_update_camera(1.0)
	print("PRACTICE_READY bodies=2 length_m=18 doors=4 scale=1m")
	if DisplayServer.get_name() == "headless" and not "--keep-running" in OS.get_cmdline_user_args():
		get_tree().quit()

func _reset() -> void:
	motion.reset(Vector2(0, 35))
	service = Service.new()
	feedback = "W acelera · S frena · P abre puertas estando detenido"
	feedback_seconds = 6

func label(parent: Node, value: String, size: int, color := "ede9df") -> Label:
	var result := Label.new()
	result.text = value
	result.add_theme_font_size_override("font_size",size)
	result.add_theme_color_override("font_color",Color(color))
	parent.add_child(result)
	return result

func panel(p: Vector2, size: Vector2, opacity := 0.91) -> PanelContainer:
	var result := PanelContainer.new()
	result.position = p
	result.custom_minimum_size = size
	var style := StyleBoxFlat.new()
	style.bg_color = Color(0.11,0.15,0.135,opacity)
	style.corner_radius_top_left = 10
	style.corner_radius_top_right = 10
	style.corner_radius_bottom_left = 10
	style.corner_radius_bottom_right = 10
	style.content_margin_left = 20
	style.content_margin_right = 20
	style.content_margin_top = 14
	style.content_margin_bottom = 14
	result.add_theme_stylebox_override("panel", style)
	ui.add_child(result)
	return result

func _make_ui() -> void:
	ui = CanvasLayer.new()
	add_child(ui)
	var top := panel(Vector2(24,24),Vector2(410,120))
	var stack := VBoxContainer.new()
	top.add_child(stack)
	label(stack,"BOGOTÁ TRANSMI",25,"e8c989")
	label(stack,"Escuela de conducción · Articulado",18)
	label(stack,"Pista de ensayo / escala métrica real",15,"b5c3c7")
	var route_panel := panel(Vector2(790,24),Vector2(626,115))
	var route_stack := VBoxContainer.new()
	route_panel.add_child(route_stack)
	label(route_stack,"PRÁCTICA 01   /   APROXIMACIÓN Y PUERTAS",16,"e8c989")
	instruction_label = label(route_stack,"",20)
	operation_label = label(route_stack,"",16,"b5c3c7")
	var dashboard := panel(Vector2(24,672),Vector2(265,196))
	var dash_stack := VBoxContainer.new()
	dashboard.add_child(dash_stack)
	speed_label = label(dash_stack,"0",56)
	vehicle_label = label(dash_stack,"",17,"bdc9cb")
	var controls := panel(Vector2(317,738),Vector2(1099,130))
	var control_stack := VBoxContainer.new()
	controls.add_child(control_stack)
	label(control_stack,"W / ↑ Acelerar   S / ↓ Frenar   A D / ← → Girar   Espacio Freno de mano",17)
	label(control_stack,"P Puertas   R D / Reversa   C Cámara   Retroceso Reiniciar   Esc Pausa   F2 Mapa de Américas",16,"bdc9cb")
	label(control_stack,"Clic derecho + ratón Mirar   Rueda Acercar   V Centrar   Q / E Mirada lateral en cabina",16,"bdc9cb")
	notice_label = label(ui,"",18,"fff0c5")
	notice_label.position = Vector2(340,700)
	notice_label.add_theme_color_override("font_shadow_color",Color("102027"))
	notice_label.add_theme_constant_override("shadow_offset_x",1)
	notice_label.add_theme_constant_override("shadow_offset_y",2)
	pause_panel = panel(Vector2(460,290),Vector2(520,270),0.98)
	var pause_stack := VBoxContainer.new()
	pause_stack.add_theme_constant_override("separation",16)
	pause_panel.add_child(pause_stack)
	pause_title = label(pause_stack,"PAUSA",32,"e8c989")
	label(pause_stack,"Pista y vehículo provisionales.\nEl mapa real se inspecciona en el explorador.",18)
	for item in [["Continuar",_toggle_pause],["Reiniciar práctica",_restart_from_menu],["Explorar Américas",_open_explorer]]:
		var button := Button.new()
		button.text = item[0]
		button.custom_minimum_size.y = 36
		button.pressed.connect(item[1])
		pause_stack.add_child(button)
	pause_panel.hide()

func _toggle_pause() -> void:
	camera.release_mouse()
	paused = not paused
	pause_panel.visible = paused

func _restart_from_menu() -> void:
	_reset()
	paused = false
	pause_panel.hide()

func _open_explorer() -> void:
	camera.release_mouse()
	get_tree().change_scene_to_file("res://scenes/main.tscn")

func _unhandled_input(event: InputEvent) -> void:
	if not paused and not capture_mode and camera.handle_input(event):
		get_viewport().set_input_as_handled()
		return
	if event is InputEventKey and event.pressed and not event.echo:
		if event.keycode == KEY_ESCAPE:
			_toggle_pause()
			return
		if paused: return
		match event.keycode:
			KEY_P:
				if not motion.toggle_doors(): _notice("Detén el bus antes de abrir las puertas")
			KEY_R:
				if not motion.toggle_gear(): _notice("Detén el bus antes de cambiar de marcha")
			KEY_C:
				camera_mode = (camera_mode+1) % 3
				camera.set_mode(camera_mode)
			KEY_BACKSPACE: _reset()
			KEY_F2: _open_explorer()

func _notice(value: String) -> void:
	feedback = value
	feedback_seconds = 3.5

func _physics_process(dt: float) -> void:
	if bus == null or paused or capture_mode: return
	var throttle := 1.0 if Input.is_physical_key_pressed(KEY_W) or Input.is_physical_key_pressed(KEY_UP) else 0.0
	var brake := 1.0 if Input.is_physical_key_pressed(KEY_S) or Input.is_physical_key_pressed(KEY_DOWN) else 0.0
	var steer := 0.0
	if Input.is_physical_key_pressed(KEY_A) or Input.is_physical_key_pressed(KEY_LEFT): steer -= 1.0
	if Input.is_physical_key_pressed(KEY_D) or Input.is_physical_key_pressed(KEY_RIGHT): steer += 1.0
	motion.control(dt,throttle,brake,steer,Input.is_physical_key_pressed(KEY_SPACE))
	motion.advance(dt,collision.resolve)
	if not motion.last_block.is_empty():
		_notice("Límite de articulación · Endereza avanzando" if motion.last_block == "articulation" else "Contacto con obstáculo · Frena y corrige la maniobra")
	if absf(motion.position.x) > 200 or absf(motion.position.y) > 270:
		_reset()
		_notice("Regreso al circuito de práctica")
	service.update(dt,motion)
	bus.sync(motion,dt)

func _process(dt: float) -> void:
	if camera == null or speed_label == null: return
	_update_camera(dt)
	speed_label.text = "%02d km/h" % roundi(absf(motion.speed)*3.6)
	var doors := "ABIERTAS" if motion.doors_fraction > .99 else ("CERRADAS" if motion.doors_fraction < .001 else "EN MOVIMIENTO")
	vehicle_label.text = "%s   ·   Puertas %s\nArticulación %.1f°" % ["D" if motion.gear == 1 else "R",doors,rad_to_deg(motion.articulation())]
	instruction_label.text = service.message
	operation_label.text = "Puertas izquierdas · %s · %s" % ["Parada atendida" if service.served else "Espera de atención: 4 s",["Seguimiento","Cabina","Exterior"][camera_mode]]
	if not paused: feedback_seconds -= dt
	notice_label.text = feedback if feedback_seconds > 0 else ("Cierra las puertas para poder avanzar" if motion.doors_target else ("Rozando el andén · Puedes seguir avanzando" if motion.sliding else ""))
	if capture_mode and capture_step >= 0:
		capture_seconds += dt
		if capture_seconds > 2.5:
			var step := capture_step
			capture_step = -1
			await RenderingServer.frame_post_draw
			var names := ["preview_practica.png","preview_cabina.png","preview_puertas.png"]
			get_viewport().get_texture().get_image().save_png(ProjectSettings.globalize_path("res://../docs/"+names[step]))
			if step == 2:
				print("PRACTICE_CAPTURE_COMPLETE")
				get_tree().quit()
				return
			camera_mode = 1 if step == 0 else 2
			camera.set_mode(camera_mode)
			motion.reset(Vector2(0,-45) if step == 0 else Vector2(0,0))
			if step == 1:
				motion.doors_target = true
				motion.doors_fraction = 1.0
				bus.sync(motion,0)
			bus.sync(motion,0)
			service.update(0,motion)
			_update_camera(1.0)
			capture_seconds = 0
			capture_step = step+1

func _update_camera(dt: float) -> void:
	camera.follow(bus.front,dt,get_world_3d().direct_space_state)

func _notification(what: int) -> void:
	if what == NOTIFICATION_APPLICATION_FOCUS_OUT and camera != null:
		camera.release_mouse()
