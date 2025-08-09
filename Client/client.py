## Run the GUI and handle user input
import pygame
import time
from ui import GameUI
from network import NetworkClient
from shared.constants import GEM_RADIUS

def gem_clicked(mouse_pos, gem):
    gx, gy = gem['position']
    mx, my = mouse_pos
    radius = GEM_RADIUS
    return (mx - gx) ** 2 + (my - gy) ** 2 <= radius ** 2    

def main():
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    clock = pygame.time.Clock()
    quitting = False
    running = False
    dragging = False
    player_id = None

    ## Variable to control how often the client sends move updates.
    MOVE_SEND_INTERVAL = 1.0 / 45.0
    last_move_send_ts = 0.0

    ## Variables for dragging gems.
    dragged_gem_id = None
    offset_x = 0
    offset_y = 0

    ui = GameUI(screen)
    game_state = None

    last_players = []
    winner_ids = []

    while not quitting: ## Player has not closed the window.
        while not running: ## Game is not running.
            ui.render(game_state, player_id)
            for event in pygame.event.get():
                if event.type == pygame.QUIT: ## User clicked the window's close button.
                    quitting = True
                    break

                elif event.type == pygame.MOUSEBUTTONDOWN: ## User clicked on the screen.
                    mouse_pos = pygame.mouse.get_pos()

                    if ui.state == "main": ## User is on the main screen.
                        if ui.start_button.is_clicked(mouse_pos):
                            running = True
                            ui.state = "loading"
                            winner_ids = []
                            if hasattr(ui, "winner_ids"):
                                ui.winner_ids = []
                        elif ui.quit_button.is_clicked(mouse_pos):
                            ui.state = "main"
                    '''
                    elif ui.state == "end":
                        if ui.quit_button.is_clicked(mouse_pos):
                            ui.state = "main"
                            winner_ids = []
                            if hasattr(ui, "winner_ids"):
                                ui.winner_ids = []
                            game_state = None
                    '''

        if quitting:
            break

        net = NetworkClient() ## Initialize the network client.

        sent_quit = False ## Flag to track if quit message has been sent.
        while running:
            ## Get messages from the server.
            msg = net.get_game_state()
            latest = None
            while msg is not None: ## Queue the latest message from server.
                latest = msg
                msg = net.get_game_state()

            if latest is not None:
                game_state = latest
                if game_state.get("type") == "state_update": ## Game state update message.
                    last_players = game_state.get("players", [])

            if game_state is not None:
                t = game_state.get("type")

                if t == "assign_id": ## Player ID assignment message.
                    player_id = game_state["player_id"]

                elif t == "game_start": ## Game start message.
                    ui.state = "game"
                    ui.clock_start = pygame.time.get_ticks() / 1000

                elif t == "game_end": ## Game end message.
                    if last_players:
                        ## Determine the winners based on scores.
                        best = max(p.get("score", 0) for p in last_players)
                        winner_ids = [p["id"] for p in last_players if p.get("score", 0) == best]
                    else:
                        winner_ids = []

                    try:
                        ui.winner_ids = winner_ids
                    except Exception:
                        pass

                    try:
                        game_state["winner_ids"] = winner_ids
                    except Exception:
                        pass

                    ui.state = "end"
                    running = False

                ui.render(game_state, player_id)

            ## Handle user input.
            for event in pygame.event.get():
                if event.type == pygame.QUIT: ## User clicked the window's close button.
                    running = False
                    quitting = True
                    ## Send quit message if player ID is known.
                    if not sent_quit and player_id is not None:
                        sent_quit = True
                        net.send({
                            'player_id': player_id,
                            'action': {
                                'type': 'quit',
                                'gem_id': None,
                                'position': None
                            }
                        })
            
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()

                    if ui.state == "game" and game_state is not None:
                        dragged_gem_id = None
                        for gem in game_state.get('gems', []):
                            if gem_clicked(mouse_pos, gem): ## Check if a gem is clicked.
                                dragging = True
                                dragged_gem_id = gem['id']
                                mx, my = mouse_pos
                                gx, gy = gem['position']
                                offset_x = gx - mx
                                offset_y = gy - my
                                break
                        if dragged_gem_id is not None:
                            if player_id is not None: ## Send server a drag message.
                                net.send({
                                    'player_id': player_id,
                                    'action': {
                                        'type': 'drag',
                                        'gem_id': dragged_gem_id
                                    }
                                })
                
                elif event.type == pygame.MOUSEMOTION and dragging:
                    mx, my = event.pos
                    moving_x = mx + offset_x
                    moving_y = my + offset_y
                    ## Make sure move updates are sent at a controlled rate.
                    if player_id is not None and (time.time() - last_move_send_ts) >= MOVE_SEND_INTERVAL:
                        last_move_send_ts = time.time()
                        net.send({
                            'player_id': player_id,
                            'action': {
                                'type': 'move',
                                'gem_id': dragged_gem_id,
                                'position': (moving_x, moving_y)
                            }
                        })
                            
                elif event.type == pygame.MOUSEBUTTONUP:
                    if dragging: ## If a gem is dropped, send a drop message.
                        dragging = False
                        drop_pos = pygame.mouse.get_pos()
                        if player_id is not None:
                            net.send({
                                'player_id': player_id,
                                'action': {
                                    'type': 'drop',
                                    'gem_id': dragged_gem_id,
                                    'drop_pos': drop_pos
                                }
                            })
                        dragged_gem_id = None
            
            pygame.display.flip()
            clock.tick(60) ## Limit the loop to run 60 times per second

        net.close()
    pygame.quit()

if __name__ == "__main__":
    main()