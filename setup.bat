choco install -y python ffmpeg git nodejs
python -m venv pyenv
pyenv\Scripts\Activate
pyenv\Scripts\pip install gtts discord requests asyncio yt_dlp pynacl openai flask waitress aiofiles flask_discord prettytable pymongo flask[async]
mkdir songcache
mkdir songcache\ytdltemp
git clone https://github.com/musicatri/NeteaseCloudMusicApi.git
cd NeteaseCloudMusicApi
npm install
cd ..
pyenv\Scripts\python setup.py