import ast
from os.path import dirname
from os.path import realpath
import codecs
import json
dirpath = dirname(realpath(__file__)) + "/"
key={}
key["name"]=[]
a=input("please enter the command prefix of the bot\n")
key["name"].append(a)
key["key"]=input("please enter the bot token\n")
key["gptkey"]=input("please enter the openai api key (leave blank if you do not wish to use that feature)\n ")
c=input("enable developer mode?(y/n)\n")
if c == 'y':
    key["devmode"]=True
else:
    key["devmode"]=False
key["ytdlproxy"]=input("enter proxy address for yt-dlp(leave blank if you don't need it)\n")
key["serverport"]=int(input("enter the port of the webui\n"))
key["songctladdr"]=input("enter the ip/domain name only for the webui(leave blank for localhost)\n") or "localhost"
key["songctlhost"]="http://"+key["songctladdr"]+":"+str(key["serverport"])
key["songctladdr"]=key["songctlhost"]+"/songctl?id="
key["NeteaseCloudMusicApiPort"]="3000"
key["NeteaseCloudMusicUsername"]=input("Enter your netease cloud music cellphone number to enable playing VIP limited songs\n")
key["NeteaseCloudMusicPassword"]=input("Enter your netease cloud music password\n")
key["DISCORD_CLIENT_ID"]=input("Enter your discord client id\n")
key["DISCORD_CLIENT_SECRET"]=input("Enter your discord client secret\n")
key["songcachedir"]=input("Enter the directory for song cache (default: ./songcache/)\n") or "./songcache/"
key["mongourl"]=input("Enter the mongodb url\n (default: mongodb://localhost:27017/)\n") or "mongodb://localhost:27017/"
key["NeteaseCloudMusicApiUseExisting"]=input("enter the address of the existing netease cloud music api server (leave blank start one locally)\n") or ""

key["fcaddress"]=input("enter the aliyun function compute address to proxy netease cloud music songs(leave blank to use the one provided by author)\n") or "https://proxy-proxy-sfqarhkqrf.cn-beijing.fcapp.run/"

with codecs.open(dirpath + "./atrikey.json", encoding='utf-8', mode='w') as f:
    f.write(json.dumps(key, indent=2))
print("finished! please run musicatri.py to start the bot")
