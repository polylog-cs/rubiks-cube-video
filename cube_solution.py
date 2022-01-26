import random
from manim import *

# Use our fork of manim_rubikscube!
from manim_rubikscube import *

# This also replaces the default colors
from solarized import *

import util
import itertools
#cube.DEFAULT_CUBE_COLORS = [BASE3, RED, GREEN, YELLOW, ORANGE, BLUE]


class BFSCircleAnimations:
    def __init__(
        self,
        center,
        iterations,
        label_angle=0.25 * PI,
        base_radius=0.9,
        radius_step=0.4,
    ):
        self.center = center
        self.iterations = iterations
        self.base_radius = base_radius
        self.radius_step = radius_step

        self.circle = Circle(color=RED, radius=base_radius).move_to(center)
        self.label = MathTex(r"1", color=RED)
        self.label.add_updater(
            lambda x: x.move_to(
                Point()
                .move_to(self.circle.get_right() + RIGHT * 0.4)
                .rotate(angle=label_angle, about_point=self.circle.get_center()),
            )
        )

        self.step = -1
        self.circles = [self.circle]

    def __next__(self):
        self.step += 1

        if self.step == 0:
            return (GrowFromCenter(self.circle), FadeIn(self.label))
        elif self.step < self.iterations:
            c2 = self.circle.copy()
            self.circles.append(c2)

            # This is needed so that the label follows properly during the animation
            # (we can't be moving `c2`, it has to be `circle`)
            self.circle, c2 = c2, self.circle

            label2 = MathTex(str(self.step + 1), color=RED)

            c3 = Circle(
                color=RED, radius=self.base_radius + self.step * self.radius_step
            ).move_to(self.center)

            return (
                self.circle.animate.become(c3),
                c2.animate.set_color(GRAY),
                self.label.animate.become(label2),
            )
        else:
            # tex.clear_updaters()
            raise StopIteration

    def __iter__(self):
        return self


def generate_path_animations(center, angle, base_radius, radius_step, n_steps):
    spread = 0.3

    def get_radius(i):
        return base_radius + i * radius_step

    points = [Dot(color=RED).shift(center)]
    animations = [[Create(points[0])]]

    for i in range(n_steps):
        if i < n_steps - 1:
            cur_spread = np.arcsin(spread / get_radius(i))
            cur_angle = np.random.uniform(angle - cur_spread, angle + cur_spread)
        else:
            # Keep the last one centered to match the other side
            cur_angle = angle

        point = (
            Dot(color=RED)
            .shift(RIGHT * get_radius(i))
            .rotate_about_origin(cur_angle)
            .shift(center)
        )
        points.append(point)
        animations.append([Create(point)])

    for i in range(1, n_steps + 1):
        animations[i].append(
            Create(Line(points[i - 1].get_center(), points[i].get_center(), color=RED))
        )

    return points, animations


