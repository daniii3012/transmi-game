extends RefCounted
## A fixture, not a real commercial route. Door anchors are independently checked.
const Motion = preload("res://scripts/bus_motion.gd")
const STOP := Vector2(0, -45)
const DWELL_SECONDS := 4.0
const PLATFORM_EDGE_X := -1.65
const MIN_GAP_M := 0.025
const MAX_GAP_M := 0.90
const LONGITUDINAL_TOLERANCE_M := 1.20
var dwell := 0.0
var served := false
var completed := false
var message := "Acércate a la estación de práctica"

func longitudinal_error(motion) -> float:
	return (STOP - motion.position).dot(Vector2(0,-1))

func aligned(motion) -> bool:
	if absf(motion.speed) > 0.05 or absf(wrapf(motion.heading,-PI,PI)) > deg_to_rad(6):
		return false
	var anchors: Array[Vector2] = motion.door_positions()
	var targets: Array[Dictionary] = motion.spec.straight_doors()
	for i in anchors.size():
		var target := STOP + Vector2(targets[i].x_m,targets[i].z_m)
		var gap := anchors[i].x - PLATFORM_EDGE_X
		if gap < MIN_GAP_M or gap > MAX_GAP_M or absf(anchors[i].y-target.y) > LONGITUDINAL_TOLERANCE_M:
			return false
	return true

func update(dt: float, motion) -> void:
	if completed:
		message = "Práctica completada · Continúa por el circuito o reinicia"
		return
	if served:
		message = "Atención completada · Cierra las puertas para salir"
		if motion.doors_fraction < 0.001 and not motion.doors_target:
			message = "Puedes continuar · Sal de la estación"
			if (motion.position-STOP).length() > 15:
				completed = true
		return
	if aligned(motion):
		if motion.doors_fraction > 0.99:
			dwell = minf(DWELL_SECONDS, dwell+dt)
			message = "Atendiendo parada · %.1f s" % (DWELL_SECONDS-dwell)
			if dwell >= DWELL_SECONDS: served = true
		else:
			dwell = 0
			message = "Bien alineado · Pulsa P para abrir puertas"
	else:
		dwell = 0
		var error := longitudinal_error(motion)
		if absf(error) < 2.5:
			message = "Detén el bus y alinea sus dos cuerpos junto al andén"
		elif error > 0:
			message = "Punto de parada a %.0f m" % error
		else:
			message = "Sobrepasaste el punto %.1f m · Corrige en reversa" % -error
