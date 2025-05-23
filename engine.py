from typing import Tuple
import pygame
from game_state import place_blue, place_red, water, piece_rank


# Update side
action = False
side = "blue"


def update_side():
    global action, side
    if action:
        if side == "blue":
            side = "red"
        else:
            side = "blue"
    action = False
    return side


def get_piece_at_position(pos, side) -> str and int:
    """
    Return (piece_name, index) if a piece is found at position 'pos'
    :param pos: Position of the mouse-click
    :type pos: Tuple
    :return: piece_name, index
    :rtype: str, int
    """
    if side == "blue":
        place = place_blue
    else:
        place = place_red
    for piece_name, values in place.items():
        for index, (x, y) in enumerate(values):
            piece_rect = pygame.Rect(x, y, 80, 80)
            if piece_rect.collidepoint(pos):
                return piece_name, index
    return None, None


# Update position after move
# In this function we change the flag action to True so that update_side gets called
def move_piece(piece_name, index, start_position, new_pos, adj_cases):
    global action
    # We break the movement of the piece if can_move returns False
    if not can_move(piece_name):
        return False
    if not valid_move(side, start_position, new_pos, adj_cases, piece_name):
        return False

    x, y = new_pos
    if side == "blue":
        place_blue[piece_name][index] = (x, y)
    if side == "red":
        place_red[piece_name][index] = (x, y)

    # print(f"{piece_name} à bougé")
    action = True
    return True


# Can the piece move (Bombs and Flags can't move)
def can_move(piece_name: str) -> bool:
    if piece_name == "Flag" or piece_name == "Bomb":
        return False
    return True


# Checks if the case where the pawn moves is an enemy
def is_enemy(side, pos) -> bool:
    if side == "blue":
        place = place_red
    else:
        place = place_blue
    for values in place.values():
        for index, (x, y) in enumerate(values):
            piece_rect = pygame.Rect(x, y, 80, 80)
            if piece_rect.collidepoint(pos):
                # print("Ceci est un ennemi")
                return True
    # print("Ceci n'est pas un ennemi")
    return False


# Get positions of cases nsew of the current case
# Returns list of surfaces
def get_adjacent_cases(side: str, pos: tuple) -> list:
    # global adjacent_cases
    adjacent_cases = []

    # Get the name and index of the piece where you clicked
    name, index = get_piece_at_position(pos, side)

    if side == "blue":
        place = place_blue
    else:
        place = place_red

    # Create the rectangles adjacent to the selected piece, ??create a surface or a set of coördinates??
    for piece_name, values in place.items():
        if piece_name == name:
            for idx, (x, y) in enumerate(values):
                if index == idx:
                    rect_n = pygame.Rect(x - 80, y, 80, 80)
                    rect_e = pygame.Rect(x, y + 80, 80, 80)
                    rect_s = pygame.Rect(x + 80, y, 80, 80)
                    rect_w = pygame.Rect(x, y - 80, 80, 80)
                    adjacent_cases.append(rect_n)
                    adjacent_cases.append(rect_e)
                    adjacent_cases.append(rect_s)
                    adjacent_cases.append(rect_w)
                    return adjacent_cases


# Checks if the move is valid
def valid_move(
    side: str, start_position: Tuple, end_position: Tuple, adj_cases: list, piece_name
):
    occupant = is_occupied(end_position)

    # Block water
    if occupant == "water":
        # print("Cannot move into water")
        return False

    # Block friendly fire
    if occupant == side:
        # print("Cannot move onto own piece")
        return False

    if piece_name == "Scout":
        return scout_movement(side, start_position, end_position)
    else:
        # Check if end_position is in the adjacent cases:
        for surface in adj_cases:
            if surface.collidepoint(end_position):
                # print("Valid move")
                return True
    # print("Non-valid move")
    return False


