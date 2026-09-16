import os
import discord
from discord import app_commands
from discord.ext import commands
from discord.ui import Button, View

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

class CloseTicketView(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Close Ticket", style=discord.ButtonStyle.red, custom_id="close_ticket")
    async def close_ticket(self, interaction: discord.Interaction, button: Button):
        await interaction.response.defer(ephemeral=True)
        await interaction.channel.delete()

class TicketButton(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Create Ticket", style=discord.ButtonStyle.green, custom_id="create_ticket")
    async def create_ticket(self, interaction: discord.Interaction, button: Button):
        await interaction.response.defer(ephemeral=True)
        
        guild = interaction.guild
        category_name = "paid cleaning"
        
        category = discord.utils.get(guild.categories, name=category_name)
        ticket_channel_name = f"ticket-{interaction.user.name}".lower()
        
        if category:
            existing_channel = discord.utils.get(category.text_channels, name=ticket_channel_name)
        else:
            existing_channel = discord.utils.get(guild.text_channels, name=ticket_channel_name)
        
        if existing_channel:
            await interaction.followup.send(f"You already have an open ticket: {existing_channel.mention}", ephemeral=True)
            return

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            interaction.user: discord.PermissionOverwrite(view_channel=True, send_messages=True),
            guild.me: discord.PermissionOverwrite(view_channel=True, send_messages=True)
        }

        ticket_channel = await guild.create_text_channel(ticket_channel_name, category=category, overwrites=overwrites)
        
        staff_pings = "<@1517950895566880809> <@1399482147961704448>"
        await ticket_channel.send(f"Hello {interaction.user.mention}! Welcome to your support ticket. {staff_pings} will be with you shortly.", view=CloseTicketView())
        await interaction.followup.send(f"Your ticket has been created: {ticket_channel.mention}", ephemeral=True)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} slash command(s).")
    except Exception as e:
        print(e)

@bot.tree.command(name="ticketsetup", description="Send the paid cleaning ticket panel")
@app_commands.checks.has_permissions(administrator=True)
async def ticketsetup(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    view = TicketButton()
    await interaction.followup.send("Click the button below to open a ticket for **paid cleaning**:", view=view)

@bot.tree.command(name="nuke", description="Delete every single channel in the server")
@app_commands.checks.has_permissions(administrator=True)
async def nuke(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    for channel in interaction.guild.channels:
        try:
            await channel.delete()
        except Exception as e:
            print(f"Failed to delete channel {channel.name}: {e}")

@bot.tree.command(name="leave", description="Make the bot leave the server")
@app_commands.checks.has_permissions(administrator=True)
async def leave(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    await interaction.guild.leave()

bot.run(os.getenv("DISCORD_TOKEN"))
