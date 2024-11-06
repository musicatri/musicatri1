# -*- coding: utf-8 -*-\
import subprocess
from os.path import dirname
from os.path import realpath
import codecs
import json
import requests
import time
from os.path import exists
from urllib.parse import quote
dirpath = dirname(realpath(__file__)) + "/"
with codecs.open(dirpath + "atrikey.json", encoding='utf-8', mode='r') as r:
    # aaa=r.read().encode().decode('utf-8-sig') win7 workaround
    key = json.loads(r.read())
    name = key["name"]
    print("主人我的云控制链接是"+key["songctladdr"])
if key["NeteaseCloudMusicApiUseExisting"]:
    cloudmusicapiurl = key["NeteaseCloudMusicApiUseExisting"]
    print("主人，亚托莉已经帮你连接了自定义的网易云音乐API喵~")
else:
    subprocess.Popen(["node",dirpath+"NeteaseCloudMusicApi/app.js"])
    cloudmusicapiurl = 'http://127.0.0.1:' + key["NeteaseCloudMusicApiPort"]
    print("主人，亚托莉已经帮你启动了网易云音乐API喵~")

if not exists(dirpath + "cookie.txt"):
    while(1):
        try:
            time.sleep(10)
            loginres = requests.get(
                cloudmusicapiurl + "/login/cellphone?phone=" + key["NeteaseCloudMusicUsername"] + "&password=" + key[
                    "NeteaseCloudMusicPassword"])
            cookie=quote(loginres.json()['cookie'])

            with codecs.open(dirpath + "cookie.txt", encoding='utf-8', mode='w') as f:
                f.write(cookie)
            print("主人，我已经登录网易云了并且保存了cookie喵~，cookie是" + quote(
                loginres.json()['cookie']))
            break
        except Exception as e:
            print(e)
            print("主人，我登录网易云失败了喵~，请检查你的账号密码是否正确喵~ 将在十秒种后重试喵~")
else:
    with codecs.open("cookie.txt", encoding='utf-8', mode='r') as r:
        cookie = r.read()

from os import system as cmd
from prettytable import PrettyTable
from prettytable import PLAIN_COLUMNS
from flask import Flask, send_from_directory,  redirect, url_for,request,send_file,render_template, session
from flask_discord import DiscordOAuth2Session, requires_authorization, Unauthorized
import ast
import asyncio
import os
import platform
import random
import traceback
import aiofiles
from datetime import date
from functools import partial
import discord
import yt_dlp
from discord.ext import commands
from discord.ext import tasks
from gtts import gTTS
import openai
import threading
import json
from mutagen.mp3 import MP3
from waitress import serve
import aiohttp
import pymongo
app = Flask(__name__)
print("主人，我的工作目录是 "+dirpath+" 喵~")
#http://musicatrictl.akutan445.com:4949/songctl?id=
if platform.system() == "Windows":
    cmd("chcp 936")

dbclient=pymongo.MongoClient(key["mongourl"])
db=dbclient["musicatri"]
songdata=db["songdata"]
globalconfig=db["globalconfig"]
userdata=db["userdata"]


app.secret_key = "asfsaghfdghrsghertyh"  # Replace with a secure secret key
#if key["devmode"]: bad idea
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "true"
# Discord OAuth2 configuration
app.config['DISCORD_CLIENT_ID'] = key["DISCORD_CLIENT_ID"]
app.config['DISCORD_CLIENT_SECRET'] = key["DISCORD_CLIENT_SECRET"]
app.config['DISCORD_REDIRECT_URI'] = key["songctlhost"]+"/account/callback"
print("Oauth2 redirect uri是"+key["songctlhost"]+"/account/callback"+"喵~")
discordauth = DiscordOAuth2Session(app)


translations={}
for file in os.listdir(dirpath+"langfiles"):
    if file.find(".json") != -1:
        with codecs.open(dirpath + "langfiles/"+file, encoding="utf-8", mode="r") as f:
            translations[file]=json.loads(f.read())


ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': key["songcachedir"]+'ytdltemp/%(id)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0',  # bind to ipv4 since ipv6 addresses cause issues sometimes
#    'download_archive':dirpath+'ytdldownloads.txt'
}
if key["ytdlproxy"]:
    ytdl_format_options['proxy']=key['ytdlproxy']
print("我的名字是" + str(name) + "。谢谢主人给我起这么好听的名字！")

ytdl = yt_dlp.YoutubeDL(ytdl_format_options)


# Storing user data
tokens={}
openai.api_key = key["gptkey"]
queues = {}
adding = {}
cs = {}
players = {}
waifucd = {}
intents = discord.Intents.all()
atri = commands.AutoShardedBot(command_prefix=name, intents=intents,help_command=None)
scm={}
songduration={}
cstarttime={}
pausetime={}

@app.route('/profile-test')
def home():
    user = discordauth.fetch_user()
    gl={}
    for g in user.fetch_guilds():
        gl[g.id]=g.name
    print(gl)
    return f"""
        <html>
        <head>
        <title>{user.name}</title>
        </head>
        <body>
        <img src='{user.avatar_url or user.default_avatar_url}' />
        <br>
        Guilds:{str(gl)}
        <br>
        <code></code>
        <br />
        </body>
        </html>
        """

@app.route('/getprofile')
def getprofile():
    try:
        user=discordauth.fetch_user()
        userjson=user.to_json()
        avatar=user.avatar_url or user.default_avatar_url
        userjson["avatar"] = avatar
        userjson["login"] = True
        return json.dumps(userjson)
    except:
        return json.dumps({"login":False})



#<a href={url_for("my_connections")}>Connections</a>
@app.route('/account/login')
def login():
    args=request.args.to_dict()
    return discordauth.create_session(scope=["guilds","identify"],data={"returnguildid":args["id"]})



@app.route("/account/logout/")
def logout():
    args=request.args.to_dict()
    discordauth.revoke()
    return redirect(key["songctladdr"]+args["id"])


@app.route('/account/callback')
def callback():
    result=discordauth.callback()
    return redirect(key["songctladdr"]+result.get('returnguildid'))

@app.route('/updatesongqueue', methods = ['POST'])
def updatesongqueue():
    if discordauth.authorized:
        if checkuser(request.json["guildid"], discordauth.fetch_user().id):
            guildid=int(request.json["guildid"])
            newqueuelist=request.json["newqueue"]
            newqueue={}
            oldqueue=queues[guildid]
            for song in newqueuelist:
                newqueue[song]=oldqueue[song]
            queues[guildid]=newqueue
            return "updated queue"+str(list(queues[guildid].keys()))
        else:
            return "unconnected"
    else:
        return  "请先登录喵~"
@app.route('/deletesong', methods = ['POST'])
def deletesong():
    if discordauth.authorized:
        if checkuser(request.json["guildid"], discordauth.fetch_user().id):

            guildid=int(request.json["guildid"])
            songname=request.json["songname"]
            queues[guildid].pop(songname)
            return "updated queue"+str(list(queues[guildid].keys()))
        else:
            return "unconnected"
    else:
        return "请先登录喵~"

def checkuser(guildid, userid):
    global players
    guildid=int(guildid)
    userid=int(userid)
    if guildid in players.keys():
        connectedusers = [member.id for member in players[guildid].channel.members]
        if userid in connectedusers:
            return True
        else:
            return False
    else:
        #bot not in voice channel
        guild = atri.get_guild(guildid)
        requester = guild.get_member(userid)
        if userid in [member.id for member in requester.voice.channel.members]:
            return requester.voice.channel

        else:
            return False
