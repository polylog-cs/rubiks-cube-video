import itertools
from numpy.linalg import norm
import random
import math
from manim import *

# Use our fork of manim_rubikscube!
from manim_rubikscube import *

# This also replaces the default colors
from solarized import *

import util


cube.DEFAULT_CUBE_COLORS = [BASE3, RED, GREEN, YELLOW, ORANGE, BLUE]

# https://colorswall.com/palette/171
cube.DEFAULT_CUBE_COLORS = [
    "#ffffff",
    "#b71234",
    "#009b48",
    "#ffd500",
    "#ff5800",
    "#0046ad",
]

"""
what you see is just a tiny part of the neighborhood
of the solved cube. Remember, every cube has 18
neighbors in the full graph!
"""


class UnzoomCubeGraph(util.RubikScene):
    def construct(self):
        self.next_section(skip_animations=False)

        solved_cube = RubiksCube(cubie_size=0.18)

        n_nodes, edges, anims_to_do, g = get_graph()

        g.fade(1)
        self.add(g)  # Necessary for zooming to work properly (for some reason)

        g2 = g.copy()
        g2.set_color(GREEN)

        self.add(solved_cube)
        cubes = {0: solved_cube}
        cubes_on_scene = [solved_cube]

        scale = 5
        g.scale(scale, about_point=ORIGIN)
        solved_cube.scale(scale, about_point=ORIGIN)

        # musi odpovidat poctu cyklu v `while anims_to_do`
        anim_steps = 12

        def scale_updater(mobject, dt):
            mobject.scale((1 / scale) ** (dt / anim_steps), about_point=ORIGIN)

        # Do one second of scaling in advance
        g.scale((1 / scale) ** (1 / anim_steps))

        g.add_updater(scale_updater)
        solved_cube.add_updater(scale_updater)

        def move_updater_factory(start, end):
            return lambda l: l.put_start_and_end_on(
                start.get_center() + IN, end.get_center() + IN
            )

        while anims_to_do:
            print(len(anims_to_do), "animations left")
            anims = [c.animate.shift(ORIGIN) for c in cubes_on_scene]
            active = set()
            to_create = {}
            leftover = []
            for (c1, c2, move) in anims_to_do:
                if c1 in cubes and not c1 in active:
                    cnew = cubes[c1].copy()

                    to_create[c2] = cnew

                    line = Line(
                        g[c1].get_center() + IN,
                        g[c2].get_center() + IN,
                        shade_in_3d=True,
                        color=GRAY,
                    )

                    line.add_updater(move_updater_factory(cubes[c1], cnew))

                    anims += [
                        CubeMove(cnew, move=move, target_position=g[c2].get_center()),
                        Create(line),
                    ]
                    cubes_on_scene.append(cnew)
                    active.add(c1)
                else:
                    leftover.append((c1, c2, move))

            self.play(*anims, run_time=1)
            anims_to_do = leftover
            cubes.update(to_create)

        for cube in cubes_on_scene:
            cube.clear_updaters()

        self.wait(2)
        return


class HighlightCubeGraph(util.RubikScene):
    def construct(self):
        self.next_section(skip_animations=False)

        solved_cube = RubiksCube(cubie_size=0.18)
        n_nodes, edges, anims_to_do, g = get_graph()
        g.fade(0)
        for v in g.vertices.values():
            v.fade(1)

        self.add(g)

        cubes = {0: solved_cube}
        cubes_on_scene = [solved_cube]

        while anims_to_do:
            leftover = []
            for (c1, c2, move) in anims_to_do:
                if c1 in cubes:
                    cnew = cubes[c1].copy()
                    cnew.do_move(move).move_to(g[c2].get_center())

                    cubes_on_scene.append(cnew)
                    cubes[c2] = cnew
                else:
                    leftover.append((c1, c2, move))

            anims_to_do = leftover

        self.add(*cubes_on_scene)

        # change to houses

        self.next_section(skip_animations=False)

        houses = [
            ImageMobject("img/house.png").move_to(c.get_center())
            for c in cubes_on_scene
        ]

        icons = [
            ImageMobject("img/icon.png").move_to(c.get_center()) for c in cubes_on_scene
        ]

        infty = 10000.0
        for c, house, icon in zip(cubes_on_scene, houses, icons):
            house.width = icon.width = c.width
            house.scale(1.0 / infty)
            icon.scale(1.0 / infty)

        # cubes disappear
        self.play(*[cube.animate.scale(1 / infty) for cube in cubes_on_scene])
        self.wait()

        # houses appear and disappear
        self.add(*houses)
        self.play(*[house.animate().scale(infty) for house in houses])
        self.wait()
        self.play(*[house.animate().scale(0) for house in houses])
        self.remove(*houses)

        # icons appear and disappear

        self.add(*icons)
        self.play(*[icon.animate().scale(infty) for icon in icons])
        self.wait()
        self.play(*[icon.animate().scale(0) for icon in icons])
        self.remove(*icons)

        # cubes appear
        self.play(*[cube.animate.scale(infty) for cube in cubes_on_scene])
        self.wait()

