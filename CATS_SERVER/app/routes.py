from app import app
from app import sql_select, sql_insert, sql_delete, sql_update
from flask import request
from flask import jsonify


@app.route('/', methods=['GET'])
@app.route('/index', methods=['GET'])
def index():
    #requête pour récupérer les joueurs
    request_sql = f'''SELECT players_id, players_pseudo 
    FROM players'''

    #on exécute la requete
    data = sql_select(request_sql)

    #on print le résultat de la requête
    print(data)

    #on parcourt le résultat
    for player in data:
        #on récupère l'id du joueur
        player_id = player["players_id"]

        #requête pour récupérer les chats d'un joueur
        request_sql = f'''SELECT * FROM cats 
        JOIN rooms ON rooms.rooms_id = cats.rooms_id 
        WHERE rooms.players_id = {player_id}'''

        cats = sql_select(request_sql)
        print(f'''CHATS DU JOUEUR {player_id} : \n''')
        print(len(cats))

        #on ajoute le nombre de chats (le nombre d'objets dans la liste renvoyée par le serveur) au player actuel
        player["cats_count"] = len(cats)

    #on renvoie le résultat jsonifié
    return jsonify(data), 200





@app.route('/login', methods=['POST'])
def login():
    #On recupere le json envoyé par le client

    formulaire_login = (request.get_json())

    #On recupere l'email et le password

    email = formulaire_login["email"]
    password = formulaire_login["password"]

    resquest_sql = f'''SELECT *
    FROM `players`
    WHERE players_email = "{email}" 
    '''

    players_login = sql_select(resquest_sql)

    if len(players_login) !=1:
        return "Mauvais email", 404


    resquest_sql = f'''SELECT * 
    FROM `players`
    WHERE players_email = "{email}" 
    AND players_password = "{password}"'''

    players_login = sql_select(resquest_sql)

    print(players_login)

    dictionnary = {"id": players_login[0]["players_id"]}

    if len(players_login) != 1:
        return "Mauvais MDP", 404
    else:
        return jsonify(dictionnary)


@app.route('/signup', methods=['POST'])
def sign_up():

        # on récupère le json envoyé par le client
        formulaire_inscription = (request.get_json())

        # on récupère l'email
        email = formulaire_inscription["email"]

        # on check si l'email existe, si oui on envoie une erreur
        sql_request = f'''SELECT * FROM players WHERE players_email = "{email}"'''

        players_avec_cette_email = sql_select(sql_request)

        if len(players_avec_cette_email) > 0:
            return "Email déjà existant", 503
        # on ajoute le joueur
        sql_request = f'''INSERT INTO players(players_pseudo, players_email, players_password)
        VALUES("{formulaire_inscription["pseudo"]}", 
        "{formulaire_inscription["email"]}", 
        "{formulaire_inscription["password"]}")'''



        players_id = sql_insert(sql_request)

        add_room(players_id, 0, 0, formulaire_inscription["seed"])

        return "OK", 200




@app.route('/users/<int:players_id>/rooms', methods=['GET', 'POST'])
def rooms_handling(players_id):
    if request.method == 'GET':
        return get_rooms_request(players_id)
    elif request.method == 'POST':
        return add_room_request(players_id, request.get_json())


def get_rooms_request(players_id):

    request_sql = f'''SELECT * FROM rooms WHERE rooms.players_id ={players_id}'''
    rooms_spawn = sql_select(request_sql)

    for room in rooms_spawn:

        room_id = room["rooms_id"]
        request_sql = f'''SELECT * FROM cats 
        WHERE cats.rooms_id = {room_id}'''
        room["cats"] = sql_select(request_sql)

    return jsonify(rooms_spawn)




def add_room_request(players_id, request_json):
    print(request_json)
    return add_room(players_id, request_json["position_x"], request_json["position_y"], request_json["seed"])


def add_room(players_id, pos_x, pos_y, seed):

    request_sql = f'''SELECT * FROM rooms WHERE rooms.players_id = {players_id} AND rooms.rooms_position_x = {pos_x} AND rooms.rooms_position_y = {pos_y}'''

    checkroom = sql_select(request_sql)

    if len(checkroom) > 0:
        return "Il y a deja une salle à cet endroit", 404
    else:
        request_sql = f'''INSERT INTO rooms(players_id, rooms_position_x, rooms_position_y, rooms_seed) 
        VALUES ('{players_id}', '{pos_x}', '{pos_y}', '{seed}')'''
        room_build = sql_insert(request_sql)
        return jsonify({"id": room_build})









@app.route('/users/<int:players_id>/rooms/<int:rooms_id>', methods=['DELETE'])
def delete_room(players_id, rooms_id):
    request_sql = f'''SELECT * FROM cats WHERE cats.rooms_id = {rooms_id}'''
    checkcat = sql_select(request_sql)

    if len(checkcat) > 0:
        return "Il y a un chat dans la salle ! ASSASSIN", 404
    else:
        request_sql = f'''DELETE FROM rooms WHERE rooms_id = {rooms_id} and rooms.players_id = {players_id} '''
        sql_delete(request_sql)
        return "la salle a été supprime", 200



@app.route('/cats', methods=['GET'])
def get_free_cats():

    request_sql = f'''SELECT * FROM cats WHERE rooms_id IS NULL'''
    freecat = sql_select(request_sql)
    return jsonify(freecat)


@app.route('/cats/<int:cats_id>', methods=['PATCH', 'DELETE'])
def update_cat(cats_id):
    return "Not implemented", 501

