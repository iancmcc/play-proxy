import logging
from gevent import monkey; monkey.patch_all()
from bs4 import BeautifulSoup
import bottle
import random
import requests
from bottle import route, run, template, request

log = logging.getLogger(__name__)

PLAY = 'http://play.google.com/store/search'

UASTRS = [
    "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET4.0C; McAfee; OfficeLiveConnector.1.5; OfficeLivePatch.1.3)",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 6_1_3 like Mac OS X) AppleWebKit/536.26 (KHTML, like Gecko) Mobile/10B329",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_4) AppleWebKit/536.30.1 (KHTML, like Gecko)",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.1; Trident/6.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C; Microsoft Outlook 14.0.6131; ms-office; MSOffice 14)",
    "Mozilla/5.0 (Linux; U; Android 1.5; de-de; HTC Magic Build/CRB17) AppleWebKit/528.5+ (KHTML, like Gecko) Version/3.1.2 Mobile Safari/525.20.1",
    "Mozilla/5.0 (Linux; U; Android 2.1-update1; en-au; HTC_Desire_A8183 V1.16.841.1 Build/ERE27) AppleWebKit/530.17 (KHTML, like Gecko) Version/4.0 Mobile Safari/530.17",
    "Mozilla/5.0 (Linux; U; Android 4.2; en-us; Nexus 10 Build/JVP15I) AppleWebKit/534.30 (KHTML, like Gecko) Version/4.0 Safari/534.30"
]

def randip():
    while True:
        yield ".".join(str(random.randint(1, 255)) for i in range(4))

RAND = randip()

def searchPlay(search):
    data = []
    if not search:
        return dict(total=len(data), data=data)
    headers = {
        "User-Agent": random.choice(UASTRS),
        "Cache-Control": "no-cache",
        "Pragma": "no-cache",
        "Expires": "Thu, 01 Jan 1970 00:00:00 GMT"
    }
    response = requests.get(PLAY, headers=headers, params={'c':'apps', 'q':search}, cookies={})
    if response.status_code != 200:
        log.warn('google play app search failed %s', search)
        return

    soup = BeautifulSoup(response.text)
    results = soup.find_all('li', {'data-docid':True})
    for result in results:
        package_name = result.get('data-docid')
        if package_name is None:
            log.warn('package_name not found skipping app')
            continue
        icon_url = result.find('a', {'class':'thumbnail'}).img['src']
        icon_url = icon_url[:-8] + '=w32'
        title = result.find('a', {'class':'title'}).text
        creator = result.find('a', {'class':'goog-inline-block'}).text
        category = result.find('span', {'class': 'category'})
        if category: category = category.a.text
        data.append(dict(icon_url=icon_url, package_name=package_name,
                        title=title, creator=creator, category=category))
    return dict(total=len(data), data=data)


@route('/query')
def query():
    search = request.query.get('q')
    return searchPlay(search)


app = bottle.default_app()
