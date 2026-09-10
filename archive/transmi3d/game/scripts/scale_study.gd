extends Node3D
## Layout comparison only. Source axes are not surveyed driving lanes.
const Visual = preload("res://scripts/bus_visual.gd")
const Motion = preload("res://scripts/bus_motion.gd")
var data: Dictionary
var camera: Camera3D
var palette: Dictionary = {}
var focus := Vector3(790,0,240)
var yaw := 0.0
var pitch := 0.94
var view_size := 1820.0
var dragging := false
var capture_mode := false
var capture_elapsed := 0.0
var capture_step := 0
var bus_instances: Array = []
var readout: Label
var map_labels: Array[Label3D] = []

func mat(color: String) -> StandardMaterial3D:
	if not palette.has(color):
		var result := StandardMaterial3D.new()
		result.albedo_color = Color(color)
		result.roughness = .94
		result.metallic_specular = .05
		result.cull_mode = BaseMaterial3D.CULL_DISABLED
		palette[color] = result
	return palette[color]

func block(label_text: String, p: Vector3, size: Vector3, color: String, angle := 0.0) -> MeshInstance3D:
	var result := MeshInstance3D.new()
	var mesh := BoxMesh.new()
	mesh.size = size
	result.name = label_text
	result.mesh = mesh
	result.material_override = mat(color)
	result.position = p
	result.rotation.y = angle
	add_child(result)
	return result

func world_point(p: Array, row: int, height := 0.0) -> Vector3:
	return Vector3(p[0],height,p[1]+row*370.0)

func sign_text(words: String, p: Vector3, pixel := .6) -> void:
	var label := Label3D.new()
	label.text = words
	label.font_size = 44
	label.pixel_size = pixel
	label.position = p
	label.modulate = Color("31473b")
	label.outline_modulate = Color("e3e8d3")
	label.outline_size = 5
	label.billboard = BaseMaterial3D.BILLBOARD_ENABLED
	label.no_depth_test = true
	add_child(label)
	map_labels.append(label)

func pose_at(variant: Dictionary, game_m: float) -> Dictionary:
	var samples: Array = variant.samples
	var left := 0
	var right := samples.size()-1
	while left+1 < right:
		var mid: int = (left+right)/2
		if float(samples[mid].game_m) < game_m: left = mid
		else: right = mid
	var a: Dictionary = samples[left]
	var b: Dictionary = samples[right]
	var t := clampf((game_m-float(a.game_m))/(float(b.game_m)-float(a.game_m)),0,1)
	var p := Vector2(a.position[0],a.position[1]).lerp(Vector2(b.position[0],b.position[1]),t)
	return {"position":[p.x,p.y],"tangent":a.tangent}

func ribbon(samples: Array, row: int, width: float, height: float, color: String) -> void:
	var surface := SurfaceTool.new()
	surface.begin(Mesh.PRIMITIVE_TRIANGLES)
	for i in samples.size()-1:
		var a: Dictionary = samples[i]
		var b: Dictionary = samples[i+1]
		var pa := world_point(a.position,row,height)
		var pb := world_point(b.position,row,height)
		var normal_a := Vector3(-a.tangent[1],0,a.tangent[0])*width*.5
		var normal_b := Vector3(-b.tangent[1],0,b.tangent[0])*width*.5
		for p in [pa-normal_a,pb-normal_b,pb+normal_b,pa-normal_a,pb+normal_b,pa+normal_a]:
			surface.set_normal(Vector3.UP)
			surface.add_vertex(p)
	var instance := MeshInstance3D.new()
	instance.mesh = surface.commit()
	var surface_material := mat(color).duplicate() as StandardMaterial3D
	surface_material.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	instance.material_override = surface_material
	add_child(instance)

func _ready() -> void:
	data = JSON.parse_string(FileAccess.get_file_as_string("res://data/scale_study.json"))
	capture_mode = "--capture-scale-study" in OS.get_cmdline_user_args()
	var environment := WorldEnvironment.new()
	var env := Environment.new()
	env.background_mode = Environment.BG_COLOR
	env.background_color = Color("dce2d3")
	env.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
	env.ambient_light_color = Color("dce4db")
	env.ambient_light_energy = .35
	env.tonemap_mode = Environment.TONE_MAPPER_ACES
	environment.environment = env
	add_child(environment)
	var sun := DirectionalLight3D.new()
	sun.rotation_degrees = Vector3(-54,-32,0)
	sun.light_color = Color("ffe4bd")
	sun.light_energy = .55
	sun.shadow_enabled = true
	sun.directional_shadow_max_distance = 4200
	add_child(sun)
	for row in data.variants.size(): _build_row(data.variants[row],row)
	camera = Camera3D.new()
	camera.projection = Camera3D.PROJECTION_ORTHOGONAL
	camera.keep_aspect = Camera3D.KEEP_WIDTH
	camera.far = 7000
	add_child(camera)
	camera.current = true
	_build_ui()
	set_view(0)
	print("SCALE_STUDY_READY variants=2 stations=3 source_m=%.3f condensed_m=%.3f buses=2" % [data.metrics.source_axis_m,data.metrics.condensed_axis_game_m])
	if DisplayServer.get_name() == "headless" and not "--keep-running" in OS.get_cmdline_user_args(): get_tree().quit()

