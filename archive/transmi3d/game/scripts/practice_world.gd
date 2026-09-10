extends Node3D
var materials: Dictionary = {}

func material(color: String, roughness := 0.85) -> StandardMaterial3D:
	if materials.has(color): return materials[color]
	var result := StandardMaterial3D.new()
	result.albedo_color = Color(color)
	result.roughness = roughness
	result.metallic_specular = 0.0
	materials[color] = result
	return result

func box(label: String, p: Vector3, size: Vector3, color: String, solid := false) -> MeshInstance3D:
	var mesh := MeshInstance3D.new()
	mesh.name = label
	var cube := BoxMesh.new()
	cube.size = size
	mesh.mesh = cube
	mesh.position = p
	mesh.material_override = material(color)
	add_child(mesh)
	if solid:
		var body := StaticBody3D.new()
		body.collision_layer = 1
		body.collision_mask = 0
		var collision := CollisionShape3D.new()
		var shape := BoxShape3D.new()
		shape.size = size
		collision.shape = shape
		body.add_child(collision)
		mesh.add_child(body)
	return mesh

func text_sign(words: String, p: Vector3, angle := 0.0, size := 80) -> Label3D:
	var label := Label3D.new()
	label.text = words
	label.position = p
	label.rotation.y = angle
	label.font_size = size
	label.pixel_size = 0.01
	label.outline_size = 8
	add_child(label)
	return label

func _ready() -> void:
	box("Terreno", Vector3(35, -.24, 0), Vector3(460, .4, 580), "879877")
	_apply_ground_material()
	_make_road()
	# Station is an original test fixture, not a claim about a Bogotá station.
	box("Plataforma", Vector3(-3.7, .55, -43), Vector3(4.1, 1.1, 32), "9b9e99", true)
	box("Borde_amarillo", Vector3(-1.72, 1.105, -43), Vector3(.15, .015, 32), "dab85e")
	box("Cubierta", Vector3(-3.7, 4.42, -43), Vector3(4.6, .18, 32.6), "6b807b")
	for z in range(-57, -27, 5):
		box("Columna", Vector3(-5.4, 2.74, z), Vector3(.15, 3.28, .15), "74848a", true)
		box("Vidrio_estacion", Vector3(-5.5, 2.53, z+2), Vector3(.055, 2.3, 3.75), "819ba1")
		box("Marco", Vector3(-5.55, 1.55, z+2), Vector3(.12, .08, 4.9), "53636c")
	box("Fascia", Vector3(-1.41, 4.11, -43), Vector3(.12, .44, 31.8), "a7443e")
	text_sign("ESTACIÓN DE PRÁCTICA", Vector3(-1.32, 4.12, -44), PI/2, 58)
	for door in preload("res://scripts/vehicle_definition.gd").new().straight_doors():
		var z: float = -45.0+float(door.z_m)
		box("Acceso", Vector3(-2.3, 1.115, z), Vector3(1.1, .02, 1.3), "cfb451")
	box("Linea_de_parada", Vector3(0, .034, -52.4), Vector3(3.5, .018, .2), "e2ded0")
	box("Senal", Vector3(2.8, 1.6, -52.4), Vector3(.06, 3.2, .06), "59636a", true)
	box("Placa", Vector3(2.8, 2.9, -52.4), Vector3(.9, .65, .08), "a12630")
	text_sign("P", Vector3(2.8, 2.9, -52.34), 0, 52)
	for p in [Vector3(-9, .55, 55), Vector3(9, .55, 55), Vector3(6, .55, 20), Vector3(75, .55, -70)]:
		box("Barrera_de_maniobra", p, Vector3(1.4, 1.1, 3.5), "ded5b4", true)
		box("Banda_roja", p + Vector3(0, .18, 0), Vector3(1.42, .2, 3.52), "af5140")
	# Sparse modular environment supplies scale; these buildings are fictional.
	var rng := RandomNumberGenerator.new()
	rng.seed = 20260909
	for side in [-1,1]:
		for z in range(-180, 210, 22):
			var x: float = -38 if side == -1 else 109
			var height := rng.randf_range(7, 19)
			var width := rng.randf_range(12, 19)
			box("Edificio_contexto", Vector3(x, height/2, z), Vector3(width,height,16), ["b78c70","c6b296","ab8870","a8afa0"][rng.randi_range(0,3)])
			box("Cornisa", Vector3(x, height, z), Vector3(width+.4,.25,16.4), "6b706c")
			for y in range(2, int(height)-1, 3):
				for dz in [-5,0,5]:
					box("Ventana_contexto", Vector3(x-side*(width/2+.02), y, z+dz), Vector3(.04,1.45,2), "577075")
	for z in range(-105, 140, 30):
		box("Poste", Vector3(5.8,4.5,z), Vector3(.11,9,.11), "6c7878")
		box("Luminaria", Vector3(4.8,9,z), Vector3(2.1,.13,.4), "c9c8b6")
		# Clustered crowns give trees an organic silhouette without dense leaf geometry.
		var offsets := [Vector3(-1.4,5.8,0),Vector3(1.3,5.5,.6),Vector3(0,7.2,.2),Vector3(.2,5.6,-1.5),Vector3(.1,5.4,1.6)]
		for i in offsets.size():
			var tree := MeshInstance3D.new()
			var crown := SphereMesh.new()
			crown.radius = 2.35 if i == 2 else 2.1
			crown.height = crown.radius*1.7
			crown.radial_segments = 9
			crown.rings = 5
			tree.mesh = crown
			tree.position = Vector3(31,0,z) + offsets[i]
			tree.rotation.y = rng.randf_range(0,TAU)
			tree.material_override = material(["7c956b","8d9f76","a7af80","718568","92a77d"][i])
			add_child(tree)
		box("Tronco", Vector3(31,2.8,z),Vector3(.42,5.6,.42),"796d58")
	var environment := WorldEnvironment.new()
	var env := Environment.new()
	env.background_mode = Environment.BG_SKY
	var sky := Sky.new()
	var sky_mat := ProceduralSkyMaterial.new()
	sky_mat.sky_top_color = Color("9cbac1")
	sky_mat.sky_horizon_color = Color("e1d8c3")
	sky_mat.ground_horizon_color = Color("c3c4a8")
	sky.sky_material = sky_mat
	env.sky = sky
	env.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
	env.ambient_light_color = Color("c8d4dc")
	env.ambient_light_energy = 0.4
	env.tonemap_mode = Environment.TONE_MAPPER_ACES
	environment.environment = env
	add_child(environment)
	var sun := DirectionalLight3D.new()
	sun.rotation_degrees = Vector3(-42,-28,0)
	sun.light_color = Color("ffe4bc")
	sun.light_energy = 0.60
	sun.shadow_enabled = true
	sun.directional_shadow_max_distance = 140
	add_child(sun)

