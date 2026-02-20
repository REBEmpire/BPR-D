extends Node

# Slingerlands RPG - Main Game Manager
# Handles game initialization, scene transitions, and core game loop

var game_state = "menu"
var current_scene = null

func _ready():
	print("Slingerlands RPG v0.1 initializing...")
	load_main_menu()

func load_main_menu():
	game_state = "menu"
	print("Loading main menu...")
	get_tree().change_scene_to_file("res://scenes/menu.tscn")

func load_game(dungeon_id: String = ""):
	game_state = "playing"
	print("Loading game - Dungeon: ", dungeon_id if dungeon_id else "Random")
	# TODO: Load dungeon/overworld scene based on dungeon_id

func load_character_creation():
	game_state = "character_creation"
	print("Loading character creation...")
	# TODO: Load character creation scene

func _process(_delta):
	# Main game loop - will be expanded
	pass

func _input(event):
	if event is InputEventKey and event.pressed:
		if event.keycode == KEY_ESCAPE:
			if game_state == "menu":
				get_tree().quit()
			else:
				return_to_menu()

func return_to_menu():
	game_state = "menu"
	load_main_menu()
