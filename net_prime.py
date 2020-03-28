import requests
import socket
import threading
# must have a separate file called keys.py with a working api-key in the same directory
from keys import *

# Netflix, Amazon prime, iTunes and Google Play API-caller
# using the Utelly API: "https://rapidapi.com/utelly/api/utelly"


def get_providers(resp):
    names = {}
    if resp['results'] and 'results' in resp:
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


def search_movie(client):
    while True:
        try:
            client.send(bytes("Enter Movie to search for", "UTF-8"))
            movie = client.recv(1024).decode("UTF-8")
            with open("amount.txt", "r") as file:
                amount = int(file.readline())
            if amount < 1000 and movie:
                url = "https://utelly-tv-shows-and-movies-availability-v1.p.rapidapi.com/lookup"
                querystring = {"term": movie, "country": "se"}
                headers = {
                    'x-rapidapi-host': "utelly-tv-shows-and-movies-availability-v1.p.rapidapi.com",
                    'x-rapidapi-key': api_key
                    }
                response = requests.request("GET", url, headers=headers, params=querystring)
                with open("amount.txt", "w") as file:
                    file.write(str(amount+1))
                movies = get_providers(response.json())
                if movies != '!':
                    movies_string = ''
                    for i in movies:
                        movies_string += f"{i} can be seen at"
                        for j in movies[i]:
                            movies_string += f" {j},"
                        movies_string = movies_string[:-1]
                        movies_string += '\n'
                    client.send(bytes(movies_string, "UTF-8"))
                else:
                    client.send(bytes("No results!", "UTF-8"))
            else:
                client.send(bytes("free quota exceeded", "UTF-8"))
        except (ConnectionAbortedError, ConnectionResetError):
            client.close()
            return


def accept(sock):
    while True:
        client, client_address = sock.accept()
        print(client_address)
        threading.Thread(target=search_movie, args=(client,)).start()


if __name__ == '__main__':
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(("", 1337))
    sock.listen(5)
    threading.Thread(target=accept, args=(sock,)).start()
