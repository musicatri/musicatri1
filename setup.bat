@REM python -m venv .\pyenv
@REM .\pyenv\Scripts\Activate
@REM pip install gtts discord requests asyncio yt-dlp aiofile
@REM pip install pynacl openai Flask Flask[async] waitress prettytable
echo [] > waifulist.txt
echo {} > plays.json
echo {} > haogan.json
echo {} > atrikey.json
echo {} > blacklist.json
echo {} > langpref.json
mkdir songcache
mkdir datacache
mkdir ytdltemp
@REM python setup.py
@REM git clone https://github.com/Binaryify/NeteaseCloudMusicApi.git
@REM cd NeteaseCloudMusicApi
@REM npm install
@REM cd ..
@REM python setup.py
