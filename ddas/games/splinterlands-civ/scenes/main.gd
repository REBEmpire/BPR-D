extends Node

# Splinterlands Civilization - Main Game Manager
# Handles game initialization, scene transitions, and core game loop

var game_state = "menu"
var current_scene = null

func _ready():
	print("Splinterlands Civilization v0.1 initializing...")
	load_main_menu()

func load_main_menu():
	game_state = "menu"
	print("Loading main menu...")
	# TODO: Load menu scene when created

func load_game(game_mode: String):
	game_state = "playing"
	print("Loading game: ", game_mode)
	# TODO: Load appropriate game scene based on game_mode
	# Modes: "single_player", "multiplayer", "campaign"

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
