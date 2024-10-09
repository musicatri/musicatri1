sudo apt update
sudo apt install ffmpeg  python3-venv git ca-certificates curl gnupg -y
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://deb.nodesource.com/gpgkey/nodesource-repo.gpg.key | sudo gpg --dearmor -o /etc/apt/keyrings/nodesource.gpg
NODE_MAJOR=20
echo "deb [signed-by=/etc/apt/keyrings/nodesource.gpg] https://deb.nodesource.com/node_$NODE_MAJOR.x nodistro main" | sudo tee /etc/apt/sources.list.d/nodesource.list
sudo apt update
sudo apt install nodejs  -y
python3 -m venv pyenv
./pyenv/bin/python3 -m pip install gtts discord requests asyncio yt_dlp pynacl openai flask waitress aiofiles flask_discord prettytable
./pyenv/bin/python3 -m pip install flask[async] pymongo
mkdir songcache
mkdir ytdltemp
git clone https://gitlab.com/Binaryify/neteasecloudmusicapi.git
cd neteasecloudmusicapi
npm install
cd ..
python3 setup.py
