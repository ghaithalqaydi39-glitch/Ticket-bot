import os
import discord
from discord.ext import commands
from discord.ui import Button, View

intents = discord.Intents.default()
intents.guilds = True

bot = commands.Bot(command_prefix="!", intents=intents)

class TicketButton(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Create Ticket", style=discord.ButtonStyle.green, custom_id="create_ticket")
    async def create_ticket(self, interaction: discord.Interaction, button: Button):
        guild = interaction.guild
        category_name = "paid cleaning"
        
        # Find or create the category
        category = discord.utils.get(guild.categories, name=category_name)
        if not category:
            category = await guild.create_category(category_name)

        # Prevent duplicate tickets by checking existing channels
        ticket_channel_name = f"ticket-{interaction.user.name}".lower()
        existing_channel = discord.utils.get(category.text_channels, name=ticket_channel_name)
        
        if existing_channel:
            await interaction.response.send_message(f"You already have an open ticket: {existing_channel.mention}", ephemeral=True)
            return

        # Set up channel permissions
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            interaction.user: discord.PermissionOverwrite(view_channel=True, send_messages=True),
            guild.me: discord.PermissionOverwrite(view_channel=True, send_messages=True)
        }

        ticket_channel = await guild.create_text_channel(ticket_channel_name, category=category, overwrites=overwrites)
        await ticket_channel.send(f"Hello {interaction.user.mention}! Welcome to your support ticket. Staff will be with you shortly.")
        await interaction.response.send_message(f"Your ticket has been created: {ticket_channel.mention}", ephemeral=True)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

@bot.command()
@commands.has_permissions(administrator=True)
async def ticketsetup(ctx):
    view = TicketButton()
    await ctx.send("Click the button below to open a ticket for **paid cleaning**:", view=view)

bot.run(os.getenv("DISCORD_TOKEN"))