func _build_row(variant: Dictionary, row: int) -> void:
	ribbon(variant.samples,row,162.0,-.07,"bccaaa" if row == 0 else "b5c8a8")
	for span in variant.protected_spans:
		var part: Array = [pose_at(variant,span.from_game_m)]
		for s in variant.samples:
			if s.game_m > span.from_game_m and s.game_m < span.to_game_m: part.append(s)
		part.append(pose_at(variant,span.to_game_m))
		ribbon(part,row,29,.015,"d4bb80")
	ribbon(variant.samples,row,float(data.assumptions.illustrative_road_width_game_m),.055,"505b54")
	for distance in range(4,int(variant.length_game_m),16):
		var pose := pose_at(variant,distance)
		var p := world_point(pose.position,row,.07)
		var angle := -atan2(float(pose.tangent[1]),float(pose.tangent[0]))
		block("Marca",p,Vector3(4,.018,.14),"e6d29e",angle)
	var colors := ["ac7e61","bea68b","baa087","c2b79f"]
	for i in variant.context.size():
		var entry: Dictionary = variant.context[i]
		var p := world_point(entry.position,row)
		var tangent := Vector3(entry.tangent[0],0,entry.tangent[1])
		var normal := Vector3(-tangent.z,0,tangent.x)
		var side: float = entry.side
		p += normal*side*48
		var height := 9.0+float(i%4)*3.0
		var length := 18.0+float(i%3)*3.0
		var angle := -atan2(tangent.z,tangent.x)
		block("Contexto_ilustrativo",p+Vector3(0,height/2,0),Vector3(length,height,17),colors[i%4],angle)
		block("Cubierta",p+Vector3(0,height+.14,0),Vector3(length+.5,.28,17.5),"777c6e",angle)
		for y in range(2,int(height)-1,3):
			for dx in [-5,0,5]:
				block("Ventana",p+tangent*dx-normal*side*8.55+Vector3(0,y,0),Vector3(2.1,1.45,.13),"627b78",angle)
		var tree_p := p+tangent*16-normal*side*21
		block("Tronco",tree_p+Vector3(0,2.2,0),Vector3(.4,4.4,.4),"81715b")
		for j in 3:
			var tree := MeshInstance3D.new()
			var crown := SphereMesh.new()
			crown.radius = 2.0
			crown.height = 3.5
			crown.radial_segments = 8
			crown.rings = 4
			tree.mesh = crown
			tree.position = tree_p+Vector3((j-1)*1.15,4.4+(1 if j == 1 else 0),.4*(j%2))
			tree.material_override = mat(["81946c","93a478","7b906b"][j])
			add_child(tree)
	for i in variant.stations.size():
		var station: Dictionary = variant.stations[i]
		var p := world_point(station.position,row)
		block("Marcador_estacion",p+Vector3(0,5,0),Vector3(2.4,10,2.4),"ab4940")
		sign_text(["Mandalay","Boyacá*","Marsella"][i],p+Vector3(0,22,-26))
	var first: Dictionary = variant.stations[0]
	var bus_pose := pose_at(variant,float(first.game_m)+28)
	var motion = Motion.new()
	var bus = Visual.new(motion.spec)
	add_child(bus)
	if not bus.ready_ok:
		get_tree().quit(1)
		return
	var bus_p := world_point(bus_pose.position,row)
	motion.reset(Vector2(bus_p.x,bus_p.z),atan2(float(bus_pose.tangent[0]),-float(bus_pose.tangent[1])))
	bus.sync(motion,0)
	bus_instances.append(bus)
	var end_pose: Dictionary = variant.samples[-1]
	block("Fin_de_estudio",world_point(end_pose.position,row,4),Vector3(2,8,14),"a55141")
	sign_text(("01 / FUENTE" if row == 0 else "02 / CONDENSADA")+"   ·   %.0f m" % variant.length_game_m,Vector3(280,5,row*370-84),.75)

func ui_label(parent: Node, words: String, size: int, color := "e6e7d8") -> Label:
	var label := Label.new()
	label.text = words
	label.add_theme_font_size_override("font_size",size)
	label.add_theme_color_override("font_color",Color(color))
	parent.add_child(label)
	return label

