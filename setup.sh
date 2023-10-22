sudo apt install python3-pip ffmpeg chromium chromium-driver
python3 -m venv ./pyenv
source ./pyenv/bin/activate
pip install gtts discord requests asyncio yt_dlp selenium==4.8.2 bs4 pynacl openai flask flask[async] waitress
echo "[]" > waifulist.txt
echo "{}" > plays.json
echo "{}" > haogan.json
echo "{}" > blacklist.json
echo "{}" > langpref.json
mkdir songcache
mkdir datacache
mkdir ytdltemp
python setup.py
