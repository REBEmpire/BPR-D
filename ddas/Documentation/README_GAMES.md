# DDAS Games - Development Guide

Quick-start guide for developing the two game prototypes.

## Prerequisites

- **Godot 4.x** (free, download from [godotengine.org](https://godotengine.org))
- **Git** (for version control)
- **Python 3.8+** (for tools and automation)
- **Optional**: VSCode with Godot Tools extension

## Game 1: Splinterlands Civilization

**Location**: `games/splinterlands-civ/`

### Overview
4X strategy game (Civilization-style) set in the Splinterlands universe. Build civilizations, manage resources, and engage in turn-based tactical combat.

### Core Systems to Implement

#### Phase 1: Foundation (Week 1-2)
- [ ] Map generation (procedural or tile-based)
- [ ] Grid/hexagon system
- [ ] Basic camera and pan/zoom controls
- [ ] UI framework (buttons, menus, panels)
- [ ] Main menu scene

#### Phase 2: Gameplay (Week 3-4)
- [ ] Turn system implementation
- [ ] Resource management (mana, gold, health, gems)
- [ ] Unit/civilization placement
- [ ] Basic combat system (turn-based)
- [ ] Victory/loss conditions

#### Phase 3: Polish & Multiplayer (Week 5+)
- [ ] Networking (Nakama or custom backend)
- [ ] Save/load system
- [ ] Advanced combat mechanics
- [ ] AI opponents
- [ ] UI polish and feedback

### Starting Development

1. Open Godot 4.x
2. File → Open Project → Select `games/splinterlands-civ/`
3. The project structure is ready:
   ```
   splinterlands-civ/
   ├── project.godot
   ├── scenes/
   │   └── main.gd              # Main game manager
   ├── scripts/
   │   ├── game_constants.gd    # Shared constants
   │   └── save_manager.gd      # Save/load system
   └── assets/                  # Will add art here
   ```

### Key Files to Create

**Scene Hierarchy** (suggested):
```
MainScene (main.tscn)
├── GameManager (main.gd)
├── Map (map_generator.gd)
│   ├── TileLayer
│   └── UnitLayer
├── UI (ui.gd)
│   ├── TopPanel (resources, turn counter)
│   ├── BottomPanel (unit info, actions)
│   └── MainMenu (menu.gd)
└── Camera2D
```

### Useful GDScript Snippets

**Resource Manager**:
```gdscript
extends Node

var resources = {
	"mana": 100,
	"gold": 50,
	"health": 100,
	"gems": 0
}

func add_resource(resource_type: String, amount: int):
	if resource_type in resources:
		resources[resource_type] += amount
		ResourcesChanged.emit()

func remove_resource(resource_type: String, amount: int) -> bool:
	if resources[resource_type] >= amount:
		resources[resource_type] -= amount
		ResourcesChanged.emit()
		return true
	return false
```

**Turn System**:
```gdscript
extends Node

signal turn_ended
signal turn_started

var current_turn = 1
var is_player_turn = true

func end_turn():
	current_turn += 1
	is_player_turn = false
	turn_ended.emit()
	await get_tree().create_timer(2.0).timeout
	is_player_turn = true
	turn_started.emit()
```

---

## Game 2: Slingerlands RPG

**Location**: `games/slingerlands-rpg/`

### Overview
Turn-based RPG in the style of Might & Magic. Explore dungeons, manage a party of characters, engage in tactical combat, and progress through an adventure.

### Core Systems to Implement

#### Phase 1: Foundation (Week 1-2)
- [ ] Character creation/selection screen
- [ ] Dungeon/overworld scene and navigation
- [ ] Camera system (follow player)
- [ ] Basic sprite system for characters and enemies
- [ ] UI framework

#### Phase 2: Gameplay (Week 3-4)
- [ ] Party system (add/manage characters)
- [ ] Combat system (turn-based)
- [ ] Inventory and equipment
- [ ] Loot drops and progression
- [ ] Dialogue/story system

#### Phase 3: Content & Polish (Week 5+)
- [ ] Multiple dungeons
- [ ] Boss encounters
- [ ] Character advancement (leveling, skills)
- [ ] Save/load system
- [ ] Networking/multiplayer (optional)

### Starting Development

1. Open Godot 4.x
2. File → Open Project → Select `games/slingerlands-rpg/`
3. Project structure is ready:
   ```
   slingerlands-rpg/
   ├── project.godot
   ├── scenes/
   │   └── main.gd              # Main game manager
   ├── scripts/
   │   ├── game_constants.gd    # Shared constants
   │   ├── save_manager.gd      # Save/load system
   │   ├── character.gd         # Character class
   │   └── party_manager.gd     # Party management
   └── assets/                  # Art and audio
   ```

### Key Files to Create

**Character System**:
```gdscript
# scripts/character.gd
extends Node

class_name Character

var name: String
var level: int = 1
var exp: int = 0
var exp_needed: int = 100

var hp: int = 100
var hp_max: int = 100
var mana: int = 50
var mana_max: int = 50

var stats = {
	"strength": 10,
	"defense": 8,
	"intelligence": 9,
	"endurance": 10
}

var equipment = {
	"weapon": null,
	"armor": null,
	"accessory": null
}

var skills: Array[String] = []

func take_damage(amount: int) -> int:
	var reduced = maxi(1, amount - (stats["defense"] / 2))
	hp = maxf(0, hp - reduced)
	return reduced

func heal(amount: int):
	hp = mini(hp + amount, hp_max)

func gain_exp(amount: int):
	exp += amount
	if exp >= exp_needed:
		level_up()

func level_up():
	level += 1
	exp = 0
	exp_needed = int(exp_needed * 1.1)
	hp_max += 10
	hp = hp_max
	mana_max += 5
	mana = mana_max
```

**Scene Hierarchy** (suggested):
```
MainScene (main.tscn)
├── GameManager (main.gd)
├── Dungeon (dungeon.gd)
│   ├── TileMap (floor)
│   ├── Player (player.gd)
│   └── Enemies (enemies.gd)
├── Combat (combat.gd)
│   ├── CombatUI
│   ├── PlayerParty
│   └── EnemyParty
├── UI (ui.gd)
│   ├── PartyPanel
│   ├── InventoryPanel
│   └── MainMenu
└── Camera2D
```

### Useful GDScript Snippets

**Party Manager**:
```gdscript
extends Node

var party: Array[Character] = []
var max_party_size: int = 6

func add_character(character: Character) -> bool:
	if party.size() < max_party_size:
		party.append(character)
		return true
	return false

func remove_character(index: int):
	if 0 <= index < party.size():
		party.remove_at(index)

func get_alive_characters() -> Array[Character]:
	return party.filter(func(c): return c.hp > 0)

func is_party_alive() -> bool:
	return get_alive_characters().size() > 0
```

**Combat Encounter**:
```gdscript
extends Node

var player_party: Array[Character]
var enemy_party: Array[Character]
var combat_log: Array[String] = []

func start_combat():
	combat_log.clear()
	combat_log.append("Combat started!")
	determine_initiative()

func player_turn(actor: Character, action: String, target: Character):
	match action:
		"attack":
			var damage = actor.stats["strength"] * 1.5
			var actual_damage = target.take_damage(int(damage))
			combat_log.append("%s attacked %s for %d damage" % [actor.name, target.name, actual_damage])
		"defend":
			actor.stats["defense"] *= 1.5  # Temporary boost
			combat_log.append("%s took a defensive stance" % actor.name)

	enemy_turn()

func enemy_turn():
	for enemy in enemy_party:
		var target = player_party.pick_random()
		var damage = enemy.stats["strength"]
		target.take_damage(damage)
		combat_log.append("%s attacked %s" % [enemy.name, target.name])

	check_combat_end()
```

---

## Shared Resources

Both games share some common code in `games/shared-assets/scripts/`:

- **game_constants.gd**: Game balance constants, UI settings, resource definitions
- **save_manager.gd**: Save/load system using JSON

These are designed to be imported in both games to avoid duplication.

### Using Shared Scripts

In your game scenes/scripts:
```gdscript
extends Node

# Reference shared constants
var max_party_size = GameConstants.MAX_PARTY_SIZE
var tile_size = GameConstants.TILE_SIZE

# Use save manager
var save_mgr = SaveManager.new()
save_mgr.save_game(game_data, "save_001")
```

---

## Graphics & Artistic Direction

**Goal**: Classic game feel with modern graphics and artistic quality

### Asset Creation Path

1. **Placeholder Phase** (Week 1-2):
   - Simple colored rectangles/circles for entities
   - Temporary UI graphics
   - Focus on functionality, not visuals

2. **Stable Diffusion Generation** (Week 3):
   - Generate base character artwork
   - Create environment/dungeon assets
   - Generate UI elements and backgrounds

3. **Professional Polish** (Week 4-5):
   - Commission or commission artists if budget allows
   - Hand-touch AI-generated assets
   - Create custom sprites for unique characters

### Asset Organization
```
games/splinterlands-civ/assets/
├── characters/          # Sprite sheets
├── environments/        # Tiles, backgrounds
├── ui/                  # Buttons, panels, icons
├── audio/               # Music, sound effects
└── fonts/               # Custom fonts

games/slingerlands-rpg/assets/
├── characters/
├── dungeons/
├── ui/
├── audio/
└── fonts/
```

### Godot Sprite Tips

- Use **SpriteSheets** and **AnimatedSprite2D** for character animations
- Import settings: Filter OFF for pixel-art look
- Use **Shader** for visual effects (lighting, damage, etc.)
- Organize in **Canvas Layers** for depth management

---

## Testing & QA

### What to Test

**Game 1 (Civ)**:
- [ ] Map generates without errors
- [ ] Turn system advances properly
- [ ] Resources update correctly
- [ ] Combat resolves properly
- [ ] UI is responsive

**Game 2 (RPG)**:
- [ ] Character creation works
- [ ] Dungeon navigation is smooth
- [ ] Combat system is balanced
- [ ] Inventory management works
- [ ] Save/load preserves state

### Testing Checklist

```bash
# Run within Godot editor
1. Press F5 to play scene
2. Test basic mechanics
3. Check console for errors
4. Verify UI responsiveness
5. Save and reload data
```

---

## Common Issues & Solutions

### Game Won't Load
- Check `project.godot` syntax
- Verify all referenced scripts exist
- Check console for error messages

### Script Errors
- Verify import paths are correct
- Check for typos in function names
- Ensure proper indentation in GDScript

### UI Not Responsive
- Check input maps in Project Settings
- Verify UI nodes are in proper Canvas Layer
- Test with simpler UI first

---

## Next Steps

1. **Pick a game** to start with
2. **Implement Phase 1** systems
3. **Create test scene** and verify basics work
4. **Commit to Git** frequently
5. **Document decisions** in code comments
6. **Test daily** to catch issues early

---

See `DDAS_Strategic_Plan.md` for broader context and timeline.

Questions? Check Godot docs or ask in Discord!
