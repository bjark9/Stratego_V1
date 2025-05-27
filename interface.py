import pygame
import sys
import os
from pygame import mixer, MOUSEBUTTONDOWN
from random import randint
from game_state import pieces, place_blue, place_red
from engine import (
    get_piece_at_position,
    move_piece,
    update_side,
    is_enemy,
    get_adjacent_cases,
    valid_move,
    winner_of_combat,
    send_to_history,
    random_move_piece_ia,
    load_game,
    save_game,
)

# TODO : create better buttons
pygame.init()  # Initialize all pygame modules

# Variables / constants
WIDTH = 1040
HEIGHT = 800
ROWS = 10
COLS = 10
SQUARE_SIZE = 80
font = pygame.font.SysFont("Comic Sans MS", 30)

# Colors
BEIGE = (245, 245, 220)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)
PINK = (255, 192, 203)

# Win text and image
win_image = pygame.image.load(os.path.join("Images", "Victory.png"))
my_font = pygame.font.SysFont("Comic Sans MS", 60)  # Call pygame system font
win_text = my_font.render("Victory!", 1, RED)

# Screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Stratego")

# Dictionary for the resized pawns -> Dict = {resized_piece : <surface>}
resized_blue_pieces = {}
resized_red_pieces = {}

# Load and resize images of the pieces
for color in ("blue", "red"):
    for piece in pieces:
        image = pygame.image.load(os.path.join("Images", f"{piece}.png"))
        image = pygame.transform.scale(image, (SQUARE_SIZE, SQUARE_SIZE))
        if color == "blue":
            blue_mask = pygame.Surface(image.get_size(), pygame.SRCALPHA)
            blue_mask.fill((0, 0, 255, 100))  # R,G,B,Alpha

            resized_blue_pieces[piece] = image
        else:
            red_mask = pygame.Surface(image.get_size(), pygame.SRCALPHA)
            red_mask.fill((255, 0, 0, 100))  # R,G,B,Alpha

            resized_red_pieces[piece] = image


# Draw grid (10x10)
def draw_grid():
    """
    Draws a 10x10 grid on the screen using alternating beige and white squares.
    """
    for row in range(ROWS):
        for col in range(COLS):
            # We draw a beige case
            if (row + col) % 2 == 0:
                pygame.draw.rect(
                    screen,
                    BEIGE,
                    (row * SQUARE_SIZE, col * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE),
                )
            # We draw a white case
            else:
                pygame.draw.rect(
                    screen,
                    WHITE,
                    (row * SQUARE_SIZE, col * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE),
                )


# Draw the water (lakes) in the middle
# Change static coordinates to variable linked one
def draw_water_in_grid():
    """
    Draws the lake tiles (water) in the center of the grid using a water image.
    """
    water_image = pygame.image.load(os.path.join("Images", "Lake.jpeg"))
    water_image = pygame.transform.scale(
        water_image, (SQUARE_SIZE * 2, SQUARE_SIZE * 2)
    )
    screen.blit(water_image, (160, 320))
    screen.blit(water_image, (480, 320))


# Place the pieces
def ini_place_blue_pawns():
    """
    Randomly places blue pawns on the lower part of the board (rows 6-9) and applies a blue mask.
    Updates the `place_blue` dictionary with the pawn positions.
    """
    used_positions = set()  # Create a list of tuples with the positions

    for res_piece in resized_blue_pieces:
        place_times = pieces[res_piece]  # Number of times we will place this piece
        for times in range(place_times):
            while True:
                i = randint(0, 9)
                j = randint(6, 9)
                if (i, j) not in used_positions:
                    used_positions.add((i, j))
                    break
            x = i * SQUARE_SIZE
            y = j * SQUARE_SIZE
            screen.blit(resized_blue_pieces[res_piece], (x, y))
            screen.blit(blue_mask, (x, y))
            place_blue[res_piece].append((x, y))


# Place the pieces the same way as you did with place_blue_pawns but apply a red mask on it
def ini_place_red_pawns():
    """
    Randomly places red pawns on the upper part of the board (rows 0-3) and applies a red mask.
    Updates the `place_red` dictionary with the pawn positions.
    """
    used_positions = set()

    for res_piece in resized_red_pieces:
        place_times = pieces[res_piece]
        for times in range(place_times):
            while True:
                i = randint(0, 9)
                j = randint(0, 3)
                if (i, j) not in used_positions:
                    used_positions.add((i, j))
                    break
            x = i * SQUARE_SIZE
            y = j * SQUARE_SIZE
            screen.blit(resized_red_pieces[res_piece], (x, y))
            screen.blit(red_mask, (x, y))
            place_red[res_piece].append((x, y))


