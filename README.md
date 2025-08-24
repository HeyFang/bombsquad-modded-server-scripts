# About
- Game Party Server for <a href="https://www.froemling.net/apps/bombsquad">Bomb Squad</a> Game
- This is a Modded Version of BombSquad linux_x86_64_server, build 1.7.48 API v9
- You can find Vanilla Version (Basic Original) <a href="https://ballistica.net/downloads">here</a>

# Instructions for Installation & Setup
Run Following steps on ur system terminal

## Installation

- Initialize newly created server and install all dependencies
```
sudo apt update && sudo apt upgrade -y
sudo add-apt-repository ppa:deadsnakes/ppa -y
sudo apt install software-properties-common python3-pip python3.12-dev python3.12-venv python3-tinydb git -y
sudo apt update && sudo apt upgrade -y
```
- Clone the repo
```
git clone https://github.com/HeyFang/bombsquad-modded-server-scripts.git
```
- Make files executable n editable
```
sudo chmod -R 777 bombsquad-modded-server-scripts
```
- Rename config_template.toml to config.toml and edit it according to your needs
(make sure u remove '#' to uncomment the the required line)

# Instructions for Running Game Server
## Start Server
- Run the following command to start server:
```
cd bombsquad-modded-server-scripts/staged
tmux new -s 43210
sudo ./ballisticakit_server
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


