import random
import math
import numpy as np
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



class Neighborhood(util.RubikScene):
    def construct(self):
        """
        Ukázat graf stavů ze do hloubky 1, pak 2.
        TODO: ve vnejsi vrstve dat nektere kostky bliz, zvetsit je?
        TODO: v druhe fazi jdou cary pres kostky
        """
        self.next_section("First layer", skip_animations=False)

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
                    run_time=0.5
                )
            )
            self.play_cube_sound(time_offset=i * 0.1) # = run_time * lag_ratio

        self.play(LaggedStart(*anims, lag_ratio=0.2), q[0].animate.shift(10 * OUT))
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
                    run_time=0.5,
                )
            )
            if i % 3 == 0:
                self.play_cube_sound(time_offset=i*0.005)
            # self.add(cube)

        for cube in cubes1 + [q[0]]:
            # Dummy animations to keep the cubes on top
            self.bring_to_front(cube)
            anims.append(cube.animate.shift(ORIGIN))

        self.play(LaggedStart(*anims, lag_ratio=0.01))
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
        font_size = 40
        smaller_font_size = 40
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
        table += [[r"$20$", r"$\sim 10^{20}$"]]

        table = [[Tex(x, color=GRAY, font_size = font_size) for x in row] for row in table]

        dots = Group(*[Tex(r"$\vdots$", color = GRAY, font_size = font_size) for _ in range(2)])

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
                Succession(
                    FadeIn(cube),
                    Rotate(cube, 2 * PI, UP)
                ),
                *[AnimationGroup(*[Write(cell) for cell in row]) for row in table[:7]],
                lag_ratio=0.5,
            )
        )
        self.wait()

        for cell in table[-2]:
            cell.set_color(RED).shift(MED_SMALL_BUFF * DOWN / 2)
        for cell in table[-1]:
            cell.shift(MED_SMALL_BUFF * DOWN)


        # 20 and 10^20 + dots
        dots[0].move_to(
            (
                table[-3][0].get_right()
                +table[-3][1].get_left()
                +table[-1][0].get_right()
                +table[-1][1].get_left()
            )/4
        )
        self.play(
            Write(dots[0]),
            LaggedStart(*[Write(cell) for cell in table[-1]], lag_ratio=0.1)
        )
        self.wait()

        # n and 10^n

        dots[1].move_to(dots[0].get_center())
        eps = 0.4
        self.play(
            dots[0].animate().shift(eps * UP).scale(0.5),
            dots[1].animate().shift(eps * DOWN).scale(0.5)
        )
        self.play(
            LaggedStart(*[Write(cell) for cell in table[-2]], lag_ratio=0.1)
        )
        self.wait()

        # dark rectangle slides
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
            Group(rubiks_group, *[dots]).animate.shift(RIGHT * 14.2 / 4),
            run_time=2,
        )

        self.wait()

        #grid graph

        grid_size = 13
        grid_center = grid_size // 2
        grid_spacing = 0.3 #0.35

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




        # add table anims
        grid_table_values = [[n, 2*n*n + 2*n + 1] for n in range(6)]

        #grid_table = [[r"\textbf{Steps}", r"\textbf{Explored}"]]
        grid_table = [[with_thousand_separator(x) for x in row] for row in grid_table_values]
        #grid_table += [["$n$", r"$2n^2 + 2n + 1$"]]

        grid_table = [[Tex(x, color=GRAY, font_size = smaller_font_size) for x in row] for row in grid_table]

        grid_table_group = Group()
        for row in grid_table:
            grid_table_group.add(*row)

        horizontal_buff2 = 0.375#0.75
        grid_table_group.arrange_in_grid(
            cols=2,
            col_alignments="rl",
            row_alignments="d" * len(table),
            buff=(horizontal_buff2, SMALL_BUFF),
        ).next_to(graph, direction=DOWN, buff=MED_SMALL_BUFF)

        for i in range(6):
            anims[i] += [Write(cell) for cell in grid_table[i]]




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




        #the grid shifts and table is finished
        self.next_section(skip_animations=False)

        values_manhattan = [[Tex(r"\textbf{Steps}", color=GRAY, font_size = font_size), Tex(r"\textbf{Explored}", color=GRAY, font_size = font_size)]]
        for a,b in grid_table_values:
            values_manhattan += [[Tex(str(a), color = GRAY, font_size = font_size), Tex(str(b), color = GRAY, font_size = font_size)]]
        values_manhattan += [[MathTex("n", color=RED, font_size = font_size), MathTex("{{2n^2}} + 2n + 1", color=RED, font_size = font_size)]]
        
        table_manhattan = Group(*[cell for row in values_manhattan for cell in row])
        table_manhattan.arrange_in_grid(
            cols=2,
            col_alignments="rl",
            row_alignments="d" * len(values_manhattan),
            buff=(horizontal_buff, MED_SMALL_BUFF),
        ).align_to(table_group, UP).align_to(table_group, LEFT).shift(14.2/2*LEFT)

        for cell in values_manhattan[-1]:
            # The constant is needed because $n^2$ is taller than 10^n
            cell.set_color(RED).shift(MED_SMALL_BUFF * DOWN * 0.5)


      
        anims = []
        for i in range(6):
            anims += [
                    cell1.animate().become(cell2) 
                    for cell1, cell2 
                    in zip(grid_table[i], values_manhattan[i+1])
                ]
        anims += [Write(cell) for cell in values_manhattan[0] + values_manhattan[-1]]

        #shifting manhattan        
        avg = sum(graph._layout.values()) / len(graph._layout)
        new_layout =  {
            key: (pos - avg)/2 + [-14.2/4, cube.get_center()[1], 0]
            for key, pos in graph._layout.items()
        }
        self.play(
            *[dot.animate().scale(0.1) for _,dot in graph.vertices.items()]
        )
        self.wait()
        self.play(
            graph.animate().change_layout(new_layout),
        )
        self.wait()
        self.play(
            *anims
        )
        self.wait()
        #change to 2n^2
        new_text = MathTex("\\sim {{2n^2}}", color = RED, font_size = font_size).move_to(
            values_manhattan[-1][1].get_center()
        ).align_to(
            values_manhattan[-1][1], LEFT
        )
        self.play(
            TransformMatchingTex(
                values_manhattan[-1][1],
                new_text
            )
        )
        self.wait()

        #indicate fives
        self.play(
            Circumscribe(Group(*values_manhattan[6]))
        )
        self.wait()


        self.play(
            Circumscribe(Group(*table[6]))
        )
        self.wait()

        self.play(
            FadeOut(background_rect),
            *[Unwrite(dot) for dot in dots],
            *[Unwrite(t) for t in table_group],
            *[(Unwrite(t) if t != values_manhattan[-1][1] else Wait(0)) for t in grid_table_group],
            Unwrite(values_manhattan[0][0]),
            Unwrite(values_manhattan[0][1]),
            Unwrite(values_manhattan[-1][0]),
            #*[AnimationGroup(Unwrite(t), Unwrite(u)) for t,u in [values_manhattan[0]] + [values_manhattan[-1]]],
            FadeOut(cube),
            Uncreate(graph),
            Unwrite(new_text)
            #*[AnimationGroup(Unwrite(t), Unwrite(u)) for t,u in [table_manhattan]],
        )

        self.wait()


