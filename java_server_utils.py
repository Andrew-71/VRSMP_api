import json
from mcstatus import JavaServer
from requests import request

from json_utils import read_from_json, write_to_json

import time

vrsmp = JavaServer.lookup("villagerrights.xyz:7110")


# Get Minecraft user's UUID from their username
# use Mojang api to get UUID
# https://api.mojang.com/users/profiles/minecraft/<username>
def get_uuid(username):
    url = "https://api.mojang.com/users/profiles/minecraft/" + username
    response = request("GET", url)
    return response.json()['id']


# Update our status of current online players
def update_java_status(data):
    try:
        query_response = vrsmp.query()
        player_names = query_response.players.names
    except TimeoutError:
        return {"online": False, "players": []}

    new_data = {"online": True, 'players': []}
    old_players = list(map(lambda x: x['username'], data['players']))
    for i in player_names:
        if i in old_players:
            for j in range(len(data['players'])):
                if data['players'][j]['username'] == i:
                    new_data['players'].append(data['players'][j])
                    break
        else:
            new_data['players'].append({'username': i, 'join_time': time.time()})
    new_data['query'] = query_response

    update_stats(new_data['players'])

    return new_data


# Update stats of players in the Java server
def update_stats(players):
    data = read_from_json("data/stats.json")
    for i in players:
        
        # We need to check for Bedrock players who have a dot as first character in their username
        # For them we will use their username as id since they don't have a UUID
        if i[0] == ".":
            uuid = i
        else:
            uuid = get_uuid(i['username'])

        if uuid in data:
            data[uuid]['playtime'] += 10  # Add 10 seconds to their playtime since we check the server every 10 seconds
        else:
            data[uuid] = {'playtime': 10, "first_seen": time.time()}
        data[uuid]['last_seen'] = time.time()
    write_to_json(data, "data/stats.json")