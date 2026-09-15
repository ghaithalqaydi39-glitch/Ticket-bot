import os
import discord
from discord import app_commands
from discord.ext import commands
from discord.ui import Button, View

intents = discord.Intents.default()
intents.guilds = True

bot = commands.Bot(command_prefix="!", intents=intents)

class CloseTicketView(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Close Ticket", style=discord.ButtonStyle.red, custom_id="close_ticket")
    async def close_ticket(self, interaction: discord.Interaction, button: Button):
        await interaction.response.send_message("Closing this ticket in 3 seconds...", ephemeral=True)
        await interaction.channel.delete()

class TicketButton(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Create Ticket", style=discord.ButtonStyle.green, custom_id="create_ticket")
    async def create_ticket(self, interaction: discord.Interaction, button: Button):
        guild = interaction.guild
        category_name = "paid cleaning"
        
        # Use existing category only
        category = discord.utils.get(guild.categories, name=category_name)
        if not category:
            await interaction.response.send_message(f"Error: The category '{category_name}' does not exist on this server.", ephemeral=True)
            return

        ticket_channel_name = f"ticket-{interaction.user.name}".lower()
        existing_channel = discord.utils.get(category.text_channels, name=ticket_channel_name)
        
        if existing_channel:
            await interaction.response.send_message(f"You already have an open ticket: {existing_channel.mention}", ephemeral=True)
            return

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            interaction.user: discord.PermissionOverwrite(view_channel=True, send_messages=True),
            guild.me: discord.PermissionOverwrite(view_channel=True, send_messages=True)
        }

        ticket_channel = await guild.create_text_channel(ticket_channel_name, category=category, overwrites=overwrites)
        
        # Find user hidden_2pulse to ping
        ping_target = discord.utils.get(guild.members, name="hidden_2pulse")
        ping_text = ping_target.mention if ping_target else "@hidden_2pulse"

        await ticket_channel.send(f"Hello {interaction.user.mention}! Welcome to your support ticket. {ping_text} will be with you shortly.", view=CloseTicketView())
        await interaction.response.send_message(f"Your ticket has been created: {ticket_channel.mention}", ephemeral=True)

@bot.event
async def on_ready():
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} slash command(s).")
    except Exception as e:
        print(e)
    print(f"Logged in as {bot.user}")

@bot.tree.command(name="ticketsetup", description="Send the paid cleaning ticket panel")
@app_commands.checks.has_permissions(administrator=True)
async def ticketsetup(interaction: discord.Interaction):
    view = TicketButton()
    await interaction.response.send_message("Click the button below to open a ticket for **paid cleaning**:", view=view)

bot.run(os.getenv("DISCORD_TOKEN"))
