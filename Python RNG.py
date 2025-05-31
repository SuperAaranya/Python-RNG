import random
import os
import time
import json
from datetime import datetime

# Python RNG Ultimate Edition with Save/Load, Roll Stats, Shop, Quests, Crafting, Biomes, Weather, and Achievements

# Define auras with rarities (rarity as 1 in X) and area-specific flags
auras = {
    "Amber":    (2,      ["Plains", "Forest"]),
    "Jade":     (4,      ["Forest", "Crystal Caves"]),
    "Cobalt":   (10,     ["Mountain", "Desert"]),
    "Topaz":    (20,     ["Desert", "Volcano"]),
    "Peridot":  (50,     ["Plains", "Mountain"]),
    "Ruby":     (100,    ["Volcano"]),
    "Emerald":  (200,    ["Forest"]),
    "Sapphire": (500,    ["Crystal Caves"]),
    "Diamond":  (1000,   ["Mountain"]),
    "Obsidian": (2500,   ["Volcano"]),
    "Galaxy":   (5000,   ["Crystal Caves"]),
    "Nebula":   (10000,  ["Desert"]),
    "Eclipse":  (25000,  ["Volcano"]),
    "Singularity": (100000, ["Crystal Caves"])
}

# Initialize counts
aura_counts       = {name: 0 for name in auras}
shiny_aura_counts = {f"Shiny {name}": 0 for name in auras}
total_rolls       = 0
roll_log          = []  # list of tuples (roll_number, aura_name)
visit_log         = []  # list of tuples (timestamp, biome)

# Item & crafting
item_inventory = []
item_effects   = {}  # maps item_name -> expiry_timestamp

# Shop data
global_shop_pool = {
    "Common":     [("Shiny Sticker", None),      ("Basic Amulet", "Amber")],
    "Uncommon":   [("Lucky Charm", "Cobalt"),    ("Forest Potion", None)],
    "Rare":       [("Mystic Scroll", "Ruby"),    ("Desert Talisman", None)],
    "Ultra Rare": [("Cosmic Key", "Diamond"),    ("Mountain Crest", None)],
    "Legendary":  [("Galactic Crown", "Singularity"), ("Volcano Heart", None)]
}
daily_shop       = {}
shop_last_refresh = None

today_date = None

# Daily quests: name -> (description, requirement_func, reward_item)
all_quests = {
    "Roll Novice":     ("Roll 10 times",
                        lambda: total_rolls >= 10,
                        "Lucky Charm"),
    "Aura Collector":  ("Collect 5 different auras",
                        lambda: len([a for a in aura_counts if aura_counts[a] > 0]) >= 5,
                        "Mystic Scroll"),
    "Biome Explorer":  ("Visit all 6 biomes",
                        lambda: visited_biomes == set(biomes.keys()),
                        "Forest Potion")
}
quest_status   = {}
visited_biomes = set()

# Item usage effects: item_name -> (effect_type, duration_seconds)
item_usage_effects = {
    "Lucky Charm":  ("luck", 60),
    "Mystic Scroll":("luck", 120),
    "Cosmic Key":   ("luck", 180)
}

# Crafting recipes: name -> { "requires": {material: qty}, "effect": (type, duration) }
crafted_recipes = {
    "Fortune Device": { "requires": {"Lucky Charm": 2, "Amber": 5},
                        "effect":   ("luck", 300) },
    "Memetic Device": { "requires": {"Shiny Sticker": 1, "Ruby": 3},
                        "effect":   ("luck", 600) }
}

# Achievements: name -> (description, requirement_func)
achievement_milestones = {
    "Aura Guru":   ("Collect 10 unique auras",
                     lambda: len([a for a in aura_counts if aura_counts[a] > 0]) >= 10),
    "Shiny Hunter":("Obtain 1 Shiny Aura",
                     lambda: any(shiny_aura_counts[a] > 0 for a in shiny_aura_counts)),
    "Roll Master": ("Complete 100 rolls",
                     lambda: total_rolls >= 100)
}
titles_earned = []

# Biomes and their drop-rate modifiers
biomes = {
    "Plains":       1.0,
    "Forest":       0.9,
    "Desert":       1.1,
    "Mountain":     0.8,
    "Volcano":      1.2,
    "Crystal Caves":0.7
}
weather_types     = ["Clear", "Rain", "Snow", "Wind"]
current_biome     = "Plains"
current_weather   = "Clear"
weather_last_change = None

sorted_auras = sorted(auras.items(), key=lambda x: x[1][0])  # list of (name, (rarity, locations))
SAVE_FILE    = "aaranya_save.json"

# ─────────────────────────────────────────────────────────────────────────────
# Utility
# ─────────────────────────────────────────────────────────────────────────────

def clear_screen():
    """Clear the console."""
    os.system('cls' if os.name == 'nt' else 'clear')


