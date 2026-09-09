extends SceneTree
const Motion = preload("res://scripts/bus_motion.gd")
const Collision = preload("res://scripts/bus_collision.gd")
const Service = preload("res://scripts/practice_service.gd")
var failures := 0
var checks := 0

func _initialize() -> void:
	_run.call_deferred()

func check(condition: bool, description: String) -> void:
	checks += 1
	if not condition:
		failures += 1
		push_error("FAIL: " + description)
	else: print("PASS: " + description)

func barrier(world: Node3D, p: Vector3, size: Vector3) -> StaticBody3D:
	var body := StaticBody3D.new()
	body.position = p
	body.collision_layer = 1
	var shape := BoxShape3D.new()
	shape.size = size
	var collision := CollisionShape3D.new()
	collision.shape = shape
	body.add_child(collision)
	world.add_child(body)
	return body

func _run() -> void:
	var m = Motion.new()
	m.speed = 5
	m.advance(2)
	check(m.position.distance_to(Vector2(0,-10)) < .001 and absf(m.articulation()) < .00001,"10 m rectos, dos cuerpos alineados")
	m.reset(Vector2.ZERO)
	for i in 600:
		m.control(1.0/60,1,0,0,false)
		m.advance(1.0/60)
	check(m.speed > 10 and m.speed <= 16.67,"aceleración progresiva y límite de velocidad")
	check(not m.toggle_gear() and not m.toggle_doors(),"no cambia marcha ni abre puertas en movimiento")
	for i in 240: m.control(1.0/60,0,1,0,false)
	check(m.speed == 0,"frenada termina sin cambiar de sentido")
	check(m.toggle_gear() and m.gear == -1,"reversa solo detenido")
	m.toggle_doors()
	for i in 120: m.control(1.0/60,1,0,0,false)
	check(m.speed == 0 and m.doors_fraction == 1,"interbloqueo con puertas abiertas")
	m.toggle_doors()
	m.control(.5,1,0,0,false)
	check(m.speed == 0 and m.doors_fraction > 0,"interbloqueo durante cierre")
	for i in 60: m.control(1.0/60,1,0,0,false)
	check(m.speed < 0 and m.doors_fraction == 0,"recupera movimiento tras cerrar")
	m.reset(Vector2.ZERO)
	m.speed = 6
	m.steering = deg_to_rad(25)
	var radius := Motion.WHEELBASE / tan(m.steering)
	for i in 3600: m.advance(1.0/60)
	var expected := Vector2(radius*(1-cos(m.heading)),-radius*sin(m.heading))
	check(m.position.distance_to(expected) < .02,"círculo delantero coincide con radio geométrico")
	var trailer_radius := sqrt(radius*radius+Motion.HITCH_OFFSET**2-Motion.TRAILER_WHEELBASE**2)
	check(absf(m.trailer_axle().distance_to(Vector2(radius,0))-trailer_radius) < .04,"remolque converge a radio interior independiente")
	m.reset(Vector2.ZERO)
	m.gear = -1
	m.steering = deg_to_rad(34)
	for i in 1200:
		m.control(1.0/60,1,0,1,false)
		m.advance(1.0/60)
	check(absf(m.articulation()) <= Motion.MAX_ARTICULATION and absf(m.articulation()) > deg_to_rad(55),"límite de articulación en reversa")
	m.speed = 0
	m.toggle_gear()
	for i in 300:
		m.control(1.0/60,1,0,0,false)
		m.advance(1.0/60)
	check(absf(m.articulation()) < deg_to_rad(35),"puede enderezarse avanzando después del límite")
	var s = Service.new()
	m.reset(Service.STOP)
	check(s.aligned(m),"las cuatro puertas coinciden con anclajes de plataforma")
	m.trailer_heading = deg_to_rad(8)
	check(not s.aligned(m),"rechaza parada con frente alineado y remolque desviado")
	m.reset(Service.STOP+Vector2(0,1.6))
	check(not s.aligned(m),"rechaza sobrepasar tolerancia longitudinal")
	m.reset(Service.STOP)
	m.toggle_doors()
	for i in 360:
		m.control(1.0/60,0,0,0,false)
		s.update(1.0/60,m)
	check(s.served and not s.completed,"atiende parada después de apertura y tiempo de intercambio")
	m.toggle_doors()
	for i in 600:
		m.control(1.0/60,1,0,0,false)
		m.advance(1.0/60)
		s.update(1.0/60,m)
	check(s.completed,"ciclo completo de parada, cierre y salida")
	var world := Node3D.new()
	root.add_child(world)
	var wall := barrier(world,Vector3(0,1.7,-20),Vector3(8,3.4,.05))
	await physics_frame
	await physics_frame
	var collision = Collision.new(world.get_world_3d().direct_space_state)
	m.reset(Vector2.ZERO)
	m.speed = 16.67
	m.advance(2,collision.check)
	check(m.last_block == "front" and m.position.y > -12.56 and m.speed == 0,"barrera de 5 cm detiene el frente incluso con paso largo")
	wall.queue_free()
	await physics_frame
	barrier(world,Vector3(0,1.7,14),Vector3(8,3.4,.05))
	await physics_frame
	await physics_frame
	m.reset(Vector2.ZERO)
	m.speed = -2.22
	m.advance(4,collision.check)
	check(m.last_block == "rear" and m.position.y < 3.43,"colisión del remolque en reversa con frente libre")
	world.queue_free()
	await process_frame
	print("DRIVING_TESTS ",checks-failures,"/",checks," passed")
	quit(1 if failures else 0)