class BFSOneSide(util.RubikScene):
    def construct(self):
        """
        animace kde je nalevo scrambled kostka, napravo složená, přidáváme
        “slupky” kolem scrambled, vnější slupka se vzdáleností 20 už obsahuje
        složenou kostku.

        Ztratí se všechny slupky, ukážeme je kolem složené (do vzdálenosti 10).

        Ukázat slupky z obou stran, musí se protínat

        """

        base_radius = 0.9
        radius_step = 0.3
        n_steps = 20
        n_steps_small = 10
        overlap = 2

        cube_distance = base_radius + radius_step * (n_steps - overlap / 2 - 1)
        
        #radius_step = (cube_distance - base_radius) / 19.0

        cube_from = RubiksCube(cubie_size=0.3, rotate_nicely=True).shift(
            LEFT * cube_distance / 2
        )
        cube_to = RubiksCube(cubie_size=0.3, rotate_nicely=True).shift(
            RIGHT * cube_distance / 2
        )
        util.scramble_to_feliks(cube_from)

        self.add(cube_from, cube_to)
        self.wait()

        circle_anims_from = BFSCircleAnimations(
            cube_from.get_center(),
            n_steps,
            label_angle=-15 * DEGREES,
            base_radius=base_radius,
            radius_step=radius_step,
        )

        if True:
            for i, anims in enumerate(circle_anims_from):
                run_time = 2 / (i + 2)
                self.play_bfs_sound(animation_run_time=run_time)
                self.play(*anims, run_time=run_time)

            self.wait()

            # Ztratí se slupky až na prvních 10, ty tu kostku neobsahují.
            label2 = MathTex(str(n_steps_small), color=RED)

            for i in reversed(range(n_steps_small, n_steps)):
                self.bfs_counter = i
                self.play_bfs_sound(
                    # time_offset=util.inverse_smooth(1 - (i - n_steps_small) / (n_steps - n_steps_small))
                    time_offset=(1 - (i - n_steps_small) / (n_steps - n_steps_small))
                )

            self.play(
                *[
                    FadeOut(circle)
                    for circle in circle_anims_from.circles[n_steps_small - 1 : -1]
                ],
                # FadeOut(circle_anims_from.label),
                circle_anims_from.circle.animate.scale_to_fit_height(
                    circle_anims_from.circles[n_steps_small - 1].height
                ),
                circle_anims_from.label.animate.become(label2),
            )

            self.wait()

            # Ztratí se všechny slupky, ukážeme je kolem složené (do vzdálenosti 10).
            self.play(
                *[
                    FadeOut(circle)
                    for circle in circle_anims_from.circles[:n_steps_small]
                ],
                FadeOut(circle_anims_from.label),
                FadeOut(circle_anims_from.circle),
            )
        
        self.wait()

        circle_anims_to = BFSCircleAnimations(
            cube_to.get_center(),
            n_steps_small,
            label_angle=(180 - 45) * DEGREES,
            base_radius=base_radius,
            radius_step=radius_step,
        )

        self.bfs_counter = 0

        for i, anims in enumerate(circle_anims_to):
            self.play_bfs_sound(animation_run_time=run_time)
            self.play(*anims, run_time=0.1)

        self.wait()

        self.play(*[FadeOut(circle) for circle in circle_anims_to.circles[:-1]])
        self.wait()

        circle_anims_from.circles[n_steps_small - 1].set_color(RED)

        new_label = MathTex(str(n_steps_small), color=RED)
        circle_anims_from.label.become(new_label)
        circle_anims_from.circle.become(circle_anims_from.circles[n_steps_small - 1])

        self.play(
            FadeIn(circle_anims_from.circles[n_steps_small - 1]),
            FadeIn(circle_anims_from.label),
        )
        self.wait()

        left_group = Group(
            circle_anims_from.circles[n_steps_small - 1],
            circle_anims_from.label,
            # new_label,
            cube_from,
        )
        right_group = Group(
            circle_anims_to.circles[n_steps_small - 1],
            circle_anims_to.label,
            cube_to,
        )

        circle_anims_from.label.clear_updaters()
        self.play(left_group.animate.shift(LEFT), right_group.animate.shift(RIGHT))
        self.wait()

        brace = Brace(
            Group(Dot(cube_from.get_center()), Dot(cube_to.get_center())),
            direction=UP,
            color=GRAY,
        ).shift(UP)
        brace_text = MathTex(">20", color=GRAY).next_to(brace, direction=UP)
        self.play(Create(brace), Create(brace_text))

        self.wait()


        self.play(
            FadeOut(circle_anims_from.circles[n_steps_small - 1]),
            FadeOut(circle_anims_from.label),
            FadeOut(circle_anims_to.circles[n_steps_small - 1]),
            FadeOut(circle_anims_to.label),
            FadeOut(brace),
            FadeOut(brace_text),
            cube_from.animate.shift(RIGHT),
            cube_to.animate.shift(LEFT),
        )
        self.wait()
        # self.play(*[FadeOut(mob) for mob in self.mobjects])


