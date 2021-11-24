import string
from manim import *
from manim.utils import tex
import numpy as np
import math
import textwrap
import random
from solarized import *
# Temne pozadi
config.background_color = BASE02

random.seed(0)

keyColor = GRAY
keyColor2= BASE1
textColor = GRAY
encodeColor = RED
decodeColor = BLUE
borderColor = GRAY
smallFontSize = 20
fontSize = 40 # TODO zmenit na vychozi velikost (jak se zjisti?)
padding = 0.5 # between the text and the border around it


def constructRandomString(lineLen = 8, numLines = 6):
	letters = string.ascii_letters + string.digits
	strList = []
	for j in range(numLines):
		str = r""
		for k in range(lineLen):
			str += random.choice(letters)
		strList.append(str)
	strList[-1] = strList[-1][:-3] + "..."
	return strList

strPlainText = [
	r"funny text",
	r"shorter t",
	r"funny text",
	r"funny text",
	r"funny text",
	r"funny text"
]
strCipherText = constructRandomString()


#first diagram constants
midDiagramPos = 0*UP
topDiagramPos = 1*UP
bottomDiagramPos = 2*DOWN
diagramWidth = 5*RIGHT
arrowLen = 3
keyWidthLarge = 2.5
keyWidth = 1.5
keyPadding = 0.8
textPadding = 0.1
keyInfoWidth = 3.0
keyInfoHeight = 2.0
leftTextPos = 5.5 * LEFT
minTime = 0.3

zeroString = "000...00000"
ourKeyString = "101...01110"
randKeyString = "001...10011"
unknownKeyString = "???...?????"

