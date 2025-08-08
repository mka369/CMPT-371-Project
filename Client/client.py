## Run the GUI and handle user input
import pygame
from ui import Button, GameUI
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
    ## net = NetworkClient()
    ## net.on_message(lambda data: print("[UI] Got: ", data))
    clock = pygame.time.Clock()
    quitting = False
    running = False
    dragging = False
    player_id = None

    ui = GameUI(screen)
    ## game_state = net.get_game_state()
    game_state = None ######################################

    while not quitting:
        while not running:
            ui.render()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    quitting = True
                    break

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    if ui.start_button.is_clicked(mouse_pos):
                        running = True
                        ui.state = "loading"
                    
                    elif ui.quit_button.is_clicked(mouse_pos):
                        ui.state = "main"
    
        net = NetworkClient()
        winner_ids = [] ################################

        counter = 0
        while running:
            if counter >= 30:
                game_state = net.get_game_state()
                counter = 0
            counter += 1

            if game_state is not None:
                if game_state["type"] == "assign_id":
                    player_id = game_state["player_id"]

                elif game_state["type"] == "game_start":
                    ui.state = "game"
                    ui.clock_start = pygame.time.get_ticks() / 1000
                
                elif game_state["type"] == "game_end":
                    ui.state = "end"
                    winner_ids = game_state.get("winner_ids", [])
                    running = False
            
            ui.render(game_state, winner_ids)
            '''
            dragged_gem_id = None
            offset_x = 0
            offset_y = 0
            '''
            for event in pygame.event.get():
                if event.type == pygame.QUIT: ## User clicked the window's close button
                    running = False
                    net.send({
                        'player_id': player_id,
                        'action': {
                            'type': 'quit',
                            'gem_id': None,
                            'position': None
                        }
                    })
                    net.close()
            
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()

                    if ui.state == "game":
                        for gem in game_state['gems']:
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
                    ## TODO: Update the position change in real-time
                    mx, my = event.pos
                    moving_x = mx + offset_x
                    moving_y = my + offset_y
                    ##game_state['gems'][dragged_gem_id]['position'] = moving_x, moving_y
                    if player_id is not None and counter % 7 == 0:
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
            
            pygame.display.flip()
            clock.tick(60) ## Limit the loop to run 60 times per second

    net.close()
    pygame.quit()

if __name__ == "__main__":
    main()
