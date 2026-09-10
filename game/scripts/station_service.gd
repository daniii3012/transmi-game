extends RefCounted
## A configurable local practice stop. Anchors describe the current prototype.
const Motion = preload("res://scripts/bus_motion.gd")
const DWELL_SECONDS := 4.0
const MIN_GAP_M := .025
const MAX_GAP_M := .90
const LONGITUDINAL_TOLERANCE_M := 1.20
var target := Vector2.ZERO
var heading := 0.0
var forward := Vector2(0,-1)
var right := Vector2(1,0)
var door_targets: Array[Vector2] = []
var departure_m := 25.0
var dwell := 0.0
var served := false
var completed := false
var message := "Acércate a Mandalay"

func _init(stop: Dictionary) -> void:
	target = Vector2(stop.position[0],stop.position[1])
	heading = stop.heading
	forward = Motion.forward(heading)
	right = Motion.right(heading)
	departure_m = stop.departure_m
	for p in stop.doors: door_targets.append(Vector2(p[0],p[1]))

func door_positions(motion) -> Array[Vector2]:
	var anchors: Array[Vector2] = []
	for z in [-4.6,-.9]:
		anchors.append(motion.position-Motion.forward(motion.heading)*z-Motion.right(motion.heading)*1.275)
	for z in [2.0,5.9]:
		anchors.append(motion.hinge()-Motion.forward(motion.trailer_heading)*z-Motion.right(motion.trailer_heading)*1.275)
	return anchors

func longitudinal_error(motion) -> float:
	return (target-motion.position).dot(forward)

func aligned(motion) -> bool:
	if absf(motion.speed) > .05 or absf(wrapf(motion.heading-heading,-PI,PI)) > deg_to_rad(6): return false
	var anchors := door_positions(motion)
	if door_targets.size() != anchors.size(): return false
	for i in anchors.size():
		var offset := anchors[i]-door_targets[i]
		var gap := offset.dot(right)
		if gap < MIN_GAP_M or gap > MAX_GAP_M or absf(offset.dot(forward)) > LONGITUDINAL_TOLERANCE_M:
			return false
	return true

func update(dt: float, motion) -> void:
	if completed:
		message = "Práctica completada · Esc para elegir otro sentido"
		return
	if served:
		message = "Atención completada · Cierra las puertas para salir"
		if motion.doors_fraction < .001 and not motion.doors_target:
			var remaining: float = departure_m-(motion.position-target).dot(forward)
			message = "Continúa hacia delante · %.0f m para terminar" % maxf(0,remaining)
			if remaining <= 0:
				completed = true
				message = "Práctica completada · Esc para elegir otro sentido"
		return
	if aligned(motion):
		if motion.doors_fraction > .99:
			dwell = minf(DWELL_SECONDS,dwell+maxf(dt,0))
			message = "Atendiendo Mandalay · %.1f s" % (DWELL_SECONDS-dwell)
			if dwell >= DWELL_SECONDS: served = true
		else:
			dwell = 0
			message = "Bien alineado · P para abrir puertas"
	else:
		dwell = 0
		var remaining := longitudinal_error(motion)
		if absf(remaining) < 2.5: message = "Detén y alinea ambos cuerpos junto al andén"
		elif remaining > 0: message = "Mandalay · Punto de parada a %.0f m" % remaining
		else: message = "Sobrepasaste el punto %.1f m · Corrige en reversa" % -remaining
