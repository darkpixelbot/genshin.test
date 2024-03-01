from telethon import TelegramClient, events, Button
from pymongo import MongoClient
import random
import types
from datetime import datetime

api_id = '26918101'
api_hash = '57d6680f6549e21aca4e93c7a4221d29'
bot_token = '6600246243:AAGu8f5rXaHPnFt-Uh0oRtQ8Ehvi3RzOlKY'
mongo_username = 'GenshinBot'
mongo_password = 'GenshinBotdp'
mongo_cluster_url = 'cluster0.vqtch8p.mongodb.net'
mongo_database_name = 'your_database_name'  # Replace with your actual database name
mongo_uri = f'mongodb+srv://{mongo_username}:{mongo_password}@{mongo_cluster_url}/{mongo_database_name}?retryWrites=true&w=majority'
mongo_client = MongoClient(mongo_uri)
db = mongo_client['your_database_name']
client = TelegramClient('your_session_name', api_id, api_hash)
client.start(bot_token=bot_token)

# MongoDB collection to store user data
users_collection = db['users']


from telethon import events

@client.on(events.NewMessage(pattern='/start'))
async def start_command(event):
    if event.is_private:
        user_id = event.sender_id
        user_record = users_collection.find_one({'_id': user_id})

        if not user_record:
            adventure_start_date = datetime.now().strftime('%Y-%m-%d')

            users_collection.insert_one({
                '_id': user_id,
                'adventure_start_date': adventure_start_date,
                # Other initialization steps...
                # (e.g., setting default characters, initializing AR rank and exp)
            })

            await event.reply("Welcome to the world of Teyvat! Choose your default character:", buttons=[
                [Button.inline("Aether", b"data_Aether"), Button.inline("Lumine", b"data_Lumine")]
            ])
        else:
            await event.reply("You're already in the world of Teyvat!")
    else:
        await event.reply("Please start your adventure in the private messages of the bot.")


@client.on(events.CallbackQuery(data=b'data_Aether'))
async def choose_aether(event):
    user_id = event.sender_id
    user_record = users_collection.find_one({'_id': user_id})
    
    if not user_record:
        users_collection.insert_one({'_id': user_id, 'characters': ["Aether"]})
        await event.edit("You've added Aether to your characters!")
    else:
        characters = user_record.get('characters', [])
        characters.append("Aether")
        users_collection.update_one({'_id': user_id}, {'$set': {'characters': characters}})
        await event.edit("You've added Aether to your characters!")

@client.on(events.CallbackQuery(data=b'data_Lumine'))
async def choose_lumine(event):
    user_id = event.sender_id
    user_record = users_collection.find_one({'_id': user_id})
    
    if not user_record:
        users_collection.insert_one({'_id': user_id, 'characters': ["Lumine"]})
        await event.edit("You've added Lumine to your characters!")
    else:
        characters = user_record.get('characters', [])
        characters.append("Lumine")
        users_collection.update_one({'_id': user_id}, {'$set': {'characters': characters}})
        await event.edit("You've added Lumine to your characters!")

@client.on(events.NewMessage(pattern='/mycharacters'))
async def mycharacters_command(event):
    user_id = event.sender_id
    user_record = users_collection.find_one({'_id': user_id})

    if user_record:
        characters = user_record.get('characters', [])

        if characters:
            unique_characters = set(characters)  # Remove duplicates
            characters_text = "\n".join([f"• {character}" for character in unique_characters])
            message_text = (
                "🌟 **Your Characters** 🌟\n"
                "┏━━━━━━━━━━━━━━━━━━━━━━━┓\n"
                f"{characters_text}\n"
                "┗━━━━━━━━━━━━━━━━━━━━━━━┛\n\n"
            )
            await event.reply(message_text)
        else:
            await event.reply("No characters chosen yet.")
    else:
        await event.respond("You haven't started the journey yet. Type /start to begin.")
@client.on(events.NewMessage(pattern='/gacha'))
async def gacha_command(event):
    user_id = event.sender_id
    user_record = users_collection.find_one({'_id': user_id})

    if user_record:
        characters = user_record.get('characters', [])
        new_character = get_random_character()

        # Check if the character is not already in the list
        if new_character not in characters:
            characters.append(new_character)
            users_collection.update_one({'_id': user_id}, {'$set': {'characters': characters}})
            await event.reply(f"Congratulations! You obtained a new character: {new_character}")
        else:
            # If the character is already in the list, give primogems instead
            primogems = 160
            # Update user's primogems count in the database
            users_collection.update_one({'_id': user_id}, {'$inc': {'primogems': primogems}})
            await event.reply(f"You already have {new_character}! You've received {primogems} primogems instead.")
    else:
        await event.reply("You haven't started the journey yet. Type /start to begin.")

