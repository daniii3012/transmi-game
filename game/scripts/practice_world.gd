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
	box("Terreno", Vector3(35, -.24, 0), Vector3(460, .4, 580), "727f61")
	_make_road()
	# Station is an original test fixture, not a claim about a Bogotá station.
	box("Plataforma", Vector3(-3.7, .55, -43), Vector3(4.1, 1.1, 32), "9b9e99", true)
	box("Borde_amarillo", Vector3(-1.72, 1.105, -43), Vector3(.15, .015, 32), "dab85e")
	box("Cubierta", Vector3(-3.7, 4.42, -43), Vector3(4.6, .18, 32.6), "566c73")
	for z in range(-57, -27, 5):
		box("Columna", Vector3(-5.4, 2.74, z), Vector3(.15, 3.28, .15), "74848a", true)
		box("Vidrio_estacion", Vector3(-5.5, 2.53, z+2), Vector3(.055, 2.3, 3.75), "819ba1")
		box("Marco", Vector3(-5.55, 1.55, z+2), Vector3(.12, .08, 4.9), "53636c")
	box("Fascia", Vector3(-1.41, 4.11, -43), Vector3(.12, .44, 31.8), "b13231")
	text_sign("ESTACIÓN DE PRÁCTICA", Vector3(-1.32, 4.12, -44), PI/2, 58)
	for z in [-49.6, -45.9, -40.3, -36.4]:
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
			box("Edificio_contexto", Vector3(x, height/2, z), Vector3(width,height,16), ["a57a62","b49c80","997561","b2ada0"][rng.randi_range(0,3)])
			box("Cornisa", Vector3(x, height, z), Vector3(width+.4,.25,16.4), "6b706c")
			for y in range(2, int(height)-1, 3):
				for dz in [-5,0,5]:
					box("Ventana_contexto", Vector3(x-side*(width/2+.02), y, z+dz), Vector3(.04,1.45,2), "435c67")
	for z in range(-105, 140, 30):
		box("Poste", Vector3(5.8,4.5,z), Vector3(.11,9,.11), "6c7878")
		box("Luminaria", Vector3(4.8,9,z), Vector3(2.1,.13,.4), "c9c8b6")
		var tree := MeshInstance3D.new()
		var crown := SphereMesh.new()
		crown.radius = 3.6
		crown.height = 7.2
		tree.mesh = crown
		tree.position = Vector3(31,5,z)
		tree.material_override = material("607a59")
		add_child(tree)
		box("Tronco", Vector3(31,1.8,z),Vector3(.5,3.6,.5),"716856")
	var environment := WorldEnvironment.new()
	var env := Environment.new()
	env.background_mode = Environment.BG_SKY
	var sky := Sky.new()
	var sky_mat := ProceduralSkyMaterial.new()
	sky_mat.sky_top_color = Color("6390ad")
	sky_mat.sky_horizon_color = Color("ccd3cb")
	sky_mat.ground_horizon_color = Color("bdc3b7")
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
	sun.light_color = Color("fff0d8")
	sun.light_energy = 0.65
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
 float grain=hash(floor(world_pos.xz*95.0));
 float patches=hash(floor(world_pos.xz*0.4));
 ALBEDO=vec3(0.17,0.18,0.18)*(0.88+grain*0.20+patches*0.11);
 ROUGHNESS=0.95;
}
"""
	var asphalt := ShaderMaterial.new()
	asphalt.shader = shader
	road.material_override = asphalt
	add_child(road)
