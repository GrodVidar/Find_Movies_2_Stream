import flask
import requests
from keys import *
from mail import send_mail
from justwatch import JustWatch
app = flask.Flask(__name__)

# Netflix, Amazon prime, iTunes and Google Play API-caller
# using the Utelly's API: "https://rapidapi.com/utelly/api/utelly"
# And Viaplay's open API


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
    movies = []
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
        for movie in movie_data:
            movie_string = f"{movie['title']} can be"
            original_string = movie_string
            for monetization_type in movie['monetization_types']:
                if len(movie['monetization_types'][monetization_type]) > 0:
                    provider_names = []
                    for provider in movie['monetization_types'][monetization_type]:
                        provider_names.append(provider['provider_name'])
                    available_providers = ', '.join(provider_names)
                    if monetization_type == 'free':
                        if original_string != movie_string:
                            movie_string += ' and'
                        movie_string += f" watched for free at {available_providers}"
                    if monetization_type == 'flatrate':
                        if original_string != movie_string:
                            movie_string += ' and'
                        movie_string += f" streamed with a subscription at {available_providers}"
                    if monetization_type == 'rent':
                        if original_string != movie_string:
                            movie_string += ' and'
                        movie_string += f" rented at {available_providers}"
                    if monetization_type == 'buy':
                        if original_string != movie_string:
                            movie_string += ' and'
                        movie_string += f" purchased at {available_providers}"
            movies.append(movie_string)
    elif len(title) < 2:
        return ["title too short"], image
    print(movie_data)
    return movie_data, image


@app.route('/', methods=['GET', 'POST'])
def home():
    title = flask.request.form.get('title')
    message = flask.request.form.get('message')
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
        info, image = find(title, providers, country)
        return flask.render_template('index.html', title=title, info=info,
                                     image=image, site_key=site_key, providers=providers)


if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True)