class CubeMITM(util.RubikScene):
    def construct(self):
        """
        Meet in the middle.

        Ok, why is this useful? Well, instead of starting on one side and trying
        to reach the other, we can actually search from both sides at once and
        stop once we meet in the middle. By that we mean searching until the two
        balls intersect for the first time. When that happens, there is a
        configuration for which we know the fastest way to reach it both from
        the scrambled cube and from the solved one. Then we simply connect these
        two partial paths to get the best solution.
        """
        base_radius = 0.9
        radius_step = 0.3
        n_steps = 9

        cube_distance = 2 * (base_radius + radius_step * (n_steps - 1))

        cube_from = RubiksCube(cubie_size=0.3, rotate_nicely=True).shift(
            LEFT * cube_distance / 2
        )
        cube_to = RubiksCube(cubie_size=0.3, rotate_nicely=True).shift(
            RIGHT * cube_distance / 2
        )
        util.scramble_to_feliks(cube_from)

        self.add(cube_from, cube_to)
        self.wait()

        circle_anims_from = BFSCircleAnimations(
            cube_from.get_center(),
            n_steps,
            label_angle=45 * DEGREES,
            base_radius=base_radius,
            radius_step=radius_step,
        )

        circle_anims_to = BFSCircleAnimations(
            cube_to.get_center(),
            n_steps,
            label_angle=(180 - 45) * DEGREES,
            base_radius=base_radius,
            radius_step=radius_step,
        )

        for anims_from, anims_to in zip(circle_anims_from, circle_anims_to):
            self.play_bfs_sound(animation_run_time=1 / 3)
            self.play(*anims_from, run_time=1 / 3)
            self.play_bfs_sound(animation_run_time=1 / 3)
            self.play(*anims_to, run_time=1 / 3)

        self.wait()

        ############ Generate the path ############

        points_from, path_anims_from = generate_path_animations(
            cube_from.get_center(), 0, base_radius, radius_step, n_steps
        )
        points_to, path_anims_to = generate_path_animations(
            cube_to.get_center(), PI, base_radius, radius_step, n_steps
        )

        for anims_from, anims_to in zip(path_anims_from, path_anims_to):
            self.play(*(anims_from + anims_to), run_time=1 / 3)
            self.add_sound(f"audio/click/click_{random.randint(0, 3)}.wav")

        self.add_sound("audio/polylog_success.wav", time_offset=0.5)

        self.wait()

        ############ Walk it ############
        # self.bring_to_front(cube_from)
        self.bring_to_back(*(circle_anims_from.circles + circle_anims_to.circles))

        points_both = points_from[1:-1] + points_to[::-1]

        self.play(
            cube_from.animate.move_to(points_from[0].get_center() + DOWN),
            FadeOut(cube_to),
        )

        for i, move in zip(range(len(points_both)), util.FELIKS_UNSCRAMBLE_MOVES):
            self.play_cube_sound()
            self.play(
                CubeMove(cube_from, move, points_both[i].get_center() + DOWN),
                run_time=1 / 3,
            )
            # if i == 4:
            #     break

        self.play(cube_from.animate.shift(ORIGIN), run_time=2)

        self.play(
            *[FadeOut(obj) for obj in self.mobjects]
        )

        return




