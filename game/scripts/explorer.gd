extends Node3D
## Geographic inspection only. No bus, collisions, terrain survey or current works yet.

var camera: Camera3D
var buildings: Array[MeshInstance3D] = []
var stations: Array = []
var metrics: Label
var seconds := 0.0
var captures := 0
var snapshot_mode := false

func material(color: Color) -> StandardMaterial3D:
	var mat := StandardMaterial3D.new()
	mat.albedo_color = color
	mat.roughness = 0.9
	mat.metallic_specular = 0.0
	mat.cull_mode = BaseMaterial3D.CULL_DISABLED
	return mat

func _ready() -> void:
	snapshot_mode = "--capture" in OS.get_cmdline_user_args()
	var data: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://data/pilot.json"))
	stations = data.stations
	var environment := WorldEnvironment.new()
	var env := Environment.new()
	env.background_mode = Environment.BG_COLOR
	env.background_color = Color("b7c7ca")
	env.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
	env.ambient_light_color = Color("d9e4e3")
	env.ambient_light_energy = 0.45
	env.tonemap_mode = Environment.TONE_MAPPER_ACES
	environment.environment = env
	add_child(environment)
	var sun := DirectionalLight3D.new()
	sun.rotation_degrees = Vector3(-48, -35, 0)
	sun.light_color = Color("fff1d8")
	sun.light_energy = 0.65
	sun.shadow_enabled = true
	sun.directional_shadow_max_distance = 2400
	add_child(sun)
	var ground := MeshInstance3D.new()
	var plane := PlaneMesh.new()
	plane.size = Vector2(2200, 1200)
	ground.mesh = plane
	ground.material_override = material(Color("8c9b8b"))
	add_child(ground)
	for group in data.groups:
		var vertices := PackedVector3Array()
		var normals := PackedVector3Array()
		for i in range(0, group.vertices.size(), 3):
			vertices.append(Vector3(group.vertices[i], group.vertices[i+1], group.vertices[i+2]))
			normals.append(Vector3(group.normals[i], group.normals[i+1], group.normals[i+2]))
		if vertices.is_empty():
			continue
		var arrays := []
		arrays.resize(Mesh.ARRAY_MAX)
		arrays[Mesh.ARRAY_VERTEX] = vertices
		arrays[Mesh.ARRAY_NORMAL] = normals
		var mesh := ArrayMesh.new()
		mesh.add_surface_from_arrays(Mesh.PRIMITIVE_TRIANGLES, arrays)
		var instance := MeshInstance3D.new()
		instance.name = group.name
		instance.mesh = mesh
		instance.material_override = material(Color(group.color))
		add_child(instance)
		if str(group.name).begins_with("buildings"):
			buildings.append(instance)
	for station in stations:
		var p: Array = station.position
		var marker := MeshInstance3D.new()
		var cylinder := CylinderMesh.new()
		cylinder.top_radius = 2.0
		cylinder.bottom_radius = 2.0
		cylinder.height = 14
		marker.mesh = cylinder
		marker.material_override = material(Color("f1b93e"))
		marker.position = Vector3(p[0], 7, p[2])
		add_child(marker)
		var label := Label3D.new()
		label.text = station.name
		label.position = Vector3(p[0], 30, p[2])
		label.font_size = 60
		label.pixel_size = 0.1
		label.modulate = Color("fff1c9")
		label.outline_modulate = Color("26343b")
		label.outline_size = 12
		label.billboard = BaseMaterial3D.BILLBOARD_ENABLED
		label.no_depth_test = true
		add_child(label)
	camera = Camera3D.new()
	camera.far = 5000
	camera.near = 0.1
	camera.fov = 60
	add_child(camera)
	camera.current = true
	view_overview()
	build_hud(data.summary)
	print("PILOT_READY triangles=", data.summary.triangle_count, " stations=", stations.size())
	if DisplayServer.get_name() == "headless":
		get_tree().quit()

