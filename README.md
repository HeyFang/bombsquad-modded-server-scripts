# About
- Game Party Server for <a href="https://www.froemling.net/apps/bombsquad">Bomb Squad</a> Game
- This is a Modded Version of BombSquad linux_x86_64_server, build 1.7.37 API v9
- You can find Vanilla Version (Basic Original) <a href="https://ballistica.net/downloads">here</a>

## <a href="https://github.com/HeyFang/bombsquad-modded-server-scripts/blob/main/Features.md#Features">Features (click here)</a>

# Instructions for Installation & Setup
To set up a cloud server, <a href="https://github.com/HeyFang/bombsquad-modded-server-scripts/blob/main/CloudSetup.md#Instructions">click here</a>. If you already have Ubuntu ready or prefer to run it locally on Ubuntu, you can skip to the next step.

## Installation
- Copy the command below exactly as it is, paste it into the Ubuntu terminal, and execute it.
```
sudo add-apt-repository ppa:deadsnakes/ppa -y
sudo apt update && sudo apt upgrade -y
sudo apt install software-properties-common python3-pip python3.12-dev python3.12-venv python3-tinydb git -y
git clone https://github.com/HeyFang/bombsquad-modded-server-scripts.git
cd bombsquad-modded-server-scripts
chmod +x ballisticakit_server dist/ballisticakit_headless
```
- This should install all the necessary packages
  
## Setup
- Open the <a href="https://github.com/HeyFang/bombsquad-modded-server-scripts/blob/main/config.toml">config.toml</a> file and configure it as you like. Make sure that you remove the `#` at the beginning of any line you want to uncomment, which makes changes effective.
- Open <a href="https://github.com/HeyFang/bombsquad-modded-server-scripts/blob/main/dist/ba_root/mods/admin.json">admin.json</a> and add PB-IDs of Admins, who can use in-game <a href="https://github.com/HeyFang/bombsquad-modded-server-scripts/blob/main/Features.md#Commands">server commands</a>

# Instructions for Running Game Server
## Start Server
- Run the following command to start server:
```
tmux new -s 43210
./ballisticakit_server
```
- We named the running tmux as `43210` to connect with it later if needed
- You can replace `43210` with any name of your choice.
- If you forget the session name, run `tmux ls` to list all tmux sessions.
- Use `Ctrl + b` then `d` to exit session and keep it running in background

## Re-Connecting
- If you are not inside Tmux Session `43210`,
- Run `tmux ls` to view all running sessions and confirm `43210` is active
- Run the following command to connect back
```
tmux attach -t 43210
```

## Stop Server
- If you are not inside Tmux Session `43210`, <a href="https://github.com/HeyFang/bombsquad-modded-server-scripts/blob/main/README.md#Re-Connecting">Reconnect as explained above</a>
- Use `Ctrl + c` to stop running server party `(ballisticakit_server)`
- Run the following cmd to terminate tmux session `43210`
```
tmux kill-session -t 43210
```
