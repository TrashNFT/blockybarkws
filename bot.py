import os
import json
import discord
import csv
from datetime import datetime
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Debug: Print current working directory and env file location
print(f"Current working directory: {os.getcwd()}")
print(f"Looking for .env file in: {os.path.join(os.getcwd(), '.env')}")
print(f"Does .env file exist? {os.path.exists('.env')}")

# Bot configuration
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
OG_ROLE_ID = os.getenv('OG_ROLE_ID')
WL_ROLE_ID = os.getenv('WL_ROLE_ID')

# Debug: Print environment variables
print(f"DISCORD_TOKEN loaded: {'Yes' if DISCORD_TOKEN else 'No'}")
print(f"OG_ROLE_ID loaded: {'Yes' if OG_ROLE_ID else 'No'}")
print(f"WL_ROLE_ID loaded: {'Yes' if WL_ROLE_ID else 'No'}")

# Check if environment variables are loaded
if not DISCORD_TOKEN or not OG_ROLE_ID or not WL_ROLE_ID:
    raise ValueError("Missing required environment variables. Please check your .env file.")

# Convert role IDs to integers
OG_ROLE_ID = int(OG_ROLE_ID)
WL_ROLE_ID = int(WL_ROLE_ID)

# Initialize bot with intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix='!', intents=intents)

# Store wallet addresses in a JSON file
WALLETS_FILE = 'wallets.json'

def load_wallets():
    if os.path.exists(WALLETS_FILE):
        try:
            with open(WALLETS_FILE, 'r') as f:
                data = json.load(f)
                # Ensure the structure is correct
                if not isinstance(data, dict):
                    data = {'og': {}, 'wl': {}}
                if 'og' not in data:
                    data['og'] = {}
                if 'wl' not in data:
                    data['wl'] = {}
                return data
        except json.JSONDecodeError:
            # If the file is corrupted or empty, return default structure
            return {'og': {}, 'wl': {}}
    return {'og': {}, 'wl': {}}

def save_wallets(wallets):
    # Ensure the structure is correct before saving
    if not isinstance(wallets, dict):
        wallets = {'og': {}, 'wl': {}}
    if 'og' not in wallets:
        wallets['og'] = {}
    if 'wl' not in wallets:
        wallets['wl'] = {}
    with open(WALLETS_FILE, 'w') as f:
        json.dump(wallets, f, indent=4)

def has_required_role(member):
    return any(role.id in [OG_ROLE_ID, WL_ROLE_ID] for role in member.roles)

def get_user_role_type(member):
    if any(role.id == OG_ROLE_ID for role in member.roles):
        return 'og'
    elif any(role.id == WL_ROLE_ID for role in member.roles):
        return 'wl'
    return None

async def get_username(bot, user_id):
    try:
        user = await bot.fetch_user(int(user_id))
        return user.name
    except:
        return f"User {user_id}"

class WalletModal(discord.ui.Modal, title='Submit Wallet Address'):
    def __init__(self, callback):
        super().__init__()
        self.callback = callback
        self.address = discord.ui.TextInput(
            label='Solana Wallet Address',
            placeholder='Enter your Solana wallet address...',
            min_length=32,
            max_length=44,
            required=True
        )
        self.add_item(self.address)

    async def on_submit(self, interaction: discord.Interaction):
        await self.callback(interaction, self.address.value)

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    try:
        print("Syncing commands...")
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s):")
        for command in synced:
            print(f"- /{command.name}")
    except Exception as e:
        print(f"Failed to sync commands: {e}")
        print("Please make sure the bot has the correct permissions and try again.")
        print("Required permissions: Send Messages, Embed Links, Use Slash Commands, Read Messages/View Channels, Manage Messages, Read Message History")

