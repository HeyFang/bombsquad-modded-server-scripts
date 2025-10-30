# Discord Bot
These steps assume you are in the root `bombsquad-modded-server-scripts` directory.

The bot and the game server should be run in **separate** `tmux` sessions.

## 1) Configure the Bot
Before you run the bot, you **must** add your Discord Bot Token and other settings to your `bot.py` file.
- Open `bot.py`.
- Add your token and Guild ID.

## 2) Setup (One-time only)
This creates a dedicated Python environment for the bot.

- Create the virtual environment (using the python3.13 you installed):
```bash
python3.13 -m venv .venv
```

### Activate the environment:
```Bash
source .venv/bin/activate
```
Your terminal prompt should now show (.venv).

### Install the required library:
```Bash
pip install -U discord.py
```
You can now leave the environment for now:

```Bash
deactivate
```

## 3) Run the Bot
Start a new, separate tmux session for the bot:
```Bash
tmux new -s bs_bot
```
Inside the tmux session, activate the venv and run the bot script:

```Bash
source .venv/bin/activate
python staged/dist/ba_data/python/bautils/discord/bot.py
```
The bot should now be running.

### Press `Ctrl+b` then `d` to detach and keep it running in the background.

### Reconnect and Stop the Bot
To check on the bot later:
```Bash
tmux attach -t bs_bot
```

### To stop the bot (inside the session): Press Ctrl+c to stop the Python script. Then end the tmux session:
```Bash
tmux kill-session -t bs_bot
```
