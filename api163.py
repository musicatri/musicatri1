"""
2021/9/20
"""
from os.path import exists
from os import remove
import codecs
import json
from ast import literal_eval as list
import requests
from os.path import dirname
from os.path import realpath
dirpath = dirname(realpath(__file__))+"/"
def __getlistdictfirst(l):
    nl=[]
    for i in l:
        nl.append(i['name'])
    return nl
def getsongdetail(id):
    if exists(dirpath+"./datacache/"+id):
        with codecs.open(dirpath+"./datacache/"+id, encoding='utf-8', mode='r') as f:
            return json.loads(f.read())
    if exists(dirpath+"./datacache/"+id+".s163dddd"):
        return False
    else:
        with codecs.open(dirpath+"./datacache/"+id, encoding='utf-8', mode='w') as f:
            d=str(requests.get("http://music.163.com/api/song/detail/?id="+id+"&ids=%5B"+id+"%5D").content.decode("utf-8"))
            f.write(d)
            return json.loads(d)

def getsongname(id):
    d=getsongdetail(id)
    if d:
        try:
            return (d["songs"][0])["name"]
        except:
            remove("./datacache/"+id)
            return "获取歌曲名称失败"
    else:
        with codecs.open(dirpath+"./datacache/"+id+".s163dddd", encoding='utf-8', mode='r') as f:
            return list(f.read())[0]
def getsongartists(id):
    d=getsongdetail(id)
    if d:
        try:
            return __getlistdictfirst((getsongdetail(id)["songs"][0])["artists"])
        except:
            remove("./datacache/"+id)
            return "获取歌曲作曲家失败"
    else:
        with codecs.open(dirpath+"./datacache/"+id+".s163dddd", encoding='utf-8', mode='r') as f:
            return list(f.read())[1]
#print(getsongartists("1315295569"))