@client.on(events.CallbackQuery())
async def team_callback_handler(event):
    user_id = event.sender_id
    user_record = get_user_record(user_id)

    if user_record:
        team = user_record.get('team', [])
        characters = user_record.get('characters', [])

        if event.data == b'add_character':
            await add_character_menu(event, user_id, team, characters)
        elif event.data == b'remove_character':
            await remove_character_menu(event, user_id, team)
        elif event.data.startswith(b'add_'):
            await add_character(event, user_id, team)
        elif event.data.startswith(b'remove_'):
            await remove_character(event, user_id, team)
        elif event.data == b'cancel':
            await event.edit("Operation canceled.")
          # Refresh the team display
    else:
        await event.answer("You haven't started the journey yet. Type /start to begin.")

def get_user_record(user_id):
    return users_collection.find_one({'_id': user_id})

@client.on(events.NewMessage(pattern='/myteam'))
async def myteam_command(event):
    try:
        if not event.message.buttons:
            user_id = event.sender_id
            user_record = get_user_record(user_id)

            if user_record:
                team = user_record.get('team', [])

                if team:
                    unique_team = set(team)  # Remove duplicates
                    team_text = "\n".join([f"• {character}" for character in unique_team])
                    message_text = (
                        "🌟 **Your Team** 🌟\n"
                        "┏━━━━━━━━━━━━━━━━━━━━━━━┓\n"
                        f"{team_text}\n"
                        "┗━━━━━━━━━━━━━━━━━━━━━━━┛\n\n"
                    )
                    buttons = [
                        [Button.inline("Add Character", b"add_character"), Button.inline("Remove Character", b"remove_character")]
                    ]
                    await event.reply(f"{message_text}\nManage your team:", buttons=buttons)
                else:
                    await show_add_remove_buttons(event, user_id)
            else:
                await event.respond("You haven't started the journey yet. Type /start to begin.")
    except Exception as e:
        print(f"Error in myteam_command: {e}")

async def handle_callback(event):
    user_id = event.sender_id
    user_record = get_user_record(user_id)

    if user_record:
        team = user_record.get('team', [])
        characters = user_record.get('characters', [])

        if isinstance(event, events.CallbackQuery):
            if event.data == b'add_character':
                await add_character_menu(event, user_id, team, characters)
            elif event.data == b'remove_character':
                await remove_character_menu(event, user_id, team)
            elif event.data.startswith(b'add_'):
                await add_character(event, user_id, team)
            elif event.data.startswith(b'remove_'):
                await remove_character(event, user_id, team)
            elif event.data == b'cancel':
                await event.edit("Operation canceled.")
            else:
                await myteam_command(event)  # Refresh the team display
        elif isinstance(event, events.NewMessage):
            await myteam_command(event)  # Refresh the team display
    else:
        await event.answer("You haven't started the journey yet. Type /start to begin.")

async def add_character(event, user_id, team):
    try:
        character_to_add = event.data.split(b'_')[1].decode('utf-8')

        if len(team) < 4 and character_to_add not in team:
            team.append(character_to_add)
            users_collection.update_one({'_id': user_id}, {'$set': {'team': team}})
            user_record = users_collection.find_one({'_id': user_id})
            updated_team = user_record.get('team', [])

            # Remove duplicate characters
            updated_team = list(set(updated_team))

            team_text = "🌟 **Your Team** 🌟\n"
            "┏━━━━━━━━━━━━━━━━━━━━━━━┓\n"

            if updated_team:
                team_text += "\n".join([f"• {character}" for character in updated_team])
            else:
                team_text += "┃  No characters in your team yet.  ┃"

            team_text += "\n┗━━━━━━━━━━━━━━━━━━━━━━━┛\n\n"

            buttons = [
                [Button.inline("Add Character", b"add_character"), Button.inline("Remove Character", b"remove_character")]
            ]
            await event.edit(f"{team_text}Manage your team:", buttons=buttons)
        else:
            await event.answer("You can't add more characters to your team.")
    except Exception as e:
        print(f"Error in add_character: {e}")
        await event.answer("An error occurred while processing your request.")
