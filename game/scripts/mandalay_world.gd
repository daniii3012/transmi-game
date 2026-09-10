extends "res://scripts/practice_world.gd"
## Cached geographic footprints plus explicitly provisional vertical architecture.
var data: Dictionary
var active_stop := 0
var guide: MeshInstance3D

func point(p: Array, y := 0.0) -> Vector3:
	return Vector3(p[0],y,p[1])

func beam(label_text: String, a: Vector3, b: Vector3, width: float, height: float, color: String, solid := false) -> MeshInstance3D:
	var direction := b-a
	var result := box(label_text,(a+b)*.5,Vector3(width,height,direction.length()),color,solid)
	if direction.length() > .001: result.look_at(b,Vector3.UP)
	return result

func _ready() -> void:
	data = JSON.parse_string(FileAccess.get_file_as_string("res://data/mandalay.json"))
	box("Terreno",Vector3(0,-.24,0),Vector3(245,.4,450),"879877")
	_apply_ground_material()
	for group in data.groups:
		var vertices := PackedVector3Array()
		var normals := PackedVector3Array()
		for i in range(0,group.vertices.size(),3):
			vertices.append(Vector3(group.vertices[i],group.vertices[i+1],group.vertices[i+2]))
			normals.append(Vector3(group.normals[i],group.normals[i+1],group.normals[i+2]))
		var arrays := []
		arrays.resize(Mesh.ARRAY_MAX)
		arrays[Mesh.ARRAY_VERTEX] = vertices
		arrays[Mesh.ARRAY_NORMAL] = normals
		var mesh := ArrayMesh.new()
		mesh.add_surface_from_arrays(Mesh.PRIMITIVE_TRIANGLES,arrays)
		var instance := MeshInstance3D.new()
		instance.name = group.name
		instance.mesh = mesh
		instance.material_override = material(group.color)
		instance.material_override.cull_mode = BaseMaterial3D.CULL_DISABLED
		add_child(instance)
		if group.collision or str(group.name).begins_with("Cubierta"):
			var body := StaticBody3D.new()
			body.collision_layer = 1
			body.collision_mask = 0
			var shape_node := CollisionShape3D.new()
			shape_node.shape = mesh.create_trimesh_shape()
			body.add_child(shape_node)
			instance.add_child(body)
	for module in data.modules: _station_module(module)
	_make_bridge()
	_decorate_buildings()
	for p in data.trees: _tree(point(p),false)
	# The interior garden is authored, not an inventory of real trees or furniture.
	for z in [-28,38]:
		box("Jardin_central",Vector3(1,1.16,z),Vector3(7,.12,15),"819874")
		_tree(Vector3(1,1.25,z),true)
	for z in [-145,-90,0,90,145]:
		for x in [-23.8,25.5]:
			box("Poste",Vector3(x,4.7,z),Vector3(.15,9.4,.15),"6e7b79")
			box("Luminaria",Vector3(x-1,9.4,z),Vector3(2.5,.17,.65),"d7d3b3")
	for z in [-177,177]:
		for x in [-15,21]:
			var angle := PI if z > 0 else 0.0
			text_sign("FIN DE MUESTRA",Vector3(x,4,z),angle,40)
	_make_light()

func _station_module(module: Dictionary) -> void:
	var a := point(module.edge[0])
	var b := point(module.edge[1])
	var f := Vector3(module.forward[0],0,module.forward[1])
	var r := Vector3(module.right[0],0,module.right[1])
	var length: float = module.length_m
	beam("Borde_anden",a+Vector3.UP*1.118-r*.09,b+Vector3.UP*1.118-r*.09,.16,.025,"ddc278")
	beam("Fascia_Mandalay",a+Vector3.UP*4.09,b+Vector3.UP*4.09,.14,.40,"b45148")
	var sign_label := text_sign("Mandalay",(a+b)*.5+Vector3.UP*4.08+r*.09,0,57)
	# Label faces outward, towards the corresponding BRT carriageway.
	sign_label.look_at(sign_label.position+r,Vector3.UP)
	sign_label.rotate_y(PI)
	# Small repeated panes, with usable gaps exactly at the practice anchors.
	var step := .8
	for i in int(length/step):
		var p := a+f*(float(i)+.5)*step
		var is_gate := false
		for door in module.doors:
			if absf((p-point(door)).dot(f)) < 2.35: is_gate = true
		if not is_gate:
			beam("Panel_vidrio",p-f*.38+Vector3.UP*2.63-r*.12,p+f*.38+Vector3.UP*2.63-r*.12,.07,2.25,"8aa3a2")
			beam("Zocalo",p-f*.39+Vector3.UP*1.38-r*.12,p+f*.39+Vector3.UP*1.38-r*.12,.09,.35,"9faeaa")
	for i in range(1,int(length/4)):
		var p := a+f*i*4-r*.4
		var is_gate := false
		for door in module.doors:
			if absf((p-point(door)).dot(f)) < 2.06: is_gate = true
		if not is_gate: box("Columna",p+Vector3.UP*2.73,Vector3(.13,3.26,.13),"607572")
	for door in module.doors:
		var p := point(door,1.125)
		beam("Umbral",p-f*.75-r*.5,p+f*.75-r*.5,1.0,.025,"d8be6c")
	# Rear edge is schematic: preserve the outline of the platform in the floor mesh.
	var back_a := a-r*2.8
	var back_b := b-r*2.8
	beam("Pasamanos_interior",back_a+Vector3.UP*2.15,back_b+Vector3.UP*2.15,.06,.06,"748980")