class Discussion(util.RubikScene):
    def construct(self):
        self.next_section(skip_animations=False)
        font_size = 90
        our_algorithm = [
            Tex(r"Meet in the middle: ", color = GRAY, font_size = font_size),
            MathTex(r"2 \cdot 10\,000\,000\,000", color = GRAY, font_size = font_size),
        ]
        previous_algorithm = [
            Tex(r"Simple solution: ", color = GRAY, font_size = font_size),
            MathTex(r"100\,000\,000\,000\,000\,000\,000", color = GRAY, font_size = font_size),
        ]
        our_algorithm[0].move_to(2*LEFT + 2*UP)
        our_algorithm[1].move_to(our_algorithm[0].get_center()
        ).shift(4*RIGHT+DOWN)
        
        previous_algorithm[0].align_to(our_algorithm[0], LEFT
        ).shift(1.5*DOWN)
        previous_algorithm[1].align_to(our_algorithm[1], RIGHT
        ).shift(2.5*DOWN)

        self.play(
            Write(our_algorithm[0])
        )
        self.wait()

        self.play(
            Write(our_algorithm[1])
        )
        self.wait()

        self.play(
            Write(previous_algorithm[0])
        )
        self.wait()

        self.play(
            Write(previous_algorithm[1])
        )
        self.wait()

        self.play(
            Unwrite(our_algorithm[0]),
            Unwrite(our_algorithm[1]),
            Unwrite(previous_algorithm[0]),
            Unwrite(previous_algorithm[1]),
        )
        self.wait()







        magic = 0.5
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
        ).shift(magic*LEFT+RIGHT * 14.2 / 4),

        cube = RubiksCube(cubie_size=0.4).shift(magic*LEFT+RIGHT * 14.2 / 4)
        # cube.next_to(table_group, direction=UP)

        rubiks_group = Group(cube, table_group)
        rubiks_group.arrange(direction=DOWN, buff=MED_LARGE_BUFF).shift(magic*LEFT+RIGHT * 14.2 / 4)

        # right column
        right_col = [
            MathTex(
                (r"\sim 10^" if i != 0 else r"= 10^") + str(i),
                color = GRAY,
                font_size = font_size
            ).move_to(
                table[i+1][1].get_left()
                + 2.2*RIGHT
            )
            for i in range(6)
        ]

        # self.play(
        #     *[Write(col) for col in right_col],
        #     table[-1][1].animate.align_to(right_col[0], LEFT)
        # )
        # self.wait()
        dots[0].move_to(
            (
                table[-3][0].get_center()
                + table[-1][0].get_center()
            )/2
        )

        self.play(
            LaggedStart(
                Succession(
                    FadeIn(cube),
                    Rotate(cube, 2 * PI, UP)
                ),
                AnimationGroup(
                    Write(table[0][0]),
                    Write(table[0][1])
                ),
                *[AnimationGroup(
                    *[Write(cell) for cell in row],
                    Write(right)
                ) for row, right in zip(table[1:7], right_col)],
                Write(dots[0]),
                AnimationGroup(
                    Write(table[-1][0]),
                    Write(table[-1][1].align_to(right_col[0], LEFT))
                ),
                lag_ratio=0.25,
            ),
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

        magic = 0.5
        self.play(
            background_rect.animate.move_to(
                # background_rect.get_boundary_point(direction=RIGHT) * RIGHT
                14.2
                / 4
                * LEFT
            ),
            run_time=2,
        )

        self.wait()









        #grid graph

        grid_size = 11
        grid_center = grid_size // 2
        grid_spacing = 0.3 #0.35

        vertices = set((i, j) for i in range(grid_size) for j in range(grid_size))
        distances = {}
        edges = []
        layout = {}
        left_side = [[] for x in range(grid_size)]
        right_side = [[] for x in range(grid_size)]

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
        graph.move_to(LEFT * 14.2 / 4)#.align_to(rubiks_group, UP)
        self.play(DrawBorderThenFill(graph, run_time=1))
        self.wait()

        for i in range(grid_size):
            for j in range(grid_size):
                left_distance = i+j
                right_distance = -i-j+2*(grid_size - 1)
                if left_distance <= right_distance:
                    left_side[left_distance].append(
                        graph.vertices[(i, j)].animate.set_color(RED)
                    )
                if left_distance >= right_distance:
                    right_side[right_distance].append(
                        graph.vertices[(i, j)].animate.set_color(RED)
                    )

        for (i1,j1), (i2,j2) in edges:
            left1 = i1+j1
            left2 = i2+j2
            right1 = -i1-j1+2*(grid_size - 1)
            right2 = -i2-j2+2*(grid_size - 1)

            if left1 > left2:
                left1, left2 = left2, left1
                right1, right2 = right2, right1

            if left1 < right1:
                left_side[left1+1].append(
                    graph.edges[((i1, j1), (i2,j2))].animate.set_color(RED)
                )
            if right1 <= left1:
                right_side[right1].append(
                    graph.edges[((i1, j1), (i2,j2))].animate.set_color(RED)
                )

        # for i in range(grid_size):
        #     for j in range(grid_size):
        #         if distances[(i, j)] <= dist:
        #             anims[distances[(i, j)]].append(
        #                 graph.vertices[(i, j)].animate.set_color(RED)
        #             )

        #         for cur in [(i + 1, j), (i, j + 1)]:
        #             if cur in vertices:
        #                 edge_distance = min(distances[(i, j)], distances[cur])
        #                 if edge_distance < dist:
        #                     # We don't know the direction of the edge.
        #                     edge = graph.edges[(((i, j), cur))]
        #                     anims[edge_distance + 1].append(edge.animate.set_color(RED))

        anims = list(itertools.chain(*zip(left_side, right_side)))

        #bigger dots for starts
        start_dots = [
            Dot(color = RED).scale(2).move_to(graph.vertices[(0,0)].get_center()),
            Dot(color = RED).scale(2).move_to(graph.vertices[(grid_size-1,grid_size-1)].get_center()),
        ]
        start_dots[0].set_z_index(100)
        start_dots[1].set_z_index(100)

        self.play(
            Create(start_dots[0]),
            Create(start_dots[1])
        )
        self.wait()

        # add sounds
        run_time = 0.25
        lag_ratio = 1
        for it in range(2, len(anims)):
            # offset = run_time * lag_ratio * (it + 0.0)
            self.add_sound(f"audio/bfs/bfs_{it:03d}", time_offset=0)
            self.play(
               *anims[it],
                run_time = 0.3
            )

        self.wait(2)

        self.play(
            FadeOut(background_rect),
            *[Unwrite(dot) for dot in start_dots],
            Unwrite(dots[0]),
            *[Unwrite(col) for col in right_col],
            *[Unwrite(t) for t in table_group[0:14]],
            *[Unwrite(t) for t in table_group[16:]],
            FadeOut(cube),
            Uncreate(graph),
        )