class BFSCubeGraph(util.RubikScene):
    def construct(self):
        self.next_section(skip_animations=False)

        solved_cube = RubiksCube(cubie_size=0.18)
        n_nodes, edges, anims_to_do, g = get_graph()
        g.fade(0)
        self.add(g)




def get_graph():
    n_nodes = 1
    edges = []
    anims_to_do = []

    def new_cube(cube, move, _shift, _outside=False):
        nonlocal n_nodes
        n_nodes += 1

        edges.append((cube, n_nodes - 1))
        anims_to_do.append((cube, n_nodes - 1, move))

        return n_nodes - 1

    def add_edge(c1, c2, move):
        edges.append((c1, c2))
        anims_to_do.append((c1, c2, move))

    # easy 4cyklus
    solved = 0
    r1 = new_cube(solved, "L", LEFT + DOWN)
    r2 = new_cube(solved, "R", DOWN + RIGHT)
    r3 = new_cube(r1, "R", RIGHT + DOWN)
    add_edge(r2, r3, "L")

    # r1 bude základem 6cyklu
    # nejdriv levo prave steny
    s1 = new_cube(solved, "L'", LEFT + UP)
    s2 = new_cube(s1, "R2", LEFT)
    # pak hordolni
    s3 = new_cube(s2, "U2", LEFT)
    s4 = new_cube(s3, "D2", LEFT)
    # a ted z druhe strany, nejdriv hordolni
    s5 = new_cube(r1, "U2", LEFT)
    s6 = new_cube(s5, "D2", LEFT)
    s7 = new_cube(s6, "L2", LEFT)
    add_edge(s7, s4, "R2")
    if True:
        # + kratky cyklus
        t0 = new_cube(r2, "R", UP + RIGHT)
        t1 = new_cube(t0, "L'", UP + LEFT)
        add_edge(t1, s1, "R2")
        add_edge(solved, t0, "R2")

        # ted chci udelat neco vedle typka ze ktereho budeme hledat
        # tim je s7
        scrambled = s7
        u1 = new_cube(scrambled, "L", DOWN)
        add_edge(u1, s6, "L")

        # dalsi cyklus co vede z r1 do s6
        v1 = new_cube(r1, "F2", DOWN)
        v2 = new_cube(v1, "B2", DOWN)
        v3 = new_cube(v2, "D2", LEFT)
        v4 = new_cube(v3, "U2", LEFT)
        v5 = new_cube(v4, "B2", UP)
        add_edge(v5, s6, "F2")

        # nejdelsi cyklus z r2
        w1 = new_cube(r2, "F'", RIGHT)
        w2 = new_cube(w1, "B2", RIGHT)
        w3 = new_cube(w2, "F'", RIGHT)
        w4 = new_cube(w3, "U2", RIGHT)
        w5 = new_cube(w4, "D2", DOWN)

        w6 = new_cube(r2, "U'", DOWN)
        w7 = new_cube(w6, "D2", RIGHT)
        w8 = new_cube(w7, "U'", RIGHT)
        w9 = new_cube(w8, "F2", RIGHT)
        add_edge(w9, w5, "B2")

        # nakonec par nahodnych hran
        n1 = new_cube(t0, "F", RIGHT, True)
        n2 = new_cube(n1, "L'", RIGHT, True)
        n3 = new_cube(n1, "U", UP, True)
        n4 = new_cube(n2, "U'", UP, True)

        n5 = new_cube(s1, "D", UP, True)
        n6 = new_cube(s2, "F'", UP, True)
        n7 = new_cube(s3, "R", UP, True)

        n8 = new_cube(n6, "L'", UP + LEFT, True)
        n9 = new_cube(n6, "R2", UP + RIGHT, True)

        n10 = new_cube(s7, "F", LEFT + UP, True)
        n11 = new_cube(s7, "L'", LEFT, True)
        n12 = new_cube(n11, "R'", LEFT + DOWN, True)
        n13 = new_cube(n11, "L'", DOWN, True)
        add_edge(n13, u1, "L'")
        n14 = new_cube(n10, "R", UP, True)

        n15 = new_cube(t1, "F'", UP, True)
        n16 = new_cube(t1, "U", UP + RIGHT, True)

        n17 = new_cube(w6, "F", DOWN, True)
        n18 = new_cube(n17, "L", RIGHT, True)
        n19 = new_cube(n17, "U'", LEFT, True)

    g = Graph(
        list(range(n_nodes)),
        edges,
        edge_config={
            "color": GRAY,
            "shade_in_3d": True,  # Needed to keep the edges behind the cube
        },
        vertex_config={
            "color": GRAY,
            "shade_in_3d": True,  # Needed to keep the edges behind the cube
        },
        layout="kamada_kawai",
    )
    g.rotate(angle=-25 * DEGREES)
    g.scale_to_fit_height(7.5)
    g.shift(-g.vertices[0].get_center())

    return n_nodes, edges, anims_to_do, g
