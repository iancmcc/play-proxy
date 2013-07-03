from gevent import monkey; monkey.patch_all()
from bs4 import BeautifulSoup
import bottle
import requests
from bottle import route, run, template, request

PLAY = 'http://play.google.com/store/search'


def searchPlay(search):
    data = []
    if not search:
        return dict(total=len(data), data=data)
    response = requests.get(PLAY, params={'c':'apps', 'q':search}, cookies={})
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
