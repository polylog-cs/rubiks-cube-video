import random
from manim import *

# Use our fork of manim_rubikscube!
from manim_rubikscube import *

# This also replaces the default colors
from solarized import *

import util

cube.DEFAULT_CUBE_COLORS = [BASE3, RED, GREEN, YELLOW, ORANGE, BLUE]


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
            self.add_sound(f"audio/click/click_{random.randint(0, 4)}.wav")

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