class DesIntro(Scene):
	def construct(self):
		# spouštět to se světlým, ne tmavým pozadím
		'''
		The meet in the middle trick is very useful in solving other problems, so let me quickly mention a different one which does not include any networks. 

		In 1970’s people created a cipher known as DES. DES means Data Encryption Standard - it was the standard cipher that everybody was using. It works as follows. 
		You give DES some text and there is a secret key that only you know. This secret key is just a short string of 56 bits. 
		The DES cipher, like other symmetric ciphers, consists of two functions. The encrypting function takes as input the text and the key and computes the enCipherText.
		The decrypting function takes as input the enCipherText and the key, and it gives you back the original text. 

		[Animace: Smysluplný enPlainText - červená šipka, nad ní klíč (číslo?) - enCipherText.
		pod tím: enCipherText - modrá šipka, nad ní klíč - stejný enPlainText, plain text i enCipherText jsou stringy charů ne bitů]
		'''
		
		
		# DES -> Data Encryption Standard
		DesTextPosition = 3*UP
		DesText = Tex(r"DES", color = textColor)
		DesText.move_to(DesTextPosition)
		DesTextLong = Tex(r"Data Encryption Standard", color = textColor)
		DesTextLong.move_to(DesTextPosition)

		self.play(Write(DesText))
		self.play(Transform(DesText, DesTextLong)) #TODO: vyhezkat, aby se písmenka DES jen posunula
		#self.wait()



		# first key occurence
		enKey, enKeyLine, enKeyCirc = constructKey(
			position = midDiagramPos,
			width = keyWidthLarge
		)

		self.play(
			Create(enKey), 
			Create(enKeyLine), 
			Create(enKeyCirc))
		self.wait()

		rec = [np.array([-keyInfoWidth/2, keyInfoHeight/2, 0]), 
				np.array([-keyInfoWidth/2, -keyInfoHeight/2, 0]), 
				np.array([keyInfoWidth/2, -keyInfoHeight/2, 0]), 
				np.array([keyInfoWidth/2, keyInfoHeight/2, 0])]
		rec = rec[1:] + rec[:1]
		rec = rec[1:] + rec[:1]
		
		enKeyInfo = Polygon(*rec, color = borderColor)
		enKeyInfo.move_to(enKey.get_center())

		self.play(Uncreate(enKeyLine),
			Uncreate(enKeyCirc))
		self.play(Transform(enKey, enKeyInfo), run_time = 2)

		
		txt = Tex(ourKeyString, color = textColor)
		brace = Brace(txt, UP, color = textColor)
		title = Tex("56 bits", color = textColor)
		
		recInside = Group(txt, brace, title).arrange(UP)
		recInside.move_to(enKeyInfo.get_center())

		self.play(Write(txt), Create(brace), Write(title))
		self.wait()

		self.play(Uncreate(txt),
			Uncreate(brace),
			Uncreate(title))

		enKeyNew, enKeyLine, enKeyCirc =  constructKey(
			position = topDiagramPos + 1*UP,
			width = keyWidthLarge
		)	

		self.play(Transform(enKey, enKeyNew))
		self.play(Create(enKeyLine),
			Create(enKeyCirc))

		self.wait()

		'''		
		self.play(FadeOut(enArrow),
		FadeOut(enKey),
		FadeOut(enKeyLine),
		FadeOut(enKeyCirc),
		FadeOut(plainGroup))
		'''
		

		#encryption

		enDescription = Tex(
			"Encryption:", 
			color = textColor, 
			font_size = fontSize
		).move_to(midDiagramPos + leftTextPos)
		self.play(Write(enDescription))
		self.wait()

		#plain text
		enPlainText = Group(*[
			Tex(str, color = textColor, font_size = smallFontSize) for str in strPlainText
		]).arrange(DOWN, center = False, aligned_edge = LEFT, buff = textPadding)
		enPlainBorder = constructTextBorder(insideObject = enPlainText)
		plainGroup = Group(enPlainText, enPlainBorder)
		plainGroup.move_to(midDiagramPos - diagramWidth/2)
		self.play(*[Write(text) for text in enPlainText], Create(enPlainBorder))
		self.wait()

		#key moves
		enKeyNew, enKeyLineNew, enKeyCircNew =  constructKey(
			position = midDiagramPos + keyPadding*UP,
			width = keyWidth
		)	
		self.play(
			Transform(enKey, enKeyNew), 
			Transform(enKeyLine, enKeyLineNew), 
			Transform(enKeyCirc, enKeyCircNew)
		)
		self.wait()

		#encrypt arrow
		startArrow = arrowLen * LEFT / 2 + midDiagramPos + keyPadding/3*DOWN
		endArrow = arrowLen * RIGHT / 2 + midDiagramPos + keyPadding/3*DOWN
		enArrow = Arrow(start = startArrow, end = endArrow, color = encodeColor)

		self.play(Create(enArrow))
		self.wait()

		

		# cipher text
		enCipherText = Group(*[
			Tex(str, color = textColor, font_size = smallFontSize) for str in strCipherText
		]).arrange(DOWN, center = False, aligned_edge = LEFT, buff = textPadding)
		enCipherText.next_to(enArrow, RIGHT)
		enCipherText.shift(padding * RIGHT + keyPadding/3*UP)
		enCipherBorder = constructTextBorder(
			insideObject = enCipherText, 
			width = enPlainBorder.get_right()[0] - enPlainBorder.get_left()[0], 
			height = enPlainBorder.get_top()[1] - enPlainBorder.get_bottom()[1]
		)
		cipherGroup = Group(enCipherText, enCipherBorder)
		self.play(*[Write(text) for text in enCipherText], Create(enCipherBorder))

		# slide up
		encryptionDiagram = Group(
			enKey, enKeyCirc, enKeyLine, enArrow, 
			enDescription, 
			enPlainText, enPlainBorder, 
			enCipherText, enCipherBorder
		)
		encryptionDiagram.generate_target()
		encryptionDiagram.target.shift(topDiagramPos - midDiagramPos)
		
		self.play(
			MoveToTarget(encryptionDiagram)
		)
		self.wait()


		# copy to decrypt 

		decDescription = Tex(
			"Decryption:", 
			color = textColor, 
			font_size = fontSize
		).move_to(bottomDiagramPos + leftTextPos)
		self.play(
			Create(decDescription)
		)
		self.wait()

		decCipher = Group(enCipherText, enCipherBorder).copy()
		self.add(decCipher)
		decCipher.generate_target()
		decCipher.target.shift(bottomDiagramPos - topDiagramPos)
		self.play(
			MoveToTarget(decCipher)
		)
		self.wait()

		decKey, decKeyCirc, decKeyLine = enKey.copy(), enKeyCirc.copy(), enKeyLine.copy()
		decKeyGroup = Group(decKey, decKeyCirc, decKeyLine)
		self.add(decKeyGroup)
		decKeyGroup.generate_target()
		decKeyGroup.target.shift(bottomDiagramPos - topDiagramPos)
		self.play(
			MoveToTarget(decKeyGroup)
		)
		self.wait()

		
		# decrypt arrow + copy plain text
		startArrow = arrowLen * LEFT / 2 + bottomDiagramPos + keyPadding/3*DOWN
		endArrow = arrowLen * RIGHT / 2 + bottomDiagramPos + keyPadding/3*DOWN
		decArrow = Arrow(
			start = endArrow, 
			end = startArrow, 
			color = decodeColor
		)

		self.play(Create(decArrow))
		self.wait()

		decPlainText, decPlainBorder = enPlainText.copy(), enPlainBorder.copy()
		decPlain = Group(decPlainText, decPlainBorder)
		self.add(decPlain)
		decPlain.generate_target()
		decPlain.target.shift(bottomDiagramPos - topDiagramPos)
		self.play(
			MoveToTarget(decPlain)
		)
		self.wait()


		
		# explode keys
		enOurKey = Tex(ourKeyString, color = textColor)
		enOurKey.move_to(enKey.get_center())
		decOurKey = enOurKey.copy().move_to(decKey.get_center())

		enKeyBorder = Rectangle(
			width = enOurKey.get_right()[0] - enOurKey.get_left()[0] + padding, 
			height = enOurKey.get_top()[1] - enOurKey.get_bottom()[1] + padding, 
			color = keyColor)
		enKeyBorder.move_to(enOurKey.get_center())
		decKeyBorder = enKeyBorder.copy().move_to(decOurKey.get_center())

		self.play(
			FadeOut(decKeyLine),
			FadeOut(decKeyCirc), 
			Transform(decKey, decKeyBorder),
			FadeOut(enKeyLine),
			FadeOut(enKeyCirc), 
			Transform(enKey, enKeyBorder)
		)
		self.play(
			Write(enOurKey),
			Write(decOurKey)
		)
		self.wait()


		# try different key

		
		randKey = Tex(randKeyString, color = textColor).move_to(decOurKey.get_center())
		randdecPlainText = Group(*[
			Tex(str, color = textColor, font_size = smallFontSize) for str in constructRandomString()
		]).arrange(
			DOWN, 
			center = False, 
			aligned_edge = LEFT, 
			buff = textPadding
		).move_to(
			decPlainText.get_center()
		)

		self.play(FadeOut(decOurKey), FadeOut(decPlainText))
		self.play(FadeIn(randKey), FadeIn(randdecPlainText))

		self.wait()

		self.play(FadeOut(randKey), FadeOut(randdecPlainText))
		self.play(FadeIn(decOurKey), FadeIn(decPlainText))

		# bring everything to forward and slide rectangle behind it

		everything = Group(
			DesText,
			enKey, enPlainText, enPlainBorder, enArrow, enCipherText, enCipherBorder, enDescription, enOurKey,
			decOurKey, decArrow, decPlain, decCipher, decDescription, decKey, decPlainText, decPlainBorder
		)

		#everything.z_index = 1

		for obj in everything:
			obj.z_index = 1

		#BACK = np.array([0, 0, -1.0]) 
		# TODO udělat to tak, aby to běželo vzadu ne vepředu

		backgroundRect = Rectangle(
			height = 8+0.5,
			width = 14+0.5,
			fill_opacity = 1,
			fill_color = BASE02,
			color = BASE02
		)
		backgroundRect.z_index = 0
		backgroundRect.move_to(
			(14+0.6)*LEFT
		)
		self.add(backgroundRect)
		backgroundRect.generate_target()
		backgroundRect.target.move_to(0*LEFT)
		self.play(
			MoveToTarget(backgroundRect),
			run_time = 3	
		)
		
		self.play(
			MoveToTarget(backgroundRect),
			*[FadeOut(obj) for obj in everything],
			run_time = 1	
		)
		
		'''for obj in everything: 
			obj.z_index = 1
		backgroundRect.z_index = 0
		self.wait(3)
		'''


		
