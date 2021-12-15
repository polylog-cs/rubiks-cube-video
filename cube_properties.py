import random
import math

from manim import *

# Use our fork of manim_rubikscube!
from manim_rubikscube import *

# This also replaces the default colors
from solarized import *

import util

try:
    from tqdm import trange
except ImportError:
    trange = range

cube.DEFAULT_CUBE_COLORS = [BASE3, RED, GREEN, YELLOW, ORANGE, BLUE]


class Neighborhood(util.RubikScene):
    def construct(self):
        """
        Ukázat graf stavů ze do hloubky 1, pak 2.

        TODO: ve vnejsi vrstve dat nektere kostky bliz, zvetsit je
        TODO: v druhe fazi jdou cary pres kostky
        """
        self.next_section("First layer", skip_animations=True)

        edges = set()
        q = [RubiksCube(cubie_size=0.2)]
        seen = set([q[0].hash()])
        layers = [[q[0].hash()], []]
        parents = {}
        parents[q[0].hash()] = None

        print("Starting BFS")
        for i in trange(262):  # 1, 19, 262
            old_hash = q[i].hash()

            for move in util.POSSIBLE_MOVES:
                if i < 19:
                    q[i].do_move(move)
                else:
                    # This is faster, but does not rotate visually
                    q[i].update_indices_after_move(move)

                new_hash = q[i].hash()
                edges.add((min(old_hash, new_hash), max(old_hash, new_hash)))

                if new_hash not in parents:
                    parents[new_hash] = old_hash

                if new_hash not in seen:
                    # We won't be showing these anyways, avoid copying
                    if i < 19:
                        q.append(q[i].copy())

                    seen.add(new_hash)
                    layers[-1].append(new_hash)

                if i < 19:
                    q[i].do_move(util.invert_move(move))
                else:
                    q[i].update_indices_after_move(util.invert_move(move))

            if old_hash == layers[-2][-1]:
                layers.append([])

        layout = {layers[0][0]: ORIGIN}

        for li, layer in enumerate(layers[1:]):
            for i, h in enumerate(layer):
                distance = (li + 1) * 3
                pos = distance * UP * np.sin(2 * PI * i / len(layer))
                pos += distance * RIGHT * np.cos(2 * PI * i / len(layer))
                layout[h] = pos

        print(f"Done with BFS, {len(seen)} vertices")

        self.add(q[0])

        anims = []
        cubes1 = []
        for i, move in enumerate(util.POSSIBLE_MOVES):
            cur_cube = q[0].copy()
            cubes1.append(cur_cube)
            anims.append(
                AnimationGroup(
                    # Add 10 * OUT to keep the cubes in front of the edges
                    CubeMove(cur_cube, move, layout[layers[1][i]] + 10 * OUT),
                    Create(
                        Line(ORIGIN, layout[layers[1][i]], shade_in_3d=True, color=GRAY)
                    ),
                    run_time=3,
                )
            )

        self.play(LaggedStart(*anims, lag_ratio=0.01), q[0].animate.shift(10 * OUT))
        anims = []

        for u, v in edges:
            if u in layers[1] and v in layers[1]:

                anims.append(
                    Create(Line(layout[u], layout[v], shade_in_3d=True, color=GRAY))
                )

        for cube in cubes1 + [q[0]]:
            # Dummy animations to keep the cubes on top
            anims.append(cube.animate.shift(ORIGIN))

        self.play(*anims)
        self.wait()

        self.next_section("Second layer", skip_animations=False)

        anims = []

        for i, cube in enumerate(q[19:]):
            h = cube.hash()
            # anims.append(
            #     Create(Dot(layout[h], color=GRAY))
            # )

            def f(cube):
                return cube.move_to(layout[cube.hash()]).set_stroke_width(0).scale(0.2)

            cube.move_to(layout[parents[h]])
            cube.shift(IN * 10)
            self.add(cube)
            # self.bring_to_back(cube)

            anims.append(
                AnimationGroup(
                    ApplyFunction(f, cube),
                    Create(
                        Line(
                            layout[parents[h]],
                            layout[h],
                            shade_in_3d=True,
                            color=GRAY,
                            stroke_width=2,
                        )
                    ),
                )
            )
            # self.add(cube)

        for cube in cubes1 + [q[0]]:
            # Dummy animations to keep the cubes on top
            self.bring_to_front(cube)
            anims.append(cube.animate.shift(ORIGIN))

        self.play(LaggedStart(*anims, lag_ratio=0.001))
        self.wait()

        anims = []
        for u0, v0 in edges:
            # Edges to vertices at distance 3 - ignore these
            if u0 in layers[3] or v0 in layers[3]:
                continue

            # Try both orderings
            for u, v in [(u0, v0), (v0, u0)]:
                if u in layers[2] or v in layers[2]:
                    if u in layers[2]:
                        u, v = v, u

                    # Skip the edge to the parent because we've already created it
                    if u != parents[v]:
                        anims.append(
                            Create(
                                Line(
                                    layout[u],
                                    layout[v],
                                    shade_in_3d=True,
                                    color=GRAY,
                                    stroke_width=2,
                                )
                            )
                        )

        for cube in cubes1 + [q[0]]:
            # Dummy animations to keep the cubes on top
            self.bring_to_front(cube)
            anims.append(cube.animate.shift(ORIGIN))

        self.play(*anims)
        self.wait()


