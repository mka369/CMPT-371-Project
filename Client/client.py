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

    MOVE_SEND_INTERVAL = 1.0 / 45.0
    last_move_send_ts = 0.0

    dragged_gem_id = None
    offset_x = 0
    offset_y = 0

    ui = GameUI(screen)
    game_state = None

    last_players = []
    winner_ids = []

    while not quitting:
        while not running:
            ui.render(game_state, player_id)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    quitting = True
                    break

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()

                    if ui.state == "main":
                        if ui.start_button.is_clicked(mouse_pos):
                            running = True
                            ui.state = "loading"
                            winner_ids = []
                            if hasattr(ui, "winner_ids"):
                                ui.winner_ids = []
                        elif ui.quit_button.is_clicked(mouse_pos):
                            ui.state = "main"

                    elif ui.state == "end":
                        if ui.quit_button.is_clicked(mouse_pos):
                            ui.state = "main"
                            winner_ids = []
                            if hasattr(ui, "winner_ids"):
                                ui.winner_ids = []
                            game_state = None

        if quitting:
            break

        net = NetworkClient()

        sent_quit = False
        while running:
            msg = net.get_game_state()
            latest = None
            while msg is not None:
                latest = msg
                msg = net.get_game_state()

            if latest is not None:
                game_state = latest
                if game_state.get("type") == "state_update":
                    last_players = game_state.get("players", [])

            if game_state is not None:
                t = game_state.get("type")

                if t == "assign_id":
                    player_id = game_state["player_id"]

                elif t == "game_start":
                    ui.state = "game"
                    ui.clock_start = pygame.time.get_ticks() / 1000

                elif t == "game_end":
                    if last_players:
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

            for event in pygame.event.get():
                if event.type == pygame.QUIT: ## User clicked the window's close button
                    running = False
                    quitting = True
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
                            if gem_clicked(mouse_pos, gem):
                                dragging = True
                                dragged_gem_id = gem['id']
                                mx, my = mouse_pos
                                gx, gy = gem['position']
                                offset_x = gx - mx
                                offset_y = gy - my
                                break
                        if dragged_gem_id is not None:
                            if player_id is not None:
                                net.send({
                                    'player_id': player_id,
                                    'action': {
                                        'type': 'drag',
                                        'gem_id': dragged_gem_id
                                    }
                                })

                    '''
                    elif result == "restart_game":
                        ## TODO: Go back to establishing connection.
                        pass
                    '''
                
                elif event.type == pygame.MOUSEMOTION and dragging:
                    mx, my = event.pos
                    moving_x = mx + offset_x
                    moving_y = my + offset_y
                    ##game_state['gems'][dragged_gem_id]['position'] = moving_x, moving_y
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
                    if dragging:
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