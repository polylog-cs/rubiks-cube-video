from manim import *
from manim.utils import tex
import numpy as np
import math
import textwrap
import random

from solarized import *
# Temne pozadi
config.background_color = BASE02

textColor = GRAY
encodeColor = RED
decodeColor = BLUE

class DesIntro(Scene):
	def construct(self):
		# TODO: na začátku napsat "DES" a "Data Encryption Standard"

		plain = Tex(r"polylog is great", color = textColor)
		cipher= Tex("101...01", color = textColor)
		encryptArrow = Arrow(start = LEFT, end = RIGHT, color = encodeColor)
		encryptKey = ImageMobject("img/key.png")
		encryptKey.width = encryptArrow.width*0.7
		encryptArrowKey = Group(encryptArrow, encryptKey).arrange(UP)
		encryptKey.shift(0.2*UP)

		plain.move_to(encryptArrow.center())
		plain.shift(3*LEFT)
		cipher.move_to(encryptArrow.center())
		cipher.shift(2*RIGHT)

		'''
		decryptArrow = Arrow(start = RIGHT, end = LEFT, color = decodeColor)
		decryptKey = ImageMobject("img/key.png")
		decryptKey.width = decryptArrow.width*0.7
		decryptArrowKey = Group(decryptArrow, decryptKey).arrange(UP)
		decryptArrowKey.shift(2*DOWN)
		decryptKey.shift(0.2*UP)
		'''

		
		self.play(Write(plain), Write(cipher), FadeIn(encryptArrowKey))
		self.wait()
		# self.play(FadeIn(decryptArrowKey))



def constructKeyPolygon(granularity = 100, scale = 1.0/200, shift = np.array([0, 0, 0])):
		key = [
		np.array([262.968, 373.851, 0]),
		np.array([285.022, 362.026, 0]),
		np.array([301.516, 361.804, 0]),
		np.array([301.806, 396.862, 0]),
		np.array([336.07, 396.501, 0]),
		np.array([358.072, 375.943, 0]),
		np.array([385.122, 404.436, 0]),
		np.array([408.927, 381.353, 0]),
		np.array([430.928, 381.353, 0]),
		np.array([457.979, 406.961, 0]),
		np.array([476.374, 390.009, 0]),
		np.array([500.539, 390.37, 0]),
		np.array([544.542, 432.569, 0]),
		np.array([538.771, 446.275, 0]),
		np.array([528.311, 453.488, 0]),
		np.array([510.277, 461.784, 0]),
		np.array([302.167, 461.062, 0]),
		np.array([301.806, 494.245, 0]),
		np.array([285.215, 494.245, 0]),
		np.array([260.219, 474.218, 0])]


		offset = key[0].copy()
		mid = np.array([164.406, 421.883, 0])
		
		midx = mid[0]
		midy = mid[1]
		fstx = key[len(key)-1][0]
		fsty = key[len(key)-1][1]
		lastx = key[0][0]
		lasty = key[0][1]

		fstangle = math.atan((fsty - midy) / (fstx - midx))
		lastangle = math.atan((lasty - midy) / (lastx - midx))
		piangle = 3.141592654

		print(fstangle)
		print(lastangle)

		r = math.sqrt((midx-fstx)*(midx-fstx) + (midy-fsty)*(midy-fsty))
		
		for i in range(granularity):
			angle = piangle * i / granularity + fstangle * (granularity - i) / granularity 
			vec = np.array([math.cos(angle), math.sin(angle), 0])
			key.append(mid + r * vec)	
		for i in range(granularity):
			angle = lastangle * i / granularity - piangle * (granularity - i) / granularity 
			vec = np.array([math.cos(angle), math.sin(angle), 0])
			key.append(mid + r * vec)	

		for pnt in key:
			pnt -= offset
			pnt *= scale
			pnt += shift 

		key.reverse()

		return key


class Key(Scene):
	def construct(self):



		keyCenter = np.array([0, 0, 0])
		key = constructKeyPolygon(shift = keyCenter)
		T1 = Polygon(*key)

		recWidth = 3.0
		recHeight = 2.0
		rec = [np.array([-recWidth/2, recHeight/2, 0]), 
				np.array([recWidth/2, recHeight/2, 0]), 
				np.array([recWidth/2, -recHeight/2, 0]), 
				np.array([-recWidth/2, -recHeight/2, 0])]
		rec = rec[1:] + rec[:1]
		rec = rec[1:] + rec[:1]
		#rec = rec[1:] + rec[:1]

		T2 = Polygon(*rec)

		self.play(Create(T1))
		self.play(Transform(T1, T2), run_time = 2)

		txt = Tex("101...01", color = textColor)
		txt.move_to(T2.center())

		brace = Brace(txt, UP)
		

		title = Tex("56 bits", color = textColor)
		title.move_to(T2.center())
		title.shift(1 * UP)

		recInside = Group(txt, brace, title)
		recInside.shift(3 * RIGHT)

		self.play(Write(txt), Create(brace), Write(title))

		self.wait(10)

class DesBruteForce(Scene):
	def construct(self):
		"""
		TODO: Animace, kde je vstupní text (něco vtipného), pak šipky nad
		kterými jsou klíče a jde to do cipher textů. Klíč je buď klipart nebo
		občas string bitů. Napravo je cipher text a checkujeme (posouváme ho?)
		zda matchuje naše ciphertexty
		"""
		pass

class TripleDes(Scene):
	def construct(self):
		"""
		TODO: animace k tomuhle:
		To fix this issue, people came up with a new cipher known as Triple DES,
		which is just the old DES but applied three times in a row with three
		different keys of combined length of 3*56 = 168 bits. But you may ask,
		why Triple DES and not just Double DES where you would apply the
		encryption function two times, each time with a different key. The
		combined length of the two keys would be 2*56 = 112 which is definitely
		enough so that bruteforce is not a possibility, because 2^56 is 10^30,
		which is just way too much. 
		"""
		pass

class DesMITM(Scene):
	def construct(self):
		"""
		TODO: Meet in the middle na double DES. Podobná animace jako pro brute force,
		ale “osově symetrická” - pozor, abychom konzistentně používali šifrovací
		a dešifrovací styl šipky
		"""
		pass

class GeneralMITM(Scene):
	def construct(self):
		"""
		TODO: Srovnání MITM na kostce a na DES. Co je společného. Nalevo kostka,
		napravo nějak vizualizovaný DES. Pak v "tabulce" ukázat čísla
		srovnávající runtime bruteforcu vs MITM.

		Pak ukázat i použité množství paměti, aby byl vidět tradeoff.

		Nakonec někde ukázat zobecnění, že potřebujeme sice jen sqrt(n) času,
		ale zato sqrt(n) paměti místo O(1).
		"""
		pass