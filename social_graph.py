from manim import *
#from solarized import *
import numpy as np
import math
import random

textColor = "white"
encodeColor = "red"
decodeColor = "blue"
keyColor = "blue"


class GraphScene(Scene):
	def construct(self):

		print(random.uniform(0, 1))

		N = 100
		M = 100
		G = {}
		vertices = []
		edges = []
		positions = {}

		box = {"corner": 6 * LEFT + 4 * UP, "width": 12 * RIGHT, "height": 8 * DOWN}

		for i in range(N):
			G[i] = []
			vertices.append(i)
			positions[i] = np.array([0.0, 0.0, 0.0])
		for i in range(M):
			u = random.randrange(0, N-1)
			v = random.randrange(0, N-1)
			if u != v:
				G[u].append(v)
				G[v].append(u)
				edges.append((u,v))
		
		for u in range(N):
			if len(G[u]) == 0:
				v = random.randrange(0, N-1)
				if v != u:
					G[u].append(v)
					G[v].append(u)
					edges.append((u,v))
		
		#odstanit kolize vrcholu
		eps = 0.6
		bad = vertices.copy()
		while len(bad) != 0:
			i = bad.pop(-1)
			#print(i)
			positions[i] = box["corner"] + random.uniform(0, 1) * box["width"] + random.uniform(0, 1) * box["height"]
			for j in range(N):
				if j != i and math.dist(positions[i], positions[j]) < eps:
					bad.append(j)


		#print(G)
		#print(vertices)
		#print(edges)
		#print(positions)

		Ganim = Graph(
			vertices,
			edges, 
			layout = positions		
		)

		self.add(Ganim)
		faces = []
		for i in range(N):
			icon = ImageMobject("img/icon.png")
			icon.height = 0.3
			icon.move_to(positions[i])
			faces.append(icon)
		self.add(*faces)