# ─────────────────────────────────────────────────────────────────────────────
# Save & Load
# ─────────────────────────────────────────────────────────────────────────────

def save_state():
    """Save all relevant game state to a JSON file."""
    state = {
        "aura_counts":        aura_counts,
        "shiny_aura_counts":  shiny_aura_counts,
        "total_rolls":        total_rolls,
        "roll_log":           roll_log,
        "visited_biomes":     list(visited_biomes),
        "item_inventory":     item_inventory,
        "item_effects":       item_effects,
        "quest_status":       quest_status,
        "titles_earned":      titles_earned,
        "current_biome":      current_biome,
        "current_weather":    current_weather,
        "today_date":         today_date
    }
    try:
        with open(SAVE_FILE, "w") as f:
            json.dump(state, f)
        print("Game saved.")
    except Exception as e:
        print(f"Error saving game: {e}")


def load_state():
    """Load game state from the JSON file, if it exists."""
    global aura_counts, shiny_aura_counts, total_rolls, roll_log, visited_biomes
    global item_inventory, item_effects, quest_status, titles_earned
    global current_biome, current_weather, today_date

    if not os.path.exists(SAVE_FILE):
        print("No save file found.")
        return

    try:
        with open(SAVE_FILE, "r") as f:
            state = json.load(f)
        aura_counts.update(state.get("aura_counts", {}))
        shiny_aura_counts.update(state.get("shiny_aura_counts", {}))
        total_rolls = state.get("total_rolls", 0)
        roll_log[:] = state.get("roll_log", [])
        visited_biomes = set(state.get("visited_biomes", []))
        item_inventory[:] = state.get("item_inventory", [])
        item_effects.update(state.get("item_effects", {}))
        quest_status.update(state.get("quest_status", {}))
        titles_earned[:] = state.get("titles_earned", [])
        current_biome   = state.get("current_biome", current_biome)
        current_weather = state.get("current_weather", current_weather)
        today_date      = state.get("today_date", today_date)
        print("Game loaded.")
    except Exception as e:
        print(f"Error loading game: {e}")


# ─────────────────────────────────────────────────────────────────────────────
# Daily Refresh: Shop & Quests
# ─────────────────────────────────────────────────────────────────────────────

def refresh_daily():
    """Refresh the daily shop and daily quests once per day."""
    global daily_shop, shop_last_refresh, quest_status, visited_biomes, today_date

    day = datetime.now().timetuple().tm_yday
    if today_date != day:
        # Refresh shop: one random item per tier
        daily_shop.clear()
        for tier, items in global_shop_pool.items():
            daily_shop[tier] = random.sample(items, min(len(items), 1))
        shop_last_refresh = day

        # Refresh quests
        quest_status.clear()
        for quest in all_quests:
            quest_status[quest] = False

        visited_biomes.clear()
        visited_biomes.add(current_biome)

        today_date = day


# ─────────────────────────────────────────────────────────────────────────────
# Weather Update
# ─────────────────────────────────────────────────────────────────────────────

def update_weather():
    """Every 5 minutes (approx.), randomly change the weather."""
    global current_weather, weather_last_change

    now = time.time()
    if weather_last_change is None or (now - weather_last_change) > 300:
        current_weather   = random.choice(weather_types)
        weather_last_change = now


# ─────────────────────────────────────────────────────────────────────────────
# Quest & Achievement Checks
# ─────────────────────────────────────────────────────────────────────────────

def check_quests():
    """Check each daily quest; if unlocked, give reward."""
    for quest, (desc, requirement, reward) in all_quests.items():
        if not quest_status.get(quest) and requirement():
            quest_status[quest] = True
            item_inventory.append(reward)
            print(f"Quest Completed: {quest}! You received: {reward}")


def check_achievements():
    """Check achievements; if unlocked, add title."""
    for title, (desc, requirement) in achievement_milestones.items():
        if title not in titles_earned and requirement():
            titles_earned.append(title)
            print(f"Achievement Unlocked: {title} - {desc}")


# ─────────────────────────────────────────────────────────────────────────────
# Item Effects Expiration
# ─────────────────────────────────────────────────────────────────────────────

def apply_item_effects():
    """Expire any item whose duration has passed."""
    now = time.time()
    expired = [item for item, expiry in item_effects.items() if expiry <= now]
    for item in expired:
        del item_effects[item]
        print(f"Effect of {item} has expired.")


# ─────────────────────────────────────────────────────────────────────────────
# Crafting System
# ─────────────────────────────────────────────────────────────────────────────

