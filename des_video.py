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


# colors
keyColor = GRAY
keyColor2= BASE1
textColor = GRAY
encodeColor = RED
decodeColor = BLUE
borderColor = GRAY
smallFontSize = 20
fontSize = 40 # TODO zmenit na vychozi velikost (jak se zjisti?)
padding = 0.5 # between the text and the border around it


#some random constants
midDiagramPos = 0*UP
topDiagramPos = 1*UP
bottomDiagramPos = 2*DOWN
diagramWidth = 5
arrowLen = 3
keyWidthLarge = 2.5
keyWidth = 1.5
keyPadding = 0.8
textPadding = 0.1
keyInfoWidth = 3.0
keyInfoHeight = 2.0
leftTextPos = 5.5 * LEFT
minTime = 0.3

posPlain = bottomDiagramPos + 6 * LEFT
posFinal = bottomDiagramPos + 6 * RIGHT

cipherPositions = [
	2*posPlain/3 + posFinal/3,
	posPlain/3 + 2*posFinal/3,
	bottomDiagramPos + 6 * RIGHT,
]

keyPositions = [
	(posPlain + cipherPositions[0])/2,
	(cipherPositions[0] + cipherPositions[1])/2,
	(cipherPositions[1] + cipherPositions[2])/2
]

def flatten(t):
	return [item for sublist in t for item in sublist]

# constructing random strings inside keys and ciphertexts
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

def constructRandomKeyString(len1 = 3, len2 = 5, prefix = None, suffix = None):
	st = ""
	if prefix is None:
		for _ in range(len1):
			st += random.choice(["0", "1"])
	else:
		st += ('{0:0'+str(len1)+'b}').format(prefix)
	st += "..."	
	if suffix is None:
		for _ in range(len2):
			st += random.choice(["0", "1"])
	else:
		st += ('{0:0'+str(len2)+'b}').format(suffix)
	return st

zeroString = "000...00000"
ourKeyString = "101...01110"
randKeyString = constructRandomKeyString()
unknownKeyString = "???...?????"
zeroStringShort = "00...00"

# text object
class Btext:
	def __init__(self, strLines, position = np.array([0, 0, 0]), width = None, height = None, fill_color = None, fill_opacity = 0.0):
		self.position = position
		self.width = width
		self.height = height
		self.strLines = strLines
		self.fill_color = fill_color
		self.fill_opacity = fill_opacity

		self.lines = Group(*[
			Tex(
				str, 
				color = textColor, 
				font_size = smallFontSize,
			) for str in strLines
		]).arrange(DOWN, center = False, aligned_edge = LEFT, buff = textPadding)

		self.border = constructTextBorder(
			insideObject = self.lines,
			width = self.width,
			height = self.height, 
			fill_color = self.fill_color,
			fill_opacity = self.fill_opacity,
		)

		self.lines = Group(*[
			Tex(
				str, 
				color = textColor, 
				font_size = smallFontSize,
			) for str in strLines
		]).arrange(DOWN, center = False, aligned_edge = LEFT, buff = textPadding)


		self.textBorder = Group(self.border, self.lines)
		if self.width == None:
			self.width = self.textBorder.width
			self.height = self.textBorder.height
	
	def changeText(self, newStrLines, empty = False):
		self.strLines = newStrLines

		newLines = Group(*[
			Tex(str, color = textColor, font_size = smallFontSize) for str in self.strLines
		]).arrange(DOWN, center = False, aligned_edge = LEFT, buff = textPadding).move_to(self.lines.get_center())

		if empty == False:
			return AnimationGroup(*[Transform(line, newline) for (line, newline) in zip(self.lines, newLines)], lag_ratio = 0.2)
		else:
			self.lines = newLines
			return AnimationGroup(*[Write(line) for line in self.lines], lag_ratio = 0.2)

	def create(self, position = None, noText = False):
		if position is not None:
			self.position = position
		
		self.border.move_to(self.position)
		self.lines.move_to(self.position + np.array([0, 0, 1]))
		
		if noText == False:
			anim = AnimationGroup(
				*[Write(text) for text in self.lines],
				lag_ratio = 0.2
			)
		else:
			anim = AnimationGroup()

		return AnimationGroup(
			Create(self.border),
			anim, 
		)
	
	def highlight(self):
		animl = [
			self.border.animate().set_z_index(9999999)#.set_color(RED) # TODO zmenit
		]
		return AnimationGroup(
			*animl
		)

	def move_to(self, position):
		self.position = position
		self.textBorder.generate_target()
		self.textBorder.target.move_to(self.position)
		return MoveToTarget(self.textBorder)

	def shift(self, vec):
		return self.move_to(self.position + vec)

	def remove(self):
		return AnimationGroup(
			*[FadeOut(l) for l in self.lines],
			*[FadeOut(self.border)]
		)


