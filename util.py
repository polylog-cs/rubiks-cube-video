from manim_rubikscube import *

# https://ruwix.com/blog/feliks-zemdegs-rubiks-world-record-2016-4-73/
FELIKS_SCRAMBLE_MOVES = [
    "U2",
    "F",
    "L2",
    "U2",
    "R2",
    "F",
    "L2",
    "F2",
    "L'",
    "D'",
    "B2",
    "R",
    "D2",
    "R'",
    "B'",
    "U'",
    "L'",
    "B'",
]

def scramble_to_feliks(cube: RubiksCube):
    for move in FELIKS_SCRAMBLE_MOVES:
        cube.do_move(move)