func build_hud(summary: Dictionary) -> void:
	var layer := CanvasLayer.new()
	add_child(layer)
	var panel := PanelContainer.new()
	panel.position = Vector2(24, 24)
	var style := StyleBoxFlat.new()
	style.bg_color = Color(0.065, 0.105, 0.125, 0.94)
	style.content_margin_left = 20
	style.content_margin_right = 20
	style.content_margin_top = 16
	style.content_margin_bottom = 16
	style.corner_radius_top_left = 12
	style.corner_radius_top_right = 12
	style.corner_radius_bottom_left = 12
	style.corner_radius_bottom_right = 12
	panel.add_theme_stylebox_override("panel", style)
	layer.add_child(panel)
	var stack := VBoxContainer.new()
	stack.add_theme_constant_override("separation", 8)
	panel.add_child(stack)
	var title := Label.new()
	title.text = "BOGOTÁ / AMÉRICAS"
	title.add_theme_font_size_override("font_size", 28)
	title.add_theme_color_override("font_color", Color("f1bf55"))
	stack.add_child(title)
	var subtitle := Label.new()
	subtitle.text = "Marsella · Av. Boyacá · Mandalay\nExploración 3D / fase 0.1"
	subtitle.add_theme_font_size_override("font_size", 18)
	stack.add_child(subtitle)
	var status := Label.new()
	status.text = "Geometría oficial · 1 unidad = 1 metro\nAlturas estimadas · Terreno plano\nEstaciones: marcadores de ubicación\nObras y desvíos: pendientes de modelar"
	status.add_theme_font_size_override("font_size", 15)
	status.add_theme_color_override("font_color", Color("b9c9cc"))
	stack.add_child(status)
	metrics = Label.new()
	metrics.add_theme_font_size_override("font_size", 15)
	stack.add_child(metrics)
	var footer := Label.new()
	footer.position = Vector2(24, 810)
	footer.text = "1 Vista general   2 Mandalay   3 Av. Boyacá   4 Marsella   B Edificios\nWASD / flechas: mover · Q/E: bajar/subir · Shift: rápido · Clic derecho: mirar · Esc: liberar cursor\nDatos: UAECD / IDECA y TRANSMILENIO S.A. · CC BY 4.0 · Instantánea " + str(summary.source_snapshot).substr(0, 8)
	footer.add_theme_font_size_override("font_size", 16)
	footer.add_theme_color_override("font_color", Color("ffffff"))
	footer.add_theme_color_override("font_shadow_color", Color("122124"))
	footer.add_theme_constant_override("shadow_offset_x", 1)
	footer.add_theme_constant_override("shadow_offset_y", 2)
	layer.add_child(footer)

func view_overview() -> void:
	camera.position = Vector3(100, 1100, 1300)
	camera.look_at(Vector3(0, 0, 0), Vector3.UP)

func view_station(index: int) -> void:
	if index >= stations.size():
		return
	var p: Array = stations[index].position
	var target := Vector3(p[0], 4, p[2])
	camera.position = target + Vector3(105, 95, 155)
	camera.look_at(target, Vector3.UP)

func _unhandled_input(event: InputEvent) -> void:
	if event is InputEventMouseButton and event.button_index == MOUSE_BUTTON_RIGHT:
		Input.mouse_mode = Input.MOUSE_MODE_CAPTURED if event.pressed else Input.MOUSE_MODE_VISIBLE
	if event is InputEventMouseMotion and Input.mouse_mode == Input.MOUSE_MODE_CAPTURED:
		camera.rotation.y -= event.relative.x * 0.0025
		camera.rotation.x = clampf(camera.rotation.x - event.relative.y * 0.0025, -1.5, 1.5)
	if event is InputEventKey and event.pressed and not event.echo:
		match event.keycode:
			KEY_1: view_overview()
			KEY_2: view_station(0)
			KEY_3: view_station(1)
			KEY_4: view_station(2)
			KEY_B:
				for mesh in buildings:
					mesh.visible = not mesh.visible
			KEY_ESCAPE: Input.mouse_mode = Input.MOUSE_MODE_VISIBLE

func _process(delta: float) -> void:
	if camera == null:
		return
	var direction := Vector3.ZERO
	if Input.is_physical_key_pressed(KEY_W) or Input.is_physical_key_pressed(KEY_UP): direction.z -= 1
	if Input.is_physical_key_pressed(KEY_S) or Input.is_physical_key_pressed(KEY_DOWN): direction.z += 1
	if Input.is_physical_key_pressed(KEY_A) or Input.is_physical_key_pressed(KEY_LEFT): direction.x -= 1
	if Input.is_physical_key_pressed(KEY_D) or Input.is_physical_key_pressed(KEY_RIGHT): direction.x += 1
	if Input.is_physical_key_pressed(KEY_E): direction.y += 1
	if Input.is_physical_key_pressed(KEY_Q): direction.y -= 1
	var speed := 180.0 if Input.is_physical_key_pressed(KEY_SHIFT) else 40.0
	if direction.length() > 0:
		camera.position += (camera.basis * direction.normalized()) * speed * delta
	camera.position.y = clampf(camera.position.y, 1.8, 1800)
	camera.position.x = clampf(camera.position.x, -1200, 1200)
	camera.position.z = clampf(camera.position.z, -900, 1200)
	seconds += delta
	metrics.text = "Altura de cámara: %.0f m   ·   %d FPS" % [camera.position.y, Engine.get_frames_per_second()]
	if snapshot_mode and seconds > 3 and captures == 0:
		captures = 1
		await RenderingServer.frame_post_draw
		get_viewport().get_texture().get_image().save_png(ProjectSettings.globalize_path("res://../docs/preview_general.png"))
		view_station(1)
	if snapshot_mode and seconds > 6 and captures == 1:
		captures = 2
		await RenderingServer.frame_post_draw
		get_viewport().get_texture().get_image().save_png(ProjectSettings.globalize_path("res://../docs/preview_boyaca.png"))
		print("CAPTURE_COMPLETE")
		get_tree().quit()
