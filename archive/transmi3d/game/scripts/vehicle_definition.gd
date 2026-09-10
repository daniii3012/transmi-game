extends RefCounted
## Canonical metric input shared with Blender and the station generator.
const DEFAULT_PATH := "res://data/vehicles/articulado_prototipo.json"
var data: Dictionary
var source_sha256: String
var front: Dictionary
var rear: Dictionary
var wheelbase: float
var trailer_wheelbase: float
var hitch_offset: float
var width: float
var length_m: float
var max_articulation: float
var dynamics: Dictionary

func _init(path := DEFAULT_PATH) -> void:
	data = JSON.parse_string(FileAccess.get_file_as_string(path))
	assert(data.schema_version == 1 and data.modules.size() == 2,"Unsupported vehicle definition")
	source_sha256 = FileAccess.get_sha256(path)
	front = data.modules[0]
	rear = data.modules[1]
	assert(front.id == "front" and rear.id == "rear","Unsupported body topology")
	wheelbase = -float(front.axles[0].z_m)
	trailer_wheelbase = float(rear.axles[0].z_m)
	hitch_offset = data.hitch_offset_m
	width = data.width_m
	length_m = hitch_offset+float(rear.z_max_m)-float(front.z_min_m)
	dynamics = data.dynamics
	max_articulation = deg_to_rad(dynamics.max_articulation_deg)
	assert(wheelbase > 0 and trailer_wheelbase > 0 and width > 0,"Invalid metric dimensions")

func module_size(module: Dictionary) -> Vector3:
	return Vector3(width,data.collision.height_m,float(module.z_max_m)-float(module.z_min_m))

func module_center(module: Dictionary) -> float:
	return (float(module.z_min_m)+float(module.z_max_m))*.5

func straight_doors() -> Array[Dictionary]:
	var result: Array[Dictionary] = []
	for module in [front,rear]:
		for door in module.doors:
			result.append({"id":door.id,"module":module.id,"x_m":-width*.5,"z_m":float(door.z_m)+(hitch_offset if module.id == "rear" else 0.0)})
	return result

func door_count() -> int:
	return front.doors.size()+rear.doors.size()

func vector(value: Array) -> Vector3:
	return Vector3(value[0],value[1],value[2])

func asset_error() -> String:
	var path: String = data.model_path
	var manifest_path := path.get_basename()+".manifest.json"
	if not FileAccess.file_exists(path) or not FileAccess.file_exists(manifest_path):
		return "Falta construir el modelo del vehículo con tools/build_bus.py"
	var manifest = JSON.parse_string(FileAccess.get_file_as_string(manifest_path))
	if not manifest is Dictionary or manifest.get("vehicle_spec_sha256","") != source_sha256:
		return "La ficha del vehículo cambió: regenera su modelo con tools/build_bus.py"
	if manifest.get("model_sha256","") != FileAccess.get_sha256(path):
		return "El modelo del vehículo no coincide con su manifiesto de construcción"
	return ""