async def add_character_menu(event, user_id, team, characters):
    try:
        if len(team) < 4:
            available_characters = [character for character in characters if character not in team]

            if available_characters:
                buttons = [
                    [Button.inline(character, f"add_{character}")]
                    for character in available_characters
                ]
                await event.edit("Select a character to add to your team:", buttons=buttons)
            else:
                await event.answer("No characters available to add.")
        else:
            await event.answer("Your team is full. Remove a character to add a new one.")
    except Exception as e:
        print(f"Error in add_character_menu: {e}")
        await event.answer("An error occurred while processing your request.")

async def remove_character_menu(event, user_id, team):
    if team:
        await event.edit("Select a character to remove from your team:", buttons=[
            [Button.inline(character, f"remove_{character}") for character in team]
        ])
    else:
        await event.answer("Your team is empty. Add a character to remove one.")

async def remove_character(event, user_id, team):
    try:
        character_to_remove = event.data.split(b'_')[1].decode('utf-8')

        if character_to_remove in team:
            team.remove(character_to_remove)
            users_collection.update_one({'_id': user_id}, {'$set': {'team': team}})
            user_record = users_collection.find_one({'_id': user_id})
            updated_team = user_record.get('team', [])

            # Remove duplicate characters
            updated_team = list(set(updated_team))

            team_text = "🌟 **Your Team** 🌟\n"
            "┏━━━━━━━━━━━━━━━━━━━━━━━┓\n"

            if updated_team:
                team_text += "\n".join([f"• {character}" for character in updated_team])
            else:
                team_text += "┃  No characters in your team yet.  ┃"

            team_text += "\n┗━━━━━━━━━━━━━━━━━━━━━━━┛\n\n"

            buttons = [
                [Button.inline("Add Character", b"add_character"), Button.inline("Remove Character", b"remove_character")]
            ]
            await event.edit(f"{team_text}Manage your team:", buttons=buttons)
        
    except Exception as e:
        print(f"Error in remove_character: {e}")
        await event.answer("An error occurred while processing your request.")

async def show_add_remove_buttons(event, user_id):
    try:
        user_record = users_collection.find_one({'_id': user_id})
        characters = user_record.get('characters', [])
        team = user_record.get('team', [])

        if characters:
            add_buttons = [
                [Button.inline(f"Add {character}", f"add_{character}")]
                for character in characters
                if character not in team
            ]
            remove_buttons = [
                [Button.inline(f"Remove {character}", f"remove_{character}")]
                for character in team
            ]

            if add_buttons:
                add_buttons.append([Button.inline("Cancel", b"cancel")])
            else:
                add_buttons = [[Button.inline("There is no characters to add", b"dummy")]]

            if remove_buttons:
                remove_buttons.append([Button.inline("Cancel", b"cancel")])
                # Check if the "No characters to remove" button is present
                if any(button[0].text == "No characters to remove" for button in remove_buttons):
                    buttons = add_buttons  # If yes, only show add buttons
                else:
                    buttons = add_buttons + remove_buttons
            else:
                buttons = add_buttons

            await event.respond("Manage your team:", buttons=buttons)
        else:
            await event.answer("There are no characters available. Type /start to choose your default character.")
    except Exception as e:
        print(f"Error in show_add_remove_buttons: {e}")
        await event.answer("An error occurred while processing your request.")

def get_random_character():

    # Add your logic to obtain a random character here
    characters = ["Amber", "Kaeya", "Lisa"]
    
    return random.choice(characters)

@client.on(events.NewMessage(pattern='/myinfo'))
async def myinfo_command(event):
    user_id = event.sender_id
    user_record = users_collection.find_one({'_id': user_id})

    if user_record:
        adventure_rank = user_record.get('adventure_rank', 1)
        ar_exp_required = calculate_next_rank_exp(adventure_rank)

        message_text = (
            "🌟 **Adventurer's Profile** 🌟\n"
            "┏━━━━━━━━━━━━━━━━━━━━━━━┓\n"
            f"┃  **Adventure Rank (AR):** {adventure_rank}\n"
            f"┣━━━━━━━━━━━━━━━━━━━━━━━┫\n"
            f"┃  **AR Experience:**      {user_record.get('ar_exp', 'N/A')} / {ar_exp_required}\n"
            f"┣━━━━━━━━━━━━━━━━━━━━━━━┫\n"
            f"┃  **Adventure Started On:** {user_record.get('adventure_start_date', 'N/A')}\n"
            "┗━━━━━━━━━━━━━━━━━━━━━━━┛\n\n"
        )

        await event.reply(message_text)
    else:
        await event.reply("You haven't started the journey yet. Type /start to begin.")