def craft_item():
    """Display crafting recipes; let user craft if materials available."""
    print("\n=== Crafting Menu ===")
    for idx, (recipe, data) in enumerate(crafted_recipes.items(), 1):
        req_list = ", ".join(f"{mat} x{qty}" for mat, qty in data["requires"].items())
        print(f"{idx}. {recipe} (Requires: {req_list})")
    print("0. Cancel")

    try:
        choice = int(input("Select recipe number: "))
        if choice == 0:
            return
        recipe_name = list(crafted_recipes.keys())[choice - 1]
        data = crafted_recipes[recipe_name]

        # Check materials
        can_craft = True
        for mat, qty in data["requires"].items():
            if mat in auras:
                if aura_counts.get(mat, 0) < qty:
                    can_craft = False
            else:
                if item_inventory.count(mat) < qty:
                    can_craft = False

        if not can_craft:
            print("You lack required materials.")
            return

        # Deduct materials
        for mat, qty in data["requires"].items():
            if mat in auras:
                aura_counts[mat] -= qty
            else:
                for _ in range(qty):
                    item_inventory.remove(mat)

        # Grant crafted item
        item_inventory.append(recipe_name)
        print(f"Crafted {recipe_name}!")
    except (ValueError, IndexError):
        print("Invalid choice.")
    print("")


# ─────────────────────────────────────────────────────────────────────────────
# Inventory Management
# ─────────────────────────────────────────────────────────────────────────────

def view_inventory():
    """Show items in inventory; allow using one if desired."""
    print("\nYour Item Inventory:")
    if not item_inventory:
        print("You have no items.")
        return

    for idx, item in enumerate(item_inventory, 1):
        print(f"{idx}. {item}")

    try:
        choice = int(input("Select item number to use (0 to cancel): "))
        if choice == 0:
            return
        selected = item_inventory.pop(choice - 1)
        if selected in item_usage_effects:
            effect_type, duration = item_usage_effects[selected]
            item_effects[selected] = time.time() + duration
            print(f"You used {selected}. {effect_type.capitalize()} boost for {duration} seconds!")
        else:
            print(f"You used {selected}. It did something mysterious...")
    except (ValueError, IndexError):
        print("Invalid choice.")
    print("")


# ─────────────────────────────────────────────────────────────────────────────
# Daily Shop Display & Purchase
# ─────────────────────────────────────────────────────────────────────────────

def open_daily_shop():
    """Show the daily shop (refresh if new day) and allow buying."""
    refresh_daily()
    update_weather()

    print(f"\n=== Daily Shop (Weather: {current_weather}) ===")
    for tier, items in daily_shop.items():
        print(f"{tier} Items:")
        for item, required_aura in items:
            req_str = f"Needs {required_aura}" if required_aura else "Free"
            print(f"  {item} ({req_str})")

    choice = input("\nEnter item name to buy (or press Enter to exit): ").strip()
    if choice == "":
        return

    for tier, items in daily_shop.items():
        for item, required in items:
            if item.lower() == choice.lower():
                if required is None or aura_counts.get(required, 0) > 0:
                    item_inventory.append(item)
                    print(f"You acquired: {item}")
                else:
                    print(f"Need {required} aura to buy this.")
                return

    print("Item not in shop.")
    print("")


# ─────────────────────────────────────────────────────────────────────────────
# Daily Quests Display
# ─────────────────────────────────────────────────────────────────────────────

def view_quests():
    """Show daily quests and completion status."""
    refresh_daily()
    print("\n=== Daily Quests ===")
    for quest, (desc, _, _) in all_quests.items():
        status = "Completed" if quest_status.get(quest) else "Incomplete"
        print(f"- {quest}: {desc} [{status}]")
    print("")


# ─────────────────────────────────────────────────────────────────────────────
# Roll Statistics Display
# ─────────────────────────────────────────────────────────────────────────────

def view_roll_stats():
    """Display total rolls, each aura count, and shiny aura counts."""
    print("\n=== Roll Stats ===")
    print(f"Total Rolls: {total_rolls}")
    print("Aura Counts:")
    for name, count in aura_counts.items():
        print(f"  {name}: {count}")
    print("Shiny Aura Counts:")
    for name, count in shiny_aura_counts.items():
        print(f"  {name}: {count}")
    print("")


# ─────────────────────────────────────────────────────────────────────────────
# Biome & Weather RNG on Menu
# ─────────────────────────────────────────────────────────────────────────────

def update_biome_and_weather():
    """1 in 5 chance to discover a new biome; 1 in 5 chance to change weather."""
    global current_biome, current_weather
    if random.randint(1, 5) == 1:
        new_biome = random.choice(list(biomes.keys()))
        if new_biome != current_biome:
            current_biome = new_biome
            visited_biomes.add(new_biome)
            print(f"\nNew biome discovered: {new_biome}!")

    if random.randint(1, 5) == 1:
        current_weather = random.choice(weather_types)
        print(f"{current_weather} weather sets in.")
    time.sleep(0.3)