# Show all pawns (used for debugging)
def show_all_pawns():
    """
    Displays all blue and red pawns on the screen with their corresponding masks.
    Primarily used for debugging purposes.
    """
    for piece_name, positions in place_blue.items():
        for x, y in positions:
            screen.blit(resized_blue_pieces[piece_name], (x, y))
            screen.blit(blue_mask, (x, y))
    for piece_name, positions in place_red.items():
        for x, y in positions:
            screen.blit(resized_red_pieces[piece_name], (x, y))
            screen.blit(red_mask, (x, y))


# Draw the pawns after movement and hide the enemy's one
def draw_all_pawns():
    """
    Draws all pawns currently on the board.
    Enemy pieces are hidden and shown as colored rectangles (red or blue).
    """
    for piece_name, positions in place_blue.items():
        for x, y in positions:
            if side == "blue":
                screen.blit(resized_blue_pieces[piece_name], (x, y))
                screen.blit(blue_mask, (x, y))
            else:
                pygame.draw.rect(screen, BLUE, (x, y, SQUARE_SIZE, SQUARE_SIZE))

    for piece_name, positions in place_red.items():
        for x, y in positions:
            if side == "red":
                screen.blit(resized_red_pieces[piece_name], (x, y))
                screen.blit(red_mask, (x, y))
            else:
                pygame.draw.rect(screen, RED, (x, y, SQUARE_SIZE, SQUARE_SIZE))


# Hide IA pawns and show player's pawns
def hide_red_pawns_and_show_blue_pawns():
    """
    Displays all blue pawns with a mask and hides red pawns as solid red squares.
    Used to simulate a fog-of-war effect for the player's perspective.
    """
    for piece_name, positions in place_blue.items():
        for x, y in positions:
            screen.blit(resized_blue_pieces[piece_name], (x, y))
            screen.blit(blue_mask, (x, y))
    for piece_name, positions in place_red.items():
        for x, y in positions:
            pygame.draw.rect(screen, RED, (x, y, SQUARE_SIZE, SQUARE_SIZE))


# Hide all the pieces
def draw_all_hidden():
    """
    Hides all pawns on the board by drawing solid color rectangles (blue for blue side, red for red side).
    """
    for piece_name, positions in place_blue.items():
        for x, y in positions:
            pygame.draw.rect(screen, BLUE, (x, y, SQUARE_SIZE, SQUARE_SIZE))
    for piece_name, positions in place_red.items():
        for x, y in positions:
            pygame.draw.rect(screen, RED, (x, y, SQUARE_SIZE, SQUARE_SIZE))


# Show the two pieces on combat
def show_enemy_on_combat(pos1, pos2, side):
    """
    Displays the attacker and defender pieces involved in a combat.

    :param pos1: Position (tuple) of the attacking piece
    :param pos2: Position (tuple) of the defending piece
    :param side: Side (str) of the attacking piece ("blue" or "red")
    :return: None
    """
    attacker_name, index = get_piece_at_position(pos1, side)
    if side == "blue":
        screen.blit(resized_blue_pieces[attacker_name], pos1)
        screen.blit(blue_mask, pos1)
        opponent_side = "red"
    else:
        screen.blit(resized_red_pieces[attacker_name], pos1)
        screen.blit(red_mask, pos1)
        opponent_side = "blue"

    defender_name, index = get_piece_at_position(pos2, opponent_side)
    if opponent_side == "blue":
        screen.blit(resized_blue_pieces[defender_name], pos2)
        screen.blit(blue_mask, pos2)
    else:
        screen.blit(resized_red_pieces[defender_name], pos2)
        screen.blit(red_mask, pos2)


# Draw save button in side panel
def draw_save_button():
    """
    Draws the 'Save Game' button on the sidebar.
    Updates the global `save_but` rect object used for click detection.
    """
    global save_but
    save_but = pygame.draw.rect(screen, PINK, (800, 0, 160, 160))
    save_text = font.render("Save game", True, WHITE)
    screen.blit(save_text, (save_but.x + 20, save_but.y + 20))


# Background sound
# mixer.music.load("C:/Users/niels/Music/Stratego/Doigby - GUERRIER (clip officiel).wav")
# mixer.music.play(-1)


# Place this outside the loop, otherwise the variables would reset every single frame
selected_piece = None
mouse_pos1 = None
mouse_pos2 = None
action = True
side = "red"
confirmation = False