def calculate_next_rank_exp(current_rank):
    # Assuming the base next rank exp is 1000 and it doubles for each rank
    base_exp = 1000
    return base_exp * (2 ** (current_rank - 1))


aether_stats = {
    "element": "Anemo",
    "level": 1,
    "base_hp": 1100,  # Example value, replace with the desired value
    "base_defense": 60,  # Example value, replace with the desired value
    "base_atk": 80,  # Example value, replace with the desired value
    "crit_rate": 0,
    "crit_dmg": 0,
    "weapon": {
        "type": "Sword"  # Specify the type of weapon Aether can use
    }
}

amber_stats = {
    "element": "Pyro",
    "level": 1,
    "base_hp": 1000,  # Example value, replace with the desired value
    "base_defense": 50,  # Example value, replace with the desired value
    "base_atk": 90,  # Example value, replace with the desired value
    "crit_rate": 0,
    "crit_dmg": 0,
    "weapon": {
        "type": "Bow"  # Specify the type of weapon Amber can use
    }
}

kaeya_stats = {
    "element": "Cryo",
    "level": 1,
    "base_hp": 1050,  # Example value, replace with the desired value
    "base_defense": 55,  # Example value, replace with the desired value
    "base_atk": 85,  # Example value, replace with the desired value
    "crit_rate": 0,
    "crit_dmg": 0,
    "weapon": {
        "type": "Sword"  # Specify the type of weapon Kaeya can use
    }
}

lisa_stats = {
    "element": "Electro",
    "level": 1,
    "base_hp": 1100,  # Example value, replace with the desired value
    "base_defense": 60,  # Example value, replace with the desired value
    "base_atk": 80,  # Example value, replace with the desired value
    "crit_rate": 0,
    "crit_dmg": 0,
    "weapon": {
        "type": "Catalyst"  # Specify the type of weapon Lisa can use
    }
}

lumine_stats = {
    "element": "Anemo",
    "level": 1,
    "base_hp": 1080,  # Example value, replace with the desired value
    "base_defense": 58,  # Example value, replace with the desired value
    "base_atk": 87,  # Example value, replace with the desired value
    "crit_rate": 0,
    "crit_dmg": 0,
    "weapon": {
        "type": "Sword"  # Specify the type of weapon Lumine can use
    }
}


@client.on(events.NewMessage(pattern='/character'))
async def character_command(event):
    try:
        # Extract character name from the command
        command_args = event.raw_text.split()
        if len(command_args) != 2:
            await event.reply("Invalid command. Use /character <character_name>")
            return

        character_name = command_args[1].capitalize()  # Assuming character names are capitalized

        # Check if the character exists in the user's collection
        user_id = event.sender_id
        user_record = users_collection.find_one({'_id': user_id})

        if not user_record:
            await event.reply("You haven't started the journey yet. Type /start to begin.")
            return

        characters = user_record.get('characters', [])
        if character_name not in characters:
            await event.reply(f"You don't have the character {character_name}.")
            return

        # Fetch character stats based on character_name
        character_stats = globals().get(f"{character_name.lower()}_stats")
        if character_stats is None:
            await event.reply(f"Character stats for {character_name} not found.")
            return

        # Retrieve the equipped weapon's name and stats for the character
        user_weapons = user_record.get('weapons', [])
        equipped_weapon = next((weapon for weapon in user_weapons
                               if weapon.get('character_name') == character_name.lower() and weapon.get('equipped')), None)

        
        

        # Construct the message text
        message_text = (
            f"🌟 **Character Info: {character_name}** 🌟\n"
            "┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓\n"
            f"┃  **Element:** {character_stats.get('element', 'N/A')} \n"
            f"┃  **Level:**  {character_stats.get('level', 'N/A')}\n"
            f"┃  **Max HP:** {character_stats.get('base_hp', 'N/A')}\n"
            f"┃  **Base ATK:** {character_stats.get('base_atk', 'N/A')} \n"
            f"┃  **Defense:** {character_stats.get('base_defense', 'N/A')} \n"
            f"┃  **Crit Rate:** {character_stats.get('crit_rate', 'N/A')}%\n"
            f"┃  **Crit Damage:** {character_stats.get('crit_dmg', 'N/A')}%\n"
            f"┃  **Weapon Type:** {character_stats['weapon'].get('type', 'N/A')}\n"
            f"┃  **Weapon Equipped:** {equipped_weapon['weapon_name'] if equipped_weapon else 'None'}\n"  # Display the equipped weapon or 'None' if not equipped
            "┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛\n\n"
        )

        # Add buttons for Change Weapon, Remove Weapon, and Level Up
        buttons = [
            [Button.inline("Change Weapon", f"change_weapon_{character_name.lower()}"),
             Button.inline("Remove Weapon", f"remove_weapon_{character_name.lower()}"),
             Button.inline("Level Up", f"level_up_{character_name.lower()}")]
        ]

        await event.reply(message_text, buttons=buttons)

    except Exception as e:
        print(f"Error in character_command: {e}")
        await event.answer("An error occurred while processing your request.")


