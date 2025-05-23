import pygame
import os
from pygame import mixer
from random import randint
from game_state import pieces, place_blue, place_red
from engine import (
    get_piece_at_position,
    move_piece,
    update_side,
    can_move,
    is_enemy,
    get_adjacent_cases,
    valid_move,
    winner_of_combat,
    send_to_history,
)

pygame.init()  # Initialize all pygame modules

# Variables / constants
WIDTH = 800  # TODO : change the size of the images in function of the width
HEIGHT = 800
ROWS = 10
COLS = 10
SQUARE_SIZE = WIDTH / COLS

# Colors
BEIGE = (245, 245, 220)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

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
        image = pygame.transform.scale(image, (80, 80))
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
    for row in range(ROWS):
        for col in range(COLS):
            if (row + col) % 2 == 0:
                pygame.draw.rect(
                    screen,
                    BEIGE,
                    (row * SQUARE_SIZE, col * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE),
                )
            else:
                pygame.draw.rect(
                    screen,
                    WHITE,
                    (row * SQUARE_SIZE, col * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE),
                )


# Draw the water (lakes) in the middle
def draw_water_in_grid():
    water_image = pygame.image.load(os.path.join("Images", "Lake.jpeg"))
    water_image = pygame.transform.scale(water_image, (160, 160))
    screen.blit(water_image, (160, 320))
    screen.blit(water_image, (480, 320))


# Place the pieces
def ini_place_blue_pawns():
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


# Draw the pawns after movement and hide the enemy's one
def draw_all_pawns():
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


# Background sound
# mixer.music.load("C:/Users/niels/Music/Stratego/Doigby - GUERRIER (clip officiel).wav")
# mixer.music.play(-1)


# Prepare the board
# This needs to be outside the while running loop else because you just need to place it once, and not every frame
draw_grid()
draw_water_in_grid()
ini_place_blue_pawns()
ini_place_red_pawns()
pygame.display.flip()

# Place this outside the loop, otherwise every single frame the variables would reset to None
selected_piece = None
mouse_pos1 = None
mouse_pos2 = None

running = True
while running:
    side = update_side()
    draw_grid()
    draw_water_in_grid()
    draw_all_pawns()
    pygame.display.flip()
    for event in pygame.event.get():
        # On mousebutton1 click
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()

            # First click
            if not selected_piece:
                # Snap mouse_pos1 to the grid, to find the top-left coordinates of the case where you clicked
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
                # Snap mouse_pos2 to the grid
                mouse_pos2 = (
                    int(mouse_pos[0] // SQUARE_SIZE) * int(SQUARE_SIZE),
                    int(mouse_pos[1] // SQUARE_SIZE) * int(SQUARE_SIZE),
                )

                # Combat management
                if can_move(piece_name):
                    if valid_move(side, mouse_pos1, mouse_pos2, list_adj, piece_name):
                        if is_enemy(side, mouse_pos2):
                            winner = winner_of_combat(mouse_pos1, mouse_pos2, side)
                            if winner:
                                print(f"{side} wins!!")
                                win_text = my_font.render(f"{side} wins!", 1, RED)
                                # screen.blit(win_image,(320,320))
                                screen.blit(win_text, (360, 360))
                                pygame.display.flip()
                                pygame.time.wait(3000)
                                running = False
                        else:
                            move_piece(
                                selected_piece[0],
                                selected_piece[1],
                                mouse_pos1,
                                mouse_pos2,
                                list_adj,
                            )
                # Send to history
                send_to_history(piece_name, mouse_pos1, mouse_pos2, side)
                # Reset after move
                selected_piece = None
                mouse_pos1 = None
                mouse_pos2 = None
        # On quit window event
        if event.type == pygame.QUIT:
            running = False

pygame.quit()
