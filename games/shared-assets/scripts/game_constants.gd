# Game Constants - Shared across both games
# Defines game balance constants, UI scales, and configuration

extends Node

# Game versions
const SPLINTERLANDS_CIV_VERSION = "0.1.0-alpha"
const SLINGERLANDS_RPG_VERSION = "0.1.0-alpha"

# Display settings
const WINDOW_WIDTH = 1920
const WINDOW_HEIGHT = 1080

# Tile/Grid settings (for both games)
const TILE_SIZE = 64  # pixels
const HEX_TILE_SIZE = 64  # for potential hexagonal grid in Civ game
const GRID_OFFSET_X = 50
const GRID_OFFSET_Y = 50

# Game speeds (Civ game)
const TURN_LENGTH_SECONDS = 10  # adjustable
const ANIMATION_SPEED = 0.3  # multiplier

# Combat settings
const MAX_PARTY_SIZE = 6  # for RPG
const MAX_SUMMONED_UNITS = 8  # for Civ

# Resource types (Civ game)
const RESOURCES = {
	"mana": {"name": "Mana", "icon": "res://assets/icons/mana.png"},
	"gold": {"name": "Gold", "icon": "res://assets/icons/gold.png"},
	"health": {"name": "Health", "icon": "res://assets/icons/health.png"},
	"gems": {"name": "Gems", "icon": "res://assets/icons/gems.png"}
}

# Difficulty levels
const DIFFICULTIES = {
	"easy": 0.8,
	"normal": 1.0,
	"hard": 1.2,
	"insane": 1.5
}

# Color palette (for UI consistency)
const COLORS = {
	"primary": Color.html("3498db"),
	"secondary": Color.html("2ecc71"),
	"danger": Color.html("e74c3c"),
	"warning": Color.html("f39c12"),
	"dark": Color.html("2c3e50"),
	"light": Color.html("ecf0f1")
}
