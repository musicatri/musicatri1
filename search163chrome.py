#借鉴 https://cloud.tencent.com/developer/article/1794963
#
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

# chrome_options.add_argument('--headless')
# chrome_options.add_argument('--disable-gpu')
if platform.system() == "Windows":
    executable_path=dirpath+'chromedriver.exe'
else:
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
        music_names = soup.select("div[class='td w0'] a b")  # 音乐名字
        music_singers = soup.select("div[class='td w1']")  # 歌手名
        searchresults=[]
        for n in range(min(len(music_ids), len(music_names), len(music_singers))):
            music_id = music_ids[n].get("href")
            music_id = music_id.split('=')[-1]
            print(music_id)
            music_name = music_names[n].get("title")
            music_singer = music_singers[n].string
            print(music_name)
            print(music_singer)
            if music_singer == None:
                music_singer=str(music_singers[n].a.string)
            if not exists(dirpath+"./datacache/"+music_id+".s163dddd") or not exists(dirpath+"./datacache/"+id):
                with open(dirpath+"./datacache/"+music_id+".s163dddd", encoding='utf-8', mode='w') as f:
                    f.write(str([music_singer,music_name]))
            #searchresults.append([music_id,music_name,music_singer])
            searchresults.append(music_id)
        browser.execute_script("window.open('about:blank');","newblank")
        browser.close()
        browser.switch_to.window(browser.window_handles[0])
        searchresults=tuple(searchresults)
        searchcache[id]=searchresults
        return [searchresults]
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
def login163():
    chrome_options = Options()

    browser = webdriver.Chrome(executable_path=executable_path, chrome_options=chrome_options,desired_capabilities=caps)
    url = "http://music.163.com/"
    browser.get(url=url)
    input("登录完成请按回车")
    browser.quit()
#
#
if __name__ == '__main__':
    login163()
