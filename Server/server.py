## Handle network requests
import socket
import threading
from game import Game
from shared.protocol import encode_message, decode_message
from shared.constants import SERVER_PORT, SERVER_ADDRESS

def handle_client(client_socket, game):
    ## Receive data from the client and update the game state.
    while True:
        try:
            message = client_socket.recv(1024)
            if not message:
                break
            data = decode_message(message)
            player_id = data.get('player_id')
            action = data.get('action')
            game.process_input(player_id, action)
        except Exception as e:
            print(f"[SERVER] Error handling client: {e}")
            break

def broadcast(game_state, clients):
    ## Send the current game state to all connected clients.
    encoded = encode_message(game_state)
    for client in clients:
        try:
            client.sendall(encoded)
        except:
            print("[SERVER] Error sending to client")

def wait_for_clients(game):
    ## Wait for clients to connect and start the game.
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((SERVER_ADDRESS, SERVER_PORT))
    server_socket.listen()
    print(f"[SERVER] Listening on port {SERVER_PORT}...")
    
    clients = []
    while len(clients) < 3:
        client_socket, addr = server_socket.accept()
        print(f"[SERVER] Client connected from {addr}")
        clients.append(client_socket)
        threading.Thread(target=handle_client, args=(client_socket, game), daemon=True).start()

    print("[SERVER] Minimum players reached. Starting game.")
    game.start(clients)

if __name__ == "__main__":  ## Main for testing
    game = Game()
    wait_for_clients(game)