workaround=[]
@app.route('/requestnewsong', methods = ['POST'])
async def requestnewsong():
    global workaround
    if discordauth.authorized:
        guildid=int(request.json["guildid"])
        userid=discordauth.fetch_user().id
        checkuserresult=checkuser(guildid, userid)
        guild = atri.get_guild(guildid)
        if checkuserresult:
            if checkuserresult != True:
                #calling channel.join() will cause a bug in the flask thread
                # players[guildid] = discord.utils.get(atri.voice_clients, name=guild) will return None


                workaround.append([checkuserresult, guildid,guild])
                while(1):
                    if guildid in players.keys():
                        break
                    await asyncio.sleep(1)
            a=request.json["songname"]
            id = await getsongid(a)
            if type(id) == type(()):
                #目前还没有实现网页歌曲选择
                #默认选取第一手歌
                id=str(id[0]["id"])
            if id == -1:
                return "这是什么歌曲，亚托莉无法播放哦!"
            if not players[guildid].is_playing():
                if id:
                    print(id)
                    if not await dl163ali(id):
                        return
                    songandartname=str(await getsongartists(id)).replace("[", "").replace("]", "").replace("'", "") + "——" + str(await getsongname(id))
                    cs[guildid] = [songandartname,False]
                    file=key["songcachedir"] + id + ".mp3"
                    songduration[songandartname]=getmp3duration(file)
                    players[guildid].play(discord.FFmpegPCMAudio(file), after=partial(ckqueue, guild))
                    cstarttime[guildid]=int(time.time()*1000)
                    add1play(id,userid)
                    return "正在播放："+songandartname
                else:
                    vid = await getyt(a)
                    cs[guildid] = [vid[1]["title"],vid[1]["thumbnail"]]
                    songduration[vid[1]["title"]]=vid[1]["duration"]

                    players[guildid].play(vid[0], after=partial(ckqueue, guild))
                    cstarttime[guildid]=int(time.time()*1000)

                    add1play(vid[1]["url"],userid)
                    return "正在播放："+vid[1]["url"]
            else:
                if id:
                    a=await dl163ali(id)
                    if not a:
                        return "暂时不支持vip歌曲，ご主人様ごめなさい！！"
                    songandartname=str(await getsongartists(id)).replace("[", "").replace("]", "").replace("'", "") + "——" + str(await getsongname(id))
                    file=key["songcachedir"] + id + ".mp3"
                    try:
                        if songandartname in queues[guildid].keys():
                            songandartname=songandartname + "⠀⠀⠀" + str(random.randint(1000001, 9999999))
                            queues[guildid][songandartname] = [discord.FFmpegPCMAudio(file),{"url":id,"title":songandartname,"thumbnail":False,"type":"163","requester":userid}]
                        else:
                            queues[guildid][songandartname] = [discord.FFmpegPCMAudio(file),{"url":id,"title":songandartname,"thumbnail":False,"type":"163","requester":userid}]
                    except Exception as e:
                        queues[guildid] = {}
                        queues[guildid][songandartname] = [discord.FFmpegPCMAudio(file),{"url":id,"title":songandartname,"thumbnail":False,"type":"163","requester":userid}]
                    songduration[songandartname]=getmp3duration(file)

                    return songandartname+"已添加到播放列表"
                else:
                    song = await getyt(a)
                    song[1]["requester"] = userid
                    try:
                        if song[1]["title"] in queues[guildid].keys():
                            newname=song[1]["title"] + "⠀⠀⠀" + str(random.randint(1000001, 9999999))
                            songduration[newname]=song[1]["duration"]
                            queues[guildid][newname] = song
                        else:
                            queues[guildid][song[1]["title"]] = song
                            songduration[song[1]["title"]]=song[1]["duration"]
                    except:
                        queues[guildid] = {}
                        queues[guildid][song[1]["title"]] = song
                        songduration[song[1]["title"]]=song[1]["duration"]
                    return song[1]["title"]+"已添加到播放列表"
            return "ok"
        else:
            print("no connect")
            return "please join the voice channel first"
    else:
        return "请先登录喵~"

@app.route('/getcurrentsong', methods = ['GET'])
def getcurrentsong():
    try:
        args = request.args.to_dict()
        a={"songname":cs[int(args["id"])][0],"duration":songduration[cs[int(args["id"])][0]],"starttime":cstarttime[int(args["id"])],"playing":players[int(args["id"])].is_playing(),"thumbnail":cs[int(args["id"])][1] if cs[int(args["id"])][1] else ""}
        return json.dumps(a)
    except:
        return json.dumps({})
@app.route('/getcurrentqueue', methods = ['GET'])
def getcurrentqueue():
    args = request.args.to_dict()
    try:
        return json.dumps(list(queues[int(args["id"])].keys()))
    except:
        return json.dumps([])

@app.route('/changesongstate', methods = ['POST'])
def changesongstate():
    if discordauth.authorized:
        if checkuser(request.json["guildid"], discordauth.fetch_user().id):
            if request.json["action"] == "next":
                players[int(request.json["guildid"])] = discord.utils.get(atri.voice_clients, guild=atri.get_guild(int(request.json["guildid"])))
                if players[int(request.json["guildid"])]:
                    try:
                        if queues[int(request.json["guildid"])]:
                            players[int(request.json["guildid"])].stop()
                    except:
                        players[int(request.json["guildid"])].stop()
                else:
                    return "no"
            elif request.json["action"] == "pause":
                players[int(request.json["guildid"])] = discord.utils.get(atri.voice_clients, guild=atri.get_guild(int(request.json["guildid"])))
                if players[int(request.json["guildid"])]:
                    if players[int(request.json["guildid"])].is_playing():
                        players[int(request.json["guildid"])].pause()
                        pausesong(int(request.json["guildid"]))
                    else:
                        players[int(request.json["guildid"])].resume()
                        cstarttime[int(request.json["guildid"])]=cstarttime[int(request.json["guildid"])]+pausesong(int(request.json["guildid"]))
                else:
                    return "no"
            else:
                return "这是什么命令，亚托莉看不懂。亚托莉去问一下夏生先生！"
            return "ok"
        else:
            return "unconnected"
    else:
        return "请先登录喵~"
@app.route('/songctl',methods = ['GET'])
def songctl():
    print("收到来自"+request.remote_addr+"的新请求喵~")
    return send_file(dirpath+"website/songctl.html")

@app.route('/<path:path>')
def send_report(path):
    return send_from_directory('website', path)


async def getsongdetails(id):
    # if exists(dirpath + "./datacache/" + id):
    #     with codecs.open(dirpath + "./datacache/" + id, encoding='utf-8', mode='r') as f:
    #         return json.loads(f.read())
    # else:
    #     async with aiohttp.ClientSession() as session:
    #         async with session.get("http://music.163.com/api/song/detail/?id="+id+"&ids=%5B"+id+"%5D") as resp:
    #             results = await resp.json(content_type=None)
    #             results=results["songs"][0]
    #             with codecs.open(dirpath + "./datacache/" + id, encoding='utf-8', mode='w') as f:
    #                 f.write(json.dumps(results))
    #             return results
    a=songdata.find_one({"_id": id})

    if a:
        return a
    else:
        print("cache miss")
        async with aiohttp.ClientSession() as session:
            async with session.get("http://music.163.com/api/song/detail/?id="+id+"&ids=%5B"+id+"%5D") as resp:
                results = await resp.json(content_type=None)
                results=results["songs"][0]
                results["_id"]=str(results["id"])
                results["title"] = results.pop("name")
                results["type"] = "163"
                results["orgin"] = "directquery"
                songdata.insert_one(results)
                return results
async def getsongname(id):
    a=await getsongdetails(id)
    return a["title"]
async def getsongartists(id):
    art = await getsongdetails(id)
    art=art["artists"]
    return artistslistpurifier(art)
