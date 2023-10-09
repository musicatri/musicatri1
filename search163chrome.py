from os.path import dirname
from os.path import realpath
import requests
from os.path import exists
import platform
import bs4
from selenium import webdriver
from time import sleep
import traceback
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.chrome.options import Options
dirpath = dirname(realpath(__file__))+"/"
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1847.137 Safari/537.36 LBBROWSER'
}


caps = DesiredCapabilities().CHROME
caps["pageLoadStrategy"] = "eager"
# 实现无可视化界面（固定写法）
chrome_options = Options()

chrome_options.add_argument('--headless')
chrome_options.add_argument('--disable-gpu')
# if platform.system() == "Windows":
#     executable_path=dirpath+'chromedriver.exe'
# else
executable_path='/usr/bin/chromedriver'
browser = webdriver.Chrome(executable_path=executable_path, chrome_options=chrome_options,desired_capabilities=caps)
searchcache={}
def get_id(id):
    # global browser
    # if not browser:
    #     browser = webdriver.Chrome(executable_path=executable_path, chrome_options=chrome_options,desired_capabilities=caps)
    browser.get(url='https://music.163.com/#/search/m/?s=' + id + '&type=1')
    browser.switch_to.frame('g_iframe')
    page_text = browser.execute_script("return document.documentElement.outerHTML")
    soup = bs4.BeautifulSoup(page_text, 'html.parser')
    music_ids = soup.select("div[class='td w0'] a")  # 音乐id
    music_id = music_ids[0].get("href")
    music_id = music_id.split('=')[-1]
    print(traceback.format_exc())
    browser.close()
    return music_id
def get_id_and_cache_data(id):
    # global browser
    try:
        if id in searchcache:
            return [searchcache[id]]

        browser.get(url='https://music.163.com/#/search/m/?s=' + id + '&type=1')


        browser.switch_to.frame('g_iframe')
        page_text = browser.execute_script("return document.documentElement.outerHTML")
        soup = bs4.BeautifulSoup(page_text, 'html.parser')
        music_ids = soup.select("div[class='td w0'] a")  # 音乐id
        music_id = music_ids[0].get("href")
        music_id = music_id.split('=')[-1]
        if not exists(dirpath+"./datacache/"+music_id+".s163dddd") or not exists(dirpath+"./datacache/"+id):
            with open(dirpath+"./datacache/"+music_id+".s163dddd", encoding='utf-8', mode='w') as f:
                music_names = soup.select("div[class='td w0'] a b")  # 音乐名字
                music_name = music_names[0].get("title")
                music_singers = soup.select("div[class='td w1'] a")  # 歌手名
                music_singer = music_singers[0].string
                a=[]
                a.append(music_name)
                a.append(music_singer)
                f.write(str(a))
        searchcache[id]=music_id
        browser.execute_script("window.open('about:blank');","newblank")
        browser.close()
        browser.switch_to.window(browser.window_handles[0])
        return [music_id]
    except:
        print("search failed")
        print(traceback.format_exc())
        return [False,traceback.format_exc()]

def get_id_name_singer(id):
    global browser
    if not browser:
        browser = webdriver.Chrome(executable_path=executable_path, chrome_options=chrome_options,desired_capabilities=caps)
    url='https://music.163.com/#/search/m/?s=' + id + '&type=1'
    browser.get(url=url)
    browser.switch_to.frame('g_iframe')
    sleep(0.5)
    page_text = browser.execute_script("return document.documentElement.outerHTML")
    soup = bs4.BeautifulSoup(page_text, 'html.parser')
    music_ids = soup.select("div[class='td w0'] a")  # 音乐id
    music_id = music_ids[0].get("href")
    music_id = music_id.split('=')[-1]
    music_names = soup.select("div[class='td w0'] a b")  # 音乐名字
    music_name = music_names[0].get("title")
    music_singers = soup.select("div[class='td w1'] a")  # 歌手名
    music_singer = music_singers[0].string
    browser.close()
    return [music_id, music_name, music_singer]
    print(traceback.format_exc())