class WalletPanel(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Submit Wallet", style=discord.ButtonStyle.green, custom_id="submit_wallet")
    async def submit_wallet(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not has_required_role(interaction.user):
            await interaction.response.send_message("You need either the OG or WL role to submit a wallet address.", ephemeral=True)
            return

        role_type = get_user_role_type(interaction.user)
        if not role_type:
            await interaction.response.send_message("You need either the OG or WL role to submit a wallet address.", ephemeral=True)
            return

        async def handle_submit(interaction: discord.Interaction, address: str):
            wallets = load_wallets()
            user_id = str(interaction.user.id)

            if user_id in wallets[role_type]:
                # Create a confirmation view
                view = discord.ui.View()
                
                async def confirm_callback(interaction: discord.Interaction):
                    wallets[role_type][user_id] = address
                    save_wallets(wallets)
                    await interaction.response.send_message(
                        f"Your {role_type.upper()} wallet address has been successfully updated!\n"
                        f"Old address: `{wallets[role_type][user_id]}`\n"
                        f"New address: `{address}`",
                        ephemeral=True
                    )
                    view.stop()

                async def cancel_callback(interaction: discord.Interaction):
                    await interaction.response.send_message("Wallet address update cancelled.", ephemeral=True)
                    view.stop()

                confirm_button = discord.ui.Button(label="Confirm", style=discord.ButtonStyle.green, custom_id="confirm")
                cancel_button = discord.ui.Button(label="Cancel", style=discord.ButtonStyle.red, custom_id="cancel")

                confirm_button.callback = confirm_callback
                cancel_button.callback = cancel_callback

                view.add_item(confirm_button)
                view.add_item(cancel_button)

                await interaction.response.send_message(
                    f"You already have a {role_type.upper()} wallet address registered: `{wallets[role_type][user_id]}`\n"
                    f"Do you want to replace it with: `{address}`?",
                    view=view,
                    ephemeral=True
                )
                return

            wallets[role_type][user_id] = address
            save_wallets(wallets)
            await interaction.response.send_message(
                f"Your {role_type.upper()} wallet address has been successfully submitted!",
                ephemeral=True
            )

        modal = WalletModal(handle_submit)
        await interaction.response.send_modal(modal)

    @discord.ui.button(label="View Wallet", style=discord.ButtonStyle.blurple, custom_id="view_wallet")
    async def view_wallet(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not has_required_role(interaction.user):
            await interaction.response.send_message("You need either the OG or WL role to view wallet addresses.", ephemeral=True)
            return

        role_type = get_user_role_type(interaction.user)
        if not role_type:
            await interaction.response.send_message("You need either the OG or WL role to view wallet addresses.", ephemeral=True)
            return

        wallets = load_wallets()
        user_id = str(interaction.user.id)

        if user_id not in wallets[role_type]:
            await interaction.response.send_message(f"You haven't submitted a {role_type.upper()} wallet address yet.", ephemeral=True)
            return

        await interaction.response.send_message(
            f"Your {role_type.upper()} wallet address: `{wallets[role_type][user_id]}`",
            ephemeral=True
        )

    @discord.ui.button(label="Remove Wallet", style=discord.ButtonStyle.red, custom_id="remove_wallet")
    async def remove_wallet(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not has_required_role(interaction.user):
            await interaction.response.send_message("You need either the OG or WL role to remove wallet addresses.", ephemeral=True)
            return

        role_type = get_user_role_type(interaction.user)
        if not role_type:
            await interaction.response.send_message("You need either the OG or WL role to remove wallet addresses.", ephemeral=True)
            return

        wallets = load_wallets()
        user_id = str(interaction.user.id)

        if user_id not in wallets[role_type]:
            await interaction.response.send_message(f"You haven't submitted a {role_type.upper()} wallet address yet.", ephemeral=True)
            return

        # Create a confirmation view
        view = discord.ui.View()
        
        async def confirm_callback(interaction: discord.Interaction):
            old_address = wallets[role_type][user_id]
            del wallets[role_type][user_id]
            save_wallets(wallets)
            await interaction.response.send_message(
                f"Your {role_type.upper()} wallet address has been successfully removed!\n"
                f"Removed address: `{old_address}`",
                ephemeral=True
            )
            view.stop()

        async def cancel_callback(interaction: discord.Interaction):
            await interaction.response.send_message("Wallet removal cancelled.", ephemeral=True)
            view.stop()

        confirm_button = discord.ui.Button(label="Confirm", style=discord.ButtonStyle.green, custom_id="confirm")
        cancel_button = discord.ui.Button(label="Cancel", style=discord.ButtonStyle.red, custom_id="cancel")

        confirm_button.callback = confirm_callback
        cancel_button.callback = cancel_callback

        view.add_item(confirm_button)
        view.add_item(cancel_button)

        await interaction.response.send_message(
            f"Are you sure you want to remove your {role_type.upper()} wallet address: `{wallets[role_type][user_id]}`?",
            view=view,
            ephemeral=True
        )

@bot.tree.command(name="create_panel", description="Create a wallet management panel")
async def create_panel(interaction: discord.Interaction):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("You need administrator permissions to create a panel.", ephemeral=True)
        return

    # Check if a panel already exists in this channel
    async for message in interaction.channel.history(limit=10):
        if message.author == bot.user and message.embeds and message.embeds[0].title == "Solana Wallet Management":
            await interaction.response.send_message("A wallet management panel already exists in this channel!", ephemeral=True)
            return

    embed = discord.Embed(
        title="Solana Wallet Management",
        description="Use the buttons below to manage your Solana wallet address.\n\n"
                   "**Submit Wallet**: Submit or update your Solana wallet address\n"
                   "**View Wallet**: View your currently registered wallet address\n"
                   "**Remove Wallet**: Remove your registered wallet address\n\n"
                   "Note: Only users with OG or WL roles can use these features.\n"
                   "Your wallet will be registered under your highest priority role (OG > WL).",
        color=discord.Color.blue()
    )
    
    await interaction.channel.send(embed=embed, view=WalletPanel())
    await interaction.response.send_message("Wallet management panel has been created!", ephemeral=True)

@bot.tree.command(name="export_wallets", description="Export all wallet addresses to a CSV file")
async def export_wallets(interaction: discord.Interaction):
    print(f"Export command triggered by {interaction.user.name}")
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("You need administrator permissions to export wallet data.", ephemeral=True)
        return

    # Create a temporary CSV file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_filename = f"wallet_export_{timestamp}.csv"
    
    wallets = load_wallets()
    
    # Write to CSV
    with open(csv_filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Role', 'User ID', 'Username', 'Wallet Address'])
        
        for role_type in ['og', 'wl']:
            for user_id, wallet_address in wallets[role_type].items():
                username = await get_username(bot, user_id)
                writer.writerow([role_type.upper(), user_id, username, wallet_address])

    # Create summary embed
    og_count = len(wallets['og'])
    wl_count = len(wallets['wl'])
    total_count = og_count + wl_count
    
    embed = discord.Embed(
        title="Wallet Database Export",
        description=f"Total wallets exported: {total_count}\n"
                   f"OG wallets: {og_count}\n"
                   f"WL wallets: {wl_count}",
        color=discord.Color.green()
    )
    embed.set_footer(text=f"Exported at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Send the file and embed
    await interaction.response.send_message(
        embed=embed,
        file=discord.File(csv_filename),
        ephemeral=True
    )

    # Clean up the temporary file
    os.remove(csv_filename)

@bot.tree.error
async def on_app_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.CommandOnCooldown):
        await interaction.response.send_message(f"This command is on cooldown. Try again in {error.retry_after:.2f}s", ephemeral=True)
    elif isinstance(error, app_commands.MissingPermissions):
        await interaction.response.send_message("You don't have permission to use this command.", ephemeral=True)
    else:
        print(f"Command error: {error}")
        await interaction.response.send_message("An error occurred while executing this command. Please try again later.", ephemeral=True)

# Run the bot
if __name__ == "__main__":
    print("Starting bot...")
    bot.run(DISCORD_TOKEN) 