func _build_ui() -> void:
	var layer := CanvasLayer.new()
	add_child(layer)
	var panel := PanelContainer.new()
	panel.position = Vector2(24,20)
	panel.custom_minimum_size = Vector2(1392,140)
	var style := StyleBoxFlat.new()
	style.bg_color = Color("2e4136")
	style.corner_radius_top_left = 12
	style.corner_radius_top_right = 12
	style.corner_radius_bottom_left = 12
	style.corner_radius_bottom_right = 12
	style.content_margin_left = 22
	style.content_margin_top = 13
	style.content_margin_bottom = 13
	style.content_margin_right = 22
	panel.add_theme_stylebox_override("panel",style)
	layer.add_child(panel)
	var stack := VBoxContainer.new()
	panel.add_child(stack)
	ui_label(stack,"AMÉRICAS, MÁS CERCA",28,"ecd098")
	ui_label(stack,"Mandalay — Av. Américas / Av. Boyacá — Marsella   ·   Comparación de escala",18)
	readout = ui_label(stack,"",18)
	ui_label(stack,"Bandas arena: espacio reservado  ·  Bus de 18 m en ambas versiones  ·  Entorno ilustrativo",16,"bbcbb7")
	var footer := PanelContainer.new()
	footer.position = Vector2(24,765)
	footer.custom_minimum_size = Vector2(1392,112)
	footer.add_theme_stylebox_override("panel",style)
	layer.add_child(footer)
	var bottom := VBoxContainer.new()
	footer.add_child(bottom)
	ui_label(bottom,"1 Comparación   2 Mandalay / fuente   3 Mandalay / condensada   ·   Clic derecho Orbitar   Rueda Zoom",17)
	ui_label(bottom,"F2 Conducir en pista   F3 Mapa geográfico   ·   Estudio de disposición; todavía no es un recorrido conducible",16)
	ui_label(bottom,"Eje oficial + 180 m por extremo · *Boyacá: reserva provisional, puente pendiente · UAECD/IDECA y TransMilenio, CC BY 4.0",14,"bbcbb7")

func set_view(index: int) -> void:
	yaw = 0
	if index == 0:
		focus = Vector3(790,0,230)
		pitch = 1.02
		view_size = 1820
		readout.text = "Fuente: %.0f m   →   Condensada: %.0f m   ·   Reducción del eje: %.1f %%" % [data.metrics.source_axis_m,data.metrics.condensed_axis_game_m,data.metrics.reduction_percent]
	else:
		var row := index-1
		var station: Dictionary = data.variants[row].stations[0]
		focus = world_point(station.position,row)+Vector3(14,0,0)
		pitch = .57
		yaw = -.4
		view_size = 115
		readout.text = ("Fuente" if row == 0 else "Condensada")+" · Mismo bus y mismo espacio reservado alrededor de Mandalay"
	_update_camera()

func _update_camera() -> void:
	camera.size = view_size
	for label in map_labels: label.visible = view_size > 400
	camera.position = focus+Vector3(sin(yaw)*cos(pitch),sin(pitch),cos(yaw)*cos(pitch))*maxf(250,view_size*1.5)
	camera.look_at(focus,Vector3.UP)

func _unhandled_input(event: InputEvent) -> void:
	if event is InputEventMouseButton:
		if event.button_index == MOUSE_BUTTON_RIGHT:
			dragging = event.pressed
			Input.mouse_mode = Input.MOUSE_MODE_CAPTURED if dragging else Input.MOUSE_MODE_VISIBLE
		elif event.pressed and event.button_index in [MOUSE_BUTTON_WHEEL_UP,MOUSE_BUTTON_WHEEL_DOWN]:
			view_size = clampf(view_size*(.88 if event.button_index == MOUSE_BUTTON_WHEEL_UP else 1.14),45,2400)
			_update_camera()
	if event is InputEventMouseMotion and dragging:
		yaw -= event.relative.x*.004
		pitch = clampf(pitch+event.relative.y*.003,.18,1.48)
		_update_camera()
	if event is InputEventKey and event.pressed and not event.echo:
		match event.keycode:
			KEY_1: set_view(0)
			KEY_2: set_view(1)
			KEY_3: set_view(2)
			KEY_F2:
				Input.mouse_mode = Input.MOUSE_MODE_VISIBLE
				get_tree().change_scene_to_file("res://scenes/practice.tscn")
			KEY_F3:
				Input.mouse_mode = Input.MOUSE_MODE_VISIBLE
				get_tree().change_scene_to_file("res://scenes/main.tscn")
			KEY_ESCAPE:
				dragging = false
				Input.mouse_mode = Input.MOUSE_MODE_VISIBLE

func _notification(what: int) -> void:
	if what == NOTIFICATION_APPLICATION_FOCUS_OUT:
		dragging = false
		Input.mouse_mode = Input.MOUSE_MODE_VISIBLE

func _process(dt: float) -> void:
	if not capture_mode or capture_step < 0: return
	capture_elapsed += dt
	if capture_elapsed < 2.0: return
	var step := capture_step
	capture_step = -1
	await RenderingServer.frame_post_draw
	var filenames := ["preview_escala.png","preview_escala_mandalay.png"]
	get_viewport().get_texture().get_image().save_png(ProjectSettings.globalize_path("res://../docs/"+filenames[step]))
	if step == 1:
		print("SCALE_STUDY_CAPTURE_COMPLETE")
		get_tree().quit()
	else:
		set_view(2)
		capture_elapsed = 0
		capture_step = 1