@client.on(events.CallbackQuery())
async def button_callback_handler(event):
    try:
        data_string = event.data.decode('utf-8')
        command_args = data_string.split('_')

        if len(command_args) > 1:
            action = command_args[0]

            if action == 'change':
                await change_weapon(event)
            elif action == 'remove':
                await remove_weapon_callback(event)
            elif action == 'choose':
                await choose_handler_callback(event)
            elif action == 'level':
                await level_up(event)

    except Exception as e:
        print(f"Error in button_callback_handler: {e}")

# Add a flag to check if removal is in progress
removal_in_progress = False
async def remove_weapon_callback(event):
    global removal_in_progress
    try:
        # Check if removal is already in progress
        if removal_in_progress:
            await event.answer("Removal in progress. Please wait.")
            return

        removal_in_progress = True

        user_id = event.sender_id
        data_string = event.data.decode('utf-8')
        command_args = data_string.split('_')
        character_name = command_args[2].capitalize()

        # Fetch the equipped weapon for the character
        user_record = users_collection.find_one({'_id': user_id})
        if not user_record:
            raise ValueError("User record not found.")

        user_weapons = user_record.get('weapons', [])
        
        # Check if the list is not empty and the index is within bounds
        if user_weapons:
            equipped_weapon_index = next((index for index, weapon in enumerate(user_weapons)
                                          if weapon.get('character_name') == character_name.lower() and weapon.get('equipped')), None)

            if equipped_weapon_index is not None and 0 <= equipped_weapon_index < len(user_weapons):
                # Fetch character stats based on character_name
                character_stats = globals().get(f"{character_name.lower()}_stats")
                if character_stats is None:
                    raise ValueError(f"Character stats for {character_name} not found.")

                # Fetch the chosen weapon's stats
                chosen_weapon_stats = available_weapons.get(user_weapons[equipped_weapon_index]['weapon_name'], {})

                # Roll back 'base_atk_increment' if applied
                if 'base_atk_increment' in chosen_weapon_stats:
                    character_stats['base_atk'] -= chosen_weapon_stats['base_atk_increment']

                # Roll back 'base_hp' if applied
                if 'base_hp' in chosen_weapon_stats:
                    character_stats['base_hp'] -= chosen_weapon_stats['base_hp']

                # Roll back 'base_defense' if applied
                if 'base_defense' in chosen_weapon_stats:
                    character_stats['base_defense'] -= chosen_weapon_stats['base_defense']

                # Roll back 'crit_rate' if applied
                if 'crit_rate' in chosen_weapon_stats:
                    character_stats['crit_rate'] -= chosen_weapon_stats['crit_rate']

                # Roll back 'crit_dmg' if applied
                if 'crit_dmg' in chosen_weapon_stats:
                    character_stats['crit_dmg'] -= chosen_weapon_stats['crit_dmg']

                # Clear the flags indicating applied stats
                users_collection.update_one(
                    {'_id': user_id, 'weapons.character_name': character_name.lower()},
                    {'$unset': {
                        'weapons.$.base_atk_increment_applied': '',
                        'weapons.$.base_hp_applied': '',
                        'weapons.$.base_defense_applied': '',
                        'weapons.$.crit_rate_applied': '',
                        'weapons.$.crit_dmg_applied': '',
                    }}
                )

                # Remove the equipped weapon from the weapons list
                del user_weapons[equipped_weapon_index]

                # Update user record with the new weapons list
                users_collection.update_one(
                    {'_id': user_id},
                    {'$set': {'weapons': user_weapons}}
                )

                # Construct the updated message text
                message_text = (
                    f"🌟 **Character Info: {character_name}** 🌟\n"
                    "┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓\n"
                    f"┃  **Element:** {character_stats.get('element', 'N/A')} \n"
                    f"┃  **Level:**  {character_stats.get('level', 'N/A')}\n"
                    f"┃  **Max HP:** {character_stats.get('base_hp', 'N/A')}\n"
                    f"┃  **Base ATK:** {character_stats.get('base_atk', 'N/A')} \n"
                    f"┃  **Defense:** {character_stats.get('base_defense', 'N/A')} \n"
                    f"┃  **Crit Rate:** {character_stats.get('crit_rate', 'N/A')}%\n"
                    f"┃  **Crit Damage:** {character_stats.get('crit_dmg', 'N/A')}%\n"
                    f"┃  **Weapon Type:** {character_stats['weapon'].get('type', 'N/A')}\n"
                    f"┃  **Weapon Equipped:** None\n"  # No weapon is equipped after removal
                    "┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛\n\n"
                )

                # Add buttons for Change Weapon and Level Up
                buttons = [
                    [Button.inline("Change Weapon", f"change_weapon_{character_name.lower()}"),
                    Button.inline("Level Up", f"level_up_{character_name.lower()}"),
                    Button.inline("Remove Weapon", f"remove_weapon_{character_name.lower()}")]
                ]

                await event.edit(message_text, buttons=buttons)
                return  # Exit the function to prevent further execution

        # If no weapons or invalid index, handle accordingly
        raise ValueError("No weapons added to remove.")

    except ValueError as ve:
        # Handle specific exceptions
        await event.answer(str(ve))
    except Exception:
        # Handle other exceptions without printing the error
        await event.answer("An error occurred while processing your request.")
    finally:
        removal_in_progress = False  # Reset the flag after processing



