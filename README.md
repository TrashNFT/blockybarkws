# Discord Solana Wallet Management Bot

A Discord bot for managing Solana wallet submissions for users with OG and WL roles.

## Features

- Submit/update Solana wallet addresses
- View registered wallet addresses
- Remove wallet addresses
- Export wallet data to CSV
- Role-based access control (OG and WL roles)

## Setup

1. Clone this repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Create a `.env` file with the following variables:
   ```
   DISCORD_TOKEN=your_discord_token_here
   OG_ROLE_ID=your_og_role_id_here
   WL_ROLE_ID=your_wl_role_id_here
   ```
   - Get your Discord bot token from the [Discord Developer Portal](https://discord.com/developers/applications)
   - Get your role IDs by enabling Developer Mode in Discord and right-clicking the roles

4. Run the bot:
   ```bash
   python main.py
   ```

## Commands

- `/create_panel` - Create a wallet management panel (Admin only)
- `/export_wallets` - Export all wallet addresses to CSV (Admin only)

## Usage

1. Use `/create_panel` in the desired channel to create the wallet management panel
2. Users with OG or WL roles can:
   - Submit their wallet address
   - View their registered wallet
   - Remove their wallet
3. Admins can export all wallet data using `/export_wallets`

## Data Storage

Wallet addresses are stored in `wallets.json` in the following format:
```json
{
    "og": {
        "user_id": "wallet_address"
    },
    "wl": {
        "user_id": "wallet_address"
    }
}
```

## Hosting

This bot is designed to be hosted on Pela.app. Make sure to:
1. Set up your environment variables in the Pela.app dashboard
2. Deploy the repository
3. The bot will automatically start using `main.py` as the entry point

## Requirements
- Python 3.8+
- Discord Bot Token
- OG and WL Role IDs from your Discord server