async def searchsong(sn):
    async with aiohttp.ClientSession() as session:
        async with session.get(cloudmusicapiurl + "/search?keywords="+sn) as resp:
            results = await resp.json()
            if results["result"]['songCount'] == 0:
                return -1
            id = results["result"]["songs"]
            nid=[]
            for i in id:
                i["title"] = i.pop("name")
                i["_id"] = str(i["id"])
                i["type"] = "163"
                i["orgin"] = ("searchresul"
                              "tcache")
                if songdata.count_documents({"_id": i["_id"]}, limit=1) == 0:
                    #doc not exist
                    # with codecs.open(dirpath + "./datacache/" + str(i["id"]), encoding='utf-8', mode='w') as f:
                    #     f.write(json.dumps(i))

                    songdata.insert_one(i)
                nid.append(i)
            return tuple(nid)

async def getplaylist(sn):
    async with aiohttp.ClientSession() as session:
        async with session.get(cloudmusicapiurl + "/playlist/track/all?id="+sn+"&limit=30") as resp:
            results = await resp.json()
            id =results["songs"]
            for i in id:
                i["artists"]=i.pop("ar")
                i["album"] = i.pop("al")
                i["_id"]=str(i["id"])
                i["title"] = i.pop("name")
                i["type"]="163"
                i["orgin"]="playlistresultcache"
                songdata.insert_one(i)

            nl = []
            for i in id:
                nl.append(str(i['id']))
            return nl
async def getalbum(sn):
    async with aiohttp.ClientSession() as session:
        async with session.get(cloudmusicapiurl + "/album?id="+sn) as resp:
            results = await resp.json()
            id =results["songs"]
            for i in id:
                i["artists"]=i.pop("ar")
                i["album"] = i.pop("al")
                i["_id"]=i["id"]
                i["title"] = i.pop("name")
                i["type"]="163"
                i["orgin"]="albumresultcache"
                songdata.insert_one(i)
            nl = []
            for i in id:
                nl.append(str(i['id']))
            return nl

def getmp3duration(file):
    audio = MP3(file)
    return audio.info.length

def mutisearch(s,t):
    for i in t:
        if s.find(i) != -1:
            return True
    return False

def replacetrans(message, userid, *replace):
    userid = str(userid)
    if "lang" not in userdata.find_one({"_id": userid}).keys():
        userdata.find_one_and_update(
            {"_id": userid},
            {"$set": {"lang": "zh.json"}},
            upsert=True
        )
        default_message = "You have not set a language, defaulting to Chinese Simplified. You can set a language with " + name[0] + "langset <language>."
        translation = translations["zh.json"][message]
        if replace:
            if len(replace) > 1:
                chosen_message = random.choice(translation)
                return default_message + "\n" + chosen_message.replace("%a", replace[0]) if "%a" in chosen_message else default_message + "\n" + chosen_message
            return default_message + "\n" + translation.replace("%a", replace[0]) if "%a" in translation else default_message + "\n" + translation
        return default_message + "\n" + translation

    translation = translations[userdata.find_one({"_id":userid})["lang"]][message]
    if replace:
        if len(replace) > 1:
            chosen_message = random.choice(translation)
            return chosen_message.replace("%a", replace[0]) if "%a" in chosen_message else chosen_message
        return translation.replace("%a", replace[0]) if "%a" in translation else translation


    return translation


def testbyn(sn):
    sl = ["youtube.com", "youtu.be", "bilibili.com", "nicovideo.jp", "nico.ms", "b23.tv"]
    return any(sub in sn for sub in sl)


class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, ):
        super().__init__(source)
        # YTDL info dicts (data) have other useful information you might want
        # https://github.com/rg3/youtube-dl/blob/master/README.md
    def __getitem__(self, item: str):
        """Allows us to access attributes similar to a dict.
        This is only useful when you are NOT downloading.
        """
        return self.__getattribute__(item)
    @classmethod
    async def create_source(cls, search: str, ):

        if mutisearch(search, ["b23.tv","bili"]):
            site="bili"
        elif mutisearch(search, ["nicovideo.jp", "nico.ms"]):
            site="nico"
        else:
            site="yt"

        loop = asyncio.get_event_loop()
        to_run = partial(ytdl.extract_info, url=search)
        data = await loop.run_in_executor(None, to_run)

        if 'entries' in data:
            lista=[]
            #it is a playlist
            for d in data['entries']:
                source = ytdl.prepare_filename(d)
                if site=="bili":
                    d["url"] = "https://www.bilibili.com/video/"+d["webpage_url_basename"]
                elif site=="nico":
                    d["url"] = "https://www.nicovideo.jp/watch/" + d["webpage_url_basename"]
                else:
                    d["url"] = d["webpage_url"]
                d["type"]="youtube"
                d["orgin"]="youtubeplaylistquery"
                d["_id"]=d["url"]
                d.pop("requested_downloads")
                if songdata.count_documents({"_id": d["url"]}, limit=1) == 0:
                    try:
                        songdata.insert_one(d)
                    except:
                        print(traceback.format_exc(),"database update error")
                        print(d)
                lista.append([discord.FFmpegPCMAudio(source),d])
            return lista

        else:

            source = ytdl.prepare_filename(data)
            if site=="bili":
                data["url"] = "https://www.bilibili.com/video/" + data["webpage_url_basename"]
            elif site=="nico":
                data["url"] = "https://www.nicovideo.jp/watch/" + data["webpage_url_basename"]
            else:
                data["url"]=data["webpage_url"]
            data["type"] = "youtube"
            data["orgin"] = "youtubedirectlink"
            data["_id"] = data["url"]
            data.pop("requested_downloads")

            if songdata.count_documents({"_id": data["url"]}, limit=1) == 0:
                try:
                    songdata.insert_one(data)
                except:
                    print(traceback.format_exc(), "database update error")
                    print(data)
            return (discord.FFmpegPCMAudio(source),data)

async def getyt(url):
    a = await YTDLSource.create_source(url)
    return a

def add1play(id,requester):
    #the input is video or song title
    songdata.find_one_and_update(
        {"_id": id},
        {"$inc": {"play_count": 1}},
        upsert=True,
    )
    userdata.find_one_and_update(
            {"_id": str(requester)},
            {"$inc": {f"play_counts.{id.replace('https://www.youtube.com/watch?v=','')}": 1}},
            upsert=True
        )


    # try:
    #     plays[id] = plays[id] + 1
    # except:
    #     plays[id] = 1


async def playt(ctx, vid,requester):
    # “a” is the video url
    cs[ctx.guild.id] = [vid[1]["title"],vid[1]["thumbnail"]]
    songduration[vid[1]["title"]]=vid[1]["duration"]
    players[ctx.guild.id].play(vid[0], after=partial(ckqueue, ctx.guild))
    cstarttime[ctx.guild.id]=int(time.time()*1000)
    await ctx.send(    replacetrans("now_playing",ctx.author.id,vid[1]["title"]) )
    await ctx.send(replacetrans("show_web_address_user",ctx.author.id,key["songctladdr"]+str(ctx.guild.id)))
    add1play(vid[1]["url"],requester)

async def addtoqueueyt(ctx, song):
    if type(song) == type([]):
        adding[ctx.guild.id] = True
        songs=song
        songaddtext=""
        for song in songs:
            if adding[ctx.guild.id]:
                if not queues[ctx.guild.id]:
                    queues[ctx.guild.id] = {}
                song[1]["requester"]=ctx.author.id
                queues[ctx.guild.id][song[1]["title"]] = song

                songduration[song[1]["title"]]=song[1]["duration"]
                songaddtext=songaddtext+song[1]["title"] + "\n"

            else:
                await ctx.send(replacetrans("stopadding",ctx.author.id))
                break
        await ctx.send(replacetrans("added_to_playlist",ctx.author.id, songaddtext))
    else:
        song[1]["requester"] = ctx.author.id

        try:
            if song[1]["title"] in queues[ctx.guild.id].keys():
                queues[ctx.guild.id][song[1]["title"] + "⠀⠀⠀" + str(random.randint(1000001, 9999999))] = song
            else:
                queues[ctx.guild.id][song[1]["title"]] = song
        except:
            queues[ctx.guild.id] = {}
            queues[ctx.guild.id][song[1]["title"]] = song
        songduration[song[1]["title"]]=song[1]["duration"]

        await ctx.send(replacetrans("added_to_playlist",ctx.author.id, song[1]["title"]))