# key object
class Key:
	def __init__(self, keyString, position = np.array([0, 0, 0]), clipartWidth = keyWidthLarge, upShift = 0.5*UP):
		self.keyString = keyString
		self.clipartWidth = clipartWidth
		self.position = position
		self.upShift = upShift

		self.text = Tex(keyString, color = textColor).move_to(self.position)
		self.brace = Brace(self.text, UP, color = textColor).shift(textPadding * UP)
		self.title = Tex("56 bits", color = textColor)
		self.braceTitle = Group(self.brace, self.title).arrange(UP)

		self.border = Rectangle(
			width = self.text.get_right()[0] - self.text.get_left()[0] + padding, 
			height = self.text.get_top()[1] - self.text.get_bottom()[1] + padding, 
			color = keyColor
		)
		#TODO maybe rotate rect

		self.border.move_to(self.position)
		
		self.braceTitle.shift(
			self.border.get_top() + padding * UP + (self.braceTitle.get_top() - self.braceTitle.get_center())/2
		)

		self.rectangleKey = Group(
			self.text,
			self.braceTitle,
			self.border
		)

		_, self.clipartKeyLine, self.clipartKeyCirc = constructKey(
			position = position,
			width = self.clipartWidth
		) 

		self.clipartKey = Group(
			self.border,
			self.clipartKeyLine,
			self.clipartKeyCirc
		)

		self.redActive = False
		self.redArrow = Arrow(
			start = 0*LEFT,
			end = 0*LEFT,
			color = encodeColor
		)

		self.blueActive = False
		self.blueArrow = Arrow(
			end = 0*LEFT,
			start = 0*LEFT,
			color = decodeColor
		)

	def changeText(self, newKeyString):
		self.keyString = newKeyString
		newText = Tex(self.keyString, color = textColor).move_to(self.text.get_center())
		return Transform(self.text, newText)

	def createRectangleKey(self, position = None, noBrace = False):
		if not position is None:
			self.position = position
		self.rectangleKey.move_to(self.position + self.upShift)
		
		if noBrace  == False:
			anims = AnimationGroup(
				Write(self.text),
				Create(self.border),
				Create(self.brace),
				Write(self.title)
			)
		else:
			anims = AnimationGroup(
				Create(self.border),
				Write(self.text)
			)

		return anims

	def createClipartKey(self, position = None):
		if not position is None:
			self.position = position

		self.border, self.clipartKeyLine, self.clipartKeyCirc = constructKey(
			position = self.position,
			width = self.clipartWidth
		)

		self.clipartKey.move_to(self.position + self.upShift)

		anims = AnimationGroup(
			Create(self.border), 
			Create(self.clipartKeyLine), 
			Create(self.clipartKeyCirc)
		)
		return anims

	def transformClipartToRectangle(self, position = None, noBrace = False):
		if not position is None:
			self.position = position

		self.text = Tex(self.keyString, color = textColor).move_to(self.position + self.upShift)
		self.brace = Brace(self.text, UP, color = textColor).shift(textPadding * UP)
		self.title = Tex("56 bits", color = textColor)
		self.braceTitle = Group(self.brace, self.title).arrange(UP)

		newBorder = Rectangle(
			width = self.text.get_right()[0] - self.text.get_left()[0] + padding, 
			height = self.text.get_top()[1] - self.text.get_bottom()[1] + padding, 
			color = keyColor
		)
		#TODO maybe rotate rect

		newBorder.move_to(self.position + self.upShift)

		anims1 = AnimationGroup( 
			Uncreate(self.clipartKeyLine),
			Uncreate(self.clipartKeyCirc)
		)

		anims2l = [Transform(
			self.border, 
			newBorder
		)]

		if self.redActive == True:
			newRedArrow = Arrow(
				start = newBorder.get_left(),
				end = newBorder.get_right(),
				color = encodeColor,
				buff = 0
			).move_to(newBorder.get_bottom() + 1*textPadding*DOWN)
			
			anims2l.append(
				Transform(self.redArrow, newRedArrow)
			)
		
		if self.blueActive == True:
			newBlueArrow = Arrow(
				end = newBorder.get_left(),
				start = newBorder.get_right(),
				color = decodeColor,
				buff = 0
			).move_to(newBorder.get_bottom() + 1*textPadding*DOWN)
			
			anims2l.append(
				Transform(self.blueArrow, newBlueArrow)
			)

		anims2 = AnimationGroup(
			*anims2l, 
			run_time = 2
		)

		self.text.move_to(self.position + self.upShift)
		self.braceTitle.move_to(self.position + self.upShift).next_to(self.text, UP).shift(textPadding * UP)

		if noBrace  == False:
			anims3 = AnimationGroup(
				Write(self.text),
				Create(self.brace),
				Write(self.title)
			)
		else:
			anims3 = AnimationGroup(
				Write(self.text)
			)
		
		return [anims1, anims2, anims3]

	def transformRectangleToClipart(self,  position = None):
		if not position is None:
			self.position = position

		self.clipartKey.move_to(self.position + self.upShift)

		anims1 = AnimationGroup(
			Uncreate(self.text),
			Uncreate(self.brace),
			Uncreate(self.title)
		)

		keyShape, self.clipartKeyLine, self.clipartKeyCirc = constructKey(
			position = self.position + self.upShift,
			width = self.clipartWidth
		)


		anims2 = AnimationGroup(
			Transform(
				self.border, 
				keyShape
			), 
			Create(self.clipartKeyLine),
			Create(self.clipartKeyCirc)
		)

		return [anims1, anims2]

	def moveClipart(self, position = None, clipartWidth = None):
		if not position is None:
			self.position = position
		if not clipartWidth is None:
			self.clipartWidth = clipartWidth

		#key moves
		shapeNew, lineNew, circNew =  constructKey(
			position = self.position + self.upShift,
			width = self.clipartWidth
		)	
		anim = [
			Transform(self.border, shapeNew), 
			Transform(self.clipartKeyLine, lineNew), 
			Transform(self.clipartKeyCirc, circNew),			
		]

		if self.redActive:
			anim.append(self.redArrow.animate().shift(circNew.get_center() - self.clipartKeyCirc.get_center()))
		if self.blueActive:
			anim.append(self.blueArrow.animate().shift(circNew.get_center() - self.clipartKeyCirc.get_center()))

		return AnimationGroup(*anim)

	def shiftRec(self, vec, noBrace = False):
		self.position += vec

		animl = [
			self.border.animate().shift(vec),
			self.text.animate().shift(vec),
		]

		if noBrace == False:
			animl.append(self.braceTitle.animate().shift(vec))

		if self.redActive == True:
			animl.append(self.redArrow.animate().shift(vec))
		if self.blueActive == True:
			animl.append(self.blueArrow.animate().shift(vec))
			

		anim = AnimationGroup(
			*animl
		)
		return anim

	def moveRec(self, pos, noBrace=False):
		return self.shiftRec(pos - self.position, noBrace = noBrace)

	def createRedArrow(self, position = None):
		if not position is None:
			self.position = position

		self.redArrow = Arrow(
			start = self.border.get_left(),
			end = self.border.get_right(),
			color = encodeColor,
			buff = 0
		).move_to(self.border.get_bottom() + 1*textPadding*DOWN)
		
		self.redActive = True

		anim = AnimationGroup(
			Create(self.redArrow)
		)

		return anim

	def removeRedArrow(self):
		self.redActive = False
		return AnimationGroup(
			Uncreate(self.redArrow)
		)	

	def createBlueArrow(self, position = None):
		if not position is None:
			self.position = position

		self.blueArrow = Arrow(
			end = self.border.get_left(),
			start = self.border.get_right(),
			color = decodeColor,
			buff = 0
		).move_to(self.border.get_bottom() + 1*textPadding*DOWN)		
		self.blueActive = True

		anim = AnimationGroup(
			Create(self.blueArrow)
		)

		return anim

	def removeBlueArrow(self):
		self.blueActive = False
		return AnimationGroup(
			Uncreate(self.blueArrow)
		)	

	def remove(self):
		anims = [
			Uncreate(self.border),
			Uncreate(self.brace),
			Unwrite(self.title),
			Unwrite(self.text),
		]
		if self.redActive == True:
			anims.append(Uncreate(self.redArrow))
		if self.blueActive == True:
			anims.append(Uncreate(self.blueArrow))
		return AnimationGroup(*anims)

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
		
		self.next_section(skip_animations=False)
		
		# DES -> Data Encryption Standard
		DesTextPosition = 3*UP
		DesText = Tex(r"DES", color = textColor)
		DesText.move_to(DesTextPosition)
		DesTextLong = Tex(r"Data Encryption Standard", color = textColor)
		DesTextLong.move_to(DesTextPosition)
		DesTextShort = DesText.copy()

		self.play(Write(DesText))
		self.play(Transform(DesText, DesTextLong)) #TODO: vyhezkat, aby se písmenka DES jen posunula
		self.wait()
		self.play(Transform(DesText, DesTextShort)) #TODO: vyhezkat, aby se písmenka DES jen posunula




		# first key occurence
		key = Key(ourKeyString, clipartWidth = keyWidthLarge)


		self.play(
			key.createClipartKey(position = midDiagramPos)
		)

		[self.play(anim) for anim in key.transformClipartToRectangle(position = midDiagramPos)]

		[self.play(anim) for anim in key.transformRectangleToClipart(position = topDiagramPos + 1*UP)]


		#encryption
		enDescription = Tex(
			"Encryption:", 
			color = textColor, 
			font_size = fontSize
		).move_to(midDiagramPos + leftTextPos)
		self.play(Write(enDescription))
		self.wait()

		#plain text
		plain = Btext(strPlainText, position = midDiagramPos + diagramWidth/2 * LEFT)
		self.play(plain.create())
		self.wait()

		#key moves down
		self.play(key.moveClipart(
			position = midDiagramPos,
			clipartWidth = keyWidth
		))

		self.next_section(skip_animations=False)

		#add red arrow
		self.play(key.createRedArrow())

		# cipher text
		cipher = Btext(
			strCipherText, 
			width = plain.width, 
			height = plain.height,
			position = midDiagramPos - plain.position[0]*RIGHT
		)

		cipher.create()

		# slide up

		self.play(
			key.moveClipart(position = key.position + topDiagramPos - midDiagramPos),
			plain.move_to(position = plain.position + topDiagramPos - midDiagramPos),
			cipher.move_to(position = cipher.position + topDiagramPos - midDiagramPos),
			enDescription.animate().shift(topDiagramPos - midDiagramPos)
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

		cipher2 = Btext(cipher.strLines, position = cipher.position) 
		self.play(
			cipher2.create(),
			run_time = 0
		)
		self.play(
			cipher2.shift(bottomDiagramPos - topDiagramPos)
		)
		self.wait()


		key2 = Key(key.keyString, position = key.position, clipartWidth = key.clipartWidth)
		self.play(key2.createClipartKey(),  run_time = 0)
		self.play(key2.moveClipart(
			position = bottomDiagramPos,
		))

		self.play(key2.createBlueArrow())

		plain2 = Btext(plain.strLines, position  = plain.position)
		self.play(
			plain2.create(),
			run_time = 0
		)
		self.play(
			plain2.shift(bottomDiagramPos - topDiagramPos)
		)
		self.wait()



		self.next_section(skip_animations=False)

		# explode keys

		anim1 = key.transformClipartToRectangle(noBrace=True)
		anim2 = key2.transformClipartToRectangle(noBrace=True)



		for i in range(len(anim2)):
			self.play(
				anim1[i],
				anim2[i]
			)


		# try different key

		self.play(
			key2.changeText(randKeyString),
			plain2.changeText(constructRandomString())
		)

		self.wait()

		self.play(
			key2.changeText(ourKeyString),
			plain2.changeText(strPlainText)
		)


		# # bring everything to front and slide rectangle behind it

		# everything = Group(
		# 	DesText,
		# 	enKey, enPlainText, enPlainBorder, enArrow, enCipherText, enCipherBorder, enDescription, enOurKey,
		# 	decOurKey, decArrow, decPlain, decCipher, decDescription, decKey, decPlainText, decPlainBorder
		# )


		#BACK = np.array([0, 0, -1.0]) 
		# TODO udělat to tak, aby to běželo vzadu ne vepředu

		self.next_section(skip_animations=False)

		eps = 0.1
		backgroundRect = Rectangle(
			height = 8 + eps,
			width = 14.2 + eps,
			fill_opacity = 1,
			fill_color = BASE02,
			color = BASE02, 
			
		)
		backgroundRect.z_index = -1
		backgroundRect.move_to(
			(14.2+2*eps)*LEFT
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
			#*[FadeOut(obj) for obj in everything],
			run_time = 1	
		)
		


class DesBruteForce(Scene):
	def construct(self):
		"""
		TODO: Animace, kde je vstupní text (něco vtipného), pak šipky nad
		kterými jsou klíče a jde to do cipher textů. Klíč je buď klipart nebo
		občas string bitů. Napravo je cipher text a checkujeme (posouváme ho?)
		zda matchuje naše CipherTexty
		"""

		# create plain and cipher text

		plain = Btext(strPlainText, position = midDiagramPos - diagramWidth * RIGHT /2)
		self.play(
			plain.create()
		)

		cipher = Btext(strCipherText, width = plain.width, height = plain.height, position = midDiagramPos + diagramWidth*RIGHT/2)
		self.play(
			cipher.create()
		)

		key = Key(unknownKeyString, position = midDiagramPos + keyPadding * UP)
		self.play(
			key.createRectangleKey()
		)

		self.play(
			plain.shift(diagramWidth/3 * LEFT),
			key.shiftRec(diagramWidth/3 * LEFT),
			cipher.shift(diagramWidth/3 * RIGHT)

		)

		guess = Btext(constructRandomString(), position = midDiagramPos + 1 * RIGHT)


		self.play(
			#key.changeText(zeroString),
			guess.create(noText = True),
			run_time = 1
		)


		waitingTimes = []
		L = 4 # TODO víc
		for i in range(L):
			waitingTimes.append(
				max(1 - i * 1.0 / L, minTime)
			)
		
		cnt = 0
		for t in waitingTimes:
			actString = "000..." + '{0:05b}'.format((cnt % 32))

			self.play(
				key.changeText(actString),
				guess.changeText(constructRandomString(),empty = (True if cnt == 0 else False)),
				run_time = t
			)
			cnt += 1
			
		# we found the correct key

		self.play(
			key.changeText(ourKeyString),
			guess.changeText(strCipherText)
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
		enough so that bruteforce is not a possibility, because 2^112 is 10^30,
		which is just way too much. 
		"""

		# beginning of the scene
		self.next_section(skip_animations=False)

		DesTextPosition = 3*UP
		DesText = Tex(r"DES", color = textColor).move_to(DesTextPosition)
		TripleDes = Tex(r"Triple DES", color = textColor).move_to(DesTextPosition)
		
		self.add(DesText)


		keyStrings = [
			constructRandomKeyString(len1 = 2, len2 = 2),
			constructRandomKeyString(len1 = 2, len2 = 2),
			constructRandomKeyString(len1 = 2, len2 = 2)
		]

		plain = Btext(strPlainText, position = midDiagramPos + diagramWidth * (5.0/6) * LEFT)
		self.play(
			plain.create(),
			run_time = 0.01  #TODO proc nula nefunguje?
		)

		self.play(Transform(DesText,TripleDes)) #TODO: vyhezkat, aby se písmenka DES jen posunula

		self.play(
			plain.shift(posPlain - plain.position)
		)

		ciphers = [
			Btext(
				constructRandomString(), 
				position = pos.copy(), 
				width = plain.width.copy()
			) for pos in cipherPositions
		]

		keys = [
			Key(
				str, 
				position = pos.copy(), 
				upShift=1*UP
			) for (pos, str) in zip(keyPositions, keyStrings)
		]

		[self.play(
				cipher.create(),
				key.createRectangleKey(),
				key.createRedArrow(),
			) for (key, cipher) in zip (keys, ciphers)
		]

		self.wait()

		topKeys = [
			Key(
				str, 
				position = pos.copy(), 
				upShift=1*UP
			) for (pos, str) in zip(keyPositions, keyStrings)
		]
		self.play(*[key.createRectangleKey(noBrace=True) for key in topKeys], run_time = 0.01)
		
		self.play(
			topKeys[0].shiftRec( 2.5*UP   
				+ (keys[1].position - keys[0].position) 
				+ (keys[0].border.get_width() + keys[1].border.get_width())/2 * LEFT
			),
			topKeys[1].shiftRec(2.5*UP),
			topKeys[2].shiftRec(2.5*UP 
				+ (keys[1].position - keys[2].position) 
				+ (keys[2].border.get_width() + keys[1].border.get_width())/2 * RIGHT
			)
		)
		
		newTitle = Tex(r"168 bits", color = textColor).move_to(topKeys[1].title.get_center())
		newBrace = Brace(Group(topKeys[0].text, topKeys[2].text), UP, color = textColor).move_to(topKeys[1].brace.get_center())
		self.play(
			FadeOut(topKeys[0].title),
			FadeOut(topKeys[0].brace),
			FadeOut(topKeys[2].title),
			FadeOut(topKeys[2].brace),
			Transform(topKeys[1].title, newTitle),
			Transform(topKeys[1].brace, newBrace)
		)

		self.wait()

		#triple des -> double des

		self.next_section(skip_animations=False)

		DoubleDes = Tex(r"Double DES", color = textColor).move_to(DesTextPosition)

		txtShift = ciphers[1].border.get_center()[0]*RIGHT
		recShift = topKeys[1].border.get_center() - topKeys[1].border.get_left()


		newKeys = [[key.border.copy().shift(recShift), key.text.copy().shift(recShift)] for key in topKeys]
		newKeys[2][0].color = RED # TODO ?
		newKeys[2][1].color = RED



		newTitle = Tex(r"112 bits", color = textColor).move_to(topKeys[1].title.get_center())
		newBrace = Brace(Group(newKeys[0][1], newKeys[1][1]), UP, color = textColor).move_to(topKeys[1].brace)
		
		self.play(
			Transform(DesText, DoubleDes),
			*[txt.shift(txtShift) for txt in ciphers+[plain]],
			*[key.shiftRec(txtShift) for key in keys],
			*flatten([
				[Transform(key.border, border), 
				Transform(key.text,text)]
				for (key, [border, text]) in zip(topKeys, newKeys)
			]),
			Transform(topKeys[1].title, newTitle),
			Transform(topKeys[1].brace, newBrace)
		)


		# TODO
		self.play(
			FadeOut(ciphers[2].border), *[FadeOut(txt) for txt in ciphers[2].lines], 
			FadeOut(topKeys[2].border), FadeOut(topKeys[2].text),
			FadeOut(keys[2].border), FadeOut(keys[2].text), FadeOut(keys[2].redArrow), FadeOut(keys[2].braceTitle),
		)


		computation = Tex(
			r"$2^{112} \approx 10^{34}$",
			color = textColor
		).move_to(4*RIGHT + 2*UP)

		self.play(
			Write(computation)
		)

		self.wait()


class DesMITM(Scene):
	def construct(self):
		"""
		But, in fact, the Double DES is not that much safer than the ordinary DES! 
		To break it, if you know a plain text and the respective cypher text, 
		you will first start yet again by bruteforcing all 2^56 keys and compute all possible encrypted texts. 
		You save them in memory -- you will need at least millions of gigabytes but remember, you are the military 
		-- and then, as in the case of the cube, you start working from the other side. 
		You use the decryption function on the ciphertext with all possible keys. 
		Whenever you decrypt the message, you compare it with the huge database you computed in the first step. 
		This comparison can be done very quickly if you put the strings you computed in a hash table. 
		You are again iterating over all 2^56 possible keys, until you find the decrypted string in the database, 
		which gives you the two keys used in the cipher. 

		"""
		
		# beginning of the scene
		self.next_section(skip_animations=False)

		global posPlain, posFinal
		for val in [posPlain, posFinal]:
			val += midDiagramPos - bottomDiagramPos
		posInter = 0.6 * posPlain + 0.4 * posFinal
		posKey = (posPlain + posInter) / 2

		posInter2 = 0.4 * posPlain + 0.6 * posFinal
		posKey2 = (posFinal + posInter2) / 2


		DesTextPosition = 3*UP
		DesText = Tex(r"Double DES", color = textColor).move_to(DesTextPosition)		
		self.add(DesText)

		plain = Btext(
			strPlainText, 
			position = posPlain,
		)
		self.play(
			plain.create(),
			run_time = 1  
		)

		cipher = Btext(
			constructRandomString(), 
			position = posFinal,
			width = plain.width,
			height = plain.height
		)
		self.play(
			cipher.create(),
			run_time = 1  
		)		

		# generating all intermediate strings


		key = Key(zeroString, position = posKey)

		self.play(
			#inter.create(),
			key.createRectangleKey(),
			key.createRedArrow()
		)

		topLeft = topDiagramPos + 1*RIGHT
		databasePositions = []
		databaseInters = []
		keyStrings = []
		
		w = 2
		h = 2
		for i in range(h):
			for j in range(w):
				databasePositions.append(topLeft + i * 0.7 * DOWN + j * 0.3 * RIGHT)
		for i in range(h*w):
			keyStrings.append(constructRandomKeyString(
				len1 = 3,
				len2 = 5,
				prefix = int(((2 ** 3)*i)/(1.0*h*w)),
				suffix = None if i<h*w-1 else (2 ** 5 - 1)
			))


		self.wait()

		anims = []
		for it, (pos, keyString) in enumerate(zip(databasePositions, keyStrings)):
			curInter = Btext( # TODO fix visibility of the text
				#strPlainText,
				constructRandomString(),
				position = posInter, 
				width = plain.width,
				height = plain.height,
				fill_color = config.background_color,
				fill_opacity = 1
			)
			databaseInters.append(curInter)

			anims.append(Succession(
				AnimationGroup(
					curInter.create(),
					run_time = 0.01
				),
				AnimationGroup(
					Wait()
				),
				AnimationGroup(
					AnimationGroup(
						curInter.move_to(pos),
						run_time = 0.3
					),
					AnimationGroup(
						key.changeText(keyString),
						run_time = 0.1
					),
					lag_ratio = 0.0
				)
			))

		self.play(AnimationGroup(
			*anims, 
			lag_ratio = 0.1
		))


		datSizeBrace = Brace(Group(*databaseInters), direction = DOWN).shift(5 * textPadding * DOWN)
		datSizeText = Text(r"$2^{56}$ intermediate texts").next_to(datSizeBrace,DOWN)
		datSize = Group(
			datSizeBrace,
			datSizeText
		)
		self.play(
			Create(datSizeBrace),
			Write(datSizeText)
		)

		self.next_section(skip_animations=False)

		# key disappears and database shifts

		shft = 4*LEFT
		self.play(
			key.remove(),
			*[
				bt.shift(4*shft) 
				for bt in databaseInters
			],
			datSize.animate().shift(4*LEFT)
		)

		# blue key appears

		key2 = Key(
			zeroString,
			position = posKey2
		)

		inter = Btext(
			constructRandomString(), 
			position = posInter2,
			width = plain.width,
			height = plain.height
		)

		self.play(
			key2.createRectangleKey(),
			key2.createBlueArrow(),
			inter.create()
		)
		
		# trying blue keys

		t = 5
		for i in range(t):
			newKeyStr = constructRandomKeyString(
				prefix = int((i * (2 ** 3)) / (1.5 * t))
			)

			self.play(
				key2.changeText(newKeyStr),
				inter.changeText(constructRandomString()),
				run_time = 0.2
			)

		self.next_section(skip_animations=False)

		# we found one
		hit = 1
		strLinesHit = databaseInters[hit].strLines.copy()

		inter2 = Btext(
			strLinesHit,
			position = databaseInters[hit].position,
			width = databaseInters[hit].width,
			height = databaseInters[hit].height,
			fill_color = config.background_color,
			fill_opacity = 1
		)

		self.play(
			key2.changeText("101...10010"),
			inter.changeText(strLinesHit),
			run_time = 0.2
		)

		self.play(
			inter2.create(),
			run_time = 0.01
		)
		self.wait()
		self.play(
			Circumscribe(inter.border),
			Circumscribe(inter2.border)
		)

		self.play(
			*[datInter.remove() for datInter in databaseInters],
			inter2.move_to(inter2.position)
		)

		self.play(
			inter.move_to((plain.position + cipher.position)/2),
			key2.moveRec(plain.position/4 + cipher.position*3.0/4),
			inter2.move_to((plain.position + cipher.position)/2 ),
		)

		key = Key(
			constructRandomKeyString(),
			position = plain.position*3.0/4 + cipher.position/4
		)
		self.play(
			key.createRectangleKey(),
			key.createRedArrow()
		)
		self.play(
			key2.removeBlueArrow(),
			key.removeRedArrow()
		)

		self.wait()


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


def constructTextBorder(insideObject = None, position = np.array([0, 0, 0]), width = None, height = None, color = borderColor, fill_color = None, fill_opacity = 0.0):
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
		],
		fill_color = fill_color,
		fill_opacity = fill_opacity
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

