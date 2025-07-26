## Handle game logic (mutex synchronization)
from shared.objects import Gem, Player
from shared.protocol import encode_message
import threading
import time

class Game:
    def __init__(self):
        ## Initialize the game with players and gems.
        self.players = [
            Player(id=1, name="Player1"),
            Player(id=2, name="Player2"),
            Player(id=3, name="Player3")
        ]
        self.gems = [
            Gem(id=0, position=(100, 100)),
            Gem(id=1, position=(200, 150)),
            Gem(id=2, position=(300, 200))
        ]
        self.game_over = False
        self.game_lock = threading.Lock()

    def start(self, clients):
        ## Start the game loop.
        print("[GAME] Game started.")
        start_time = time.time()
        duration = 30

        while not self.game_over:
            time.sleep(0.5) ## Broadcast every 0.5s
            state = self.get_state()
            encoded = encode_message(state)
            for client in clients:
                try:
                    client.sendall(encoded)
                except:
                    print("[GAME] Failed to send state to a client")
            
            if time.time() - start_time >= duration:
                self.game_over = True
                print("[GAME] Time's up. Game over.")
    
    def process_input(self, player_id, action):
        ## Process player input and update game state.
        with self.game_lock:
            if action["type"] == "drag":
                for gem in self.gems:
                    if gem.id == action["gem_id"] and not gem.is_collected:
                        gem.is_collected = True
                        gem.owner_id = player_id
                        for player in self.players:
                            if player.id == player_id:
                                player.score += 1
                                break
    
    def get_state(self):
        ## Get the current game state.
        with self.game_lock:
            return {
                'players': [player.to_dict() for player in self.players],
                'gems': [gem.to_dict() for gem in self.gems],
                'game_over': self.game_over
            }
game_lock = threading.Lock()