async def addtoqueue163(ctx, id,requester):
    if id==-1:
        #canceled
        return
    if type(id) == type([]):
        adding[ctx.guild.id] = True
        for i in id:
            if adding[ctx.guild.id]:
                if not await dl163ali(i):
                    await ctx.send(replacetrans("error_vip_not_supported",ctx.author.id))
                    continue
                else:
                    songname=str(await getsongartists(i)).replace("[", "").replace("]", "").replace("'","") + "——" + str(await getsongname(i))
                    file=key["songcachedir"] + i + ".mp3"
                    try:
                        songduration[songname]=getmp3duration(file)
                        try:
                            if songname in queues[ctx.guild.id].keys():
                                songname=songname + "⠀⠀⠀" + str(random.randint(1000001, 9999999))
                                queues[ctx.guild.id][songname] = [discord.FFmpegPCMAudio(file),{"url":i,"title":songname,"thumbnail":False,"type":"163","requester":ctx.author.id}]
                            else:
                                queues[ctx.guild.id][songname] = [discord.FFmpegPCMAudio(file),{"url":i,"title":songname,"thumbnail":False,"type":"163","requester":ctx.author.id}]
                        except Exception as e:
                            #print(e)
                            queues[ctx.guild.id] = {}
                            #print("reset queue")
                            queues[ctx.guild.id][songname] = [discord.FFmpegPCMAudio(file),{"url":i,"title":songname,"thumbnail":False,"type":"163","requester":ctx.author.id}]

                        await ctx.send(replacetrans("added_to_playlist",ctx.author.id,songname))
                    except:
                        await ctx.send(replacetrans("error_vip_not_supported",ctx.author.id))
            else:
                await ctx.send(replacetrans("stopading",ctx.author.id))
                break
    else:
        a=await dl163ali(id)
        if not a:
            await ctx.send(replacetrans("error_vip_not_supported",ctx.author.id))
            return
        songname=str(await getsongartists(id)).replace("[", "").replace("]", "").replace("'", "") + "——" + str(await getsongname(id))
        file=key["songcachedir"] + id + ".mp3"
        songduration[songname]=getmp3duration(file)
        try:
            if songname in queues[ctx.guild.id].keys():
                queues[ctx.guild.id][songname + "⠀⠀⠀" + str(random.randint(1000001, 9999999))] = [discord.FFmpegPCMAudio(file),{"url":id,"title":songname,"thumbnail":False}]
            else:
                queues[ctx.guild.id][songname] = [discord.FFmpegPCMAudio(file),{"url":id,"title":songname,"thumbnail":False}]
        except Exception as e:
            queues[ctx.guild.id] = {}
            queues[ctx.guild.id][songname] =  [discord.FFmpegPCMAudio(file),{"url":id,"title":songname,"thumbnail":False}]
        await ctx.send(replacetrans("added_to_playlist",ctx.author.id,songname))

def ckqueue(guild, uselessd, uselessd2=None):
    try:
        if guild.id not in queues or not queues[guild.id]:
            cs.pop(guild.id)
            return
        id = list(queues[guild.id].keys())[0]
        cs[guild.id] = [id,queues[guild.id][id][1]["thumbnail"]]
        song = queues[guild.id].pop(id)
        players[guild.id] = discord.utils.get(atri.voice_clients, guild=guild)
        players[guild.id].play(song[0], after=partial(ckqueue, guild))
        cstarttime[guild.id]=int(time.time()*1000)
        print(song)
        add1play(song[1]["url"],song[1]["requester"])
    except Exception as e:
        print(traceback.format_exc())
        cs.pop(guild.id)


# @atri.event
# async def on_member_update(before, after):
#     if str(before.guild.id) == "937939784494612570":
#         if str(before.id) in waifulist:
#             if before.status == after.status:
#                 pass
#             else:
#                 if before.id in waifucd.keys():
#                     if waifucd[str(before.id)] + 1800 > round(time.time()):
#                         return
#                 if str(after.status) == "online" or (str(after.status) == "away" and str(before.status) == "offline"):
#                     await after.send(replacetrans("master_arrive_home_catgirl",before.id,str(after.name),True))
#                     waifucd[str(before.id)] = round(time.time())
#                 elif str(after.status) == "offline" or str(after.status) == "away":
#                     await after.send(replacetrans("choice_master_leave",before.id,str(after.name),True))
#                     waifucd[str(before.id)] = round(time.time())
#                 else:
#                     pass

class chatgpt():
    def __init__(self, channel):
        self.messages=[]
        self.channel=channel
    async def loadmessages(self,messageurl):
        r = requests.get(messageurl)
        self.messages=ast.literal_eval(r.text.replace("\n","").replace("'","\""))
        await self.channel.send("ok")
    async def savemessages(self):
        with codecs.open("savechat.txt",encoding='utf-8', mode='w') as f:
            f.write(str(self.messages))
        with open("savechat.txt", "rb") as file:
            await self.channel.send("聊天文件:", file=discord.File(file, "savechat.txt"))
            return
    async def loadpreset(self,preset):
        with codecs.open(dirpath+"/gptprompt/"+preset+".txt",encoding='utf-8', mode='r') as f:
            prompt=f.read()
        self.messages.append({"role": "user", "content":  prompt})
        await self.channel.send("ok")
    async def gererateresponse(self,newmessage):
        try:
            self.messages.append({"role": "user", "content":  newmessage})
            completion =  await asyncio.to_thread( openai.ChatCompletion.create,
                model="gpt-3.5-turbo",
                messages=self.messages,

            )
            chat_response = completion.choices[0].message.content
            #chat_response = "testing"
            await self.channel.send(chat_response)
            self.messages.append({"role": "assistant", "content": chat_response})
        except:
            if key['devmode']:
                await self.channel.send("亚托莉，坏掉了！")
                with codecs.open(dirpath + "./err.txt", encoding='utf-8', mode='w') as file:
                    file.write(str(traceback.format_exc()))
                # send file to Discord in message
                with open("err.txt", "rb") as file:
                    await self.channel.send("错误文件：", file=discord.File(file, "err.txt"))
                return
            else:
                await self.channel.send("ChatGPT API调用失败，请重试。")

@atri.event
async def on_message(message):
    if key["gptkey"]:
        if message.author == atri.user:
            return
        askgpt=False
        atri_id = f"{atri.user.id}".split("#")[0]
        if message.reference:
            try:
                replied_message = await message.channel.fetch_message(message.reference.message_id)
                if replied_message.author == atri.user:
                    askgpt = True
            except discord.NotFound:
                pass
        if not askgpt and not message.content.startswith(f"<@{atri_id}>"):
            if userdata.count_documents({"_id": str(message.author.id)}, limit=1) == 0:
                await atri.process_commands(message)
            else:
                if "blacklist" in userdata.find_one({"_id": str(message.author.id)}).keys() and userdata.find_one({"_id": str(message.author.id)})["blacklist"]:
                    return
                else:
                    await atri.process_commands(message)

        else:
            cleanmessage=message.content.replace(f"<@{atri_id}>", "").strip()
            if message.guild.id not in scm.keys():
                scm[message.guild.id]=chatgpt(message.channel)
            gpt=scm[message.guild.id]
            if cleanmessage[:4]=="保存对话":
                await gpt.savemessages()
            elif cleanmessage[:4]=="加载对话":
                await gpt.loadmessages(cleanmessage[4:].replace(" ",""))
            elif cleanmessage[:4]=="加载角色":
                await gpt.loadpreset(cleanmessage[4:].replace(" ",""))
            else:
                await gpt.gererateresponse(cleanmessage)
    else:

        if userdata.count_documents({"_id": str(message.author.id)}, limit=1) == 0:
            await atri.process_commands(message)
        else:
            if "blacklist" in userdata.find_one({"_id": str(message.author.id)}).keys() and userdata.find_one({"_id": str(message.author.id)})["blacklist"]:
                return
            else:
                await atri.process_commands(message)

