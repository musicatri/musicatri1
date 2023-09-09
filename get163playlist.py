import json
import platform
import re
from os.path import dirname
from os.path import realpath

import bs4
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

dirpath = dirname(realpath(__file__))+"/"
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1847.137 Safari/537.36 LBBROWSER'
}

#C:\Users\Administrator\AppData\Local\Google\Chrome\User Data\Default
caps = DesiredCapabilities().CHROME
caps["pageLoadStrategy"] = "eager"
# 实现无可视化界面（固定写法）
chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--disable-gpu')
# if platform.system() == "Windows":
#     executable_path=dirpath+'chromedriver.exe'
# else:
executable_path='chromedriver'

def getlistids(url):
    browser = webdriver.Chrome(executable_path=executable_path, chrome_options=chrome_options,desired_capabilities=caps)
    url = "http://music.163.com/"+url[url.find("playlist"):].replace('/#', '').replace('https', 'http')
    browser.get(url=url)
    browser.switch_to.frame('g_iframe')
    page_text = browser.execute_script("return document.documentElement.outerHTML")
    soup = bs4.BeautifulSoup(page_text, 'html.parser')
    music_datas = soup.select("div[class='f-cb'] a")  # 音乐id
    music_ids=[]
    for music_data in music_datas:
        try:
            int(music_data.get("href").split('=')[-1])
            music_ids.append(music_data.get("href").split('=')[-1])
        except:
            pass
    # if not exists("./datacache/"+music_id+".s163dddd") or not exists("./datacache/"+id):
    #     with open(dirpath+"./datacache/"+music_id+".s163dddd",, encoding='utf-8', mode='r') as f:
    #         music_names = soup.select("div[class='td w0'] a b")  # 音乐名字
    #         music_name = music_names[0].get("title")
    #         music_singers = soup.select("div[class='td w1'] a")  # 歌手名
    #         music_singer = music_singers[0].string
    #         a=[]
    #         a.append(music_name)
    #         a.append(music_singer)
    #         a=str(a)
    #         print(a)
    #         f.write(a)
    # browser.quit()
    print(music_ids)
    browser.quit()
    return music_ids

def getlistidsnochrome(url):
    from lxml import etree
    url = "http://music.163.com/"+url[url.find("playlist"):].replace('/#', '').replace('https', 'http')  # 对字符串进行去空格和转协议处理

    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36',
        'Referer': 'https://music.163.com/',
        'Host': 'music.163.com'
    }
    res = requests.get(url=url, headers=headers).text

    tree = etree.HTML(res)
    # 音乐列表
    song_list = tree.xpath('//ul[@class="f-hide"]/li/a')
    # 如果是歌手页面
    artist_name_tree = tree.xpath('//h2[@id="artist-name"]/text()')
    artist_name = str(artist_name_tree[0]) if artist_name_tree else None
    # 如果是歌单页面：
    #song_list_tree = tree.xpath('//*[@id="m-playlist"]/div[1]/div/div/div[2]/div[2]/div/div[1]/table/tbody')
    song_list_name_tree = tree.xpath('//h2[contains(@class,"f-ff2")]/text()')
    song_list_name = str(song_list_name_tree[0]) if song_list_name_tree else None
    idlist=[]
    titlelist=[]
    for i, s in enumerate(song_list):
        href = str(s.xpath('./@href')[0])
        song_id = href.split('=')[-1]
        title = str(s.xpath('./text()')[0])  # 音乐的名字
        idlist.append(song_id)
        titlelist.append(title)
    browser.quit()
    return idlist

def getgeci( song_id):
    url = 'http://music.163.com/api/song/lyric?id={}&lv=-1&kv=-1&tv=-1'.format(song_id)
    # 请求头
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36',
        'Referer': 'https://music.163.com/',
        'Host': 'music.163.com'
        # 'Origin': 'https://music.163.com'
    }
    # 请求页面的源码
    res = requests.get(url=url, headers=headers).text
    json_obj = json.loads(res)
    lyric = json_obj['lrc']['lyric']
    reg = re.compile(r'\[.*\]')
    lrc_texto = re.sub(reg, '', lyric).strip()
    try:
        json_obj = json.loads(res)
        lyric = json_obj['tlyric']['lyric']
        reg = re.compile(r'\[.*\]')
        lrc_textt = re.sub(reg, '', lyric).strip()
        return [lrc_texto,lrc_textt]
    except:
        return [lrc_texto]
def login163():
    browser = webdriver.Chrome(executable_path=executable_path,desired_capabilities=caps)
    url = "http://music.163.com/"
    browser.get(url=url)
    input("登录完成请按回车")
    browser.quit()
#
if __name__ == '__main__':
    login163()
# def get_id_name_singer(id):
#     url='https://music.163.com/#/search/m/?s=' + id + '&type=1'
#     browser.get(url=url)
#     browser.switch_to.frame('g_iframe')
#     sleep(0.5)
#     page_text = browser.execute_script("return document.documentElement.outerHTML")
#     soup = bs4.BeautifulSoup(page_text, 'html.parser')
#     music_ids = soup.select("div[class='td w0'] a")  # 音乐id
#     music_id = music_ids[0].get("href")
#     music_id = music_id.split('=')[-1]
#     music_names = soup.select("div[class='td w0'] a b")  # 音乐名字
#     music_name = music_names[0].get("title")
#     music_singers = soup.select("div[class='td w1'] a")  # 歌手名
#     music_singer = music_singers[0].string
#     return [music_id, music_name, music_singer]
