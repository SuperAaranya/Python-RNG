import random
import os
import time
import json
from datetime import datetime
from pathlib import Path

class PythonRNGGame:
    def __init__(self):
        self.script_dir = Path(__file__).parent
        self.save_file = self.script_dir / "AaranyaRNGSaves.json"
        
        self.auras = {
            "Amber": (2, ["Plains", "Forest"]),
            "Jade": (4, ["Forest", "Crystal Caves"]),
            "Cobalt": (10, ["Mountain", "Desert"]),
            "Topaz": (20, ["Desert", "Volcano"]),
            "Peridot": (50, ["Plains", "Mountain"]),
            "Ruby": (100, ["Volcano"]),
            "Emerald": (200, ["Forest"]),
            "Sapphire": (500, ["Crystal Caves"]),
            "Diamond": (1000, ["Mountain"]),
            "Obsidian": (2500, ["Volcano"]),
            "Galaxy": (5000, ["Crystal Caves"]),
            "Nebula": (10000, ["Desert"]),
            "Eclipse": (25000, ["Volcano"]),
            "Singularity": (100000, ["Crystal Caves"]),
            "Void": (250000, ["Crystal Caves"]),
            "Cosmic": (500000, ["Mountain"]),
            "Ethereal": (1000000, ["Forest"]),
            "Divine": (2500000, ["Plains"]),
            "Celestial": (5000000, ["Volcano"]),
            "Omnipotent": (10000000, ["Crystal Caves"])
        }

        self.aura_counts = {name: 0 for name in self.auras}
        self.shiny_aura_counts = {f"Shiny {name}": 0 for name in self.auras}
        self.total_rolls = 0
        self.roll_log = []
        self.visit_log = []
        
        self.item_inventory = []
        self.item_effects = {}
        
        self.global_shop_pool = {
            "Common": [
                ("Shiny Sticker", None),
                ("Basic Amulet", "Amber"),
                ("Lucky Penny", None),
                ("Crystal Shard", "Jade")
            ],
            "Uncommon": [
                ("Lucky Charm", "Cobalt"),
                ("Forest Potion", None),
                ("Mountain Essence", "Peridot"),
                ("Desert Sand", "Topaz")
            ],
            "Rare": [
                ("Mystic Scroll", "Ruby"),
                ("Desert Talisman", None),
                ("Emerald Dust", "Emerald"),
                ("Sapphire Fragment", "Sapphire")
            ],
            "Ultra Rare": [
                ("Cosmic Key", "Diamond"),
                ("Mountain Crest", None),
                ("Obsidian Blade", "Obsidian"),
                ("Galaxy Orb", "Galaxy")
            ],
            "Legendary": [
                ("Galactic Crown", "Singularity"),
                ("Volcano Heart", None),
                ("Nebula Stone", "Nebula"),
                ("Eclipse Mirror", "Eclipse")
            ],
            "Mythical": [
                ("Void Crystal", "Void"),
                ("Cosmic Medallion", "Cosmic"),
                ("Ethereal Essence", "Ethereal"),
                ("Divine Relic", "Divine")
            ]
        }
        
        self.daily_shop = {}
        self.shop_last_refresh = None
        self.today_date = None
        
        self.all_quests = {
            "Roll Novice": (
                "Roll 10 times",
                lambda: self.total_rolls >= 10,
                "Lucky Charm"
            ),
            "Roll Apprentice": (
                "Roll 50 times",
                lambda: self.total_rolls >= 50,
                "Mystic Scroll"
            ),
            "Roll Expert": (
                "Roll 100 times",
                lambda: self.total_rolls >= 100,
                "Cosmic Key"
            ),
            "Aura Collector": (
                "Collect 5 different auras",
                lambda: len([a for a in self.aura_counts if self.aura_counts[a] > 0]) >= 5,
                "Forest Potion"
            ),
            "Aura Master": (
                "Collect 10 different auras",
                lambda: len([a for a in self.aura_counts if self.aura_counts[a] > 0]) >= 10,
                "Galaxy Orb"
            ),
            "Biome Explorer": (
                "Visit all 6 biomes",
                lambda: self.visited_biomes == set(self.biomes.keys()),
                "Desert Talisman"
            ),
            "Shiny Hunter": (
                "Obtain any shiny aura",
                lambda: any(self.shiny_aura_counts[a] > 0 for a in self.shiny_aura_counts),
                "Galactic Crown"
            ),
            "Rare Collector": (
                "Collect an aura with rarity 1000+",
                lambda: any(self.aura_counts[name] > 0 for name, (rarity, _) in self.auras.items() if rarity >= 1000),
                "Volcano Heart"
            )
        }
        
        self.quest_status = {}
        self.visited_biomes = set()
        
        self.item_usage_effects = {
            "Lucky Charm": ("luck", 60),
            "Mystic Scroll": ("luck", 120),
            "Cosmic Key": ("luck", 180),
            "Forest Potion": ("biome_luck", 300),
            "Desert Talisman": ("rare_boost", 240),
            "Galaxy Orb": ("shiny_boost", 180),
            "Galactic Crown": ("mega_luck", 600),
            "Volcano Heart": ("ultra_rare_boost", 480)
        }
        
        self.crafted_recipes = {
            "Fortune Device": {
                "requires": {"Lucky Charm": 2, "Amber": 5},
                "effect": ("luck", 300)
            },
            "Memetic Device": {
                "requires": {"Shiny Sticker": 1, "Ruby": 3},
                "effect": ("luck", 600)
            },
            "Probability Manipulator": {
                "requires": {"Cosmic Key": 1, "Diamond": 2, "Mystic Scroll": 3},
                "effect": ("mega_luck", 900)
            },
            "Reality Bender": {
                "requires": {"Galactic Crown": 1, "Singularity": 1, "Volcano Heart": 2},
                "effect": ("ultimate_luck", 1800)
            },
            "Dimensional Anchor": {
                "requires": {"Void Crystal": 1, "Cosmic Medallion": 1, "Ethereal Essence": 2},
                "effect": ("godmode", 3600)
            }
        }
        
        self.achievement_milestones = {
            "Aura Guru": (
                "Collect 10 unique auras",
                lambda: len([a for a in self.aura_counts if self.aura_counts[a] > 0]) >= 10
            ),
            "Aura Legend": (
                "Collect 15 unique auras",
                lambda: len([a for a in self.aura_counts if self.aura_counts[a] > 0]) >= 15
            ),
            "Shiny Hunter": (
                "Obtain 1 Shiny Aura",
                lambda: any(self.shiny_aura_counts[a] > 0 for a in self.shiny_aura_counts)
            ),
            "Shiny Master": (
                "Obtain 5 different Shiny Auras",
                lambda: len([a for a in self.shiny_aura_counts if self.shiny_aura_counts[a] > 0]) >= 5
            ),
            "Roll Master": (
                "Complete 100 rolls",
                lambda: self.total_rolls >= 100
            ),
            "Roll Legend": (
                "Complete 1000 rolls",
                lambda: self.total_rolls >= 1000
            ),
            "Roll God": (
                "Complete 10000 rolls",
                lambda: self.total_rolls >= 10000
            ),
            "Biome Wanderer": (
                "Visit all biomes",
                lambda: len(self.visited_biomes) >= len(self.biomes)
            ),
            "Rare Finder": (
                "Find an aura with 1000+ rarity",
                lambda: any(self.aura_counts[name] > 0 for name, (rarity, _) in self.auras.items() if rarity >= 1000)
            ),
            "Legendary Seeker": (
                "Find an aura with 100000+ rarity",
                lambda: any(self.aura_counts[name] > 0 for name, (rarity, _) in self.auras.items() if rarity >= 100000)
            ),
            "Mythical Being": (
                "Find an aura with 5000000+ rarity",
                lambda: any(self.aura_counts[name] > 0 for name, (rarity, _) in self.auras.items() if rarity >= 5000000)
            )
        }
        
        self.titles_earned = []
        
        self.biomes = {
            "Plains": 1.0,
            "Forest": 0.9,
            "Desert": 1.1,
            "Mountain": 0.8,
            "Volcano": 1.2,
            "Crystal Caves": 0.7,
            "Void Realm": 0.5,
            "Cosmic Nexus": 0.6,
            "Ethereal Plane": 0.4,
            "Divine Sanctum": 0.3
        }
        
        self.weather_types = [
            "Clear", "Rain", "Snow", "Wind", "Storm", "Mist", 
            "Aurora", "Eclipse", "Starfall", "Void Storm"
        ]
        
        self.current_biome = "Plains"
        self.current_weather = "Clear"
        self.weather_last_change = None
        
        self.sorted_auras = sorted(self.auras.items(), key=lambda x: x[1][0])

    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def save_state(self):
        state = {
            "aura_counts": self.aura_counts,
            "shiny_aura_counts": self.shiny_aura_counts,
            "total_rolls": self.total_rolls,
            "roll_log": self.roll_log,
            "visited_biomes": list(self.visited_biomes),
            "item_inventory": self.item_inventory,
            "item_effects": self.item_effects,
            "quest_status": self.quest_status,
            "titles_earned": self.titles_earned,
            "current_biome": self.current_biome,
            "current_weather": self.current_weather,
            "today_date": self.today_date,
            "visit_log": self.visit_log
        }
        try:
            with open(self.save_file, "w", encoding='utf-8') as f:
                json.dump(state, f, indent=4, ensure_ascii=False, sort_keys=True)
            print("✅ Game saved successfully!")
        except Exception as e:
            print(f"❌ Error saving game: {e}")

    def load_state(self):
        if not self.save_file.exists():
            print("📁 No save file found - starting fresh!")
            return

        try:
            with open(self.save_file, "r", encoding='utf-8') as f:
                state = json.load(f)
            
            self.aura_counts.update(state.get("aura_counts", {}))
            self.shiny_aura_counts.update(state.get("shiny_aura_counts", {}))
            self.total_rolls = state.get("total_rolls", 0)
            self.roll_log[:] = state.get("roll_log", [])
            self.visited_biomes = set(state.get("visited_biomes", []))
            self.item_inventory[:] = state.get("item_inventory", [])
            self.item_effects.update(state.get("item_effects", {}))
            self.quest_status.update(state.get("quest_status", {}))
            self.titles_earned[:] = state.get("titles_earned", [])
            self.current_biome = state.get("current_biome", self.current_biome)
            self.current_weather = state.get("current_weather", self.current_weather)
            self.today_date = state.get("today_date", self.today_date)
            self.visit_log[:] = state.get("visit_log", [])
            
            print("✅ Game loaded successfully!")
        except Exception as e:
            print(f"❌ Error loading game: {e}")

    def refresh_daily(self):
        day = datetime.now().timetuple().tm_yday
        if self.today_date != day:
            self.daily_shop.clear()
            for tier, items in self.global_shop_pool.items():
                available_items = min(len(items), random.randint(1, 3))
                self.daily_shop[tier] = random.sample(items, available_items)
            self.shop_last_refresh = day

            self.quest_status.clear()
            for quest in self.all_quests:
                self.quest_status[quest] = False

            self.visited_biomes.clear()
            self.visited_biomes.add(self.current_biome)
            self.today_date = day

    def update_weather(self):
        now = time.time()
        if self.weather_last_change is None or (now - self.weather_last_change) > 300:
            self.current_weather = random.choice(self.weather_types)
            self.weather_last_change = now

    def check_quests(self):
        for quest, (desc, requirement, reward) in self.all_quests.items():
            if not self.quest_status.get(quest) and requirement():
                self.quest_status[quest] = True
                self.item_inventory.append(reward)
                print(f"🎯 Quest Completed: {quest}! Reward: {reward}")

    def check_achievements(self):
        for title, (desc, requirement) in self.achievement_milestones.items():
            if title not in self.titles_earned and requirement():
                self.titles_earned.append(title)
                print(f"🏆 Achievement Unlocked: {title} - {desc}")

    def apply_item_effects(self):
        now = time.time()
        expired = [item for item, expiry in self.item_effects.items() if expiry <= now]
        for item in expired:
            del self.item_effects[item]
            print(f"⏰ Effect of {item} has expired.")

    def get_luck_multiplier(self):
        multiplier = 1.0
        active_effects = []
        
        for item, expiry in self.item_effects.items():
            if expiry > time.time():
                if item in self.item_usage_effects:
                    effect_type, _ = self.item_usage_effects[item]
                    active_effects.append(effect_type)
        
        if "godmode" in active_effects:
            multiplier *= 100
        elif "ultimate_luck" in active_effects:
            multiplier *= 50
        elif "mega_luck" in active_effects:
            multiplier *= 25
        elif "luck" in active_effects:
            multiplier *= 10
        
        if "rare_boost" in active_effects:
            multiplier *= 5
        if "shiny_boost" in active_effects:
            multiplier *= 3
        if "biome_luck" in active_effects:
            multiplier *= 2
            
        return multiplier

    def craft_item(self):
        print("\n🔨 === Crafting Menu ===")
        if not self.crafted_recipes:
            print("No crafting recipes available.")
            return
            
        recipes = list(self.crafted_recipes.items())
        for idx, (recipe, data) in enumerate(recipes, 1):
            req_list = ", ".join(f"{mat} x{qty}" for mat, qty in data["requires"].items())
            effect_type, duration = data["effect"]
            print(f"{idx}. {recipe}")
            print(f"   Requires: {req_list}")
            print(f"   Effect: {effect_type} for {duration}s")
            print()
        print("0. Cancel")

        try:
            choice = int(input("Select recipe number: "))
            if choice == 0:
                return
            if choice < 1 or choice > len(recipes):
                print("Invalid choice.")
                return
                
            recipe_name, data = recipes[choice - 1]

            can_craft = True
            missing_items = []
            
            for mat, qty in data["requires"].items():
                if mat in self.auras:
                    if self.aura_counts.get(mat, 0) < qty:
                        can_craft = False
                        missing_items.append(f"{mat} (need {qty}, have {self.aura_counts.get(mat, 0)})")
                else:
                    available = self.item_inventory.count(mat)
                    if available < qty:
                        can_craft = False
                        missing_items.append(f"{mat} (need {qty}, have {available})")

            if not can_craft:
                print("❌ Cannot craft - missing materials:")
                for item in missing_items:
                    print(f"   - {item}")
                return

            for mat, qty in data["requires"].items():
                if mat in self.auras:
                    self.aura_counts[mat] -= qty
                else:
                    for _ in range(qty):
                        self.item_inventory.remove(mat)

            self.item_inventory.append(recipe_name)
            print(f"✅ Successfully crafted {recipe_name}!")
            
        except (ValueError, IndexError):
            print("Invalid choice.")
        
        input("\nPress Enter to continue...")

    def view_inventory(self):
        print("\n🎒 === Your Item Inventory ===")
        if not self.item_inventory:
            print("Your inventory is empty.")
            input("\nPress Enter to continue...")
            return

        item_counts = {}
        for item in self.item_inventory:
            item_counts[item] = item_counts.get(item, 0) + 1

        items = list(item_counts.keys())
        for idx, item in enumerate(items, 1):
            count = item_counts[item]
            count_str = f" x{count}" if count > 1 else ""
            print(f"{idx}. {item}{count_str}")

        print("0. Back to menu")
        
        try:
            choice = int(input("\nSelect item number to use: "))
            if choice == 0:
                return
            if choice < 1 or choice > len(items):
                print("Invalid choice.")
                return
                
            selected = items[choice - 1]
            if selected in self.item_inventory:
                self.item_inventory.remove(selected)
                
                if selected in self.item_usage_effects:
                    effect_type, duration = self.item_usage_effects[selected]
                    self.item_effects[selected] = time.time() + duration
                    print(f"✨ Used {selected}! {effect_type.replace('_', ' ').title()} boost for {duration} seconds!")
                else:
                    print(f"🔮 Used {selected}. Something mystical happens...")
            else:
                print("Item not found in inventory.")
                
        except (ValueError, IndexError):
            print("Invalid choice.")
            
        input("\nPress Enter to continue...")

    def open_daily_shop(self):
        self.refresh_daily()
        self.update_weather()

        print(f"\n🏪 === Daily Shop (Weather: {self.current_weather}) ===")
        
        if not self.daily_shop:
            print("The shop is closed today. Come back tomorrow!")
            input("\nPress Enter to continue...")
            return
            
        all_items = []
        item_index = 1
        
        for tier, items in self.daily_shop.items():
            print(f"\n📦 {tier} Items:")
            for item, required_aura in items:
                req_str = f"Needs {required_aura}" if required_aura else "Free"
                can_afford = required_aura is None or self.aura_counts.get(required_aura, 0) > 0
                status = "✅" if can_afford else "❌"
                print(f"  {item_index}. {item} ({req_str}) {status}")
                all_items.append((item, required_aura, can_afford))
                item_index += 1

        print("\n0. Exit shop")
        
        try:
            choice = int(input("\nEnter item number to buy: "))
            if choice == 0:
                return
            if choice < 1 or choice > len(all_items):
                print("Invalid choice.")
                return
                
            item, required_aura, can_afford = all_items[choice - 1]
            
            if not can_afford:
                print(f"❌ You need {required_aura} aura to buy this item.")
            else:
                if required_aura:
                    self.aura_counts[required_aura] -= 1
                self.item_inventory.append(item)
                print(f"✅ Purchased: {item}")
                
        except (ValueError, IndexError):
            print("Invalid choice.")
            
        input("\nPress Enter to continue...")

    def view_quests(self):
        self.refresh_daily()
        print("\n📋 === Daily Quests ===")
        
        for quest, (desc, _, reward) in self.all_quests.items():
            status = "✅ Completed" if self.quest_status.get(quest) else "⏳ Incomplete"
            print(f"🎯 {quest}: {desc}")
            print(f"   Reward: {reward} [{status}]")
            print()
            
        input("Press Enter to continue...")

    def view_roll_stats(self):
        print("\n📊 === Roll Statistics ===")
        print(f"🎲 Total Rolls: {self.total_rolls:,}")
        print(f"🏆 Titles Earned: {len(self.titles_earned)}")
        print(f"🌍 Biomes Visited: {len(self.visited_biomes)}")
        print(f"🎒 Items in Inventory: {len(self.item_inventory)}")
        
        print("\n✨ Aura Collection:")
        total_auras = sum(self.aura_counts.values())
        unique_auras = len([a for a in self.aura_counts if self.aura_counts[a] > 0])
        print(f"   Total Auras: {total_auras:,}")
        print(f"   Unique Auras: {unique_auras}/{len(self.auras)}")
        
        print("\n🌟 Shiny Collection:")
        total_shinies = sum(self.shiny_aura_counts.values())
        unique_shinies = len([a for a in self.shiny_aura_counts if self.shiny_aura_counts[a] > 0])
        print(f"   Total Shinies: {total_shinies}")
        print(f"   Unique Shinies: {unique_shinies}/{len(self.auras)}")
        
        if self.titles_earned:
            print("\n🏅 Your Titles:")
            for title in self.titles_earned:
                print(f"   • {title}")
                
        input("\nPress Enter to continue...")

    def update_biome_and_weather(self):
        if random.randint(1, 10) == 1:
            new_biome = random.choice(list(self.biomes.keys()))
            if new_biome != self.current_biome:
                self.current_biome = new_biome
                self.visited_biomes.add(new_biome)
                self.visit_log.append((datetime.now().isoformat(), new_biome))
                print(f"🗺️  Discovered new biome: {new_biome}!")

        if random.randint(1, 8) == 1:
            old_weather = self.current_weather
            self.current_weather = random.choice(self.weather_types)
            if old_weather != self.current_weather:
                print(f"🌤️  Weather changed to: {self.current_weather}")

    def calculate_roll_outcome(self):
        base_modifier = self.biomes.get(self.current_biome, 1.0)
        luck_multiplier = self.get_luck_multiplier()
        
        weather_modifier = 1.0
        if self.current_weather in ["Storm", "Eclipse", "Starfall", "Void Storm"]:
            weather_modifier = 0.8
        elif self.current_weather in ["Aurora", "Mist"]:
            weather_modifier = 0.9
        
        roll_pool = []
        for name, (rarity, locations) in self.auras.items():
            if self.current_biome in locations:
                adjusted_rarity = max(1, int(rarity * base_modifier * weather_modifier / luck_multiplier))
                roll_pool.append((name, adjusted_rarity))

        if not roll_pool:
            roll_pool.append(("Amber", max(1, int(2 * base_modifier * weather_modifier / luck_multiplier))))

        return roll_pool

    def roll_once(self):
        self.refresh_daily()
        self.apply_item_effects()
        self.total_rolls += 1
        self.update_biome_and_weather()

        roll_pool = self.calculate_roll_outcome()
        
        attempts = 0
        max_attempts = len(roll_pool) * 10
        
        while roll_pool and attempts < max_attempts:
            attempts += 1
            name, adjusted_rarity = random.choice(roll_pool)
            
            if random.randint(1, adjusted_rarity) == 1:
                original_rarity = self.auras[name][0]
                
                shiny_chance = 250
                if "shiny_boost" in [effect for effect, _ in self.item_effects.items() if self.item_effects[effect] > time.time()]:
                    shiny_chance = 100
                elif "godmode" in [effect for effect, _ in self.item_effects.items() if self.item_effects[effect] > time.time()]:
                    shiny_chance = 10
                
                if random.randint(1, shiny_chance) == 1:
                    shiny_name = f"Shiny {name}"
                    self.shiny_aura_counts[shiny_name] += 1
                    self.roll_log.append((self.total_rolls, shiny_name))
                    print(f"✨🌟 SHINY AURA! You rolled: {shiny_name} (1 in {original_rarity:,}) 🌟✨")
                    if original_rarity >= 1000000:
                        print("🎆 BEYOND LEGENDARY SHINY! THE UNIVERSE TREMBLES! 🎆")
                    elif original_rarity >= 100000:
                        print("🌌 MYTHICAL SHINY! REALITY BENDS! 🌌")
                    elif original_rarity >= 10000:
                        print("💫 LEGENDARY SHINY! INCREDIBLE! 💫")
                    elif original_rarity >= 1000:
                        print("🔥 ULTRA RARE SHINY! AMAZING! 🔥")
                else:
                    self.aura_counts[name] += 1
                    self.roll_log.append((self.total_rolls, name))
                    print(f"🎲 You rolled: {name} (1 in {original_rarity:,})")
                    
                    if original_rarity >= 5000000:
                        print("🎆 OMNIPOTENT PULL! THE COSMOS ACKNOWLEDGES YOU! 🎆")
                    elif original_rarity >= 1000000:
                        print("🌟 DIVINE PULL! THE GODS SMILE UPON YOU! 🌟")
                    elif original_rarity >= 100000:
                        print("🌌 MYTHICAL PULL! LEGENDS WILL BE TOLD! 🌌")
                    elif original_rarity >= 10000:
                        print("💫 LEGENDARY PULL! EXTRAORDINARY! 💫")
                    elif original_rarity >= 1000:
                        print("⚡ ULTRA RARE PULL! INCREDIBLE! ⚡")
                    elif original_rarity >= 100:
                        print("🔥 RARE PULL! GREAT JOB! 🔥")
                
                self.check_quests()
                self.check_achievements()
                return
            else:
                if len(roll_pool) > 1:
                    roll_pool.remove((name, adjusted_rarity))

        self.aura_counts["Amber"] += 1
        self.roll_log.append((self.total_rolls, "Amber"))
        print("🎲 You rolled: Amber (1 in 2)")
        self.check_quests()
        self.check_achievements()

    def roll_multiple(self):
        try:
            amount = int(input("How many times do you want to roll? "))
            if amount <= 0:
                print("Please enter a positive number.")
                return
            if amount > 10000:
                confirm = input(f"Rolling {amount} times might take a while. Continue? (y/n): ")
                if confirm.lower() != 'y':
                    return
        except ValueError:
            print("Invalid number.")
            return

        print(f"\n🎲 Rolling {amount} times...")
        start_time = time.time()
        notable_rolls = []
        
        for i in range(amount):
            if i > 0 and i % 100 == 0:
                print(f"Progress: {i}/{amount} rolls completed...")
            
            old_total = self.total_rolls
            self.roll_once()
            
            if self.roll_log:
                last_roll = self.roll_log[-1]
                roll_name = last_roll[1]
                
                if "Shiny" in roll_name:
                    notable_rolls.append(f"✨ {roll_name} (Roll #{last_roll[0]})")
                elif any(roll_name == name for name, (rarity, _) in self.auras.items() if rarity >= 1000):
                    rarity = self.auras[roll_name][0]
                    notable_rolls.append(f"🔥 {roll_name} (1 in {rarity:,}) (Roll #{last_roll[0]})")
            
            time.sleep(0.01)
        
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"\n✅ Completed {amount} rolls in {duration:.2f} seconds!")
        
        if notable_rolls:
            print(f"\n🎉 Notable Rolls ({len(notable_rolls)}):")
            for roll in notable_rolls[-10:]:
                print(f"   {roll}")
            if len(notable_rolls) > 10:
                print(f"   ... and {len(notable_rolls) - 10} more!")
        
        input("\nPress Enter to continue...")

    def view_collection(self):
        print("\n🎨 === Your Aura Collection ===")
        
        regular_collection = []
        shiny_collection = []
        
        for name, (rarity, locations) in sorted(self.auras.items(), key=lambda x: x[1][0]):
            count = self.aura_counts[name]
            shiny_count = self.shiny_aura_counts.get(f"Shiny {name}", 0)
            
            if count > 0:
                rarity_str = f"1 in {rarity:,}"
                location_str = ", ".join(locations)
                regular_collection.append(f"📜 {name} ({rarity_str}) - Count: {count:,}")
                regular_collection.append(f"    Locations: {location_str}")
                
            if shiny_count > 0:
                rarity_str = f"1 in {rarity:,}"
                location_str = ", ".join(locations)
                shiny_collection.append(f"✨ Shiny {name} ({rarity_str}) - Count: {shiny_count:,}")
                shiny_collection.append(f"    Locations: {location_str}")
        
        if not regular_collection and not shiny_collection:
            print("Your collection is empty. Start rolling to collect auras!")
        else:
            total_regular = sum(self.aura_counts.values())
            total_shiny = sum(self.shiny_aura_counts.values())
            unique_regular = len([a for a in self.aura_counts if self.aura_counts[a] > 0])
            unique_shiny = len([a for a in self.shiny_aura_counts if self.shiny_aura_counts[a] > 0])
            
            print(f"📊 Collection Stats:")
            print(f"   Regular Auras: {total_regular:,} total, {unique_regular}/{len(self.auras)} unique")
            print(f"   Shiny Auras: {total_shiny:,} total, {unique_shiny}/{len(self.auras)} unique")
            print()
            
            if regular_collection:
                print("🎭 Regular Auras:")
                for item in regular_collection:
                    print(f"   {item}")
                print()
                
            if shiny_collection:
                print("✨ Shiny Auras:")
                for item in shiny_collection:
                    print(f"   {item}")
        
        input("\nPress Enter to continue...")

    def view_biome_info(self):
        print(f"\n🌍 === Biome Information ===")
        print(f"Current Biome: {self.current_biome}")
        print(f"Current Weather: {self.current_weather}")
        print()
        
        print("🗺️ All Biomes:")
        for biome, modifier in self.biomes.items():
            visited = "✅" if biome in self.visited_biomes else "❌"
            current = "📍" if biome == self.current_biome else "  "
            modifier_str = f"{modifier:.1f}x" if modifier != 1.0 else "1.0x"
            print(f"   {current} {biome} (Drop Rate: {modifier_str}) {visited}")
        
        print(f"\n🌤️ Weather Types:")
        for weather in self.weather_types:
            current = "📍" if weather == self.current_weather else "  "
            print(f"   {current} {weather}")
        
        print(f"\n📈 Available Auras in {self.current_biome}:")
        available_auras = [(name, rarity) for name, (rarity, locations) in self.auras.items() 
                          if self.current_biome in locations]
        available_auras.sort(key=lambda x: x[1])
        
        for name, rarity in available_auras:
            owned = self.aura_counts.get(name, 0)
            shiny_owned = self.shiny_aura_counts.get(f"Shiny {name}", 0)
            status = "✅" if owned > 0 else "❌"
            shiny_status = "✨" if shiny_owned > 0 else "  "
            print(f"   {status}{shiny_status} {name} (1 in {rarity:,})")
        
        input("\nPress Enter to continue...")

    def view_active_effects(self):
        print("\n⚡ === Active Effects ===")
        
        now = time.time()
        active_effects = []
        
        for item, expiry in self.item_effects.items():
            if expiry > now:
                remaining = int(expiry - now)
                minutes = remaining // 60
                seconds = remaining % 60
                time_str = f"{minutes}m {seconds}s" if minutes > 0 else f"{seconds}s"
                
                if item in self.item_usage_effects:
                    effect_type, _ = self.item_usage_effects[item]
                    effect_display = effect_type.replace('_', ' ').title()
                    active_effects.append(f"🔥 {item}: {effect_display} ({time_str} remaining)")
                else:
                    active_effects.append(f"🔮 {item}: Unknown Effect ({time_str} remaining)")
        
        if not active_effects:
            print("No active effects.")
        else:
            luck_mult = self.get_luck_multiplier()
            print(f"🍀 Current Luck Multiplier: {luck_mult:.1f}x")
            print()
            for effect in active_effects:
                print(f"   {effect}")
        
        input("\nPress Enter to continue...")

    def show_leaderboard(self):
        print("\n🏆 === Personal Records ===")
        
        if not self.roll_log:
            print("No rolls recorded yet.")
            input("\nPress Enter to continue...")
            return
        
        rarest_regular = None
        rarest_shiny = None
        
        for roll_num, aura_name in self.roll_log:
            if "Shiny" in aura_name:
                base_name = aura_name.replace("Shiny ", "")
                if base_name in self.auras:
                    rarity = self.auras[base_name][0]
                    if rarest_shiny is None or rarity > rarest_shiny[1]:
                        rarest_shiny = (aura_name, rarity, roll_num)
            else:
                if aura_name in self.auras:
                    rarity = self.auras[aura_name][0]
                    if rarest_regular is None or rarity > rarest_regular[1]:
                        rarest_regular = (aura_name, rarity, roll_num)
        
        print(f"🎲 Total Rolls: {self.total_rolls:,}")
        print(f"🎯 Success Rate: {(len(self.roll_log) / max(self.total_rolls, 1) * 100):.2f}%")
        
        if rarest_regular:
            name, rarity, roll_num = rarest_regular
            print(f"🔥 Rarest Regular: {name} (1 in {rarity:,}) - Roll #{roll_num}")
        
        if rarest_shiny:
            name, rarity, roll_num = rarest_shiny
            print(f"✨ Rarest Shiny: {name} (1 in {rarity:,}) - Roll #{roll_num}")
        
        recent_rolls = self.roll_log[-10:] if len(self.roll_log) >= 10 else self.roll_log
        if recent_rolls:
            print(f"\n📋 Recent Rolls:")
            for roll_num, aura_name in recent_rolls:
                if aura_name.startswith("Shiny"):
                    base_name = aura_name.replace("Shiny ", "")
                    rarity = self.auras.get(base_name, (0,))[0]
                    print(f"   Roll #{roll_num}: ✨ {aura_name} (1 in {rarity:,})")
                else:
                    rarity = self.auras.get(aura_name, (0,))[0]
                    print(f"   Roll #{roll_num}: {aura_name} (1 in {rarity:,})")
        
        input("\nPress Enter to continue...")

    def show_help(self):
        print("\n❓ === Game Help ===")
        print("🎲 Rolling: Each roll has different chances based on your current biome")
        print("🌍 Biomes: Different locations have different aura availability and drop rates")
        print("🌤️ Weather: Affects your luck - some weather types are more favorable")
        print("✨ Shiny Auras: Rare variants of regular auras with special visual effects")
        print("🎒 Items: Use items from your inventory to boost your luck temporarily")
        print("🔨 Crafting: Combine materials to create powerful luck-boosting devices")
        print("🎯 Quests: Complete daily objectives to earn rewards")
        print("🏆 Achievements: Unlock titles by reaching various milestones")
        print("🏪 Shop: Buy items using auras you've collected")
        print("💾 Save/Load: Your progress is automatically saved when you save manually")
        print()
        print("💡 Tips:")
        print("   • Explore different biomes to find rare auras")
        print("   • Stack multiple luck items for better results")
        print("   • Check the shop daily for new items")
        print("   • Complete quests for valuable rewards")
        print("   • Weather changes over time - some weather boosts rare finds")
        
        input("\nPress Enter to continue...")

    def show_menu(self):
        self.load_state()
        
        while True:
            self.clear_screen()
            self.refresh_daily()
            self.apply_item_effects()
            self.check_achievements()
            
            title_display = f" - {self.titles_earned[-1]}" if self.titles_earned else ""
            luck_mult = self.get_luck_multiplier()
            luck_display = f" (🍀 {luck_mult:.1f}x)" if luck_mult > 1 else ""
            
            print("=" * 80)
            print(f"🎲 PYTHON RNG ULTIMATE EDITION{title_display} 🎲")
            print("=" * 80)
            print(f"🌍 Biome: {self.current_biome} | 🌤️ Weather: {self.current_weather}{luck_display}")
            print(f"🎯 Total Rolls: {self.total_rolls:,} | 🎭 Unique Auras: {len([a for a in self.aura_counts if self.aura_counts[a] > 0])}/{len(self.auras)}")
            print("=" * 80)
            
            menu_options = [
                "🎲 Roll Once",
                "🎰 Roll Multiple",
                "🎨 View Collection",
                "🌍 Biome Information",
                "🏪 Daily Shop",
                "🎒 Item Inventory",
                "🎯 View Daily Quests",
                "🔨 Crafting Menu",
                "⚡ Active Effects",
                "📊 Roll Statistics",
                "🏆 Personal Records",
                "❓ Help & Tips",
                "💾 Save Game",
                "📁 Load Game",
                "🚪 Exit Game"
            ]
            
            for i, option in enumerate(menu_options, 1):
                print(f"{i:2d}. {option}")
            
            print("=" * 80)
            choice = input("🎮 Choose an option: ").strip()

            if choice == "1":
                self.roll_once()
                input("\nPress Enter to continue...")
            elif choice == "2":
                self.roll_multiple()
            elif choice == "3":
                self.view_collection()
            elif choice == "4":
                self.view_biome_info()
            elif choice == "5":
                self.open_daily_shop()
            elif choice == "6":
                self.view_inventory()
            elif choice == "7":
                self.view_quests()
            elif choice == "8":
                self.craft_item()
            elif choice == "9":
                self.view_active_effects()
            elif choice == "10":
                self.view_roll_stats()
            elif choice == "11":
                self.show_leaderboard()
            elif choice == "12":
                self.show_help()
            elif choice == "13":
                self.save_state()
                input("\nPress Enter to continue...")
            elif choice == "14":
                self.load_state()
                input("\nPress Enter to continue...")
            elif choice == "15":
                print("🎉 Thanks for playing Python RNG Ultimate Edition!")
                print("🌟 Your adventure ends here, but legends never die!")
                print("💫 Come back anytime to continue your collection!")
                break
            else:
                print("❌ Invalid choice. Please try again.")
                time.sleep(1)

def main():
    """Main entry point for the game."""
    try:
        game = PythonRNGGame()
        game.show_menu()
    except KeyboardInterrupt:
        print("\n\n🛑 Game interrupted. Your progress has been saved!")
    except Exception as e:
        print(f"\n❌ An unexpected error occurred: {e}")
        print("🔧 Please report this issue if it persists.")

if __name__ == "__main__":
    main()