@atri.event
async def on_ready():
    print("主人我上线啦(｡･ω･｡)ﾉ♡")
    print("主人我目前加入了"+str(len(atri.guilds))+"个服务器哦")
    writeplays.start()
    connecttovoice.start()
    await atri.change_presence(activity=discord.Activity(type=discord.ActivityType.listening,name="主人的命令||" + name[0] + "play <歌曲>||支持网易云，哔哩哔哩，youtube，ニコニコ"))

async def getsongid(sn):
    b = sn.find("song?id=")
    id = ""
    if b == -1:
        id = sn
        try:
            int(id)
        except:
            if testbyn(sn):
                return False
            listtextl = sn.find("lbum?id=")
            if listtextl != -1:

                # slow
                sn = sn[listtextl + 8:]
                return await getalbum(sn)
            listtextl = sn.find("list?id=")
            if listtextl != -1:
                # slow
                sn=sn[listtextl + 8:]
                return await getplaylist(sn)
            # reload(search163)
            # slow
            #id = await asyncio.get_event_loop().run_in_executor(None, search163.get_id_and_cache_data, sn)
            # searcg 1


            id= await searchsong(sn)
            #lbum?id=


    else:
        n = sn[b + 8:]
        if n.find("&") == -1:
            id = n
        else:
            id = n[:n.find("&")]
    return id

async def dl163ali(id):
    if exists(key["songcachedir"] + id + ".mp3"):
        return True
    #/song/url/v1?id=33894312&level=exhigh
    async with aiohttp.ClientSession() as session:
        async with session.get(cloudmusicapiurl+"/song/url/v1?id="+id+"&level=higher&cookie="+cookie) as resp:
            #print(cloudmusicapiurl+"/song/url/v1?id="+id+"&level=exhigh&cookie="+cookie)
            results=await resp.json()
            async with aiohttp.ClientSession() as session:
                async with session.get(results["data"][0]["url"]) as resp:
                    if resp.status == 200:
                        f = await aiofiles.open(key["songcachedir"] + id + ".mp3", "wb")
                        await f.write(await resp.read())
                        await f.close()
                        return True
@atri.command(aliases=["封"])
async def ban(ctx, id, reason=" "):
    if str(ctx.message.author.id) == "834651231871434752":
        userdata.find_one_and_update({"_id":str(id)},{"$set":{"blacklist":True,"blacklistreason":reason}},upsert=True)

        await ctx.send("ok")

@atri.command(aliases=["解封"])
async def unban(ctx, id):
    if str(ctx.message.author.id) == "834651231871434752":
        userdata.find_one_and_update({"_id":str(id)},{"$set":{"blacklist":False}},upsert=True)

        await ctx.send(replacetrans("master_is_so_kind",ctx.author.id))

@atri.command()
async def langset(ctx, *lang):
    userdata.find_one_and_update({"_id":str(ctx.author.id)},
                                  {"$inc":{"interactions":1}},upsert=True)
    if not lang:
        await ctx.send("available languages:"+str(translations.keys())
                       +"\nalangset <language>\nExample: alangset jp"
                       )
    else:
        if lang[0] in translations.keys() or lang[0]+".json" in translations.keys():
            userdata.find_one_and_update(
                {"_id": str(ctx.author.id)},
                {"$set": {"lang": lang[0].replace(".json","")+".json"}},
                upsert=True
            )
            await ctx.send(replacetrans("lang_set",ctx.author.id))
            #langpref[str(ctx.author.id)]=lang[0].replace(".json","")+".json"
        else:
            await ctx.send("available languages:"+str(translations.keys()))

@atri.command()
async def spelling(ctx):
    userdata.find_one_and_update({"_id":str(ctx.author.id)},
                                  {"$inc":{"interactions":1}},upsert=True)
    def check(m):
        return m.channel == ctx.channel

    if ctx.author.voice:
        pass
    else:
        await ctx.send(replacetrans("spelling_please_connect_to_voice",ctx.author.id))
        return
    await ctx.send(replacetrans("spelling_test_start_add",ctx.author.id))
    returnlist = await atri.wait_for('message', check=check)

    try:
        splist = ast.literal_eval(returnlist.content)
        random.shuffle(splist)
        await ctx.send(replacetrans("spelling_start",ctx.author.id))
        await returnlist.delete()
        if ctx.voice_client:
            if ctx.voice_client.is_connected:
                await ctx.voice_client.disconnect()
        await ctx.message.author.voice.channel.connect()
        players[ctx.guild.id] = discord.utils.get(atri.voice_clients, guild=ctx.guild)
        reviewlist = []
        for w in splist:
            while (1):
                if exists(dirpath + "./temp" + str(ctx.guild.id) + ".mp3"):
                    os.remove(dirpath + "./temp" + str(ctx.guild.id) + ".mp3")
                word = gTTS(text=w, lang="en", slow=True)
                word.save(dirpath + "./temp" + str(ctx.guild.id) + ".mp3")
                try:
                    players[ctx.guild.id].play(discord.FFmpegPCMAudio(dirpath + "./temp" + str(ctx.guild.id) + ".mp3"))
                    cstarttime[ctx.guild.id]=int(time.time()*1000)
                except:
                    pass
                await ctx.send(replacetrans("spelling_test_please_respond",ctx.author.id))
                ansobj = await atri.wait_for('message', check=check)
                #print("waiting")
                ans = ansobj.content
                if ans.lower() == w.lower():
                    #print("correct")
                    await ctx.send(replacetrans("spelling_correct",ctx.author.id))
                    break
                elif ans == "r":
                    #print("retry")
                    pass
                elif ans == "q":
                    #print("retry")
                    await ctx.send("ok")
                    return
                else:
                    #print("wrong")
                    await ctx.send(replacetrans("spelling_wrong",ctx.author.id,w))
                    reviewlist.append(w)
                    while (1):
                        players[ctx.guild.id].play(discord.FFmpegPCMAudio(dirpath + "./temp" + str(ctx.guild.id) + ".mp3"))
                        await ctx.send(replacetrans("spelling_wrong_reenter",ctx.author.id,w))
                        ansobj = await atri.wait_for('message', check=check)
                        ans = ansobj.content
                        if ans.lower() == w.lower():
                            await ctx.send(replacetrans("spelling_wrong_correct",ctx.author.id))
                            break
                        elif ans == "r":
                            pass
                        else:
                            await ctx.send(replacetrans("spelling_wrong_wrong",ctx.author.id))
                    break
        await ctx.send(str((len(splist) - len(reviewlist) / len(splist))) + "分")
        await ctx.send(replacetrans("spelling_learned_words",ctx.author.id,splist))
        await ctx.send(replacetrans("spelling_failed_words",ctx.author.id,reviewlist))

    except:
        await ctx.send(replacetrans("error_atri_broken",ctx.author.id))
        with codecs.open(dirpath + "./err.txt", encoding='utf-8', mode='w') as file:
            file.write(str(traceback.format_exc()))
        # send file to Discord in message
        with open("err.txt", "rb") as file:
            await ctx.send("错误文件：", file=discord.File(file, "err.txt"))
        return

