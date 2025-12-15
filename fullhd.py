# =================== 智能万能 CDN 加速块（2025-12-08 按实测排序） ===================
import requests, time, threading, queue
from functools import lru_cache

sess = requests.Session()
adapter = requests.adapters.HTTPAdapter(pool_connections=20, pool_maxsize=50)
sess.mount('http://', adapter)
sess.mount('https://', adapter)

# 1. 按你最新测速结果排序（DNS 0 ms，下载均值由低到高）
CDN_POOL = ['lib.baomitu.com', 'open.oppomobile.com']

# 2. 死链替换表（保持最新可用节点）
DEAD_MAP = {
    'lib.baomitu.com':   CDN_POOL[0],
    'open.oppomobile.com': CDN_POOL[0]
}

# 3. 并发测速（返回 ms，失败 9999）
def _ping(host):
    try:
        t0 = time.perf_counter()
        sess.head(f'https://{host}/favicon.ico', timeout=0.8)
        return int((time.perf_counter() - t0) * 1000)
    except:
        return 9999

# 4. 启动时自动排序（只跑一次）
def _rank_cdn():
    q = queue.Queue()
    for h in CDN_POOL:
        threading.Thread(target=lambda h: q.put((_ping(h), h)), args=(h,), daemon=True).start()
    ranked = sorted([q.get() for _ in CDN_POOL])
    return [h for _, h in ranked if _ < 9999] or CDN_POOL
FASTEST_CDN = _rank_cdn()
print('[CDN] 自动测速完成，最优顺序：', FASTEST_CDN)

# 5. 智能选路 + 缓存（lru_cache 线程安全）
@lru_cache(maxsize=256)
def auto_cdn_url(url: str, follow_redirect: bool = False, proxy_base: str = None):
    if not url:
        return ''
    # 5.1 先替换死链
    for dead, fast in DEAD_MAP.items():
        url = url.replace(dead, fast)
    # 5.2 轮询最优 CDN
    host = url.split('/')[2]
    for cdn in FASTEST_CDN:
        if cdn == host:
            continue
        test = url.replace(host, cdn)
        try:
            r = sess.head(test, allow_redirects=False, timeout=2)
            if r.status_code == 200:
                url = test
                break
        except:
            continue
    # 5.3 302 追踪（播放链需要）
    if follow_redirect:
        url = sess.get(url, stream=True, timeout=5).url
    # 5.4 代理前缀（可选）
    if proxy_base and not url.startswith(proxy_base):
        url = f'{proxy_base}{requests.utils.quote(url)}'
    return url
# =================== 智能CDN块结束 ===================
import requests
from bs4 import BeautifulSoup
import re
from base.spider import Spider
import sys
import json
import base64
import urllib.parse
from Crypto.Cipher import ARC4
from Crypto.Util.Padding import unpad
import binascii

sys.path.append('..')

xurl = "https://www.fullhd.xxx/zh/"

headerx = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.87 Safari/537.36'
          }

pm = ''