# Can move multiple cases, but can't jump over occupied cases
def scout_movement(side: str, start_pos: tuple, end_pos: tuple):
    list_possible_rect = []
    x1, y1 = start_pos

    for i in range(1, 9):  # start at 1 to exclude the current square
        step = i * 80
        list_possible_rect.append(pygame.Rect(x1 + step, y1, 80, 80))  # right
        list_possible_rect.append(pygame.Rect(x1 - step, y1, 80, 80))  # left
        list_possible_rect.append(pygame.Rect(x1, y1 + step, 80, 80))  # down
        list_possible_rect.append(pygame.Rect(x1, y1 - step, 80, 80))  # up

    x2, y2 = end_pos

    if not any(rectangle.collidepoint(x2, y2) for rectangle in list_possible_rect):
        # print("Can't move diagonally")
        return False

    dx = (x2 - x1) // 80
    dy = (y2 - y1) // 80

    steps = max(abs(dx), abs(dy))
    if steps == 0:
        return False  # No movement

    if dx == 0:
        step_x = 0
    else:
        step_x = dx // abs(dx)
    if dy == 0:
        step_y = 0
    else:
        step_y = dy // abs(dy)

    for i in range(1, steps):
        xi = x1 + i * step_x * 80
        yi = y1 + i * step_y * 80
        if is_occupied((xi, yi)):
            # print("Not the first piece in its track")
            return False

    target = is_occupied(end_pos)
    if target == "water" or target == side:
        # print("Can't land on water or own piece")
        return False

    # print("Valid move for scout")
    return True


# Checks if the case is occupied, and checks if it's an enemy/ally/water/empty
def is_occupied(pos):
    # Water
    for wat in water:
        if wat.collidepoint(pos):
            return "water"
    # Red pieces
    for values in place_red.values():
        for x, y in values:
            if pygame.Rect(x, y, 80, 80).collidepoint(pos):
                return "red"
    # Blue pieces
    for values in place_blue.values():
        for x, y in values:
            if pygame.Rect(x, y, 80, 80).collidepoint(pos):
                return "blue"
    return None  # Empty


def winner_of_combat(pos1, pos2, side):
    global action
    attacker_name, attacker_index = get_piece_at_position(pos1, side)
    # Change side after getting the attacker
    if side == "blue":
        opponent_side = "red"
    else:
        opponent_side = "blue"
    defender_name, defender_index = get_piece_at_position(pos2, opponent_side)
    attacker_rank = piece_rank.get(attacker_name)
    defender_rank = piece_rank.get(defender_name)

    if attacker_rank is None or defender_rank is None:
        print("Combat error: unknown piece rank.")
        return

    # Win the game
    if defender_name == "Flag":
        return True

    # Miner -> bomb interaction
    if attacker_name == "Miner" and defender_name == "Bomb":
        print("Miner defeats the bomb")
        if opponent_side == "red":
            del place_red[defender_name][defender_index]
        else:
            del place_blue[defender_name][defender_index]

        # Move attacker to defender's position
        if side == "blue":
            place_blue[attacker_name][attacker_index] = pos2
        else:
            place_red[attacker_name][attacker_index] = pos2

    # Spy -> Marshall
    elif attacker_name == "Spy" and defender_name == "Marshall":
        print("Spy attacks and defeats the Marshall")
        if opponent_side == "red":
            del place_red[defender_name][defender_index]
        else:
            del place_blue[defender_name][defender_index]

        # Move attacker to defender's position
        if side == "blue":
            place_blue[attacker_name][attacker_index] = pos2
        else:
            place_red[attacker_name][attacker_index] = pos2

    # Attacker wins
    elif attacker_rank < defender_rank:
        print("Attacker wins!")
        # Remove defender
        if opponent_side == "red":
            del place_red[defender_name][defender_index]
        else:
            del place_blue[defender_name][defender_index]

        # Move attacker to defender's position
        if side == "blue":
            place_blue[attacker_name][attacker_index] = pos2
        else:
            place_red[attacker_name][attacker_index] = pos2

    # Defender wins
    elif attacker_rank > defender_rank:
        print("Defender wins")
        # Remove attacker
        if side == "blue":
            del place_blue[attacker_name][attacker_index]
        else:
            del place_red[attacker_name][attacker_index]

        # Defender stays in place

    # Draw: both die
    else:
        print("Draw. Both pieces die.")
        if side == "blue":
            del place_blue[attacker_name][attacker_index]
            del place_red[defender_name][defender_index]
        else:
            del place_red[attacker_name][attacker_index]
            del place_blue[defender_name][defender_index]
    action = True


# After a move, send the move to the game_history.txt file
def send_to_history(piece_name, start_position, end_position, side):
    with open("game_history.txt", "a") as file:
        side = side.capitalize()
        file.write(
            f"{side} {piece_name} moved from {start_position} to {end_position}  \n"
        )


# TODO
def show_enemy_on_combat(): ...
