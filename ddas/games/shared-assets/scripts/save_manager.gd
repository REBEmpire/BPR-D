# Save Manager - Handles game save/load for both games
# Uses JSON format for easy sharing and version control

extends Node

var save_path = "user://saves/"
var current_game_id = ""

func _ready():
	# Create saves directory if it doesn't exist
	if not DirAccess.dir_exists_absolute(save_path):
		DirAccess.make_absolute(save_path, 0o755)

func save_game(game_data: Dictionary, filename: String) -> bool:
	var full_path = save_path + filename + ".json"
	var json_string = JSON.stringify(game_data)

	var file = FileAccess.open(full_path, FileAccess.WRITE)
	if file == null:
		print("Error: Could not save game to ", full_path)
		return false

	file.store_string(json_string)
	print("Game saved: ", full_path)
	return true

func load_game(filename: String) -> Dictionary:
	var full_path = save_path + filename + ".json"

	if not FileAccess.file_exists(full_path):
		print("Error: Save file not found: ", full_path)
		return {}

	var file = FileAccess.open(full_path, FileAccess.READ)
	var json_string = file.get_as_text()
	var json = JSON.new()

	if json.parse(json_string) != OK:
		print("Error: Could not parse save file: ", full_path)
		return {}

	print("Game loaded: ", full_path)
	return json.get_data()

func get_save_list() -> Array:
	var saves = []
	var dir = DirAccess.open(save_path)

	if dir:
		dir.list_dir_begin()
		var file_name = dir.get_next()
		while file_name != "":
			if file_name.ends_with(".json"):
				saves.append(file_name.trim_suffix(".json"))
			file_name = dir.get_next()

	return saves

func delete_save(filename: String) -> bool:
	var full_path = save_path + filename + ".json"
	var result = DirAccess.remove_absolute(full_path)

	if result == OK:
		print("Save deleted: ", full_path)
		return true
	else:
		print("Error: Could not delete save: ", full_path)
		return false
