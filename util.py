import glob
import random

from manim_rubikscube import *
from manim import *

from manim_rubikscube import cube_utils


class RubikScene(ThreeDScene):
    def __init__(self, *args, **kwargs):
        super(RubikScene, self).__init__(*args, **kwargs)
        self.camera.set_focal_distance(20000.0)
        self.camera.should_apply_shading = False
        self.bfs_counter = 0
        self.cube_sounds = []

    def play_bfs_sound(self, time_offset=0, animation_run_time=None):
        if animation_run_time is not None:
            assert (
                time_offset == 0
            ), "Nelze nastavit jak time_offset tak animation_length"
            time_offset = max(
                0, min(animation_run_time - 0.2, animation_run_time * 0.5)
            )

        self.add_sound(f"audio/bfs/bfs_{self.bfs_counter:03d}", time_offset=time_offset)
        self.bfs_counter += 1
    
    def play_cube_sound(self, time_offset=0, animation_run_time=None):
        if animation_run_time is not None:
            assert (
                time_offset == 0
            ), "Nelze nastavit jak time_offset tak animation_length"
            time_offset = max(
                0, min(animation_run_time - 0.2, animation_run_time * 0.5)
            )

        if not self.cube_sounds:
            self.cube_sounds = glob.glob("audio/cube/r*.wav")
            random.shuffle(self.cube_sounds)

        self.add_sound(self.cube_sounds.pop(), time_offset=time_offset)


def bfs(adj, start):
    res_vertices = [[start]]
    res_edges = [[]]
    seen = set([start])

    while True:
        cur_vertices = []
        cur_edges = []

        for v1 in res_vertices[-1]:
            for v2 in adj[v1]:
                cur_edges.append((v1, v2))

                if v2 not in seen:
                    cur_vertices.append(v2)
                    seen.add(v2)

        if cur_vertices:
            res_vertices.append(cur_vertices)
            res_edges.append(cur_edges)
        else:
            res_edges.append(cur_edges)
            break

    return res_vertices, res_edges


# https://ruwix.com/blog/feliks-zemdegs-rubiks-world-record-2016-4-73/
# TODO check (with our program?) this is indeed the best solution
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


def invert_move(move):
    face, n_turns = parse_move(move)
    # Note these are already inverted
    endings = {
        1: "'",
        2: "2",
        3: "",
    }
    return face + endings[(n_turns + 4) % 4]


FELIKS_UNSCRAMBLE_MOVES = [invert_move(move) for move in FELIKS_SCRAMBLE_MOVES[::-1]]


def scramble_to_feliks(cube: RubiksCube):
    for move in FELIKS_SCRAMBLE_MOVES:
        cube.do_move(move)


FELIKS_ACTUAL_SOLUTION_MOVES_RAW = [
    "U'",
    "R",
    "F",
    "R'",
    "U'",
    "D",
    "L'",
    "U2",
    "L2",
    "U'",
    "L'",
    "U",
    "R'",
    "U",
    "R",
    "R'",
    "U",
    "R",
    "U",
    "R'",
    "U'",
    "R",
    "F",
    "R",
    "U'",
    "R'",
    "U'",
    "R",
    "U",
    "R'",
    "F'",
    "R",
    "U'",
    "R",
    "U",
    "R",
    "U",
    "R",
    "U'",
    "R'",
    "U'",
    "R2",
    "U",
]


def apply_feliks_turn(move):
    # Apply the INVERSE of x' y'. These are rotations of the whole cube,
    # so they essentially transform the moves performed
    replacements = {
        "U": "B",
        "D": "F",
        "L": "D",
        "R": "U",
        "F": "L",
        "B": "R",
    }
    return replacements[move[0]] + move[1:]


FELIKS_ACTUAL_SOLUTION_MOVES = [
    apply_feliks_turn(move) for move in FELIKS_ACTUAL_SOLUTION_MOVES_RAW
]

POSSIBLE_MOVES = [
    "U",
    "U'",
    "U2",
    "D",
    "D'",
    "D2",
    "L",
    "L'",
    "L2",
    "R",
    "R'",
    "R2",
    "F",
    "F'",
    "F2",
    "B",
    "B'",
    "B2",
]
POSSIBLE_MOVES = [
    "U",
    "D",
    "L",
    "R",
    "F",
    "B",
    "U2",
    "D2",
    "L2",
    "R2",
    "F2",
    "B2",
    "U'",
    "D'",
    "L'",
    "R'",
    "F'",
    "B'",
]

#https://colorswall.com/palette/171
cube.DEFAULT_CUBE_COLORS = ["#ffffff", "#b71234", "#009b48", "#ffd500", "#ff5800", "#0046ad"]
# cube.DEFAULT_CUBE_COLORS = [BASE3, RED, GREEN, YELLOW, ORANGE, BLUE]


def gen_house(color = RED, height = 1, z_index = 100):
    pnts = [
        np.array([232.535, 333.808, 0.0]),
        np.array([277.698, 333.811, 0.0]),
        np.array([277.387, 373.503, 0.0]),
        np.array([318.11, 373.566, 0.0]),
        np.array([318.057, 333.881, 0.0]),
        np.array([363.215, 333.935, 0.0]),
        np.array([362.703, 419.758, 0.0]),
        np.array([368.717, 425.367, 0.0]),
        np.array([379.969, 415.454, 0.0]),
        np.array([390.258, 426.885, 0.0]),
        np.array([297.362, 509.816, 0.0]),
        np.array([256.582, 472.796, 0.0]),
        np.array([256.626, 497.065, 0.0]),
        np.array([232.588, 497.017, 0.0]),
        np.array([232.899, 451.371, 0.0]),
        np.array([204.978, 426.922, 0.0]),
        np.array([215.11, 415.777, 0.0]),
        np.array([225.569, 425.578, 0.0]),
        np.array([232.235, 419.834, 0.0]),
        np.array([232.549, 333.833, 0.0]),
    ]

    house = Polygon(
        *pnts,
        color = color,
        fill_color = color,
		fill_opacity = 1,
        z_index = z_index
    ).move_to(
        0*DOWN
    ).scale_to_fit_height(
        height
    )

    return house   


def gen_icon(color = BLUE, height = 1, z_index = 100):
    pnts = [
        np.array([407.837, 313.233, 0.0]),
        np.array([340.843, 431.234, 0.0]),
        np.array([297.995, 558.503, 0.0]),
        np.array([253.986, 431.689, 0.0]),
        np.array([187.414, 311.624, 0.0]),
    ]

    icon = ArcPolygon(
        *pnts,
        color = color,
        arc_config = [
            { 'radius': 119.256, 'color': color},
            { 'radius': 70.9444, 'color': color},
            { 'radius': 70.9444, 'color': color},
            { 'radius': 119.256, 'color': color},
            { 'radius': 216.488, 'color': color},

        ],
        fill_color = color,
		fill_opacity = 1,
        z_index = z_index
    ).move_to(
        0*DOWN
    ).scale_to_fit_height(
        height
    )

    return icon





