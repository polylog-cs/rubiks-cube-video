from manim import *
from manim.utils import tex
import numpy as np
import math
import textwrap
import random

from solarized import *
# Temne pozadi

config.background_color = BASE02

keyColor = GRAY
textColor = GRAY
encodeColor = RED
decodeColor = BLUE

class DesIntro(Scene):
	def construct(self):
		# TODO: na začátku napsat "DES" a "Data Encryption Standard"


		#plain text

		plainText = Tex(r"funny text", color = textColor)
		plainText.shift(3*LEFT)
		self.play(Write(plainText))


		padding = 0.5
		plainBorder = Rectangle(width = plainText.get_right()[0] - plainText.get_left()[0] + padding, 
			height = plainText.get_top()[1] - plainText.get_bottom()[1] + padding)
		plainBorder.move_to(plainText.get_center())

		plainGroup = Group(plainText, plainBorder)

		self.play(Create(plainBorder))

		#encrypt arrow

		arrowlen = 3
		startArrow = plainBorder.get_right() + padding * RIGHT
		endArrow = startArrow + arrowlen * RIGHT
		enArrow = Arrow(start = startArrow, end = endArrow, color = encodeColor)

		enKey, enKeyLine, enKeyCirc = constructKey(shift = enArrow.get_center() + UP, width = enArrow.get_width())

		#enKeyGroup = Group(enArrow, enKey, enKeyLine, enKeyCirc)

		self.play(Create(enArrow), 
			Create(enKey), 
			Create(enKeyLine), 
			Create(enKeyCirc))



		# cipher text

		cipherText = Tex("101011101...01", color = textColor)
		cipherText.next_to(enArrow, RIGHT)
		cipherText.shift(padding * RIGHT)

		self.play(Create(cipherText))

		cipherBorder = Rectangle(width = cipherText.get_right()[0] - cipherText.get_left()[0] + padding, 
			height = cipherText.get_top()[1] - cipherText.get_bottom()[1] + padding)
		cipherBorder.move_to(cipherText.get_center())

		self.play(Create(cipherBorder))


		# animate key

		keyInfoWidth = 3.0
		keyInfoHeight = 2.0
		rec = [np.array([-keyInfoWidth/2, keyInfoHeight/2, 0]), 
				np.array([-keyInfoWidth/2, -keyInfoHeight/2, 0]), 
				np.array([keyInfoWidth/2, -keyInfoHeight/2, 0]), 
				np.array([keyInfoWidth/2, keyInfoHeight/2, 0])]
		rec = rec[1:] + rec[:1]
		rec = rec[1:] + rec[:1]
		#rec = rec[1:] + rec[:1]

		enKeyInfo = Polygon(*rec)
		enKeyInfo.move_to(enArrow.get_center())
		enKeyInfo.next_to(enArrow, UP)
		enKeyInfo.shift(padding * UP)

		self.play(Uncreate(enKeyLine),
			Uncreate(enKeyCirc))
		self.play(Transform(enKey, enKeyInfo), run_time = 2)

		ourKeyString = "10111...01"
		txt = Tex(ourKeyString, color = textColor)
		brace = Brace(txt, UP)
		title = Tex("56 bits", color = textColor)
		
		recInside = Group(txt, brace, title).arrange(UP)
		recInside.move_to(enKeyInfo.get_center())

		self.play(Write(txt), Create(brace), Write(title))

		self.wait()

		self.play(Uncreate(txt),
			Uncreate(brace),
			Uncreate(title))

		enKeyNew, enKeyLine, enKeyCirc = constructKey(shift = enArrow.get_center() + UP, width = enArrow.get_width())		

		self.play(Transform(enKey, enKeyNew))
		self.play(Create(enKeyLine),
			Create(enKeyCirc))

		self.wait()

		self.play(FadeOut(enArrow),
		FadeOut(enKey),
		FadeOut(enKeyLine),
		FadeOut(enKeyCirc),
		FadeOut(plainGroup))

		# decrypt arrow 
		decArrow = Arrow(start = endArrow, end = startArrow, color = decodeColor)

		decKey, decKeyLine, decKeyCirc = constructKey(shift = decArrow.get_center() + UP, width = decArrow.get_width())		

		self.play(Create(decArrow), 
			Create(decKey), 
			Create(decKeyLine), 
			Create(decKeyCirc))


		# decrypted message

		self.play(Write(plainText), Create(plainBorder))

		# explode key

		ourKey = Tex(ourKeyString, color = textColor)
		ourKey.move_to(decKey.get_center())

		keyBorder = Rectangle(width = ourKey.get_right()[0] - ourKey.get_left()[0] + padding, 
			height = ourKey.get_top()[1] - ourKey.get_bottom()[1] + padding, 
			color = keyColor)
		keyBorder.move_to(ourKey.get_center())

		self.play(FadeOut(decKeyLine),
			FadeOut(decKeyCirc))
		self.play(Transform(decKey, keyBorder))
		self.play(Write(ourKey))


		# try different key

		randKeyString = "10101...11"
		randKey = Tex(randKeyString, color = textColor).move_to(ourKey.get_center())
		randPlainText = Tex("dkDm2,Lkp", color = textColor).move_to(plainText.get_center())

		randKeyString2 = "11001...10"
		randKey2 = Tex(randKeyString2, color = textColor).move_to(ourKey.get_center())
		randPlainText2 = Tex("Dy.dOnj:kp", color = textColor).move_to(plainText.get_center())


		self.play(FadeOut(ourKey), FadeOut(plainText))
		self.play(FadeIn(randKey), FadeIn(randPlainText))

		self.play(FadeOut(randKey), FadeOut(randPlainText))
		self.play(FadeIn(randKey2), FadeIn(randPlainText2))

		self.play(FadeOut(randKey2), FadeOut(randPlainText2))
		self.play(FadeIn(ourKey), FadeIn(plainText))



		self.wait(3)
		