class DesBruteForce(Scene):
	def construct(self):
		"""
		TODO: Animace, kde je vstupní text (něco vtipného), pak šipky nad
		kterými jsou klíče a jde to do cipher textů. Klíč je buď klipart nebo
		občas string bitů. Napravo je cipher text a checkujeme (posouváme ho?)
		zda matchuje naše CipherTexty
		"""

		# create plain and cipher text

		plainText = Group(*[
			Tex(str, color = textColor, font_size = smallFontSize) for str in strPlainText
		]).arrange(DOWN, center = False, aligned_edge = LEFT, buff = textPadding)
		plainBorder = constructTextBorder(
			insideObject = plainText,
			color = BASE0
		)
		plainGroup = Group(plainText, plainBorder)

		plainGroup.move_to(midDiagramPos - diagramWidth/2)
		self.play(*[Write(text) for text in plainText], Create(plainBorder))
		self.wait()


		cipherText = Group(*[
			Tex(str, color = textColor, font_size = smallFontSize) for str in strCipherText
		]).arrange(DOWN, center = False, aligned_edge = LEFT, buff = textPadding)
		cipherBorder = constructTextBorder(
			insideObject = cipherText,
			width = plainBorder.get_right()[0] - plainBorder.get_left()[0], 
			height = plainBorder.get_top()[1] - plainBorder.get_bottom()[1],
			color = BASE0
		)
		cipherGroup = Group(cipherText, cipherBorder)

		cipherGroup.move_to(midDiagramPos + diagramWidth/2)
		self.play(*[Write(text) for text in cipherText], Create(cipherBorder))
		self.wait()

		
		# create the key
		
		keyText = Tex(unknownKeyString, color = textColor)
		brace = Brace(keyText, UP, color = textColor)
		title = Tex("56 bits", color = textColor)
		braceTitle = Group(brace, title).arrange(UP)

		#TODO: udělat takle klíč i v předchozí animaci
		keyBorder = Rectangle(
			width = keyText.get_right()[0] - keyText.get_left()[0] + padding, 
			height = keyText.get_top()[1] - keyText.get_bottom()[1] + padding, 
			color = keyColor)
		keyBorder.move_to(keyText.get_center())
		
		braceTitle.shift(
			keyBorder.get_top() + padding * UP + (braceTitle.get_top() - braceTitle.get_center())/2
		)

		Key = Group(keyText, keyBorder, braceTitle)

		Key.move_to(
			keyPadding * UP
		)

		self.play(
			Write(keyText),
			Create(keyBorder),
			Create(brace),
			Write(title)
		)
		self.wait()


	
		#encrypt arrow
		'''startArrow = arrowLen * LEFT / 2 + midDiagramPos + keyPadding/3*DOWN
		endArrow = arrowLen * RIGHT / 2 + midDiagramPos + keyPadding/3*DOWN
		enArrow = Arrow(start = startArrow, end = endArrow, color = encodeColor)

		self.play(Create(enArrow))
		self.wait()'''

		# split

		plainGroup.generate_target()
		plainGroup.target.shift(diagramWidth/3 * LEFT)
		cipherGroup.generate_target()
		cipherGroup.target.shift(diagramWidth/3 * RIGHT)

		self.play(
			MoveToTarget(plainGroup),
			MoveToTarget(cipherGroup),
			FadeOut(Key)
		)

		self.wait()

		keyBorder.shift(diagramWidth/3 * LEFT)

		
		keyText = Tex(
			zeroString, 
			color = textColor
		).move_to(keyBorder.get_center())

		guessText = cipherText.copy() # jak se mění text aniž bych vytvářel nový objekt?
		guessBorder = cipherBorder.copy()
		guessGroup = Group(guessText, guessBorder)

		guessGroup.move_to(midDiagramPos + diagramWidth/5)
		self.play(
			*[Write(text) for text in guessText], 
			Create(guessBorder),
			FadeIn(keyText),
			FadeIn(keyBorder)
		)
		self.wait()

		waitingTimes = []
		L = 1
		for i in range(L):
			waitingTimes.append(
				max(1 - i * 1.0 / L, minTime)
			)
		
		cnt = 0
		for t in waitingTimes:
			cnt += 1
			actString = "000..." + '{0:05b}'.format((cnt % 32))
			newKeyText = Tex(actString, color = textColor)
			newKeyText.move_to(keyText.get_center())
			
			newGuessText = Group(*[
				Tex(str, color = textColor, font_size = smallFontSize) for str in constructRandomString()
			]).arrange(DOWN, center = False, aligned_edge = LEFT, buff = textPadding)
			newGuessText.move_to(guessText.get_center())

			self.play(
				Transform(keyText, newKeyText),
				*[Transform(txt, ntxt) for (txt, ntxt) in zip(guessText, newGuessText)],
				run_time = t
			)


		# we found the correct key

		newKeyText = Tex(ourKeyString, color = textColor)
		newKeyText.move_to(keyText.get_center())
		
		newGuessText = Group(*[
			Tex(str, color = textColor, font_size = smallFontSize) for str in strCipherText
		]).arrange(DOWN, center = False, aligned_edge = LEFT, buff = textPadding)
		newGuessText.move_to(guessText.get_center())

		self.play(
			Transform(keyText, newKeyText),
			*[Transform(txt, ntxt) for (txt, ntxt) in zip(guessText, newGuessText)],
			Flash(keyBorder),
			Flash(guessBorder),
			Flash(cipherBorder),
			run_time = minTime
		)

		self.wait()

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