class BFSTest(util.RubikScene):
    def construct(self):
        """
        Ukázka BFS z jednoho vrcholu, pro testování
        """

        edges = set()
        q = [RubiksCube()]
        seen = set([q[0].hash()])
        layers = [[q[0].hash()], []]

        print("Starting BFS")
        for i in trange(262):
            old_hash = q[i].hash()

            for move in util.POSSIBLE_MOVES:
                q[i].update_indices_after_move(move)
                new_hash = q[i].hash()
                edges.add((min(old_hash, new_hash), max(old_hash, new_hash)))

                if new_hash not in seen:
                    q.append(q[i].copy())
                    seen.add(new_hash)
                    layers[-1].append(new_hash)

                q[i].update_indices_after_move(util.invert_move(move))

            if old_hash == layers[-2][-1]:
                layers.append([])

        layout = {layers[0][0]: ORIGIN}

        for li, layer in enumerate(layers[1:]):
            for i, h in enumerate(layer):
                distance = (li + 1) ** 2
                pos = distance * UP * np.sin(2 * PI * i / len(layer))
                pos += distance * RIGHT * np.cos(2 * PI * i / len(layer))
                layout[h] = pos

        print(f"Done with BFS, {len(seen)} vertices")
        print([len(x) for x in layers])
        graph = Graph(
            list(seen),
            list(edges),
            # layout="kamada_kawai",
            layout=layout,
            vertex_config={"fill_color": GRAY, "radius": 0.04},
            edge_config={"stroke_color": GRAY},
        )
        self.add(graph)
        self.wait()


