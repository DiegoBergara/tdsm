# Security

## Access control

The bot restricts access to **allowlisted users only**. Set the environment variable `ALLOWED_USER_IDS` to a comma-separated list of Telegram user IDs. Only those users can send commands or run code in sessions. All other users receive an "Access denied" message.

To find your Telegram user ID, use [@userinfobot](https://t.me/userinfobot) or similar.

## Trust model

- The bot runs with the same privileges as the user who starts it. Commands executed in tmux run as that user.
- There is no per-chat or per-session authentication beyond the initial allowlist. Any allowlisted user can use any session if they know its name.
- Telegram’s API is used to identify the user; the bot relies on Telegram’s authentication. Do not expose the bot token.

## Recommendations

- Run the bot in a dedicated user or container with minimal privileges.
- Keep `TELEGRAM_BOT_TOKEN` and `ALLOWED_USER_IDS` in environment or a secure secret store, not in code.
- Use a dedicated SQLite file with restricted permissions if multiple processes might access the host.
