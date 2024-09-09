# Discord Bot for Monitoring and Restoring Channels and Roles

This is a Python-based Discord bot that monitors actions related to channel and role deletions or creations in a Discord server. It can kick users who perform these actions excessively and restore deleted channels and roles.

## Features

* Monitors and logs channel and role deletions or creations.
* Automatically kicks users who exceed the maximum allowed actions.
* Restores deleted channels and roles.
* Excludes specified users from getting kicked.

## Installation

1. **Clone the repository**:
    ```bash
    git clone https://github.com/zentonik/EasyAntiRaid.git
    cd EasyAntiRaid
    ```

2. **Install the required libraries**:
    ```bash
    pip install discord.py
    ```

3. **Configure the bot**:
    * Replace `'TOKEN'` with your actual bot token in the `bot.run('TOKEN')` line.
    * Update the `EXCLUDED_USERS` set with the user IDs you want to exclude from kicking.

## Usage

1. **Run the bot**:
    ```bash
    python bot.py
    ```

2. **Grant the necessary permissions**:
    Make sure the bot has the following permissions in your Discord server:
    * `Kick Members`
    * `Manage Channels`
    * `Manage Roles`
    * `View Audit Log`

## Explanation

The bot works by listening to certain events:

* **on_ready**: Triggered when the bot has connected to the server.
* **on_guild_channel_delete**: Triggered when a channel is deleted.
* **on_guild_role_delete**: Triggered when a role is deleted.
* **on_guild_channel_create**: Triggered when a channel is created.
* **on_guild_role_create**: Triggered when a role is created.

When these events occur, the bot logs the action and checks if the user who performed it has exceeded the maximum allowed actions (`MAX_ACTIONS`). If they have, and they are not in the `EXCLUDED_USERS` list, the bot will attempt to kick them and restore the deleted channel or role.

## Configuration

* **`MAX_ACTIONS`**: Set the maximum number of actions allowed before a user is kicked. Default is `2`.
* **`TIME_ACTION`**: Set the time window (in seconds) within which the actions are counted. Default is `10` seconds.
* **`EXCLUDED_USERS`**: A set of user IDs that are excluded from being kicked.
