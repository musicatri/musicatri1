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
from selenium.webdriver.firefox.options import Options

dirpath = dirname(realpath(__file__))+"/"
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1847.137 Safari/537.36 LBBROWSER'
}

caps = DesiredCapabilities().FIREFOX
caps["pageLoadStrategy"] = "eager"

firefox_options = Options()
firefox_options.binary_location = r'/usr/bin/firefox'
firefox_options.headless = True
executable_path = 'geckodriver'
browser = webdriver.Firefox(executable_path=executable_path, options=firefox_options, desired_capabilities=caps)


def get_id(id):
    browser.get(url='https://music.163.com/#/search/m/?s=' + id + '&type=1')
    browser.switch_to.frame('g_iframe')
    page_text = browser.execute_script("return document.documentElement.outerHTML")
    soup = bs4.BeautifulSoup(page_text, 'html.parser')
    music_ids = soup.select("div[class='td w0'] a")  # 音乐id
    music_id = music_ids[0].get("href")
    music_id = music_id.split('=')[-1]
    print(traceback.format_exc())
    return music_id


def get_id_and_cache_data(id):
    try:
        browser.get(url='https://music.163.com/#/search/m/?s=' + id + '&type=1')
        browser.switch_to.frame('g_iframe')
        page_text = browser.execute_script("return document.documentElement.outerHTML")
        soup = bs4.BeautifulSoup(page_text, 'html.parser')
        music_ids = soup.select("div[class='td w0'] a")  # 音乐id
        music_id = music_ids[0].get("href")
        music_id = music_id.split('=')[-1]
        if not exists(dirpath + "./datacache/" + music_id + ".s163dddd") or not exists(dirpath + "./datacache/" + id):
            with open(dirpath + "./datacache/" + music_id + ".s163dddd", encoding='utf-8', mode='w') as f:
                music_names = soup.select("div[class='td w0'] a b")  # 音乐名字
                music_name = music_names[0].get("title")
                music_singers = soup.select("div[class='td w1'] a")  # 歌手名
                music_singer = music_singers[0].string
                a = []
                a.append(music_name)
                a.append(music_singer)
                a = str(a)
                print(a)
                f.write(a)
        return [music_id]
    except:
        return [False]


def get_id_name_singer(id):
    url = 'https://music.163.com/#/search/m/?s=' + id + '&type=1'
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
    return [music_id, music_name, music_singer]
