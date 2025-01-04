sudo apt update && sudo apt upgrade -y
sudo apt install software-properties-common -y
sudo add-apt-repository ppa:deadsnakes/ppa -y
sudo apt install python3-pip python3.12-dev python3.12-venv -y
sudo apt install python3-tinydb -y
sudo apt update -y
git clone https://github.com/HeyFang/bombsquad-modded-server-scripts.git
cd bombsquad-modded-server-scripts
tmux new -s 43210
chmod +x ballisticakit_server
chmod +x dist/ballisticakit_headless
./ballisticakit_server