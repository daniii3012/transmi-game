extends SceneTree
const Scene = preload("res://scenes/mandalay.tscn")
const Motion = preload("res://scripts/bus_motion.gd")
const Service = preload("res://scripts/station_service.gd")
var failures := 0
func _initialize() -> void:
	_run.call_deferred()
func verify(ok: bool, description: String) -> void:
	print("PASS_MANDALAY: " if ok else "FAIL_MANDALAY: ",description)
	if not ok: failures += 1
func _run() -> void:
	var scene = Scene.instantiate()
	root.add_child(scene)
	await physics_frame
	await physics_frame
	scene.paused = true
	verify(scene.world.data.modules.size() == 4 and scene.world.data.stops.size() == 2,"cuatro huellas y dos sentidos de práctica cargados")
	for stop_index in 2:
		scene.stop_index = stop_index
		scene._reset()
		var m = scene.motion
		var service = scene.service
		var direction: String = scene.world.data.stops[stop_index].direction
		var blocked := false
		for i in 2400:
			var remaining: float = service.longitudinal_error(m)
			var target := minf(7.0,sqrt(maxf(0,remaining-.18)*5.0))
			m.control(1.0/60,1.0 if m.speed < target-.12 else 0.0,1.0 if m.speed > target else 0.0,0,false)
			m.advance(1.0/60,scene.collision.resolve)
			if not m.last_block.is_empty():
				blocked = true
				print("BLOCK at ",m.position," remaining=",remaining," body=",m.last_block)
				break
			if remaining < .65 and m.speed < .05: break
		verify(not blocked and service.aligned(m),direction+": aproximación de 75 m y alineación con colisiones reales de la escena")
		m.toggle_doors()
		for i in 360:
			m.control(1.0/60,0,0,0,false)
			service.update(1.0/60,m)
		scene.bus.sync(m,0)
		var visual_open := true
		for door in scene.bus.doors:
			visual_open = visual_open and absf(door.node.position.z-door.base) > .58
		verify(service.served and visual_open,direction+": atención y ocho hojas abiertas")
		m.toggle_doors()
		for i in 100: m.control(1.0/60,0,0,0,false)
		for i in 900:
			m.control(1.0/60,1 if m.speed < 3 else 0,0,0,false)
			m.advance(1.0/60,scene.collision.resolve)
			service.update(1.0/60,m)
			if service.completed or not m.last_block.is_empty(): break
		verify(service.completed and m.last_block.is_empty(),direction+": cierre y salida de 25 m sin bloqueos")
		# Alignment tolerance is invariant to station orientation; every door matters.
		var configured = Service.new(scene.world.data.stops[stop_index])
		m.reset(configured.target+configured.right*.45,configured.heading)
		verify(configured.aligned(m),direction+": margen lateral de 82,5 cm aceptado")
		m.position += configured.right*.15
		verify(not configured.aligned(m),direction+": separación de 97,5 cm rechazada")
		m.reset(configured.target,configured.heading)
		m.trailer_heading += .15
		verify(not configured.aligned(m),direction+": cola torcida impide atender la parada")
		m.reset(configured.target,configured.heading)
		m.doors_fraction = 1
		m.doors_target = true
		configured.update(2,m)
		m.position += configured.forward*3
		configured.update(.1,m)
		m.position -= configured.forward*3
		configured.update(2,m)
		verify(not configured.served,direction+": salir de alineación reinicia la espera")
		configured.update(2,m)
		m.doors_target = false
		m.doors_fraction = 0
		m.position -= configured.forward*30
		configured.update(1,m)
		verify(not configured.completed,direction+": retroceder no completa la salida")
	scene.queue_free()
	await process_frame
	print("MANDALAY_TEST ","PASS" if failures == 0 else "FAIL", " failures=",failures)
	quit(0 if failures == 0 else 1)