def constructTextBorder(insideObject = None, position = np.array([0, 0, 0]), width = None, height = None, color = borderColor):
	#rec = RoundedRectangle(corner_radius = 0.1, color = color, height = height, width = width)
	#rec.move_to(position)

	if insideObject != None:
		topPadding = 0.1 * padding
		if width == None:
			width = (insideObject.get_right() - insideObject.get_left())[0] + padding
		if height == None:
			height = (insideObject.get_top() - insideObject.get_bottom())[1] + padding + topPadding
		position = insideObject.get_center() + topPadding + width/2 * LEFT + (height/2 + topPadding ) * UP

	topleft = position
	topright= topleft + width * RIGHT
	bottomleft = position + height * DOWN
	bottomright= bottomleft + width * RIGHT

	d = width / 10
	D = width / 4
	infty = 10000000

	noAngle = {'radius': infty, 'color': color}
	dAngle = {'radius': d, 'color': color}
	DAngle = {'radius': D*0.8, 'color': color}

	rec = ArcPolygon(
		topright + D * LEFT, 
		topleft + d * RIGHT,
		topleft + d * DOWN,
		bottomleft + d * UP,
		bottomleft + d * RIGHT,
		bottomright + d * LEFT,
		bottomright + d * UP,
		topright + D * DOWN,
		topright + D * LEFT,
		topright + D * DOWN,
		color = color,
		arc_config = [
			noAngle.copy(),
			dAngle.copy(),
			noAngle.copy(),
			dAngle.copy(),
			noAngle.copy(),
			dAngle.copy(),
			noAngle.copy(),
			noAngle.copy(),
			DAngle.copy(),
			noAngle.copy()
		]
	)


	return rec


def constructKey(position = np.array([0, 0, 0]), granularity = 100, width = 1, color = [keyColor, keyColor2]):
		
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
			pnt += position 
		
		return Polygon(*key, fill_opacity = 1, color = color[0]), \
			Polygon(*keyline, color = color[1]), \
			Circle(radius = radcirc, color = color[1]).move_to(midcirc)
