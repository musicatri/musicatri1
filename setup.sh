sudo apt install python3 python3-pip ffmpeg  python3-venv git -y
sudo apt-get update
sudo apt-get install -y ca-certificates curl gnupg
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://deb.nodesource.com/gpgkey/nodesource-repo.gpg.key | sudo gpg --dearmor -o /etc/apt/keyrings/nodesource.gpg
NODE_MAJOR=20
echo "deb [signed-by=/etc/apt/keyrings/nodesource.gpg] https://deb.nodesource.com/node_$NODE_MAJOR.x nodistro main" | sudo tee /etc/apt/sources.list.d/nodesource.list
sudo apt-get update
sudo apt-get install nodejs  -y
python3 -m venv pyenv
./pyenv/bin/python3 -m pip install gtts discord requests asyncio yt_dlp pynacl openai flask flask[async] waitress aiofiles flask_discord prettytable
echo "[]" > waifulist.txt
echo "{}" > plays.json
echo "{}" > haogan.json
echo "{}" > blacklist.json
echo "{}" > langpref.json
mkdir songcache
mkdir datacache
mkdir ytdltemp
git clone https://github.com/Binaryify/NeteaseCloudMusicApi.git
cd NeteaseCloudMusicApi
npm install
cd .. -y
python3 setup.py