func _make_road() -> void:
	var points: Array[Vector3] = []
	for i in range(49): points.append(Vector3(0,0,120-i*5))
	for i in range(1,49):
		var a := PI + PI * float(i)/48
		points.append(Vector3(35+35*cos(a),0,-120+35*sin(a)))
	for i in range(1,49): points.append(Vector3(70,0,-120+i*5))
	for i in range(1,49):
		var a := PI * float(i)/48
		points.append(Vector3(35+35*cos(a),0,120+35*sin(a)))
	var surface := SurfaceTool.new()
	surface.begin(Mesh.PRIMITIVE_TRIANGLES)
	for i in range(points.size()-1):
		var a := points[i]
		var b := points[i+1]
		var cross := (b-a).normalized().cross(Vector3.UP) * 4.0
		for vertex in [a-cross,a+cross,b+cross,a-cross,b+cross,b-cross]:
			surface.add_vertex(vertex+Vector3(0,.016,0))
		if i % 2 == 0:
			var line := box("Marca", (a+b)/2+Vector3(0,.025,0), Vector3(.13,.016,(b-a).length()*.55),"c7bd97")
			line.rotation.y = atan2((b-a).x,(b-a).z)
	surface.generate_normals()
	var road := MeshInstance3D.new()
	road.mesh = surface.commit()
	var shader := Shader.new()
	shader.code = """shader_type spatial;
render_mode cull_disabled;
varying vec3 world_pos;
float hash(vec2 p) { return fract(sin(dot(p,vec2(127.1,311.7)))*43758.5453); }
void vertex() { world_pos = (MODEL_MATRIX * vec4(VERTEX,1.0)).xyz; }
void fragment() {
 float grain=hash(floor(world_pos.xz*28.0));
 float patches=hash(floor(world_pos.xz*0.4));
 ALBEDO=vec3(0.27,0.29,0.27)*(0.94+grain*0.04+patches*0.04);
 ROUGHNESS=0.95;
}
"""
	var asphalt := ShaderMaterial.new()
	asphalt.shader = shader
	road.material_override = asphalt
	add_child(road)

func _apply_ground_material() -> void:
	var ground := get_node("Terreno") as MeshInstance3D
	var shader := Shader.new()
	shader.code = """shader_type spatial;
uniform vec4 base_color : source_color = vec4(0.53,0.60,0.47,1.0);
varying vec3 world_pos;
float hash(vec2 p) { return fract(sin(dot(p,vec2(127.1,311.7)))*43758.5453); }
float noise(vec2 p) { vec2 i=floor(p); vec2 f=fract(p); f=f*f*(3.0-2.0*f); return mix(mix(hash(i),hash(i+vec2(1,0)),f.x),mix(hash(i+vec2(0,1)),hash(i+vec2(1,1)),f.x),f.y); }
void vertex() { world_pos=(MODEL_MATRIX*vec4(VERTEX,1.0)).xyz; }
void fragment() { float variation=noise(world_pos.xz*0.12)*0.12+noise(world_pos.xz*1.1)*0.025; ALBEDO=base_color.rgb*(0.94+variation); ROUGHNESS=1.0; SPECULAR=0.0; }
"""
	var surface := ShaderMaterial.new()
	surface.shader = shader
	surface.set_shader_parameter("base_color",Color("899b78"))
	ground.material_override = surface
