import flask
import requests
from keys import *
from net_prime import get_providers

app = flask.Flask(__name__)


@app.route('/<movieName>', methods=['GET'])
def find(movieName):
    with open("amount.txt", "r") as file:
        amount = int(file.readline())
    if amount < 1000 and movieName:
        url = "https://utelly-tv-shows-and-movies-availability-v1.p.rapidapi.com/lookup"
        querystring = {"term": movieName, "country": "se"}
        headers = {
            'x-rapidapi-host': "utelly-tv-shows-and-movies-availability-v1.p.rapidapi.com",
            'x-rapidapi-key': api_key
        }
        response = requests.request("GET", url, headers=headers, params=querystring)
        with open("amount.txt", "w") as file:
            file.write(str(amount + 1))
        movies = get_providers(response.json())
        if movies != '!':
            movies_string = ''
            for i in movies:
                movies_string += f"{i} can be seen at"
                for j in movies[i]:
                    movies_string += f" {j},"
                movies_string = movies_string[:-1]
                movies_string += '\n'
            return movies_string
        else:
            return "No results!"
    else:
        return "free quota exceeded"


@app.route('/', methods=['GET'])
def home():
    return "<h1>Yellow World!</h1>"


app.run(host="0.0.0.0")
