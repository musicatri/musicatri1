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
key["songctladdr"]=input("enter the ip/domain name for the webui(leave blank for localhost)\n")
key["fcaddress"]=input("enter the aliyun function compute address to proxy netease cloud music songs(leave blank to use the one provided by author)\n")
if key["fcaddress"] == "":
    key["fcaddress"]="https://proxy-proxy-sfqarhkqrf.cn-beijing.fcapp.run/"

if key["songctladdr"]=="":
    key["songctladdr"]="localhost"
key["songctladdr"]="http://"+key["songctladdr"]+":"+str(key["serverport"])+"/songctl?id="

key["NeteaseCloudMusicApiPort"]="3000"
key["NeteaseCloudMusicUsername"]=input("Enter your netease cloud music cellphone number to enable playing VIP limited songs\n")
key["NeteaseCloudMusicPassword"]=input("Enter your netease cloud music password\n")
with codecs.open(dirpath + "./atrikey.json", encoding='utf-8', mode='w') as f:
    f.write(json.dumps(key))
print("finished! please run musicatri.py to start the bot")
