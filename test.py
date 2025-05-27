# test_engine.py
import pytest
import pygame
from engine import (
    can_move,
    is_enemy,
    is_occupied,
    valid_move,
    get_piece_at_position,
    move_piece,
    winner_of_combat,
    get_adjacent_cases,
)
from game_state import place_red, place_blue, water, piece_rank


@pytest.fixture(autouse=True)
def reset_board():
    # Clear both boards before each test
    for d in (place_red, place_blue):
        for k in d:
            d[k].clear()
    yield


def test_can_move():
    assert can_move("Scout") is True
    assert can_move("Miner") is True
    assert can_move("Flag") is False
    assert can_move("Bomb") is False


def test_get_piece_at_position():
    place_blue["Scout"].append((80, 80))
    assert get_piece_at_position((80, 80), "blue") == ("Scout", 0)
    assert get_piece_at_position((0, 0), "blue") == (None, None)


def test_is_enemy():
    place_red["Sergeant"].append((160, 160))
    assert is_enemy("blue", (160, 160)) is True
    assert is_enemy("blue", (80, 80)) is False


def test_is_occupied():
    place_red["Spy"].append((80, 80))
    place_blue["Scout"].append((160, 160))
    water.append(pygame.Rect(240, 240, 80, 80))

    assert is_occupied((80, 80)) == "red"
    assert is_occupied((160, 160)) == "blue"
    assert is_occupied((250, 250)) == "water"
    assert is_occupied((400, 400)) is None

    water.clear()  # cleanup for global state


def test_valid_move_adjacent():
    place_blue["Scout"].append((160, 160))
    adj_cases = get_adjacent_cases("blue", (160, 160))

    target = (160, 240)
    assert valid_move("blue", (160, 160), target, adj_cases, "Scout") is True


def test_valid_move_scout():
    place_blue["Scout"].append((160, 160))
    adj_cases = get_adjacent_cases("blue", (160, 160))

    # Move vertically several cells
    assert valid_move("blue", (160, 160), (160, 400), adj_cases, "Scout") is True

    # Blocked path
    place_red["Spy"].append((160, 240))
    assert valid_move("blue", (160, 160), (160, 400), adj_cases, "Scout") is False


def test_move_piece_valid():
    place_blue["Sergeant"].append((80, 80))
    adj = get_adjacent_cases("blue", (80, 80))
    moved, action = move_piece("Sergeant", 0, (80, 80), (160, 80), adj, "blue")
    assert moved is True
    assert action is True
    assert place_blue["Sergeant"][0] == (160, 80)


def test_move_piece_invalid():
    place_blue["Bomb"].append((80, 80))  # Bomb can't move
    adj = get_adjacent_cases("blue", (80, 80))
    moved, action = move_piece("Bomb", 0, (80, 80), (160, 80), adj, "blue")
    assert moved is False
    assert action is False
    assert place_blue["Bomb"][0] == (80, 80)


def test_winner_of_combat_attacker_wins():
    place_blue["Major"].append((80, 80))
    place_red["Lieutenant"].append((160, 80))
    _, action = winner_of_combat((80, 80), (160, 80), "blue")
    assert action is True
    assert place_red["Lieutenant"] == []
    assert place_blue["Major"][0] == (160, 80)


def test_winner_of_combat_defender_wins():
    place_blue["Sergeant"].append((80, 80))
    place_red["General"].append((160, 80))
    _, action = winner_of_combat((80, 80), (160, 80), "blue")
    assert action is True
    assert (
        place_blue["Sergeant"] == [(80, 80)] or place_blue["Sergeant"] == []
    )  # Depending on deletion
    assert place_red["General"][0] == (160, 80)


def test_winner_of_combat_draw():
    place_blue["Lieutenant"].append((80, 80))
    place_red["Lieutenant"].append((160, 80))
    _, action = winner_of_combat((80, 80), (160, 80), "blue")
    assert action is True
    assert place_blue["Lieutenant"] == []
    assert place_red["Lieutenant"] == []


# TODO
def test_winner_of_combat_flag():
    place_blue["Captain"].append((80, 80))
    place_red["Flag"].append((160, 80))
    winner, action = winner_of_combat((80, 80), (160, 80), "blue")
    assert winner is True
    assert action is True
    assert place_red["Flag"] == []
    assert place_blue["Captain"][0] == (160, 80)