# @atri.command(aliases=["すき", "最喜欢了", "喜欢", "爱"])
# async def suki(ctx, *v):
#     user_id = str(ctx.author.id)
#
#     def reset_daily_limits():
#         userdata[user_id]["dailylimits"] = {"pat": 0, "suki": 0, "727": 0}
#
#     def update_haogandu(value):
#         userdata[user_id]["haogandu"] += value
#
#     async def send_message(key, value_change):
#         await ctx.send(replacetrans(key, user_id))
#         update_haogandu(value_change)
#
#     if not v or not v[0].isdigit():
#         await ctx.send(replacetrans("suki_missing_args", user_id))
#         return
#
#     user_data = userdata.get(user_id, {})
#     if user_data.get("dailylimittime") != str(date.today()):
#         reset_daily_limits()
#
#     haogandu = user_data.get("haogandu", 0)
#     daily_limit = user_data.get("dailylimits", {}).get("suki", 0)
#
#     if haogandu >= -20:
#         if daily_limit < 10:
#             if int(v[0]) > 5:
#                 await send_message("suki_love", 1)
#             else:
#                 await send_message("suki_kirai", -5 if haogandu <= 500 else -400)
#         else:
#             await send_message("suki_atricon", -10 if haogandu <= 500 else 10)
#     else:
#         await send_message("suki_report_police", -20)
#
#     userdata[user_id]["dailylimits"]["suki"] = daily_limit + 1
#
#
# @atri.command(aliases=["摸头"])
# async def pat(ctx):
#     try:
#         if userdata[str(ctx.author.id)]["dailylimittime"] != str(date.today()):
#             userdata[str(ctx.author.id)]["dailylimits"]["pat"] = 0
#             userdata[str(ctx.author.id)]["dailylimits"]["suki"] = 0
#             userdata[str(ctx.author.id)]["dailylimits"]["727"] = 0
#         if not userdata[str(ctx.author.id)]["haogandu"] < 0:
#             if userdata[str(ctx.author.id)]["dailylimits"]["pat"] > 5:
#                 await ctx.send("呜~头发都被弄乱了，主人能不能休息一下吗？")
#             if userdata[str(ctx.author.id)]["dailylimits"]["pat"] > 10:
#                 await ctx.send("主人怎么一天到晚就只会摸小萝莉的头。难道是萝莉控？？好恶心！")
#                 userdata[str(ctx.author.id)]["haogandu"] = userdata[str(ctx.author.id)]["haogandu"] - 10
#             else:
#                 userdata[str(ctx.author.id)]["haogandu"] = userdata[str(ctx.author.id)]["haogandu"] + random.randint(0,
#                                                                                                                     5)
#                 await ctx.send("好舒服~最喜欢被主人摸头啦")
#             userdata[str(ctx.author.id)]["dailylimits"]["pat"] = userdata[str(ctx.author.id)]["dailylimits"]["pat"] + 1
#             userdata[str(ctx.author.id)]["dailylimittime"] = str(date.today())
#         else:
#             await ctx.send("救命！！这边有个变态在骚扰我！")
#     except:
#         # print(traceback.format_exc())
#         userdata[str(ctx.author.id)] = {}
#         userdata[str(ctx.author.id)]["dailylimits"] = {}
#         userdata[str(ctx.author.id)]["dailylimits"]["pat"] = 1
#         userdata[str(ctx.author.id)]["dailylimittime"] = str(date.today())
#         userdata[str(ctx.author.id)]["dailylimits"]["suki"] = 0
#         userdata[str(ctx.author.id)]["dailylimits"]["727"] = 0
#         userdata[str(ctx.author.id)]["haogandu"] = random.randint(0, 5)
#         await ctx.send("好舒服~最喜欢被主人摸头啦")
#
# @atri.command(aliases=["誓约"])
# async def marry(ctx):
#     if userdata[str(ctx.author.id)]["haogandu"] < 100:
#         await ctx.send("No no we are friends! friends!")
#     else:
#         await ctx.send("ok")
#         await ctx.author.send("主人来这里！https://discord.gg/x2VMR2uAju")
#         waifulist.append(str(ctx.author.id))

@atri.command(aliases=["排行榜"])
async def rankings(ctx):
    global songdata
    userdata.find_one_and_update({"_id":str(ctx.author.id)},
                                  {"$inc":{"interactions":1}},upsert=True)
    songtable = PrettyTable()
    songtable.field_names = ["排名","播放次数", "歌手/歌曲名"]
    songtable.align = 'l'
    songtable.set_style(PLAIN_COLUMNS)
    ct = 1
    msg = "```!全dc亚托莉放的最多的歌曲前二十!\n"
    #rankedlist= sorted(plays, key=plays.get, reverse=True)[:20]
    rankedlist = list(songdata.find({"play_count": { "$exists":True,"$ne": 0 }}).sort("play_count", -1).limit(20))
    for song in rankedlist[:10]:
        id=song["_id"]
        if song["type"]=="163":
            songtable.add_row([ct,  song["play_count"],str(await getsongartists(id)) + "——" + str(await getsongname(id))])
            ct = ct + 1
        else:
            songtable.add_row([ct, song["play_count"], song["title"] ])
            ct = ct + 1
    await ctx.send(msg+str(songtable)+"```")
    songtable = PrettyTable()
    songtable.field_names = [" ", "  ", "   "]
    songtable.align = 'l'
    songtable.set_style(PLAIN_COLUMNS)
    ct = 1
    #the next 10 songs
    for song in rankedlist[10:]:
        id = song["_id"]
        if song["type"] == "163":
            int(id)
            songtable.add_row([ct+10, song["play_count"], str(await getsongartists(id)) + "——" + str(await getsongname(id))])
            ct = ct + 1
        else:
            songtable.add_row([ct+10, song["play_count"] , song["title"]])
            ct = ct + 1
    await ctx.send("```" + str(songtable) + "```")

def artistslistpurifier(j):
    nl=[]
    for i in j:
        nl.append(i['name'])
    return "，".join(nl)
async def songchoice(ctx,xuanze):
    def check(m):
        return m.channel == ctx.channel
    await ctx.send(replacetrans("select_song",str(ctx.author.id)))
    msg=""
    for x in range(len(xuanze)):
        cr=xuanze[x]
        msg = msg + str(x) + ".  " + str(artistslistpurifier(cr['artists'])) + "——" + cr["title"] +"\n"
    await ctx.send(msg)
    selection = await atri.wait_for('message',check=check )
    selection=selection.content
    try:
        return str(xuanze[int(selection)-1]["id"])
    except:
        await ctx.send(replacetrans("select_song_cancel",str(ctx.author.id)))
        return -1