# ─────────────────────────────────────────────────────────────────────────────
# Rolling Logic (Single & Multiple)
# ─────────────────────────────────────────────────────────────────────────────

def roll_once():
    """Perform a single roll, accounting for biome, weather, and luck effects."""
    global total_rolls
    refresh_daily()
    apply_item_effects()
    check_achievements()

    total_rolls += 1
    update_biome_and_weather()

    base_modifier = biomes.get(current_biome, 1.0)
    bonus_luck = any(effect == "luck" for effect, _ in item_effects.items())

    # Build area-specific roll pool
    roll_pool = []
    for name, (rarity, locations) in auras.items():
        if current_biome in locations:
            adjusted = max(1, int(rarity * base_modifier))
            if bonus_luck:
                adjusted = max(1, adjusted // 2)
            roll_pool.append((name, adjusted))

    # Always include a fallback common aura
    roll_pool.append(("Amber", int(auras["Amber"][0] * base_modifier)))

    # Attempt random draws until one succeeds
    while roll_pool:
        name, adjusted_rarity = random.choice(roll_pool)
        if random.randint(1, adjusted_rarity) == 1:
            # Shiny check (1 in 250 chance)
            if random.randint(1, 250) == 1:
                shiny = f"Shiny {name}"
                shiny_aura_counts[shiny] += 1
                roll_log.append((total_rolls, shiny))
                print(f"🌟 SHINY! You rolled: {shiny} 🌟")
                check_quests()
                check_achievements()
                return
            else:
                aura_counts[name] += 1
                roll_log.append((total_rolls, name))
                print(f"You rolled: {name}")
                if auras[name][0] >= 100 and auras[name][0] < 1000:
                    print("WOW GREAT JOB")
                elif auras[name][0] >= 1000:
                    print("GLOBAL PULL!!!")
                check_quests()
                check_achievements()
                return
        else:
            roll_pool.remove((name, adjusted_rarity))

    # Fallback if nothing succeeded
    aura_counts["Amber"] += 1
    roll_log.append((total_rolls, "Amber"))
    print("You rolled: Amber\n")
    check_quests()
    check_achievements()


def roll_multiple():
    """Prompt user for a count, then perform that many rolls."""
    try:
        amount = int(input("How many times do you want to roll? "))
    except ValueError:
        print("Invalid number.")
        return

    for _ in range(amount):
        roll_once()
        time.sleep(0.1)


# ─────────────────────────────────────────────────────────────────────────────
# Show Collection (non-duplicating auras + shinies)
# ─────────────────────────────────────────────────────────────────────────────

def view_collection():
    """Display each aura you own (once), plus any shiny variants, sorted by rarity."""
    print("\nYour Aura Collection:")
    display = []
    order = 1

    for name, (rarity, _) in sorted(auras.items(), key=lambda x: x[1][0]):
        count       = aura_counts[name]
        shiny_count = shiny_aura_counts.get(f"Shiny {name}", 0)
        if count > 0:
            display.append((rarity, f"No. {order} {name} 1 in {rarity}: You have {count}!"))
            order += 1
        if shiny_count > 0:
            display.append((rarity - 0.1,
                            f"No. {order} ⭐ Shiny {name} 1 in {rarity}: You have {shiny_count}!"))
            order += 1

    for _, line in sorted(display):
        print(line)
    print("")


# ─────────────────────────────────────────────────────────────────────────────
# Main Menu
# ─────────────────────────────────────────────────────────────────────────────

def show_menu():
    """Main interactive loop showing all features."""
    while True:
        clear_screen()
        update_biome_and_weather()
        refresh_daily()
        apply_item_effects()
        check_achievements()

        print(f"=== Python RNG (Biome: {current_biome}, Weather: {current_weather}) ===")
        print("1. Roll Once")
        print("2. Roll Multiple")
        print("3. View Collection")
        print("4. Daily Shop")
        print("5. Item Inventory")
        print("6. View Daily Quests")
        print("7. Crafting")
        print("8. Roll Stats")
        print("9. Save Game")
        print("10. Load Game")
        print("11. Exit")

        choice = input("Choose an option: ").strip()

        if choice == "1":
            roll_once()
        elif choice == "2":
            roll_multiple()
        elif choice == "3":
            view_collection()
        elif choice == "4":
            open_daily_shop()
        elif choice == "5":
            view_inventory()
        elif choice == "6":
            view_quests()
        elif choice == "7":
            craft_item()
        elif choice == "8":
            view_roll_stats()
        elif choice == "9":
            save_state()
        elif choice == "10":
            load_state()
        elif choice == "11":
            print("Thanks for playing Python RNG! Come back again next time!")
            break
        else:
            print("Invalid choice, try again.\n")

        time.sleep(0.5)


if __name__ == "__main__":
    clear_screen()
    show_menu()