# Choice between playing vs IA and playing vs player
but_ia = pygame.draw.rect(screen, RED, (240, 240, SQUARE_SIZE, SQUARE_SIZE))
but_player = pygame.draw.rect(screen, BLUE, (360, 240, SQUARE_SIZE, SQUARE_SIZE))
pygame.display.flip()
vs_ia_text = font.render("IA", True, WHITE)
vs_player_text = font.render("Player", True, WHITE)
screen.blit(vs_ia_text, (but_ia.x + 20, but_ia.y + 20))
screen.blit(vs_player_text, (but_player.x + 20, but_player.y + 20))
pygame.display.flip()

# Need to assign flags otherwise they would be None and while-loops will crash
flag_IA = False
flag_player = False
start = True
ft = True
while start:
    for event in pygame.event.get():
        if event.type == MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            if ft:
                if but_ia.collidepoint(mouse_pos):
                    print("Choisi pour l'IA")
                    flag_IA = True
                if but_player.collidepoint(mouse_pos):
                    print("Choisi de jouer contre un jouer")
                    flag_player = True
                start = False
        if event.type == pygame.QUIT:
            start = False
            sys.exit()

# Choice to load the game/ new game
screen.fill(BLACK)
pygame.display.flip()  # RESET THE SCREEN
new_game_button = pygame.draw.rect(screen, WHITE, (0, 0, 320, 720))
load_button = pygame.draw.rect(screen, WHITE, (400, 0, 320, 720))
pygame.display.flip()
new_game_text = font.render("New game", True, BLUE)
load_text = font.render("Load game", True, RED)
screen.blit(new_game_text, (new_game_button.x + 20, new_game_button.y + 20))
screen.blit(load_text, (load_button.x + 20, load_button.y + 20))
pygame.display.flip()

new_or_load = True
flag_load = False
flag_new = False
while new_or_load:
    for event in pygame.event.get():
        if event.type == MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            if load_button.collidepoint(mouse_pos):
                flag_load = True
                new_or_load = False
            if new_game_button.collidepoint(mouse_pos):
                flag_new = True
                new_or_load = False
        if event.type == pygame.QUIT:
            new_or_load = False
            sys.exit()

# If the player wants to start a new game, the pieces get placed randomly
if flag_new:
    ini_place_blue_pawns()  # Places the blue pieces randomly and draw them on the board
    ini_place_red_pawns()  # ^^


# If the player wants to load the previous game, the previous game state gets loaded
if flag_load:
    red_pieces, blue_pieces = load_game()
    print(f"Red pieces: {red_pieces}")
    print(f"Blue pieces: {blue_pieces}")
    for piece_name, positions in red_pieces.items():
        print(piece_name)
        print(positions)
        for pos in positions:
            place_red[piece_name].append(pos)
    for piece_name, positions in blue_pieces.items():
        for pos in positions:
            place_blue[piece_name].append(pos)


