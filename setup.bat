python -m venv .\pyenv
.\pyenv\Scripts\Activate
pip install gtts discord requests asyncio yt-dlp aiofile
pip install pynacl openai Flask Flask[async] waitress
echo [] > waifulist.txt
echo {} > plays.json
echo {} > haogan.json
echo {} > atrikey.json
echo {} > blacklist.json
echo {} > langpref.json
mkdir songcache
mkdir datacache
mkdir ytdltemp
python setup.py
git clone https://github.com/Binaryify/NeteaseCloudMusicApi.git
cd NeteaseCloudMusicApi
npm install
cd ..
python setup.py
