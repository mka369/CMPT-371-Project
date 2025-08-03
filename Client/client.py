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
    running = True
    dragging = False

    ui = GameUI(screen)
    ## game_state = net.get_game_state()
    game_state = None ######################################

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: ## User clicked the window's close button
                running = False
                net.close()
                ## TODO: If connected to server, tell the server I'm quitting.
    
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                result = ui.button_click(mouse_pos)

                if result == "start_game":
                    net = NetworkClient() ######################################
                    net.on_message(lambda data: print("[UI] Got: ", data))
                    game_state = net.get_game_state()

                    if game_state["type"] == "game_start":
                        ui.draw_game_screen()
                    else:
                        ## TODO: Show the loading window until the game starts.
                        pass
                
                elif result == "play_game":
                    ui.draw_game_screen(game_state)

                    for gem in game_state['gems']:
                        if gem_clicked(mouse_pos, gem):
                            dragging = True
                            dragged_gem_id = gem['id']
                            mx, my = mouse_pos
                            gx, gy = gem['position']
                            offset_x = gx + mx
                            offset_y = gy + my
                            break
                
                elif result == "restart_game":
                    ## TODO: Go back to establishing connection.
                
                elif result == "quit_to_main":
                    ui.draw_main_screen()
            
            elif event.type == pygame.MOUSEMOTION and dragging:
                ## TODO: Update the position change in real-time
                mx, my = event.pos
                moving_x = mx + offset_x
                moving_y = my + offset_y
                game_state['gems'][dragged_gem_id]['position'] = moving_x, moving_y
                    
            elif event.type == pygame.MOUSEBUTTONUP:
                if dragging:
                    dragging = False
                    drop_pos = pygame.mouse.get_pos()
                    net.send({
                        'player_id': 1, ## TODO: Read the ID properly
                        'action': { 'type': "drag", 'gem_id': dragged_gem_id, 'final_pos': drop_pos }
                    }) ## TODO: Send the action type, dragged gem's ID, and its final position.
                    dragged_gem = None
                
        game_state = net.get_game_state()
        pygame.display.flip()
        clock.tick(60) ## Limit the loop to run 60 times per second

    net.close()
    pygame.quit()

if __name__ == "__main__":
    main()
