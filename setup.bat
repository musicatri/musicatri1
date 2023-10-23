python -m venv .\pyenv
.\pyenv\Scripts\Activate
pip install gtts discord requests asyncio yt-dlp==2021.6.6
pip install selenium==4.8.2 bs4 pynacl openai Flask Flask[async] waitress
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