async def change_weapon(event):
    try:
        user_id = event.sender_id
        command_args = event.data.decode('utf-8').split('_')
        character_name = command_args[2]

        # Set the changing_weapon flag to True to prevent multiple triggers
        users_collection.update_one(
            {'_id': user_id},
            {'$set': {'changing_weapon': True}}
        )

        # Fetch character stats based on character_name
        character_stats = globals().get(f"{character_name.lower()}_stats")
        if character_stats is None:
            raise ValueError(f"Character stats for {character_name} not found.")

        # Fetch available weapons for the character
        available_character_weapons = [
            weapon_name for weapon_name, weapon_info in available_weapons.items()
            if weapon_info.get('weapon_type') == character_stats['weapon'].get('type')
        ]

        # Fetch equipped weapon for the character
        user_record = users_collection.find_one({'_id': user_id})
        equipped_weapon = next((weapon['weapon_name'] for weapon in user_record.get('weapons', [])
                                if weapon.get('character_name') == character_name.lower() and weapon.get('equipped')), None)

        # Exclude the equipped weapon from the list
        available_character_weapons = [weapon for weapon in available_character_weapons if weapon != equipped_weapon]

        buttons = [
            [Button.inline(weapon_name, f"choose_weapon_{character_name}_{weapon_name}")]
            for weapon_name in available_character_weapons
        ]

        buttons.append([Button.inline("Cancel", "cancel")])

        await event.edit(f"Choose a weapon for {character_name.capitalize()}:", buttons=buttons)
    except Exception as e:
        print(f"Error in change_weapon: {e}")
        await event.answer("An error occurred while processing your request.")

