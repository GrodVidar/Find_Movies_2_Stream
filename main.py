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
                    movie = products[i]['_links']['self']['title']
                    movies[movie] = {}
                    if 'tvod' in products[i]['system']['availability']:
                        movies[movie]['rent_price'] = products[i]['system']['availability']['tvod']['planInfo']['price']
                    if 'est' in products[i]['system']['availability']:
                        movies[movie]['purchase_price'] = products[i]['system']['availability']['est']['planInfo']['price']
                    if 'svod' in products[i]['system']['availability']:
                        movies[movie]['is_streamable'] = True
                return movies
    return None


def find(title, params):
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
        movies_list = []
        if movies != '!':
            for i in movies:
                movies_string = ''
                movies_string += f"{i} can be seen at"
                for j in movies[i]:
                    if j in params[title]:
                        movies_string += f" {j},"
                movies_string = movies_string[:-1]
                movies_list.append(movies_string)
        else:
            return "No results!"
        if 'Viaplay' in params[title]:
            via_movies = viaplay_finder(title)
            if via_movies:
                for i in via_movies:
                    och = False
                    movies_string = f"{i} can be "
                    if 'is_streamable' in via_movies[i]:
                        if och:
                            movies_string += '& '
                        movies_string += "streamed "
                        och = True
                    if 'rent_price' in via_movies[i]:
                        if och:
                            movies_string += '& '
                        movies_string += f"rented for {via_movies[i]['rent_price']} SEK "
                        och = True
                    if 'purchase_price' in via_movies[i]:
                        if och:
                            movies_string += '& '
                        movies_string += f"purchased for {via_movies[i]['purchase_price']} SEK "
                    movies_string += "at Viaplay"
                    movies_list.append(movies_string)
        print(movies_list)
        return movies_list
    else:
        return "free quota exceeded or name too short"


@app.route('/', methods=['GET', 'POST'])
def home():
    title = flask.request.form.get('title')
    print(flask.request.form)
    if not title:
        return flask.render_template('index.html')
    else:
        my_dict = {title: []}
        if flask.request.form.get('Netflix'):
            my_dict[title].append('Netflix')
        if flask.request.form.get('Amazon'):
            my_dict[title].append('Amazon Prime Video')
        if flask.request.form.get('Google Play'):
            my_dict[title].append('Google Play')
        if flask.request.form.get('iTunes'):
            my_dict[title].append('iTunes')
        if flask.request.form.get('Viaplay'):
            my_dict[title].append('Viaplay')
        return flask.render_template('index.html', title=title, info=find(title, my_dict))


if __name__ == '__main__':
    # print(viaplay_finder("shrek"))
    app.run(host="0.0.0.0", debug=True)
