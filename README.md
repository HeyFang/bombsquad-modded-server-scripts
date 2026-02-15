# About
- Game party server for <a href="https://www.froemling.net/apps/bombsquad">BombSquad</a>
- Modded Linux x86_64 server, build 1.7.61 (API v9)
- For the vanilla server, see <a href="https://ballistica.net/downloads">ballistica.net/downloads</a>

# Install and setup
Follow the steps below on a Debian/Ubuntu-based system.

## 1) System packages

- Update and install prerequisites (includes tmux):
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y software-properties-common git tmux
sudo add-apt-repository ppa:deadsnakes/ppa -y
sudo apt update
sudo apt install -y python3-pip python3.13 python3.13-dev python3.13-venv
```

## 2) Get the files

```bash
git clone https://github.com/HeyFang/bombsquad-modded-server-scripts.git
cd bombsquad-modded-server-scripts
```

## 3) Configure

- Make a config.toml:
```bash
sudo cp config_template.toml config.toml
```
- Edit the `config.toml` according to your needs.
- Tip: remove the `#` to uncomment any required setting.
- Make sure to add pb-ids of admins in config.toml


## 4) Permissions

- Make the server binary executable (avoid using chmod 777):
```bash
sudo chmod +x ballisticakit_server dist/ballisticakit_headless
```

# Run the game server

## Start server

```bash
tmux new -s 43210
sudo ./ballisticakit_server
```

- Session name `43210` is arbitrary; pick any name you like.
- Press `Ctrl+b` then `d` to detach and keep it running in the background.
- To list sessions later: `tmux ls`.
- Note: Running as root is not required; prefer running as a normal user unless binding privileged ports.

## Reconnect to the session

```bash
tmux attach -t 43210
```

## Stop the server

- Inside the session, press `Ctrl+c` to stop `ballisticakit_server`.
- Then end the tmux session:
```bash
tmux kill-session -t 43210
```

# Discord bot
- check README.md in dist/ba_data/python/bautils/Discord/README.md