async def choose_handler_callback(event):
    try:
        user_id = event.sender_id
        data_string = event.data.decode('utf-8')
        command_args = data_string.split('_')
        character_name = command_args[2].capitalize()
        chosen_weapon = command_args[3]

        # Fetch character stats based on character_name
        character_stats = globals().get(f"{character_name.lower()}_stats")
        if character_stats is None:
            raise ValueError(f"Character stats for {character_name} not found.")

        # Fetch the chosen weapon's stats
        chosen_weapon_stats = available_weapons.get(chosen_weapon, {})
        if not chosen_weapon_stats:
            raise ValueError(f"Stats for the chosen weapon {chosen_weapon} not found.")

        # Update the equipped weapon in the user's record
        user_record = users_collection.find_one({'_id': user_id})
        if not user_record:
            raise ValueError("User record not found.")

        # Update or add the weapon to the weapons list
        user_weapons = user_record.get('weapons', [])

        # Check if the user already has a weapon for the character
        existing_weapon = next((weapon for weapon in user_weapons if weapon.get('character_name') == character_name.lower()), None)

        if existing_weapon and existing_weapon.get('equipped'):
            # If the weapon is already equipped, do nothing
            await event.answer("Weapon already equipped.")
            return

        if existing_weapon:
            # Update the existing weapon
            existing_weapon['equipped'] = True
            existing_weapon['weapon_name'] = chosen_weapon
        else:
            # Add a new weapon entry
            new_weapon = {'character_name': character_name.lower(), 'equipped': True, 'weapon_name': chosen_weapon}
            user_weapons.append(new_weapon)

        # Update user record with the new weapons list
        users_collection.update_one(
            {'_id': user_id},
            {'$set': {'weapons': user_weapons}}
        )

        # Update character stats with the chosen weapon's attributes
        if 'base_atk_increment' in chosen_weapon_stats:
            character_stats['base_atk'] += chosen_weapon_stats['base_atk_increment']

        if 'base_hp' in chosen_weapon_stats:
            character_stats['base_hp'] += chosen_weapon_stats['base_hp']  # Fix here
         #write for other stats also to update 
        # Update user record with the modified character stats
        users_collection.update_one(
            {'_id': user_id},
            {'$set': {'characters.$[character].stats': character_stats}},
            array_filters=[{'character.name': character_name}]
        )

        # Fetch available weapons for the character
        available_character_weapons = [
            weapon_name for weapon_name, weapon_info in available_weapons.items()
            if weapon_info.get('weapon_type') == character_stats['weapon'].get('type')
        ]

        # Exclude the equipped weapon from the list
        available_character_weapons = [weapon for weapon in available_character_weapons if weapon != chosen_weapon]

        # Construct the updated message text
        message_text = (
            f"🌟 **Character Info: {character_name}** 🌟\n"
            "┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓\n"
            f"┃  **Element:** {character_stats.get('element', 'N/A')} \n"
            f"┃  **Level:**  {character_stats.get('level', 'N/A')}\n"
            f"┃  **Max HP:** {character_stats.get('base_hp', 'N/A')}\n"
            f"┃  **Base ATK:** {character_stats.get('base_atk', 'N/A')} \n"
            f"┃  **Defense:** {character_stats.get('base_defense', 'N/A')} \n"
            f"┃  **Crit Rate:** {character_stats.get('crit_rate', 'N/A')}%\n"
            f"┃  **Crit Damage:** {character_stats.get('crit_dmg', 'N/A')}%\n"
            f"┃  **Weapon Type:** {character_stats['weapon'].get('type', 'N/A')}\n"
            f"┃  **Weapon Equipped:** {chosen_weapon}\n"
            "┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛\n\n"
        )

        # Add buttons for Change Weapon and Level Up
        buttons = [
            [Button.inline("Change Weapon", f"change_weapon_{character_name.lower()}"),
             Button.inline("Level Up", f"level_up_{character_name.lower()}"),
             Button.inline("Remove Weapon", f"remove_weapon_{character_name.lower()}")]
        ]

        await event.edit(message_text, buttons=buttons)

    except Exception as e:
        print(f"Error in choose_handler_callback: {e}")
        await event.answer("An error occurred while processing your request.")


available_weapons_key = 'available_weapons'
available_weapons = {}

# Fetch available_weapons from the existing documents in users_collection
for user_doc in users_collection.find({available_weapons_key: {'$exists': True}}):
    available_weapons = user_doc[available_weapons_key]

# Default stats for Dull Blade
default_dull_blade_stats = {
    "weapon_type": "Sword",
    "weapon_level": 1,
    "base_atk_increment": 23,
    "max_level": 70,
    # Add more stats if needed
}

# Add default Dull Blade stats to available_weapons
available_weapons.setdefault("Dull Blade", default_dull_blade_stats)

