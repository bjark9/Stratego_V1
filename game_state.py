# Rank of the pieces -> Dict = {piece : rank}
rank = {
    "Marshall": 1,
    "General": 2,
    "Colonel": 3,
    "Major": 4,
    "Captain": 5,
    "Lieutenant": 6,
    "Sergeant": 7,
    "Miner": 8,
    "Scout": 9,
    "Spion": 10,
    "Bomb": 0,
    "Flag": "F",
}

# Number of pieces -> Dict = {piece : times}
pieces = {
    "Marshall": 1,
    "General": 1,
    "Colonel": 2,
    "Major": 3,
    "Captain": 4,
    "Lieutenant": 4,
    "Sergeant": 4,
    "Miner": 5,
    "Scout": 8,
    "Spion": 1,
    "Bomb": 6,
    "Flag": 1,
}

# Cases where there is water
water = {}


# Place of the pieces -> Dict = {piece : [(pos1,pos2),(pos1,pos2)]} ------> list of tuples
place_blue = {piece: [] for piece in pieces}

place_red = {piece: [] for piece in pieces}