@atri.command(aliases=["播放", "queue", "播放列表"])
async def play(ctx, *a):
    userdata.find_one_and_update({"_id":str(ctx.author.id)},
                                  {"$inc":{"interactions":1}},upsert=True)
    try:
        if a:
            if ctx.author.voice:
                players[ctx.guild.id] = discord.utils.get(atri.voice_clients, guild=ctx.guild)
                if not players[ctx.guild.id]:
                    await ctx.message.author.voice.channel.connect()
                    players[ctx.guild.id] = discord.utils.get(atri.voice_clients, guild=ctx.guild)
                a =" ".join(a)
                id = await getsongid(a)
                if id == -1:
                    return
                if not players[ctx.guild.id].is_playing():
                    if players[ctx.guild.id].channel != ctx.message.author.voice.channel:
                        await players[ctx.guild.id].move_to(ctx.message.author.voice.channel)
                    if id:
                        if type(id) == type([]):
                            fid = id.pop(0)
                            await play163(ctx, fid)
                            await addtoqueue163(ctx, id)
                        elif type(id) == type(()):
                            await play163(ctx,await songchoice(ctx, id))
                        else:
                            await play163(ctx, id)
                    else:
                        song = await getyt(a)
                        if type(song) == type([]):
                            fid = song.pop(0)
                            await playt(ctx, fid,ctx.author.id)
                            await addtoqueueyt(ctx, song)
                        else:
                            await playt(ctx, song,ctx.author.id)
                else:
                    if id:
                        #returned a search reult list

                        if type(id)==type(()):
                            await addtoqueue163(ctx, await songchoice(ctx,id))
                        else:
                            await addtoqueue163(ctx, id)
                    else:
                        song = await getyt(a)
                        await addtoqueueyt(ctx,song)
            else:
                await ctx.send(replacetrans("error_not_connected",str(ctx.author.id)))
        else:
            if not key["devmode"]:
                await ctx.send(replacetrans("playlist",str(ctx.author.id)))
                try:
                    if queues[ctx.guild.id].keys() == []:
                        await ctx.send(replacetrans("no_songs",str(ctx.author.id)))
                    else:
                        bbbb = ""
                        for aaa in queues[ctx.guild.id].keys():
                            badidea = aaa.find("⠀⠀⠀")
                            if badidea != -1:
                                aaa = aaa[:badidea]

                            bbbb = bbbb + "\n" + aaa
                        await ctx.send(bbbb)
                except Exception as e:
                    #print(e)
                    await ctx.send(replacetrans("no_songs",str(ctx.author.id)))
            else:
                await ctx.send(str(queues))
                await ctx.send(replacetrans("playlist",str(ctx.author.id)))
                try:
                    if queues[ctx.guild.id].keys() == []:
                        await ctx.send(replacetrans("no_songs",str(ctx.author.id)))
                    else:
                        bbbb = ""
                        for aaa in queues[ctx.guild.id].keys():
                            badidea = aaa.find("⠀⠀⠀")
                            if badidea != -1:
                                aaa = aaa[:badidea]

                            bbbb = bbbb + "\n" + aaa
                        await ctx.send(bbbb)
                except Exception as e:
                    #print(e)
                    await ctx.send(replacetrans("no_songs",str(ctx.author.id)))
                #print(str(queues))
        authordata=userdata.find_one({"_id": str(ctx.author.id)})
        if authordata["interactions"]>40 and "begged" not in authordata:
            await ctx.author.send("你好，亚托莉已经和你互动了超过40次了，请务必考虑支持亚托莉的运行和开发喵~ "+key["songctlhost"]+"/support.jpg")
            userdata.find_one_and_update({"_id":str(ctx.author.id)},
                                  {"$set":{"begged":True}},upsert=True)
    except Exception as e:

        if key["devmode"]:
            await ctx.send(replacetrans("error_atri_broken",str(ctx.author.id)))
            with codecs.open(dirpath + "./err.txt", encoding='utf-8', mode='w') as file:
                file.write(str(traceback.format_exc()))
            # send file to Discord in message
            print(traceback.format_exc())
            with open("err.txt", "rb") as file:
                await ctx.send( replacetrans("error_traceback",str(ctx.author.id)), file=discord.File(file, "err.txt"))
        else:
            await ctx.send("播放失败（现在可能播放不了b站）")

async def play163(ctx, id):
    if id==-1:
        #canceled
        return
    if not await dl163ali(id):  # 调用await dl163ali，如果歌曲可以下载会下载歌曲，不可以的话会返回 False 所以下面不需要调用
        await ctx.send(replacetrans("error_vip_not_supported",ctx.author.id))
        return
    songname=str(await getsongartists(id)) + "——" + str(await getsongname(id))
    cs[ctx.guild.id] = [songname,False]
    file=key["songcachedir"] + id + ".mp3"
    songduration[songname]=getmp3duration(file)
    players[ctx.guild.id].play(discord.FFmpegPCMAudio(file), after=partial(ckqueue, ctx.guild))
    cstarttime[ctx.guild.id]=int(time.time()*1000)
    await ctx.send(replacetrans("now_playing",ctx.author.id,songname))
    await ctx.send(replacetrans("show_web_address_user",ctx.author.id,key["songctladdr"]+str(ctx.guild.id)))
    add1play(id,ctx.author.id)
def pausesong(guildid):
    if guildid in pausetime.keys():
        timea=pausetime.pop(guildid)
        return int(time.time()*1000)-timea
    else:
        pausetime[guildid]=int(time.time()*1000)
        return -1

@atri.command(aliases=["断开"])
async def disconnect(ctx, *a):
    userdata.find_one_and_update({"_id":str(ctx.author.id)},
                                  {"$inc":{"interactions":1}},upsert=True)
    players[ctx.guild.id] = discord.utils.get(atri.voice_clients, guild=ctx.guild)
    if players[ctx.guild.id]:
        await players[ctx.guild.id].disconnect()
        players.pop(ctx.guild.id)
        await ctx.send(replacetrans("bye",ctx.author.id))
    else:
        await ctx.send(replacetrans("bye_mad",ctx.author.id))

@atri.command(aliases=["连接"])
async def connect(ctx, *a):
    userdata.find_one_and_update({"_id":str(ctx.author.id)},
                                  {"$inc":{"interactions":1}},upsert=True)
    if ctx.author.voice:
        if ctx.guild.id in players.keys():
            if players[ctx.ctx.guild.id] and  not players[ctx.guild.id].is_playing():
                await players[ctx.guild.id].move_to(ctx.message.author.voice.channel)
            else:
                players.pop(ctx.guild.id)
                await  ctx.message.author.voice.channel.connect()
                players[ctx.guild.id] = discord.utils.get(atri.voice_clients, guild=ctx.guild)
                await ctx.send(replacetrans("connect", ctx.author.id))
                await ctx.send(
                    replacetrans("show_web_address_user", ctx.author.id, key["songctladdr"] + str(ctx.guild.id)))
        else:
            await ctx.message.author.voice.channel.connect()
            players[ctx.guild.id] = discord.utils.get(atri.voice_clients, guild=ctx.guild)

            await ctx.send(replacetrans("connect",ctx.author.id))
            await ctx.send(replacetrans("show_web_address_user",ctx.author.id,key["songctladdr"]+str(ctx.guild.id)))
    else:
        await ctx.send(replacetrans("error_not_connected",ctx.author.id))


@atri.command(aliases=["数数"])
async def count(ctx, *v):
    userdata.find_one_and_update({"_id":str(ctx.author.id)},
                                  {"$inc":{"interactions":1}},upsert=True)
    if ctx.author.voice:
        await ctx.message.author.voice.channel.connect()
        players[ctx.guild.id] = discord.utils.get(atri.voice_clients, guild=ctx.guild)
        players[ctx.guild.id].play(discord.FFmpegPCMAudio(dirpath + "count.mp3"))
    else:
        await ctx.send(replacetrans("error_not_connected",ctx.author.id))


@atri.command(aliases=["gomenasai", "对不起", "本当にごめんなさい", "ほんどにごめなさい"])
async def sorry(ctx, *v):
    userdata.find_one_and_update({"_id":str(ctx.author.id)},
                                  {"$inc":{"interactions":1}},upsert=True)
    try:
        if ctx.message.author.voice:
            for m in ctx.message.author.voice.channel.members:
                if m.id == 652615081682796549:
                    # await ctx.send("目标频道里有可怕的coffee，拒绝执行。红豆泥！私密马赛~~~")
                    raise RuntimeError("当前频道里有可怕的coffee，拒绝执行。红豆泥！私密马赛~~~")
        if ctx.voice_client:
            if ctx.voice_client.is_connected:
                for m in ctx.voice_client.channel.members:
                    if m.id == 652615081682796549:
                        # await ctx.send("当前频道里有可怕的coffee，拒绝执行。红豆泥！私密马赛~~~")
                        raise RuntimeError("当前频道里有可怕的coffee，拒绝执行。红豆泥！私密马赛~~~")
        pass
    except Exception as e:
        await ctx.send("亚托莉炸了 QAQ")
        with open("err.txt", "w") as file:
            file.write(str(traceback.format_exc()))
        # send file to Discord in message
        with open("err.txt", "rb") as file:
            await ctx.send("错误文件：", file=discord.File(file, "err.txt"))
        return
    if ctx.author.voice:
        if ctx.voice_client:
            if ctx.voice_client.is_connected:
                await ctx.voice_client.disconnect()
        await ctx.message.author.voice.channel.connect()
        players[ctx.guild] = discord.utils.get(atri.voice_clients, guild=ctx.guild)
        players[ctx.guild].play(discord.FFmpegPCMAudio(dirpath + "honndonigomenasai.mp3"))
        await asyncio.sleep(5)
        await ctx.voice_client.disconnect()
    else:
        await ctx.send("红豆泥！私密马赛~~~")

