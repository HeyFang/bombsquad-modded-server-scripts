# About
- Game Party Server for <a href="https://www.froemling.net/apps/bombsquad">BombSquad</a> Game
- This is a Modded Server for Version linux_x86_64_server 1.7.37 API v9
- You can find Original Non-Modded Version <a href="https://ballistica.net/downloads">here</a>
## <a href="https://github.com/HeyFang/bombsquad-modded-server-scripts/blob/main/Features.md#Features">Features (click here)</a>

# Instructions for Installation & Setup
- To Make a Cloud Server, <a href="https://github.com/HeyFang/bombsquad-modded-server-scripts/blob/main/CloudSetup.md#Instructions">click here</a> OR skip to next step if you are already ready with ubuntu OR if you just want to run in local Ubuntu
## Installation
- Copy The following command text as is and paste it in ubuntu terminal & run it
```
sudo add-apt-repository ppa:deadsnakes/ppa -y
sudo apt update && sudo apt upgrade -y
sudo apt install software-properties-common python3-pip python3.12-dev python3.12-venv python3-tinydb git -y
git clone https://github.com/HeyFang/bombsquad-modded-server-scripts.git
cd bombsquad-modded-server-scripts
chmod +x ballisticakit_server dist/ballisticakit_headless
```
- This Should have Installed all the necessary Packages
## Setup
- Open <a href="https://github.com/HeyFang/bombsquad-modded-server-scripts/blob/main/config.toml">config.toml</a> and configure it as you like (Made sure to remove `#` at the start of the line to uncomment it which makes changes effective)
- Open <a href="https://github.com/HeyFang/bombsquad-modded-server-scripts/blob/main/dist/ba_root/mods/admin.json">admin.json</a> and Add Admins, who can use in-game <a href="https://github.com/HeyFang/bombsquad-modded-server-scripts/blob/main/Feaures.md#Commands">server commands</a>
# Instructions for Running Game Server
## Start Server
- Run the following command to start server:
```
tmux new -s 43210
./ballisticakit_server
```
- we named the running tmux as `43210` to connect with it later if needed
  - you can use any name as you want.
  - run `tmux ls` to list running tmux, in case u forget the name used before.
## Stop Server
- If you not inside Tmux Session `43210`, <a href="https://github.com/HeyFang/bombsquad-modded-server-scripts/blob/main/README.md#Re-Connecting">Reconnect as explained below</a>
- Use `Ctrl + C` to stop running server party `(ballisticakit_server)`
- Use `Ctrl + D` or run `exit` to exit Tmux Session
- Run the following cmd to Close/Stop Tmux Session `43210`
```
tmux kill-session -t 43210
```
## Re-Connecting
- If you are not inside Tmux Session `43210`,
  - Run `tmux ls` to view running tmux to make sure `43210` is online
  - Run the following command to connect back
  ```
  tmux attach -t 43210
  ```