class NeighborCount(util.RubikScene):
    def construct(self):
        """
        Čísla s počtem vrcholů do vzdálenosti n, pro n = 1, 2, 3. Pak
        ukázat, že je to vždycky zhruba *10.

        Well, one clear property is that the number of reachable configurations
        grows very quickly. We already found out that there are about 10^20 cube
        configurations but people have also computed that every cube can be
        solved in at most 20 moves, so it looks like the number of reachable
        configurations grows by a factor of 10 in every step. At the beginning
        it is a bit faster than that, and the last few steps it is probably
        going to get smaller, but it makes sense to assume it is around 10 every
        step.

        The fact that it grows so quickly is not a matter of course, which we
        will see once we compare the Rubik’s cube graph with a road network
        graph. For example, consider this network of crossroads in Manhattan. In
        this network, the number of nodes explored grows quadratically with the
        distance, whereas for the cube graph it grows exponentially. This means
        that if you explore up to distance 5, the number of nodes visited in
        Manhattan will be around 5^2 = 25. It is roughly twice as much, but that
        is not so important. On the other hand, in the cube graph, the number of
        nodes seen will be around 10^5. Again, it’s actually about 6 times
        larger, but close enough.
        """
        self.next_section("Table", skip_animations=False)

        table_group = Group()

        table_values = [
            [0, 1],
            [1, 19],
            [2, 262],
            [3, 3502],
            [4, 46741],
            [5, 621649],
        ]

        def with_thousand_separator(x):
            return f"{x:,d}".replace(",", r"\,")

        table = [[r"\textbf{Steps}", r"\textbf{Explored}"]]
        table += [[with_thousand_separator(x) for x in row] for row in table_values]
        table += [["$n$", r"$\sim 10^n$"]]

        table = [[Tex(x, color=GRAY) for x in row] for row in table]

        for row in table:
            table_group.add(*row)

        horizontal_buff = 0.75
        table_group.arrange_in_grid(
            cols=2,
            col_alignments="rl",
            row_alignments="d" * len(table),
            buff=(horizontal_buff, MED_SMALL_BUFF),
        )

        cube = RubiksCube(cubie_size=0.4)
        # cube.next_to(table_group, direction=UP)

        rubiks_group = Group(cube, table_group)
        rubiks_group.arrange(direction=DOWN, buff=MED_LARGE_BUFF)

        self.play(
            LaggedStart(
                FadeIn(cube),
                *[Write(cell) for row in table[:7] for cell in row],
                lag_ratio=0.1,
            )
        )
        # self.play(
        #     *[AnimationGroup(*[Write(cell) for cell in row]) for row in table_tex[:7]],
        # )
        self.wait()

        for cell in table[-1]:
            cell.set_color(RED).shift(MED_SMALL_BUFF * DOWN)

        self.play(LaggedStart(*[Write(cell) for cell in table[-1]], lag_ratio=0.1))
        self.wait()

        self.next_section("Manhattan comparison", skip_animations=False)

        background_rect = Rectangle(
            height=8,
            width=14.2 / 2,
            fill_opacity=1,
            fill_color=BASE02,
            color=BASE02,
            # shade_in_3d=True,  # for the edges of the graph to be in front
            z_index=-10,
        )

        background_rect.next_to(14.2 / 2 * LEFT, direction=LEFT)
        self.add(background_rect)

        self.play(
            background_rect.animate.move_to(
                # background_rect.get_boundary_point(direction=RIGHT) * RIGHT
                14.2
                / 4
                * LEFT
            ),
            rubiks_group.animate.shift(RIGHT * 14.2 / 4),
            run_time=2,
        )

        self.wait()

        grid_size = 13
        grid_center = grid_size // 2
        grid_spacing = 0.35

        vertices = set((i, j) for i in range(grid_size) for j in range(grid_size))
        distances = {}
        edges = []
        layout = {}
        for i in range(grid_size):
            for j in range(grid_size):
                layout[(i, j)] = np.array([i * grid_spacing, j * grid_spacing, 0.0])
                distances[(i, j)] = abs(i - grid_center) + abs(j - grid_center)

                for cur in [(i + 1, j), (i, j + 1)]:
                    if cur in vertices:
                        edges.append(((i, j), cur))

        graph = Graph(
            vertices,
            edges,
            layout=layout,
            # BASE0 is a bit lighter than BASE00 == GRAY
            vertex_config={"fill_color": GRAY},
            edge_config={"stroke_color": GRAY},
        )
        graph.move_to(LEFT * 14.2 / 4).align_to(rubiks_group, UP)
        self.play(DrawBorderThenFill(graph, run_time=1))
        self.wait()

        dist = 5
        anims = [[] for _ in range(dist + 1)]

        for i in range(grid_size):
            for j in range(grid_size):
                if distances[(i, j)] <= dist:
                    anims[distances[(i, j)]].append(
                        graph.vertices[(i, j)].animate.set_color(RED)
                    )

                for cur in [(i + 1, j), (i, j + 1)]:
                    if cur in vertices:
                        edge_distance = min(distances[(i, j)], distances[cur])
                        if edge_distance < dist:
                            # We don't know the direction of the edge.
                            edge = graph.edges[(((i, j), cur))]
                            anims[edge_distance + 1].append(edge.animate.set_color(RED))

        run_time = 0.25
        lag_ratio = 0.9

        for it in range(len(anims)):
            offset = run_time * lag_ratio * (it + 0.5)
            self.add_sound(f"audio/bfs/bfs_{it:03d}", time_offset=offset)

        self.play(
            LaggedStart(
                *[AnimationGroup(*anims_step, run_time=0.25) for anims_step in anims],
                lag_ratio=0.9,
            )
        )

        self.wait()

        values_manhattan = [
            [Tex(r"\textbf{Steps}", color=GRAY), Tex(r"\textbf{Explored}", color=GRAY)],
            [MathTex("5", color=GRAY), MathTex("61", color=GRAY)],
            [MathTex("n", color=RED), MathTex("\sim 2n^2", color=RED)],
        ]
        table_manhattan = Group(*[cell for row in values_manhattan for cell in row])
        table_manhattan.arrange_in_grid(
            col_alignments="rl",
            row_alignments="ddd",
            buff=(horizontal_buff, MED_SMALL_BUFF),
        )
        for cell in values_manhattan[-1]:
            # The constant is needed because $n^2$ is taller than 10^n
            cell.set_color(RED).shift(MED_SMALL_BUFF * DOWN * 0.6)

        table_manhattan.align_to(rubiks_group, DOWN).shift(14.2 / 4 * LEFT)

        self.play(
            LaggedStart(
                *[Write(cell) for cell in values_manhattan[0]],
                *[Write(cell) for cell in values_manhattan[1]],
                *[Write(cell) for cell in values_manhattan[2]],
                lag_ratio=0.1,
            )
        )

        self.wait()


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


