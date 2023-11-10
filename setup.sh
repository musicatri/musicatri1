sudo apt install python3-pip ffmpeg
python3 -m venv ./pyenv
source ./pyenv/bin/activate
pip install gtts discord requests asyncio yt_dlp pynacl openai flask flask[async] waitress
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
cd ..
python setup.py
