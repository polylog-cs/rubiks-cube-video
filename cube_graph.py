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

        solved_cube = RubiksCube(cubie_size=0.15).set_stroke_width(0.5)

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


# houses and icons
class HighlightCubeGraph(util.RubikScene):
    def construct(self):
        self.next_section(skip_animations=False)

        solved_cube = RubiksCube(cubie_size=0.15).set_stroke_width(0.5)
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
            gen_house().move_to(c.get_center())
            for c in cubes_on_scene
        ]

        icons = [
            gen_icon().move_to(c.get_center()) for c in cubes_on_scene
        ]
        

        infty = 10000.0
        for c, house, icon in zip(cubes_on_scene, houses, icons):
            house.width = icon.width = c.width * 0.7
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

        solved_cube = RubiksCube(cubie_size=0.15).set_stroke_width(0.5).shift(OUT)
        n_nodes, _edges, anims_to_do, g = get_graph()
        g.shift(IN)
        g.fade(0)
        self.add(g)

        cubes = {0: solved_cube}
        cubes_on_scene = [solved_cube]

        while anims_to_do:
            leftover = []
            for (c1, c2, move) in anims_to_do:
                if c1 in cubes:
                    cnew = cubes[c1].copy()
                    cnew.do_move(move).move_to(g[c2].get_center() + OUT)

                    cubes_on_scene.append(cnew)
                    cubes[c2] = cnew
                else:
                    leftover.append((c1, c2, move))

            anims_to_do = leftover

        self.add(*cubes_on_scene)

        solved_i = 0
        scrambled_i = 10
        radius = 0.6
        radius2 = 0.45

        solved_circle = Dot(
            g[solved_i].get_center(), radius=radius, fill_color=RED, shade_in_3d=True
        )
        scrambled_circle = Dot(
            g[scrambled_i].get_center(), radius=radius, fill_color=RED, shade_in_3d=True
        )

        self.play(GrowFromCenter(solved_circle), GrowFromCenter(scrambled_circle))

        self.wait()
        shortest_path = set([0, 1, 8, 9, 10])
        edges = [
            (u, v)
            for (u, v) in g.edges.keys()
            if u in shortest_path and v in shortest_path
        ]
        circles = [
            Dot(radius=radius2, fill_color=RED, shade_in_3d=True).move_to(g[v])
            for v in shortest_path
        ]

        self.play(
            g.edges[edges[3]].animate.set_color(RED),
            GrowFromCenter(circles[3]),
            run_time=0.75,
        )
        self.play(
            g.edges[edges[2]].animate.set_color(RED),
            GrowFromCenter(circles[2]),
            run_time=0.75,
        )
        self.play(
            g.edges[edges[1]].animate.set_color(RED),
            GrowFromCenter(circles[1]),
            run_time=0.75,
        )
        self.play(
            g.edges[edges[0]].animate.set_color(RED),
            run_time=0.75,
        )
        # self.play( 
        #     AnimationGroup(
        #         *[g.edges[e].animate.set_color(RED) for e in edges],
        #         *[GrowFromCenter(circle) for circle in circles],
        #     )
        # )
        self.wait()

        self.play(
            *[g.edges[e].animate.set_color(GRAY) for e in edges],
            *[ShrinkToCenter(circle) for circle in circles],
            ShrinkToCenter(solved_circle),
        )

        self.wait()
        self.next_section("BFS", skip_animations=False)

        adj = [[] for _ in range(n_nodes)]
        for u, v in g.edges.keys():
            adj[u].append(v)
            adj[v].append(u)

        bfs_vertices, bfs_edges = util.bfs(adj, scrambled_i)
        bfs_vertices.append([])

        circles = {
            v: Dot(
                g[v].get_center(),
                radius=radius2 if v != solved_i else radius,
                fill_color=RED,
                shade_in_3d=True,
            )
            for v in range(n_nodes)
        }

        seen = set()
        for i, (l_vertices, l_edges) in enumerate(zip(bfs_vertices, bfs_edges)):
            anims = []
            for v in l_vertices:
                anims.append(GrowFromCenter(circles[v]))
                seen.add(v)

            for e in l_edges:
                if e not in g.edges:
                    e = e[1], e[0]

                edge = g.edges[e]
                anims.append(edge.animate.set_color(RED))

            print(i)
            if i > 0:
                self.play_bfs_sound(time_offset=0.2)
            self.play(*anims)

            if solved_i in l_vertices:
                break

        self.wait()

        self.play(
            *[
                g.edges[(u, v)].animate.set_color(GRAY)
                for (u, v) in g.edges.keys()
                if (u not in shortest_path or v not in shortest_path)
            ],
            *[
                ShrinkToCenter(circles[v])
                for v in range(n_nodes)
                if v not in shortest_path and v in seen
            ],
        )
        self.wait()


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


def gen_house(color=RED, height=1, z_index=100):
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

    house = (
        Polygon(*pnts, color=color, fill_color=color, fill_opacity=1, z_index=z_index)
        .move_to(0 * DOWN)
        .scale_to_fit_height(height)
    )

    return house


def gen_icon(color=BLUE, height=1, z_index=100):
    pnts = [
        np.array([407.837, 313.233, 0.0]),
        np.array([340.843, 431.234, 0.0]),
        np.array([297.995, 558.503, 0.0]),
        np.array([253.986, 431.689, 0.0]),
        np.array([187.414, 311.624, 0.0]),
    ]

    icon = (
        ArcPolygon(
            *pnts,
            color=color,
            arc_config=[
                {"radius": 119.256, "color": color},
                {"radius": 70.9444, "color": color},
                {"radius": 70.9444, "color": color},
                {"radius": 119.256, "color": color},
                {"radius": 216.488, "color": color},
            ],
            fill_color=color,
            fill_opacity=1,
            z_index=z_index,
        )
        .move_to(0 * DOWN)
        .scale_to_fit_height(height)
    )

    return icon