class FriendshipGraph(util.RubikScene):
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
        """
        self.next_section(skip_animations=False)
        N = 50

        # re-generate graph until
        max_steps = 3

        random.seed(4)
        attempts = 0

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

            bfs_vertices, bfs_edges = util.bfs(g, 0)
            bfs_vertices.append([])

            # print("Actual steps:", len(bfs_vertices) - 2)
            if len(bfs_vertices) <= max_steps + 2 and len(g[0]) <= 3:
                break

            attempts += 1
            if attempts % 100 == 0:
                print(f"{attempts} unsuccessful attempts")


        ganim = Graph(
            vertices,
            edges,
            layout="kamada_kawai",
            layout_scale=5,
            # vertex_mobjects = icons2,
            vertex_config={"fill_color": GRAY},
            edge_config={"stroke_color": GRAY},
        ).move_to(ORIGIN)

        positions = {}
        for i in range(N):
            positions[i] = np.array([ganim.vertices[i].get_center()[0]*1.2, ganim.vertices[i].get_center()[1], 0.0])

        positions[0] += 0.3*RIGHT
        positions[7] += 1.2*LEFT + 2*UP
        positions[27] += 2*LEFT + 1*DOWN
        positions[45] += 0.5*RIGHT + 0.5*DOWN
        positions[31] += 1*LEFT + 1*DOWN
        positions[18] += 1*RIGHT + 1*UP
        positions[48] = positions[33] + 0.5*(UP+RIGHT)
        positions[33] += 0.2*(RIGHT + DOWN)
        positions[24] += 0.5 * DOWN
        positions[15] += 0.3*(DOWN + LEFT)
        positions[21] += 0.8*(DOWN + RIGHT)+0.1*RIGHT
        positions[38] += 0.8*(LEFT)+0.4*UP
        positions[20] += 0.4*(LEFT + UP)
        positions[14] += 0.4*(UP)
        positions[17] += 0.2*(UP)
        positions[25] += 0.2*(DOWN)
        positions[9] += 0.8*(UP)
        positions[48] += 0.4*(UP)
        positions[2] += 0.3*(RIGHT)


        ganim.change_layout(positions)

        ganim.scale_to_fit_height(6.7)
        #ganim.move_to(RIGHT * 2)


        text_scale = 1
        steps_tex = (
            Tex("Steps: 0", color=GRAY)
            .scale(text_scale)
            .next_to(ganim, direction=LEFT, buff=0.2)
            .shift(3*UP)
        )

        #ganim.move_to(ORIGIN)


        # icons are separate from graph, scale to fit height does not like vertex_mobjects
        icons = []
        for i in range(N):
            icons.append(Dot(color = GRAY, z_index = 100).move_to(
                    ganim.vertices[i].get_center()
                ))


        guy = ImageMobject("img/excited_guy.png").set_z_index(100)

        # reveal graph
        self.play(
            FadeIn(ganim),
        )

        self.play(
            *[FadeIn(icon) for icon in icons]
        )

        # reveal icons
        self.play(
            *[Transform(
                icon,
                # Tex("$" + str(i) + "$", color = BLACK).move_to(icon.get_center())
                gen_icon(
                    height = 0.5
                ).move_to(
                    icon.get_center()
                )
            ) for i, icon in enumerate(icons)]
        )
        self.wait()


        # reveal guy
        self.play(FadeIn(guy))
        self.wait()
        self.play(guy.animate.move_to(ganim.vertices[0].get_center()).scale(0.2))
        self.wait()


        # fadein counter
        self.play(
            # ganim.animate.shift(RIGHT * 2),
            # guy.animate.shift(RIGHT * 2),
            # *[icon.animate.shift(RIGHT*2) for icon in icons],
            FadeIn(steps_tex),
        )
        self.wait()

        highlight_color = RED
        flash_color = YELLOW

        visited = set()
        dots = []
        edges = []
        important_edges = []
        for i, (l_vertices, l_edges) in enumerate(zip(bfs_vertices, bfs_edges)):
            anims = []

            if i != len(bfs_vertices) - 1:
                steps_tex2 = (
                    Tex(f"Steps: {i}", color=GRAY)
                    .scale(text_scale)
                    .move_to(steps_tex.get_center())
                )
                anims.append(steps_tex.animate.become(steps_tex2))

                for v in l_vertices:
                    d = Dot(
                        ganim.vertices[v].get_center(),
                        color=highlight_color,
                        z_index=1000,
                    )
                    dots.append(d)
                    anims.append(
                        FadeIn(
                            d
                        )
                    )
                    anims.append(
                        Succession(
                            Wait(0),
                            Flash(
                                ganim.vertices[v].get_center(),
                                color=flash_color,
                                z_index=10,
                                time_width=0.5,
                            )
                        )
                    )

                for e in l_edges:
                    swapped = False
                    if e not in ganim.edges:
                        e = e[1], e[0]
                        swapped = True

                    edge = ganim.edges[e]

                    start, end = edge.get_start_and_end()
                    if swapped:
                        start, end = end, start

                    if not e[0] in visited or not e[1] in visited:
                        line = Line(
                            start, 
                            end, 
                            color=highlight_color,
                            z_index = 0
                        )
                        if (e[0] == 0 and e[1] == 35)\
                            or (e[0] == 22 and e[1] == 27)\
                            or (e[0] == 27 and e[1] == 35):
                            important_edges.append(line)
                        else:
                            edges.append(line)
                        anims.append(Create(line))
                        visited.add(e[0])
                        visited.add(e[1])

                if i > 0:
                    self.play_bfs_sound(time_offset=0.2)
                
                
                self.play(
                    *anims,
                    *[icon.animate.shift(0.0*UP) for icon in icons]
                )

        self.wait()

        # reveal feliks

        self.play(
            icons[22].animate.scale(0.0)
        )
        feliks = ImageMobject(
            "img/feliks.png"
        )
        feliks.scale_to_fit_height(0.001).move_to(icons[22].get_center())
        self.play(
            feliks.animate.scale_to_fit_height(guy.get_height())
        )
        self.wait()


        #highlight path
        newheight = 0.75
        self.play(
            icons[35].animate.scale_to_fit_height(newheight),
            icons[27].animate.scale_to_fit_height(newheight),
        )
        self.wait()

        #remove graph
        self.play(
            FadeOut(ganim),
            *[FadeOut(dot) for dot in dots],
            *[Uncreate(edge) for edge in edges],
            *[Uncreate(icon) for icon in icons[0:27]+icons[28:35]+icons[36:50]],
            Unwrite(steps_tex)
        )
        self.wait()

        self.next_section(skip_animations=False)

        left_pos = 5.5*LEFT
        right_pos = 5.5*RIGHT
        right_mid_pos = (left_pos + 2*right_pos)/3
        left_mid_pos = (2*left_pos + right_pos)/3

        icon1 = icons[35]
        icon2 = icons[27]
        line1, line2, line3 = important_edges
        line1.generate_target()
        line1.target = Line(left_pos, left_mid_pos, color = highlight_color)
        line2.generate_target()
        line2.target = Line(left_mid_pos, right_mid_pos, color = highlight_color)
        line3.generate_target()
        line3.target = Line(right_mid_pos, right_pos, color = highlight_color)
        
        # straighten the path
        diagram_height = 1.5
        self.play(
            guy.animate.move_to(left_pos).scale_to_fit_height(diagram_height),
            feliks.animate.move_to(right_pos).scale_to_fit_height(diagram_height),
            icon1.animate.move_to(left_mid_pos).scale_to_fit_height(diagram_height),
            icon2.animate.move_to(right_mid_pos).scale_to_fit_height(diagram_height),
            MoveToTarget(line1),
            MoveToTarget(line2),
            MoveToTarget(line3),
        )
        self.wait()

        # make six icons
        icons6 = [icon1, icon1.copy(), icon1.copy(), 
            icon2, icon2.copy(), icon2.copy()]

        self.play(
            *[
                icon.animate.move_to( 
                    ((6-i)*left_pos + (i+1)*right_pos)    /    7.0
                )
                for i, icon in enumerate(icons6)
            ]
        )
        self.wait()

        # change feliks to grant
        grant = ImageMobject("img/grant.png").scale_to_fit_height(0.001).move_to(feliks.get_center())

        self.play(
            feliks.animate.scale(0.001)
        )
        self.remove(
            feliks
        )
        self.play(
            grant.animate.scale_to_fit_height(guy.get_height())
        )
        self.wait()

        brace_shift = 1.3*DOWN
        brace = Brace(Group(Dot(icons6[0].get_center()), Dot(icons6[5].get_center())), DOWN, color = GRAY).shift(brace_shift)
        txt = (
            Tex(r"$6$ degrees of separation", color = GRAY)
            .move_to(brace.get_center())
            .next_to(brace, DOWN)
        )
        
        self.play(
            Create(brace),
            Write(txt)
        )
        self.wait()

        # change to 4
        icons4 = icons6[0:2] + icons6[4:6]
        self.play(
            Uncreate(icons6[2]),
            Uncreate(icons6[3]),
        )
        for i, icon in enumerate(icons4):
            icon.generate_target()
            icon.target.move_to(
                ((4-i)*left_pos + (i+1)*right_pos) / 5.0
            )
        brace.generate_target()
        brace.target = Brace(Group(Dot(icons6[0].target.get_center()), Dot(icons6[5].target.get_center())), DOWN, color = GRAY).shift(brace_shift)
        newtxt = Tex(r"$4$ degrees of separation", color = GRAY).move_to(txt.get_center())
        fbtxt = Tex("(on Facebook)", color = GRAY).move_to(txt.get_center()).next_to(txt, DOWN)
        self.play(
            *[MoveToTarget(icon) for icon in icons4],
            MoveToTarget(brace),
            Transform(txt, newtxt),
            Write(fbtxt)
            #txt.animate.become(newtxt)
        )

        # labels above icons
        nums = [
            r"1",
            r"100",
            r"10\,000",
            r"1\,000\,000",
            r"100\,000\,000",
            r"1\,000\,000\,000",
        ]
        labels = [
            (
                Tex(r"$" + num + "$", color = GRAY)
                .move_to(obj.get_center())
                .next_to(obj, UP, buff=0.5)
                .shift((i % 2) * 0.5 * UP)
            )
            for i, (num, obj) in enumerate(zip(nums, [guy] + icons4 + [grant]))
        ]

        self.play(
            AnimationGroup(*[Write(label) for label in labels], lag_ratio = 1)
        )
        self.wait(2)



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