func _make_bridge() -> void:
	# Footprint direction follows the inspected 2021 ortho; elevations are design estimates.
	# No ramps or pedestrian navigation enabled in the planar bus prototype.
	var north := Vector3(-47,6.3,-63)
	var center := Vector3(3,6.3,-64)
	var south := Vector3(61,6.3,-35)
	for pair in [[north,center],[center,south]]:
		beam("Puente_peatonal",pair[0],pair[1],3.0,.42,"bfc1af",true)
		var f: Vector3 = (pair[1]-pair[0]).normalized()
		var r := f.cross(Vector3.UP)
		for side in [-1,1]:
			beam("Baranda_puente",pair[0]+r*1.45*side+Vector3.UP*.8,pair[1]+r*1.45*side+Vector3.UP*.8,.08,.85,"99aaa1")
	for p in [north,center,south]:
		box("Apoyo_puente",Vector3(p.x,3.12,p.z),Vector3(.8,6.24,1.5),"abae9e",true)
	# Simplified access inclines terminate inside sidewalk/median space.
	for pair in [[north,Vector3(-47,.6,-106)],[center,Vector3(3,1.4,-111)],[south,Vector3(61,.6,12)]]:
		beam("Acceso_provisional",pair[0],pair[1],2.5,.24,"b3b6a5")
		var f: Vector3 = (pair[1]-pair[0]).normalized()
		var r := f.cross(Vector3.UP).normalized()
		for side in [-1,1]:
			beam("Pasamanos_acceso",pair[0]+r*1.2*side+Vector3.UP*.8,pair[1]+r*1.2*side+Vector3.UP*.8,.06,.8,"9fac9d")

func _decorate_buildings() -> void:
	for building in data.buildings:
		var coords: Array = building.outline
		var height: float = building.height_m
		for i in coords.size():
			var a := point(coords[i])
			var b := point(coords[(i+1)%coords.size()])
			var length := a.distance_to(b)
			if length < 3 or length > 80: continue
			beam("Cornisa",a+Vector3.UP*(height+.15),b+Vector3.UP*(height+.15),.24,.23,"777b70")
			var midpoint := (a+b)*.5
			# Decoration is concentrated on facades nearest the avenue.
			if absf(midpoint.x) > 80: continue
			var f := (b-a).normalized()
			for y in range(2,mini(int(height),20),3):
				for j in range(1,int(length/3)):
					var p := a+f*j*3+Vector3.UP*y
					beam("Ventana",p-f*.64,p+f*.64,.065,1.25,"647e80")

func _tree(p: Vector3, small: bool) -> void:
	var size := .65 if small else 1.0
	box("Tronco",p+Vector3.UP*2.4*size,Vector3(.34,4.8,.34)*size,"897864")
	for i in 4:
		var crown := MeshInstance3D.new()
		var sphere := SphereMesh.new()
		sphere.radius = 2.25*size
		sphere.height = 3.6*size
		sphere.radial_segments = 9
		sphere.rings = 5
		crown.mesh = sphere
		crown.material_override = material(["81976d","93a27a","abb383","78916d"][i])
		crown.position = p+Vector3(sin(i*2)*1.3,5.4+(1.3 if i == 0 else 0),cos(i*2)*1.3)*size
		add_child(crown)

func set_stop(index: int) -> void:
	active_stop = index
	if guide != null: guide.queue_free()
	var stop: Dictionary = data.stops[index]
	var p := point(stop.position,.058)
	var r := Vector3(stop.right[0],0,stop.right[1])
	var f := Vector3(stop.forward[0],0,stop.forward[1])
	guide = beam("Objetivo_practica",p-r*1.24+f*7.5,p+r*1.24+f*7.5,.16,.02,"e1c77b")

func _make_light() -> void:
	var world_environment := WorldEnvironment.new()
	var env := Environment.new()
	env.background_mode = Environment.BG_SKY
	var sky := Sky.new()
	var sky_material := ProceduralSkyMaterial.new()
	sky_material.sky_top_color = Color("9cbac1")
	sky_material.sky_horizon_color = Color("e1d8c3")
	sky_material.ground_horizon_color = Color("c3c4a8")
	sky_material.ground_bottom_color = Color("8d9f97")
	sky.sky_material = sky_material
	env.sky = sky
	env.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
	env.ambient_light_color = Color("ccd5d4")
	env.ambient_light_energy = .40
	env.tonemap_mode = Environment.TONE_MAPPER_ACES
	world_environment.environment = env
	add_child(world_environment)
	var sun := DirectionalLight3D.new()
	sun.rotation_degrees = Vector3(-46,-28,0)
	sun.light_color = Color("ffe7c5")
	sun.light_energy = .60
	sun.shadow_enabled = true
	sun.directional_shadow_max_distance = 220
	add_child(sun)