running = True
# Play against player
while running and flag_player:
    # This will run every frame
    draw_save_button()
    # hide enemy pieces
    if confirmation:
        draw_grid()
        draw_water_in_grid()
        draw_all_hidden()
        # Create button
        button_rect = pygame.Rect(0, 320, 800, 160)
        pygame.draw.rect(screen, (100, 100, 100), button_rect)
        font = pygame.font.SysFont("Arial", 30)
        text = font.render("Next Player", True, (255, 255, 255))
        screen.blit(text, (button_rect.x + 30, button_rect.y + 35))
        pygame.display.flip()
    else:
        side, action = update_side(action, side)
        draw_grid()
        draw_water_in_grid()
        draw_all_pawns()
        pygame.display.flip()
    for event in pygame.event.get():
        # On mousebutton1 click
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            if confirmation:
                if button_rect.collidepoint(mouse_pos):
                    confirmation = False
            elif save_but.collidepoint(mouse_pos):
                save_game()
            else:
                # First click
                if not selected_piece:
                    # Find the top-left coordinates of the case where you clicked
                    mouse_pos1 = (
                        int(mouse_pos[0] // SQUARE_SIZE) * int(SQUARE_SIZE),
                        int(mouse_pos[1] // SQUARE_SIZE) * int(SQUARE_SIZE),
                    )
                    is_enemy(side, mouse_pos1)

                    piece_name, index = get_piece_at_position(mouse_pos1, side)
                    print(piece_name, index)
                    if piece_name:
                        selected_piece = (piece_name, index)
                        list_adj = get_adjacent_cases(side, mouse_pos1)
                # Second click
                else:
                    # Find the top-left coordinates of the case where you clicked
                    mouse_pos2 = (
                        int(mouse_pos[0] // SQUARE_SIZE) * int(SQUARE_SIZE),
                        int(mouse_pos[1] // SQUARE_SIZE) * int(SQUARE_SIZE),
                    )

                    # Combat management
                    if valid_move(side, mouse_pos1, mouse_pos2, list_adj, piece_name):
                        moved = False
                        if is_enemy(side, mouse_pos2):
                            draw_grid()
                            draw_water_in_grid()
                            draw_all_hidden()
                            show_enemy_on_combat(mouse_pos1, mouse_pos2, side)
                            pygame.display.flip()
                            pygame.time.wait(2000)
                            winner, action = winner_of_combat(
                                mouse_pos1, mouse_pos2, side
                            )
                            if winner:
                                print(f"{side} wins!!")
                                win_text = my_font.render(f"{side} wins!", 1, RED)
                                # screen.blit(win_image,(320,320))
                                screen.blit(win_text, (360, 360))
                                pygame.display.flip()
                                pygame.time.wait(3000)
                                running = False
                            confirmation = True

                        else:
                            moved, action = move_piece(
                                selected_piece[0],
                                selected_piece[1],
                                mouse_pos1,
                                mouse_pos2,
                                list_adj,
                                side,
                            )
                        if moved:
                            confirmation = True
                    # Send to history
                    send_to_history(piece_name, mouse_pos1, mouse_pos2, side)
                    # Reset after move
                    selected_piece = None
                    mouse_pos1 = None
                    mouse_pos2 = None
        # On quit window event
        if event.type == pygame.QUIT:
            running = False

# Play against IA, IA always plays red
while running and flag_IA:
    draw_save_button()
    # Drawing of the board
    draw_grid()
    draw_water_in_grid()
    hide_red_pawns_and_show_blue_pawns()
    # show_all_pawns()
    pygame.display.flip()

    # run code for IA
    if side == "red":
        piece_name, start_pos, end_pos, index = random_move_piece_ia()
        adj_cases = get_adjacent_cases("red", start_pos)
        if is_enemy("red", end_pos):
            show_enemy_on_combat(start_pos, end_pos, "red")
            pygame.display.flip()
            pygame.time.wait(2000)
            winner_of_combat(start_pos, end_pos, "red")
        else:
            move_piece(piece_name, index, start_pos, end_pos, adj_cases, "red")

        # Change side after action of IA
        pygame.time.wait(50)
        # Change side after IA's action
        side = "blue"

    # run code for player
    for event in pygame.event.get():
        if event.type == MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            # first click
            if not selected_piece:
                mouse_pos1 = (
                    int(mouse_pos[0] // SQUARE_SIZE) * int(SQUARE_SIZE),
                    int(mouse_pos[1] // SQUARE_SIZE) * int(SQUARE_SIZE),
                )
                is_enemy(side, mouse_pos1)
                piece_name, index = get_piece_at_position(mouse_pos1, side)
                if piece_name:
                    selected_piece = (piece_name, index)
                    list_adj = get_adjacent_cases(side, mouse_pos1)
            # Second click
            else:
                # Find the top-left coordinates of the case where you clicked
                mouse_pos2 = (
                    int(mouse_pos[0] // SQUARE_SIZE) * int(SQUARE_SIZE),
                    int(mouse_pos[1] // SQUARE_SIZE) * int(SQUARE_SIZE),
                )
                print(mouse_pos2)
                # Combat management
                if valid_move(side, mouse_pos1, mouse_pos2, list_adj, piece_name):
                    if is_enemy(side, mouse_pos2):
                        draw_grid()
                        draw_water_in_grid()
                        draw_all_hidden()
                        show_enemy_on_combat(mouse_pos1, mouse_pos2, side)
                        pygame.display.flip()
                        pygame.time.wait(2000)
                        winner, action = winner_of_combat(mouse_pos1, mouse_pos2, side)
                        if winner:
                            print(f"{side} wins!!")
                            win_text = my_font.render(f"{side} wins!", 1, RED)
                            # screen.blit(win_image,(320,320))
                            screen.blit(win_text, (360, 360))
                            pygame.display.flip()
                            pygame.time.wait(3000)
                            running = False

                    else:
                        moved, action = move_piece(
                            selected_piece[0],
                            selected_piece[1],
                            mouse_pos1,
                            mouse_pos2,
                            list_adj,
                            side,
                        )
                    if action:
                        side = "red"
                # Send to history
                send_to_history(piece_name, mouse_pos1, mouse_pos2, side)
                # Reset after move
                selected_piece = None
                mouse_pos1 = None
                mouse_pos2 = None
        if event.type == pygame.QUIT:
            running = False


pygame.quit()