@client.on(events.NewMessage(pattern='/gacha_weapon'))
async def gacha_weapon_command(event):
    try:
        weapon_names = ["Dull Blade", "Hunter's Bow", "Apprentice's Notes", "Waster Greatsword"]

        # Print details before the gacha_weapon command
        print("Before gacha_weapon:")
        print("available_weapons:", available_weapons)

        # Simulate obtaining a new weapon with random stats
        new_weapon_name = random.choice(weapon_names)

        if new_weapon_name == "Dull Blade":
            weapon_type = "Sword"
        elif new_weapon_name == "Hunter's Bow":
            weapon_type = "Bow"
        elif new_weapon_name == "Apprentice's Notes":
            weapon_type = "Catalyst"
        elif new_weapon_name == "Waster Greatsword":
            weapon_type = "Claymore"
        else:
            weapon_type = "Unknown Type"

        new_weapon_stats = {
            "weapon_type": weapon_type,
            "weapon_level":1,
            "base_atk_increment": 23,
            "max_level": 70 ,
            # Add more stats if needed
        }

        # Update the available_weapons in the users_collection
        users_collection.update_one(
            {'_id': event.sender_id},
            {'$set': {available_weapons_key: {new_weapon_name: new_weapon_stats}}},
            upsert=True
        )

        # Update the available_weapons dictionary
        available_weapons[new_weapon_name] = new_weapon_stats

        # Print details after the gacha_weapon command
        print("After gacha_weapon:")
        print("available_weapons:", available_weapons)

        # ... rest of your logic ...

        await event.reply(f"You obtained a new weapon: {new_weapon_name}!")

    except Exception as e:
        print(f"Error in gacha_weapon_command: {e}")
        await event.reply("An error occurred while processing your request.")



@client.on(events.NewMessage(pattern='/myweapons'))
async def myweapons_command(event):
    try:
        # Print details before the myweapons command
        print("Before myweapons:")
        print("available_weapons:", available_weapons)

        # Construct the message text
        message_text = "🗡️ **Your Weapons** 🗡️\n"
        for weapon_name, weapon_info in available_weapons.items():
            emoji = ""
            weapon_type = weapon_info.get("weapon_type", "Unknown")
            if weapon_type == "Sword":
                emoji = "⚔️"
            elif weapon_type == "Bow":
                emoji = "🏹"
            elif weapon_type == "Catalyst":
                emoji = "🔮"
            elif weapon_type == "Claymore":
                emoji = "🔨"
            else:
                emoji = "❓"

            message_text += f"{emoji} {weapon_name}\n"

        # Print details after the myweapons command
        print("After myweapons:")
        print("available_weapons:", available_weapons)

        await event.reply(message_text)

    except Exception as e:
        print(f"Error in myweapons_command: {e}")
        await event.reply("An error occurred while processing your request.")


@client.on(events.NewMessage(pattern='/weapon'))
async def weapon_command(event):
    try:
        # Extract weapon name from the command
        command_args = event.raw_text.split()
        if len(command_args) < 2:
            await event.reply("Invalid command. Use /weapon <weapon_name>")
            return

        # Join the command arguments to handle spaces in weapon names
        weapon_name = ' '.join(command_args[1:])

        # Check if the weapon exists in available_weapons
        weapon_info = available_weapons.get(weapon_name)
        if not weapon_info:
            await event.reply(f"Weapon not found: {weapon_name}")
            return

        # Construct the message text with weapon stats
        message_text = f"🗡️ **Weapon Stats: {weapon_name}** 🗡️\n"
        message_text += f"┏━━━━━━━━━━━━━━━━━━━━━━━━━━━┓\n"
        message_text += f"┃  **Type:** {weapon_info.get('weapon_type', 'N/A')}\n"
        message_text += f"┃  **Level:** {weapon_info.get('weapon_level', 'N/A')}\n"
        message_text += f"┃  **Base ATK Increment:** {weapon_info.get('base_atk_increment', 'N/A')}\n"
        message_text += f"┃  **Max Level:** {weapon_info.get('max_level', 'N/A')}\n"
        message_text += f"┗━━━━━━━━━━━━━━━━━━━━━━━━━━━┛\n\n"

        # Add the "Upgrade This Weapon" button
        button = Button.inline("Upgrade This Weapon", f"upgrade_weapon_{weapon_name}")
        await event.reply(message_text, buttons=[[button]])

    except Exception as e:
        print(f"Error in weapon_command: {e}")
        await event.answer("An error occurred while processing your request.")


client.run_until_disconnected()
