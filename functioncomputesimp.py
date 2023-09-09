#阿里云函数计算歌曲代理api
import requests
def dlsong(id):
    a=requests.get("http://music.163.com/song/media/outer/url?id="+id.replace(" ","")+".mp3", headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36'})
    if a.headers['content-type'].find("audio") == -1:
        return False
    return a.content
def handler(environ, start_response):
    res=""
    try:
        response_headers = [('Content-type', 'audio/mp3')]
        res = dlsong(environ['QUERY_STRING'])
        if not res:
            res= "vipnotsupported".encode('utf-8')
    except (KeyError):
        response_headers = [('Content-type', 'text/plain')]
        res= "请提供一个id".encode('utf-8')
    start_response('200 OK', response_headers)
    return [res]