class Spider(Spider):
    global xurl
    global headerx

    def getName(self):
        return "首页"

    def init(self, extend):
        pass

    def isVideoFormat(self, url):
        pass

    def manualVideoCheck(self):
        pass

    def extract_middle_text(self, text, start_str, end_str, pl, start_index1: str = '', end_index2: str = ''):
        if pl == 3:
            plx = []
            while True:
                start_index = text.find(start_str)
                if start_index == -1:
                    break
                end_index = text.find(end_str, start_index + len(start_str))
                if end_index == -1:
                    break
                middle_text = text[start_index + len(start_str):end_index]
                plx.append(middle_text)
                text = text.replace(start_str + middle_text + end_str, '')
            if len(plx) > 0:
                purl = ''
                for i in range(len(plx)):
                    matches = re.findall(start_index1, plx[i])
                    output = ""
                    for match in matches:
                        match3 = re.search(r'(?:^|[^0-9])(\d+)(?:[^0-9]|$)', match[1])
                        if match3:
                            number = match3.group(1)
                        else:
                            number = 0
                        if 'http' not in match[0]:
                            output += f"#{'📽️' + match[1]}${number}{xurl}{match[0]}"
                        else:
                            output += f"#{'📽️' + match[1]}${number}{match[0]}"
                    output = output[1:]
                    purl = purl + output + "$$$"
                purl = purl[:-3]
                return purl
            else:
                return ""
        else:
            start_index = text.find(start_str)
            if start_index == -1:
                return ""
            end_index = text.find(end_str, start_index + len(start_str))
            if end_index == -1:
                return ""

        if pl == 0:
            middle_text = text[start_index + len(start_str):end_index]
            return middle_text.replace("\\", "")

        if pl == 1:
            middle_text = text[start_index + len(start_str):end_index]
            matches = re.findall(start_index1, middle_text)
            if matches:
                jg = ' '.join(matches)
                return jg

        if pl == 2:
            middle_text = text[start_index + len(start_str):end_index]
            matches = re.findall(start_index1, middle_text)
            if matches:
                new_list = [f'✨{item}' for item in matches]
                jg = '$$$'.join(new_list)
                return jg

    def homeContent(self, filter):
        result = {}
        result = {"class": [
        {"type_id": "latest-updates", "type_name": "最新视频🌠"},
        {"type_id": "top-rated", "type_name": "最佳视频🌠"},
        {"type_id": "most-popular", "type_name": "热门影片🌠"},
        {"type_id": "networks/brazzers-com", "type_name": "Brazzers🌠"},
        {"type_id": "networks/tushy-com", "type_name": "Tushy🌠"},
        {"type_id": "networks/naughtyamerica-com", "type_name": "Naughtyamerica🌠"},
        {"type_id": "sites/sexmex", "type_name": "Sexmex🌠"},
        {"type_id": "sites/passion-hd", "type_name": "Passion-HD🌠"},
        {"type_id": "categories/animation", "type_name": "Animation🌠"},
        {"type_id": "categories/18-years-old", "type_name": "Teen🌠"},
        {"type_id": "categories/pawg", "type_name": "Pawg🌠"},
        {"type_id": "categories/thong", "type_name": "Thong🌠"},
        {"type_id": "categories/stockings", "type_name": "Stockings🌠"},
        {"type_id": "categories/jav-uncensored", "type_name": "JAV🌠"},
        {"type_id": "categories/pantyhose", "type_name": "Pantyhose🌠"}
                            ],
                 }
        return result

    def homeVideoContent(self):
        videos = []
        try:
            detail = requests.get(url=xurl, headers=headerx)
            detail.encoding = "utf-8"
            res = detail.text
            doc = BeautifulSoup(res, "lxml")

            # Get videos from different sections
            sections = {
                "latest-updates": "最新视频",
                "top-rated": "最佳视频",
                "most-popular": "热门影片"
            }
            
            for section_id, section_name in sections.items():
                section = doc.find('div', id=f"list_videos_videos_watched_right_now_items")
                if not section:
                    continue
                    
                vods = section.find_all('div', class_="item")
                for vod in vods:
                    names = vod.find_all('a')
                    name = names[0]['title'] if names and 'title' in names[0].attrs else section_name

                    ids = vod.find_all('a')
                    id = ids[0]['href'] if ids else ""

                    # 获取图片 - 适配两种不同的img标签结构
                    pic = ""
                    # 第一种方式：查找带有data-src属性的img标签
                    pics = vod.find('img', class_="lazyload")
                    if pics and pics.get('data-src'):
                        pic = pics['data-src']
                    # 第二种方式：查找带有src属性的img标签
                    if not pic:
                        pics = vod.find('img', class_="thumb_img")
                        if pics and pics.get('src'):
                            pic = pics['src']
                    
                    # 如果找到了图片但URL不完整，添加基础URL
                    if pic and 'http' not in pic:
                        pic = xurl + pic

                    remarks = vod.find('span', class_="duration")
                    remark = remarks.text.strip() if remarks else ""

                    video = {
                        "vod_id": id,
                        "vod_name": name,
                        "vod_pic": pic,
                        "vod_remarks": remark
                    }
                    videos.append(video)

            result = {'list': videos}
            return result
        except Exception as e:
            print(f"Error in homeVideoContent: {str(e)}")
            return {'list': []}

    def categoryContent(self, cid, pg, filter, ext):
        result = {}
        videos = []
        try:
            if pg and int(pg) > 1:
                url = f'{xurl}/{cid}/{pg}/'
            else:
                url = f'{xurl}/{cid}/'

            detail = requests.get(url=url, headers=headerx)
            detail.encoding = "utf-8"
            res = detail.text
            doc = BeautifulSoup(res, "lxml")

            section = doc.find('div', class_="list-videos")
            if section:
                vods = section.find_all('div', class_="item")
                for vod in vods:
                    names = vod.find_all('a')
                    name = names[0]['title'] if names and 'title' in names[0].attrs else ""

                    ids = vod.find_all('a')
                    id = ids[0]['href'] if ids else ""

                    # 获取图片 - 适配两种不同的img标签结构
                    pic = ""
                    # 第一种方式：查找带有data-src属性的img标签
                    pics = vod.find('img', class_="lazyload")
                    if pics and pics.get('data-src'):
                        pic = pics['data-src']
                    # 第二种方式：查找带有src属性的img标签
                    if not pic:
                        pics = vod.find('img', class_="thumb_img")
                        if pics and pics.get('src'):
                            pic = pics['src']
                    
                    # 如果找到了图片但URL不完整，添加基础URL
                    if pic and 'http' not in pic:
                        pic = xurl + pic

                    remarks = vod.find('span', class_="duration")
                    remark = remarks.text.strip() if remarks else ""

                    video = {
                        "vod_id": id,
                        "vod_name": name,
                        "vod_pic": pic,
                        "vod_remarks": remark
                    }
                    videos.append(video)

        except Exception as e:
            print(f"Error in categoryContent: {str(e)}")

        result = {
            'list': videos,
            'page': pg,
            'pagecount': 9999,
            'limit': 90,
            'total': 999999
        }
        return result

    def detailContent(self, ids):
        global pm
        did = ids[0]
        result = {}
        videos = []
        playurl = ''
        if 'http' not in did:
            did = xurl + did
        res1 = requests.get(url=did, headers=headerx)
        res1.encoding = "utf-8"
        res = res1.text

        content = '👉' + self.extract_middle_text(res,'<h1>','</h1>', 0)

        yanuan = self.extract_middle_text(res, '<span>Pornstars:</span>','</div>',1, 'href=".*?">(.*?)</a>')

        bofang = did

        videos.append({
            "vod_id": did,
            "vod_actor": yanuan,
            "vod_director": '',
            "vod_content": content,
            "vod_play_from": '书生玩剣ⁱ·*₁＇',
            "vod_play_url": bofang
                     })

        result['list'] = videos
        return result

    def playerContent(self, flag, id, vipFlags):
        parts = id.split("http")
        xiutan = 0
        if xiutan == 0:
            if len(parts) > 1:
                before_https, after_https = parts[0], 'http' + parts[1]
            res = requests.get(url=after_https, headers=headerx)
            res = res.text

            url2 = self.extract_middle_text(res, '<video', '</video>', 0).replace('\\', '')
            soup = BeautifulSoup(url2, 'html.parser')
            first_source = soup.find('source')
            src_value = first_source.get('src')

            response = requests.head(src_value, allow_redirects=False)
            if response.status_code == 302:
                redirect_url = response.headers['Location']

            response = requests.head(redirect_url, allow_redirects=False)
            if response.status_code == 302:
                redirect_url = response.headers['Location']

            result = {}
            result["parse"] = xiutan
            result["playUrl"] = ''
            result["url"] = redirect_url
            result["header"] = headerx
            return result

    def searchContentPage(self, key, quick, page):
        result = {}
        videos = []
        if not page:
            page = '1'
        if page == '1':
            url = f'{xurl}/search/{key}/'
        else:
            url = f'{xurl}/search/{key}/{str(page)}/'

        try:
            detail = requests.get(url=url, headers=headerx)
            detail.encoding = "utf-8"
            res = detail.text
            doc = BeautifulSoup(res, "lxml")

            section = doc.find('div', class_="list-videos")
            if section:
                vods = section.find_all('div', class_="item")
                for vod in vods:
                    names = vod.find_all('a')
                    name = names[0]['title'] if names and 'title' in names[0].attrs else ""

                    ids = vod.find_all('a')
                    id = ids[0]['href'] if ids else ""

                    # 获取图片 - 适配两种不同的img标签结构
                    pic = ""
                    # 第一种方式：查找带有data-src属性的img标签
                    pics = vod.find('img', class_="lazyload")
                    if pics and pics.get('data-src'):
                        pic = pics['data-src']
                    # 第二种方式：查找带有src属性的img标签
                    if not pic:
                        pics = vod.find('img', class_="thumb_img")
                        if pics and pics.get('src'):
                            pic = pics['src']
                    
                    # 如果找到了图片但URL不完整，添加基础URL
                    if pic and 'http' not in pic:
                        pic = xurl + pic

                    remarks = vod.find('span', class_="duration")
                    remark = remarks.text.strip() if remarks else ""

                    video = {
                        "vod_id": id,
                        "vod_name": name,
                        "vod_pic": pic,
                        "vod_remarks": remark
                    }
                    videos.append(video)
        except Exception as e:
            print(f"Error in searchContentPage: {str(e)}")

        result = {
            'list': videos,
            'page': page,
            'pagecount': 9999,
            'limit': 90,
            'total': 999999
        }
        return result

    def searchContent(self, key, quick):
        return self.searchContentPage(key, quick, '1')

    def localProxy(self, params):
        if params['type'] == "m3u8":
            return self.proxyM3u8(params)
        elif params['type'] == "media":
            return self.proxyMedia(params)
        elif params['type'] == "ts":
            return self.proxyTs(params)

        return None
