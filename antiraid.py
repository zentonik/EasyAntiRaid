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

MAX_ACTIONS = 2 # max actions until user gets kicked out
TIME_ACTION = 10  # Time ( if user deletes something in 10 seconds he will get kicked. )

EXCLUDED_USERS = {123456789012345678}  # Replace with actual user IDs

@bot.event
async def on_ready():
    print(f'Bot {bot.user.name} is logged in and ready!')

@bot.event
async def on_guild_channel_delete(channel):
    await handle_action(channel.guild, 'channel')

@bot.event
async def on_guild_role_delete(role):
    await handle_action(role.guild, 'role')

@bot.event
async def on_guild_channel_create(channel):
    await handle_action(channel.guild, 'channel_creation')

async def handle_action(guild, action_type):
    current_time = time.time()
    
    async for entry in guild.audit_logs(limit=1, action=discord.AuditLogAction.channel_delete if action_type == 'channel' else
                                       discord.AuditLogAction.role_delete if action_type == 'role' else
                                       discord.AuditLogAction.channel_create):
        user = entry.user
        user_id = user.id
        print(f"Audit log entry found: User ID {user_id} performed action")

        if user_id in user_actions:
            user_actions[user_id] = [t for t in user_actions[user_id] if t > current_time - TIME_ACTION]
        user_actions[user_id].append(current_time)
        
        if len(user_actions[user_id]) > MAX_ACTIONS and user_id not in EXCLUDED_USERS:
            
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
                print("Completed.")

@bot.event
async def on_guild_role_create(role):
    await handle_action(role.guild, 'role_creation')

bot.run('TOKEN') # YOUR_TOKEN
