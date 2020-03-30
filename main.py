import flask
import requests
from keys import *

app = flask.Flask(__name__)

# Netflix, Amazon prime, iTunes and Google Play API-caller
# using the Utelly API: "https://rapidapi.com/utelly/api/utelly"


def get_providers(resp):
    names = {}
    if resp and 'results' in resp:
        for j in range(len(resp['results'])):
            name = resp['results'][j]['name']
            if 'locations' in resp['results'][j]:
                names[name] = []
                for i in range(len(resp['results'][j]['locations'])):
                    if 'display_name' in resp['results'][j]['locations'][i]:
                        names[name].append(resp['results'][j]['locations'][i]['display_name'])
            else:
                return "!"
        return names
    else:
        return "!"


def viaplay_finder(name):
    resp = requests.get("https://content.viaplay.se/pcdash-se/search?query="+name)
    if resp:
        json_resp = resp.json()
        if '_embedded' in json_resp:
            if json_resp['_embedded']['viaplay:blocks'][0]['_embedded']['viaplay:products']:
                products = json_resp['_embedded']['viaplay:blocks'][0]['_embedded']['viaplay:products']
                movies = {}
                for i in range(len(products)):
                    movies[i] = {}
                    movies[i]['name'] = products[i]['_links']['self']['title']
                    if 'tvod' in products[i]['system']['availability']:
                        movies[i]['rent_price'] = products[i]['system']['availability']['tvod']['planInfo']['price']
                    if 'est' in products[i]['system']['availability']:
                        movies[i]['purchase_price'] = products[i]['system']['availability']['est']['planInfo']['price']
                    if 'svod' in products[i]['system']['availability']:
                        movies[i]['is_streamable'] = True
                return movies


def find(title):
    with open("amount.txt", "r") as file:
        amount = int(file.readline())
    if amount < 1000 and title and len(title) > 1:
        url = "https://utelly-tv-shows-and-movies-availability-v1.p.rapidapi.com/lookup"
        querystring = {"term": title, "country": "se"}
        headers = {
            'x-rapidapi-host': "utelly-tv-shows-and-movies-availability-v1.p.rapidapi.com",
            'x-rapidapi-key': api_key
        }
        response = requests.request("GET", url, headers=headers, params=querystring)
        with open("amount.txt", "w") as file:
            file.write(str(amount + 1))
        movies = get_providers(response.json())
        if movies != '!':
            movies_list = []
            for i in movies:
                movies_string = ''
                movies_string += f"{i} can be seen at"
                for j in movies[i]:
                    movies_string += f" {j},"
                movies_string = movies_string[:-1]
                movies_list.append(movies_string)
            print(movies_list)
            return movies_list
        else:
            return "No results!"
    else:
        return "free quota exceeded or name too short"


@app.route('/', methods=['GET', 'POST'])
def home():
    title = flask.request.form.get('title')
    print(flask.request.form.get('title'))
    if not title:
        return flask.render_template('index.html')
    else:
        return flask.render_template('index.html', title=title, info=find(title))


if __name__ == '__main__':
    # print(viaplay_finder("shrek"))
    app.run(host="0.0.0.0", debug=True)
