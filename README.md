# Solana Wallet Collection Discord Bot

A Discord bot that manages Solana wallet submissions for users with specific roles (OG and WL).

## Features
- Role-based wallet submission (OG and WL roles)
- One wallet address per user
- Secure storage of wallet addresses
- Easy-to-use commands
- Export functionality for administrators

## Setup Instructions

1. Install Python 3.8 or higher
2. Install required packages:
   ```
   pip install -r requirements.txt
   ```
3. Create a `.env` file in the root directory with the following:
   ```
   DISCORD_TOKEN=your_discord_bot_token
   OG_ROLE_ID=your_og_role_id
   WL_ROLE_ID=your_wl_role_id
   ```
4. Run the bot:
   ```
   python bot.py
   ```

## Commands
- `/create_panel` - Create a wallet management panel (Admin only)
- `/export_wallets` - Export all wallet addresses to CSV (Admin only)

## Requirements
- Python 3.8+
- Discord Bot Token
- OG and WL Role IDs from your Discord server #   d i s c o r d - b o t  
 