def constructKey(shift = np.array([0, 0, 0]), granularity = 100, width = 1):
		
		#right part of the key
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
		
		# adding the circly left part

		midx = mid[0]
		midy = mid[1]
		fstx = key[len(key)-1][0]
		fsty = key[len(key)-1][1]
		lastx = key[0][0]
		lasty = key[0][1]

		fstangle = math.atan((fsty - midy) / (fstx - midx))
		lastangle = math.atan((lasty - midy) / (lastx - midx))
		piangle = 3.141592654

		r = math.sqrt((midx-fstx)*(midx-fstx) + (midy-fsty)*(midy-fsty))
		
		for i in range(granularity):
			angle = piangle * i / granularity + fstangle * (granularity - i) / granularity 
			vec = np.array([math.cos(angle), math.sin(angle), 0])
			key.append(mid + r * vec)	
		for i in range(granularity):
			angle = lastangle * i / granularity - piangle * (granularity - i) / granularity 
			vec = np.array([math.cos(angle), math.sin(angle), 0])
			key.append(mid + r * vec)	
		#key.reverse() 


		# compute offsets

		left = min([pnt[0] for pnt in key])
		right = max([pnt[0] for pnt in key])
		top = max([pnt[1] for pnt in key])
		bottom = min([pnt[1] for pnt in key])
		
		keyWidth = right - left
		offset = np.array([(left + right)/2, (top + bottom)/2, 0])
		
		# line in the key

		keyline = [
		np.array([539.002, 427.256, 0]),
		np.array([253.473, 425.757, 0]),
		np.array([286.295, 412.773, 0]),
		np.array([525.775, 414.571, 0])]


		# middle circle
		midcirc = np.array([109.552, 425.451, 0])
		radcirc = 25.2117 * width / keyWidth


		for pnt in key + keyline + [midcirc]:
			pnt -= offset
			pnt *= width / keyWidth
			pnt += shift 
		
		return Polygon(*key, fill_opacity = 1, color = keyColor), Polygon(*keyline, color = "red"), Circle(radius = radcirc, color = "red").move_to(midcirc)


class Key(Scene):
	def construct(self):



		keyCenter = np.array([0, 0, 0])
		T1 = constructKey(shift = keyCenter)

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
		recInside.shift(0.4 * DOWN)

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