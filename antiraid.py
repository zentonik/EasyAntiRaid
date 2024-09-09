import discord
from discord.ext import commands
from collections import defaultdict
import time

intents = discord.Intents.default()
intents.guilds = True
intents.guild_messages = True
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

user_actions = defaultdict(list)

MAX_ACTIONS = 2  # Max actions before user gets kicked out
TIME_ACTION = 10  # Time window in seconds
EXCLUDED_USERS = {123456789012345678}  # Replace with actual user IDs

deleted_channels = {}
deleted_roles = {}

@bot.event
async def on_ready():
    guild = bot.guilds[0]
    bot_member = guild.get_member(bot.user.id)
    print(f"Bot permissions: {bot_member.guild_permissions}")
    print(f"Bot is ready and logged in as {bot.user.name}!")

@bot.event
async def on_guild_channel_delete(channel):
    deleted_channels[channel.id] = {
        'name': channel.name,
        'category': channel.category_id,
        'permissions': channel.overwrites,
        'position': channel.position,
        'type': channel.type
    }
    await handle_action(channel.guild, 'channel')

@bot.event
async def on_guild_role_delete(role):
    deleted_roles[role.id] = {
        'name': role.name,
        'permissions': role.permissions,
        'color': role.color,
        'hoist': role.hoist,
        'mentionable': role.mentionable
    }
    await handle_action(role.guild, 'role')

@bot.event
async def on_guild_channel_create(channel):
    await handle_action(channel.guild, 'channel_creation')

@bot.event
async def on_guild_role_create(role):
    await handle_action(role.guild, 'role_creation')

async def handle_action(guild, action_type):
    current_time = time.time()
    
    async for entry in guild.audit_logs(limit=1, action=discord.AuditLogAction.channel_delete if action_type == 'channel' else
                                       discord.AuditLogAction.role_delete if action_type == 'role' else
                                       discord.AuditLogAction.channel_create):
        user = entry.user
        user_id = user.id
        print(f"Audit log entry found: User ID {user_id} performed action")

        if user_id == bot.user.id or user_id in EXCLUDED_USERS:
            print(f"Skipping action for user: {user.name} ({user_id})")
            return

        if user_id in user_actions:
            user_actions[user_id] = [t for t in user_actions[user_id] if t > current_time - TIME_ACTION]
        user_actions[user_id].append(current_time)
        
        if len(user_actions[user_id]) > MAX_ACTIONS:
            if guild.me.guild_permissions.kick_members:
                try:
                    member = await guild.fetch_member(user_id)
                    print(f"Kicking user: {member.name} ({member.id})")
                    await member.kick(reason='Punished for deleting or creating channels or roles.')
                    await member.send('You have been kicked from the server for deleting or creating channels or roles.')
                except discord.NotFound:
                    print(f"User with ID {user_id} not found in the guild.")
                except discord.Forbidden:
                    print("Bot does not have permission to kick members or send messages.")
                except discord.HTTPException as e:
                    print(f"HTTP error occurred: {e}")
            else:
                print("Bot does not have permission to kick members.")
            
            if action_type == 'channel' and deleted_channels:
                await recreate_channel(guild)
            elif action_type == 'role' and deleted_roles:
                await recreate_role(guild)

async def recreate_channel(guild):
    for channel_id, channel_data in list(deleted_channels.items()):
        try:
            print(f"Restoring channel: {channel_data['name']}")
            category = discord.utils.get(guild.categories, id=channel_data['category'])
            new_channel = await guild.create_text_channel(
                name=channel_data['name'],
                category=category,
                overwrites=channel_data['permissions'],
                position=channel_data['position']
            )
            print(f"Channel {new_channel.name} restored successfully.")
            del deleted_channels[channel_id]
        except discord.HTTPException as e:
            print(f"Failed to restore channel: {e}")

async def recreate_role(guild):
    for role_id, role_data in list(deleted_roles.items()):
        try:
            print(f"Restoring role: {role_data['name']}")
            new_role = await guild.create_role(
                name=role_data['name'],
                permissions=role_data['permissions'],
                color=role_data['color'],
                hoist=role_data['hoist'],
                mentionable=role_data['mentionable']
            )
            print(f"Role {new_role.name} restored successfully.")
            del deleted_roles[role_id]
        except discord.HTTPException as e:
            print(f"Failed to restore role: {e}")

bot.run('TOKEN')  # Replace TOKEN with your bot token