class FriendshipGraph(Scene):
    def construct(self):
        """
        For example, you may have heard about the six degrees of separation
        phenomenon that says that you can reach anybody on earth via 6
        intermediate friends.

        In fact, researchers have verified that, at least on Facebook, you are
        connected to pretty much anybody with just 4 intermediate friends.
        Again, this is because, intuitively, the number of people reached is
        always multiplied by something like 50-100 in every step, since the
        average person has around 100 friends.

        TODO: po BFS zvyraznit cestu mezi excited typkem a Feliksem,
        pak nechat zmizet zbytek grafu, ukazat jen "rovnou" cestu.
        Pak Feliks zmizi a misto nej bude Grant Sanderson, s tim
        ze se taky zvysi pocet intermediaries.
        """
        N = 50

        # re-generate graph until
        max_steps = 3

        random.seed(4)

        while True:
            g = dict([(i, []) for i in range(N)])
            vertices = []
            edges = []

            for i in range(N):
                vertices.append(i)
                # the distribution of k defines the graph's density
                k = random.randrange(2, 5)
                adj = set(random.choices(range(N), k=k))

                try:
                    # Remove self-loop
                    adj.remove(i)
                except KeyError:
                    pass

                for j in adj:
                    g[i].append(j)
                    g[j].append(i)
                    edges.append((i, j))

            bfs_vertices, bfs_edges = bfs(g, 0)
            bfs_vertices.append([])

            print("Actual steps:", len(bfs_vertices) - 2)
            if len(bfs_vertices) <= max_steps + 2 and len(g[0]) <= 3:
                break

        ganim = Graph(
            vertices,
            edges,
            layout="kamada_kawai",
            layout_scale=5,
            vertex_config={"fill_color": GRAY},
            edge_config={"stroke_color": GRAY},
        )

        ganim.scale_to_fit_height(6.5)
        ganim.move_to(RIGHT * 2)

        text_scale = 1.8
        steps_tex = (
            Tex("Steps: 0", color=GRAY)
            .scale(text_scale)
            .next_to(ganim, direction=LEFT, buff=1)
        )

        ganim.move_to(ORIGIN)

        guy = ImageMobject("img/excited_guy.png").set_z_index(100)

        self.play(FadeIn(ganim))
        self.wait()
        self.play(FadeIn(guy))
        self.wait()
        self.play(guy.animate.move_to(ganim.vertices[0].get_center()).scale(0.2))
        self.wait()
        self.play(
            ganim.animate.shift(RIGHT * 2),
            guy.animate.shift(RIGHT * 2),
            FadeIn(steps_tex),
        )
        self.wait()

        highlight_color = RED
        flash_color = YELLOW

        for i, (l_vertices, l_edges) in enumerate(zip(bfs_vertices, bfs_edges)):
            anims = []

            if i != len(bfs_vertices) - 1:
                steps_tex2 = (
                    Tex(f"Steps: {i}", color=GRAY)
                    .scale(text_scale)
                    .align_to(steps_tex, direction=LEFT)
                )
                anims.append(steps_tex.animate.become(steps_tex2))

            for v in l_vertices:
                anims.append(
                    FadeIn(
                        Dot(
                            ganim.vertices[v].get_center(),
                            color=highlight_color,
                            z_index=10,
                        )
                    )
                )
                anims.append(
                    Flash(
                        ganim.vertices[v].get_center(),
                        color=flash_color,
                        z_index=10,
                        time_width=0.5,
                    )
                )

            for e in l_edges:
                swapped = False
                if e not in ganim.edges:
                    i, j = e
                    e = j, i
                    swapped = True

                edge = ganim.edges[e]

                start, end = edge.get_start_and_end()
                if swapped:
                    start, end = end, start

                anims.append(Create(Line(start, end, color=highlight_color)))

            self.play(*anims)

        self.wait()
