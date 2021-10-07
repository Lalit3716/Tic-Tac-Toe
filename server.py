import socket
import threading
import pickle
import random


def create_room(client):
    global rooms
   
    if (room_id := client["room_id"]) not in rooms.keys():
        rooms[room_id] = [client]
        client["client"].send(pickle.dumps(
            {"name": client["name"], "room_id": room_id, "event": "room_created"}))
   
    else:
        client["client"].send(pickle.dumps({"event": "error", "message": "Room Already Exists Try Creating Again!"}))


def join_room(client):
    global rooms
    if (room_id := client["room_id"]) in rooms.keys():
        if len(rooms[room_id]) == 2:  # Make Sure Only Two People In One Room
            client["client"].send(pickle.dumps({"event": "error", "message": "Room Full"}))
            client["client"].close()

        else:
            # Let Both Player Know That Someone Has Joined
            rooms[room_id].append(client)
            players = rooms[room_id]
            boolean = random.choice([True, False])  # For Deciding Who Go First

            # P1
            data = pickle.dumps(
                {
                    "event": "p2_joined",
                    "p1": players[0]["name"],
                    "p2": players[1]["name"],
                    "room_id": room_id,
                    "player_turn": boolean})
            players[0]["client"].send(data)
            
            # P2
            data = pickle.dumps(
                {
                    "p1": players[1]["name"],
                    "p2": players[0]["name"],
                    "room_id": room_id,
                    "event": "p2_joined",
                    "player_turn": not boolean})
            players[1]["client"].send(data)

    else:
        client["client"].send(pickle.dumps({"event": "error", "message": "Room does not Exist"}))


def send_data(obj, room, from_client):
    players = rooms[room]
    to_client = list(filter(lambda x: x != from_client, players))[0]
    to_client["client"].send(pickle.dumps(obj))


def handle_client(client):
    global rooms
    while True:
        try:
            response = client["client"].recv(5000)
            if response:
                response = pickle.loads(response)
                if response == "Select Button Clicked":
                    rooms[client["room_id"]].remove(client)
                    num_clients = len(rooms[client["room_id"]])
                    
                    if num_clients == 1:
                        rooms[client["room_id"]][0]["client"].send(pickle.dumps({"event": "Opponent Left"}))
            
                    elif num_clients == 0:
                        rooms.pop(client["room_id"])

                    client["client"].close()
                    break

                elif response == "Restart Button Clicked":
                    boolean = random.choice([True, False])
                    for client in rooms[client["room_id"]]:
                        client["client"].send(pickle.dumps({"event": "restart", "player_turn": boolean}))
                        boolean = not boolean

                else:
                    response = {
                        "event": "player_move",
                        "ix": response["ix"],
                        "iy": response["iy"]}
                    send_data(response, room=client["room_id"], from_client=client)

        except:
            client["client"].close()
            break


server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
IP = ""
PORT = 5556

server.bind((IP, PORT))
server.listen()

print("Server Running")

rooms = {}

while True:
    client, addr = server.accept()

    client_obj = pickle.loads(client.recv(5000))

    client_obj["client"] = client

    if client_obj["req"] == "create":
        create_room(client_obj)

    elif client_obj["req"] == "join":
        join_room(client_obj)

    if not client._closed:
        thread = threading.Thread(target=handle_client, args=(client_obj, ))
        thread.start()