@atri.command(aliases=["暂停","resume","继续"])
async def pause(ctx, *a):
    userdata.find_one_and_update({"_id":str(ctx.author.id)},
                                  {"$inc":{"interactions":1}},upsert=True)
    players[ctx.guild.id] = discord.utils.get(atri.voice_clients, guild=ctx.guild)
    if players[ctx.guild.id]:
        if players[ctx.guild.id].is_playing():
            players[ctx.guild.id].pause()
            pausesong(int(ctx.guild.id))
        else:
            players[int(ctx.guild.id)].resume()
            cstarttime[int(ctx.guild.id)]=cstarttime[ctx.guild.id]+pausesong(ctx.guild.id)
    else:
        await ctx.send(replacetrans("not_connected_pause",ctx.author.id))

@atri.command(aliases=["停"])
async def stop(ctx, *a):
    userdata.find_one_and_update({"_id":str(ctx.author.id)},
                                  {"$inc":{"interactions":1}},upsert=True)
    players[ctx.guild.id] = discord.utils.get(atri.voice_clients, guild=ctx.guild)
    if players[ctx.guild.id]:
        players[ctx.guild.id].stop()
        await ctx.send(replacetrans("stop",ctx.author.id))
    else:
        await ctx.send(replacetrans("not_connected_stop",ctx.author.id))

@atri.command(aliases=["跳过", "下一首"])
async def skip(ctx, a=1):
    userdata.find_one_and_update({"_id":str(ctx.author.id)},
                                  {"$inc":{"interactions":1}},upsert=True)
    players[ctx.guild.id] = discord.utils.get(atri.voice_clients, guild=ctx.guild)
    if players[ctx.guild.id]:
        try:
            if queues[ctx.guild.id]:
                try:
                    for x in range(int(a)):
                        players[ctx.guild.id].stop()
                except:
                    players[ctx.guild.id].stop()
            else:
                players[ctx.guild.id].stop()
        except:
            players[ctx.guild.id].stop()
    else:
        await ctx.send(replacetrans("not_conneted_skip",ctx.author.id))

# @atri.command()
# async def level(ctx, *a):
#     await ctx.send(userdata[str(ctx.author.id)]["haogandu"])
#


@atri.command()
async def stopadding(ctx):
    userdata.find_one_and_update({"_id":str(ctx.author.id)},
                                  {"$inc":{"interactions":1}},upsert=True)
    adding[ctx.guild.id] = False
    await ctx.send("ok")
@atri.command()
async def help(ctx):
    userdata.find_one_and_update({"_id":str(ctx.author.id)},
                                  {"$inc":{"interactions":1}},upsert=True)
    await ctx.send(key["songctlhost"]+"/help.html")
@atri.command()
async def clearqueue(ctx):
    userdata.find_one_and_update({"_id":str(ctx.author.id)},
                                  {"$inc":{"interactions":1}},upsert=True)
    await ctx.send("ok")
    queues[ctx.guild.id] = {}

@atri.command(aliases=["当前歌曲", "cs"])
async def currentsong(ctx, *a):
    userdata.find_one_and_update({"_id":str(ctx.author.id)},
                                  {"$inc":{"interactions":1}},upsert=True)
    if cs[ctx.guild.id]:
        await ctx.send(replacetrans("now_playing",ctx.author.id,cs[ctx.guild.id][0]))
@atri.command()
async def fix(ctx):
    userdata.find_one_and_update({"_id":str(ctx.author.id)},
                                  {"$inc":{"interactions":1}},upsert=True)
    user=await atri.fetch_user(834651231871434752)
    efn=dirpath + "./err"+str(round(time.time()))+".txt"
    with codecs.open(efn, encoding='utf-8', mode='w') as file:
        file.write(str(traceback.format_exc())+"\n\n"+str(cs)+"\n\n"+str(queues)+"\n\n"+str(players))
    await user.send("快过来修我！")
    await user.send("错误文件：", file=discord.File(efn, "err.txt"))

    await ctx.send(replacetrans("developer_notified",ctx.author.id))

@atri.command()
async def status(ctx):
    userdata.find_one_and_update({"_id":str(ctx.author.id)},
                                  {"$inc":{"interactions":1}},upsert=True)
    await ctx.send("亚托莉目前加入了"+str(len(atri.guilds))+"个服务器")
    await ctx.send("已连接到"+str(len(players))+"个语音频道")
    await ctx.send("有"+str(userdata.count_documents({}))+"个人使用过亚托莉")
    await ctx.send("正在播放"+str(len(cs.keys()))+"首歌曲")
    await ctx.send("播放过"+str(songdata.count_documents({"play_count":{"$exists":True,"$ne":0}}))+"首歌曲（不重复计算）")
@tasks.loop(seconds=30 )
async def writeplays():
    activitymap={"listening":discord.ActivityType.listening,"watching":discord.ActivityType.watching,"playing":discord.ActivityType.playing,"streaming":discord.ActivityType.streaming,"competing":discord.ActivityType.competing}
    if globalconfig.find_one() is None or globalconfig.find_one()["custompresense"]=="":
        await atri.change_presence(activity=discord.Activity(type=discord.ActivityType.listening,name="主人的命令||" + name[0] + "play <歌曲>||支持网易云，哔哩哔哩，youtube，ニコニコ"))
    else:
        await atri.change_presence(activity=discord.Activity(type=activitymap[globalconfig.find_one()["activitytype"]],name=globalconfig.find_one()["custompresense"]))

    #await asyncio.sleep(5)
    #print("主人我正在保存数据喵~")
    # with codecs.open(dirpath + "./haogan.json", encoding='utf-8', mode='w') as f:
    #     f.write(json.dumps(userdata))
    # with codecs.open(dirpath + "./waifulist.txt", encoding='utf-8', mode='w') as f:
    #     f.write(str(waifulist))
    # with codecs.open(dirpath + "blacklist.json", encoding="utf-8", mode="w") as f:
    #     f.write(json.dumps(blacklist))
    #print("数据保存完毕，大家的信息我已经完美的记录下来的喵~")
    # print("主人我正在打扫房间~")
    # # for f in os.listdir(dirpath+"ytdltemp"):
    # #     os.remove(os.path.join(dirpath+"ytdltemp", f))
    # # for filename in os.listdir(dirpath+"songcache"):
    # #     if os.stat(filename).st_size==0:
    # #         os.remove(filename)
    # #1
    # print("主人，房间已经清扫的干干净净了喵~")
@tasks.loop(seconds=1)
async def connecttovoice():
    if len(workaround)>0:
        connectinfo=workaround.pop()
        await connectinfo[0].connect()
        players[connectinfo[1]] = discord.utils.get(atri.voice_clients, guild=connectinfo[2])


def startatri():

    atri.run(key["key"])

if __name__ == '__main__':
    thread = threading.Thread(target=serve,args=[app],kwargs={ "host":"0.0.0.0", "port":key["serverport"]})
    thread.start()
    startatri()
    thread.join()
