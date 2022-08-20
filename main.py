import flask
import requests
import json
from keys import *
from mail import send_mail
from justwatch import JustWatch
app = flask.Flask(__name__)

IPSTACK_URL = 'http://api.ipstack.com/{client_ip}?access_key={api_key}'


def get_provider(name, providers):
    for provider in providers:
        if provider['short_name'] == name:
            return provider['clear_name']


def get_movie_image(title):
    url = "https://imdb8.p.rapidapi.com/auto-complete"
    querystring = {"q": title}

    headers = {
        'x-rapidapi-host': "imdb8.p.rapidapi.com",
        'x-rapidapi-key': api_key
    }

    response = requests.request("GET", url, headers=headers, params=querystring).json()
    if 'd' in response:
        if response['d']:
            if len(response['d']) > 0:
                return response['d'][0]['i']['imageUrl']
    return ''


def get_movie_providers(monetization_type, movie):
    providers = []
    for i in movie['monetization_types'][monetization_type]:
        providers.append(i['provider_name'])
    return providers


def find(title, params, country):
    image = ''
    movie_data = []
    if title and len(title) > 1:
        just_watch = JustWatch(country=country)
        results = just_watch.search_for_item(query=title, providers=params)
        providers = just_watch.get_providers()
        for result in results['items']:
            if image == '':
                image = get_movie_image(result['title'])
            movie = {
                'title': result['title'],
                'monetization_types': {
                    'free':  [],
                    'flatrate': [],
                    'rent': [],
                    'buy': []
                }
            }
            if 'offers' in result:
                for offer in result['offers']:
                    if offer['monetization_type'] in movie['monetization_types']:
                        if offer['package_short_name'] in params:
                            if get_provider(offer['package_short_name'], providers) not in \
                                    get_movie_providers(offer['monetization_type'], movie):
                                provider_dict = {'provider_name': get_provider(offer['package_short_name'], providers)}
                                if 'retail_price' in offer:
                                    provider_dict['price'] = f"{offer['retail_price']} {offer['currency']}"
                                if 'urls' in offer:
                                    provider_dict['url'] = offer['urls']['standard_web']
                                movie['monetization_types'][offer['monetization_type']].append(provider_dict)
            movie_data.append(movie)
    elif len(title) < 2:
        return ["title too short"], image
    print(movie_data)
    return movie_data, image


@app.route('/', methods=['GET', 'POST'])
def home():
    title = flask.request.form.get('title')
    message = flask.request.form.get('message')
    country = ''
    if not flask.request.form.get('country'):
        client_ip = flask.request.headers.get('X-Forwarded-For')
        if client_ip:
            ip_request = requests.get(IPSTACK_URL.format(client_ip=client_ip, api_key=ipstack_key))
            ip_data = json.loads(ip_request.text)
            country = ip_data['country_code']
    else:
        country = flask.request.form.get('country')
    print(flask.request.form)
    if not title:
        if message:
            send_mail(flask.request.form.get('mail'), message, flask.request.form.get('name'))
        return flask.render_template('index.html')

    else:
        providers = []
        if flask.request.form.get('Netflix'):
            providers.append('nfx')
        if flask.request.form.get('Amazon'):
            providers.append('prv')
        if flask.request.form.get('iTunes'):
            providers.append('itu')
        if flask.request.form.get('Google Play'):
            providers.append('ply')
        if flask.request.form.get('Viaplay'):
            providers.append('vip')
        if flask.request.form.get('Disney Plus'):
            providers.append('dnp')
        if flask.request.form.get('Cmore'):
            providers.append('cmr')
        if flask.request.form.get('Paramount Plus'):
            providers.append('pmp')
        if flask.request.form.get('Blockbuster'):
            providers.append('bck')
        if flask.request.form.get('SF Anytime'):
            providers.append('sfa')
        if flask.request.form.get('HBO Max'):
            providers.append('hbm')
        if flask.request.form.get('SVT Play'):
            providers.append('svt')
        if flask.request.form.get('Apple TV Plus'):
            providers.append('atp')
        if flask.request.form.get('Discovery Plus'):
            providers.append('dpe')
        if len(providers) < 1:
            return flask.render_template('index.html', error='No providers selected')
        info, image = find(title, providers, country)
        return flask.render_template('index.html', title=title, info=info,
                                     image=image, site_key=site_key, providers=providers, country=country)


if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True)
