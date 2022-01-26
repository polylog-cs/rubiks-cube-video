from curses import COLOR_CYAN
from os import wait
import string
from manim import *
from manim.utils import tex
import numpy as np
import math
import textwrap
import random
from solarized import *
from tqdm import tqdm

# Use our fork of manim_rubikscube!
from manim_rubikscube import *

# Temne pozadi, ale zakomentovat pro DesIntro a GeneralMITM !!!
# config.background_color = BASE02


random.seed(0)


# colors
keyColor = GRAY
keyColor2= BASE1
textColor = GRAY
encodeColor = RED
decodeColor = BLUE
borderColor = GRAY
#plainCipherColor = DARK_BROWN
plainColor = CYAN
cipherColor = YELLOW2
smallFontSize = 18
tinyFontSize = 5
fontSize = 40 
padding = 0.5 # between the text and the border around it


#first diagram constants
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
invMinTime = 6
minTime = 1.0 / invMinTime

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
rng_state_1 = random.getstate()

def constructRandomString(lineLen = 30, numLines = 12):
	global rng_state_1
	old_state = random.getstate()
	random.setstate(rng_state_1)

	letters = string.ascii_letters + string.digits
	strList = []
	for j in range(numLines):
		str = r""
		for k in range(lineLen):
			str += random.choice(letters)
		strList.append(str)
	strList[-1] = strList[-1][:-3] + "..."
	strList[0] = strList[0][0: int(lineLen * tinyFontSize / smallFontSize - 1)]

	rng_state_1 = random.getstate()
	random.setstate(old_state)
	fontSizes = [smallFontSize] + [tinyFontSize]*(len(strList) - 1)
	return [(str, fontSize) for str, fontSize in zip(strList, fontSizes)]




strPlainText = [
	("Hi mom,", smallFontSize),
	("yes, I am watching all Polylog videos", 5),
	("as you wanted me to. Just now I watch ", 5),
	("the one about the meet in the middle", 5),
	("technique, the part about breaking", 5),
	("the double DES cipher. Did you read", 5),
	("the dummy plain text message in that", 5),
	("part of the video? It starts with:", 5),
	("\"Hi mom, yes, I am watching all", 5),
	("Polylog videos as you wanted me to. ", 5),
	("Just now I watch the one about the ", 5),
	("meet in the middle technique, the...", 5)
	##123456789012345678901234567890
]


strCipherText = constructRandomString()

rng_state_2 = random.getstate()

def constructRandomKeyString(len1 = 3, len2 = 5, prefix = None, suffix = None):
	global rng_state_2
	old_state = random.getstate()
	random.setstate(rng_state_2)

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

	rng_state_2 = random.getstate()
	random.setstate(old_state)
	return st


def random_click_file():
	return f"audio/click/click_{random.randint(0, 3)}.wav"


zeroString = "000...00000"
oneString = "000...00001"
ourKeyString = "101...01110"
randKeyString = constructRandomKeyString()
unknownKeyString = "???...?????"

# text object
class Btext:
	def __init__(self, strLines, position = np.array([0, 0, 0]), color = textColor, width = None, height = None, scale = 1.0, fill_color = None, fill_opacity = 0.0):
		self.position = position
		self.width = width
		self.height = height
		self.strLines = strLines
		self.fill_color = fill_color
		self.fill_opacity = fill_opacity
		self.color = color
		self.tag = False

		self.lines = Group(*[
			Tex(
				str, 
				color = self.color, 
				font_size = size,
			).scale(scale) for str, size in strLines
		]).arrange(DOWN, center = False, aligned_edge = LEFT, buff = textPadding)

		self.border = constructTextBorder(
			insideObject = self.lines,
			width = self.width,
			height = self.height, 
			color = self.color,
			fill_color = self.fill_color,
			fill_opacity = self.fill_opacity,
		).scale(scale)


		self.textBorder = Group(self.border, self.lines)
		if self.width == None:
			self.width = self.textBorder.width
			self.height = self.textBorder.height
		
	def changeText(self, newStrLines, empty = False):
		self.strLines = newStrLines

		newLines = Group(*[
			Tex(str, color = self.color, font_size = size) for str,size in self.strLines
		]).arrange(DOWN, center = False, aligned_edge = LEFT, buff = textPadding).move_to(self.lines.get_center())

		if empty == False:
			return AnimationGroup(*[Transform(line, newline) for (line, newline) in zip(self.lines, newLines)], lag_ratio = 0.2)
		else:
			self.lines = newLines
			return AnimationGroup(*[Write(line) for line in self.lines], lag_ratio = 0.2) 

	def create(self, position = None, noText = False, tag = False, tagStr = ""):
		if position is not None:
			self.position = position.copy()
		
		self.border.move_to(self.position)
		self.lines.move_to(self.position)
		
		anim = []

		if noText == False:
			anim.append(
				AnimationGroup(
					Write(self.lines[0]),
					AnimationGroup(
						*[Write(text) for text in self.lines[1:]],
						lag_ratio = 0.2,
						run_time = 1
					)
				)
			)

		if tag == True:
			self.tag = True
			self.tagText = Tex(
				tagStr,
				color = self.color,
				font_size = fontSize
			).move_to(
				self.border.get_center()
			).next_to(self.border, DOWN)

			anim.append(
				Write(self.tagText)
			)

		return AnimationGroup(
			AnimationGroup(
				DrawBorderThenFill(self.border),
			),
			*anim,
		)

	def highlight(self):
		animl = [
			self.border.animate().set_z_index(9999999)
		]
		return AnimationGroup(
			*animl
		)

	def move_to(self, position):
		self.textBorder.generate_target()
		self.textBorder.target.move_to(position)


		anims = [MoveToTarget(self.textBorder)]

		if self.tag == True:
			self.tagText.generate_target()
			self.tagText.target.shift(position - self.position)
			anims.append(
				MoveToTarget(self.tagText)
			)

		self.position = position

		return AnimationGroup(
			*anims
		) 

	def shift(self, vec):
		return self.move_to(self.position + vec)

	def remove(self):
		return AnimationGroup(
			*[FadeOut(self.border)],
			*[FadeOut(l) for l in self.lines],
		)

	def removeTag(self):
		self.tag = False
		return Unwrite(self.tagText)

	def addTag(self, tagStr):
		self.tag = True
		self.tagText = Tex(
			tagStr,
			color = self.color,
			font_size = fontSize
		).move_to(
			self.border.get_center()
		).next_to(self.border, DOWN)

		return Write(self.tagText)

# key object
class Key:
	def __init__(self, keyString, position = np.array([0, 0, 0]), scale = 1.0, clipartWidth = keyWidthLarge, upShift = 0.0*UP):
		self.keyString = keyString
		self.clipartWidth = clipartWidth
		self.position = position
		self.upShift = upShift

		self.text = Tex(keyString, color = textColor).move_to(self.position).scale(scale)
		self.brace = Brace(self.text, UP, color = textColor).shift(textPadding * UP).scale(scale)
		self.title = Tex("56 bit key", color = textColor).scale(scale)
		self.braceTitle = Group(self.brace, self.title).arrange(UP)

		self.border = Rectangle(
			width = self.text.get_right()[0] - self.text.get_left()[0] + padding, 
			height = self.text.get_top()[1] - self.text.get_bottom()[1] + padding, 
			color = keyColor
		).scale(scale)

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

	def changeText(self, newKeyString, fst = False):
		self.keyString = newKeyString
		newText = Tex(self.keyString, color = textColor).move_to(self.text.get_center())
		return Transform(self.text, newText)


	def changeTextandSize(self, newKeyString, shift = 0):
		self.keyString = newKeyString
		newText = Tex(self.keyString, color = textColor).move_to(self.text.get_center())
		newBorder = Rectangle(
			width = newText.get_right()[0] - newText.get_left()[0] + padding, 
			height = newText.get_top()[1] - newText.get_bottom()[1] + padding, 
			color = keyColor
		).move_to(self.border.get_center())
		newBrace = Brace(newText, UP, color = textColor).move_to(self.brace.get_center())
		newTitle = Tex("56 bit key", color = textColor).move_to(self.title.get_center())
		newRedArrow = Arrow(
			start = newBorder.get_left(),
			end = newBorder.get_right(),
			color = encodeColor,
			buff = 0
		).move_to(self.redArrow.get_center())
	

		Group(
			newText,
			newBorder,
			newBrace,
			newTitle,
			newRedArrow
		).shift(shift)

		return AnimationGroup(
			Transform(self.text, newText),
			Transform(self.border, newBorder),
			Transform(self.brace, newBrace),
			Transform(self.title, newTitle),
			Transform(self.redArrow, newRedArrow)
		)

	def createRectangleKey(self, position = None, noBrace = False):
		if position is None:
			position = self.position.copy()

		self.rectangleKey.move_to(position + self.rectangleKey.get_center() - self.border.get_center() )
		
		self.position = position

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
			self.position = position.copy()

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
		self.title = Tex("56 bit key", color = textColor)
		self.braceTitle = Group(self.brace, self.title).arrange(UP)

		newBorder = Rectangle(
			width = self.text.get_right()[0] - self.text.get_left()[0] + padding, 
			height = self.text.get_top()[1] - self.text.get_bottom()[1] + padding, 
			color = keyColor
		)

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

	def removeRec(self, noBrace = False):
		
		anims = [
			Uncreate(self.border),
			Unwrite(self.text)
		]

		if noBrace == False:
			anims.append(Uncreate(self.brace))
			anims.append(Unwrite(self.title))

		return AnimationGroup(
			*anims
		)

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

	def remove(self, noBrace = False):
		anims = [
			Uncreate(self.border),
			Unwrite(self.text),
		]
		if noBrace == False:
			anims.append(Unwrite(self.title)),
			anims.append(Uncreate(self.brace))

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
		topDiagramPos = 0.5 * UP

		self.next_section(skip_animations=False)
		
		# DES -> Data Encryption Standard
		DesTextPosition = 3*UP
		DesText = Tex(r"{{D}}{{E}}{{S}}", color = textColor)
		DesText.move_to(DesTextPosition)
		DesTextLong = Tex(r"{{Data }}{{Encryption }}{{Standard}}", color = textColor)
		DesTextLong.move_to(DesTextPosition)
		DesTextShort = DesText.copy()

		# DesTextPosition2 = DesTextPosition + 1*DOWN
		# delta = 0.35
		# D = Tex(r"D", color = textColor).move_to(DesTextPosition2).shift(delta * LEFT)
		# E = Tex(r"E", color = textColor).move_to(DesTextPosition2)
		# S = Tex(r"S", color = textColor).move_to(DesTextPosition2).shift(delta * RIGHT)

		# # first just letters

		# self.play(
		# 	Write(DesText),
		# 	Write(D),
		# 	Write(E),
		# 	Write(S),
		# )

	
		self.play(Transform(DesText, DesTextLong))
		self.wait()
		self.play(Transform(DesText, DesTextShort))
		self.wait()


		# first key occurence
		key = Key(ourKeyString, clipartWidth = keyWidthLarge)


		self.play(
			key.createClipartKey(position = midDiagramPos.copy())
		)

		[self.play(anim) for anim in key.transformClipartToRectangle(position = midDiagramPos.copy())]

		#encryption
		enDescription = Tex(
			"Encryption:", 
			color = textColor, 
			font_size = fontSize
		).move_to(midDiagramPos.copy() + leftTextPos.copy())
		self.play(Write(enDescription))
		self.wait()

		#plain text
		plain = Btext(strPlainText, color = plainColor, position = midDiagramPos.copy() + diagramWidth/2 * LEFT)
		self.play(
			plain.create(tag = True, tagStr = "plain text")
		)
		self.wait()

		#add red arrow
		self.play(key.createRedArrow())

		# cipher text
		cipher = Btext(
			strCipherText, 
			color = cipherColor,
			width = plain.width, 
			height = plain.height,
			position = midDiagramPos.copy() - plain.position[0]*RIGHT
		)

		self.play(
			cipher.create(tag = True, tagStr = "cipher text")
		)

		# slide up
		
		self.play(
			AnimationGroup(
			plain.move_to( plain.position + topDiagramPos - midDiagramPos),
			cipher.move_to(position = cipher.position + topDiagramPos - midDiagramPos),
			key.moveRec(pos = key.position + topDiagramPos - midDiagramPos),
			),
			AnimationGroup(
				enDescription.animate().shift(0.5 * UP)
			)
		)

		self.play(
			plain.removeTag(),
			cipher.removeTag()
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

		cipher2 = Btext(
			cipher.strLines, 
			position = cipher.position.copy(),
			width = cipher.width,
			color = cipherColor,
			height = cipher.height,
		) 

		self.play(
			cipher2.create(),
			run_time = 0
		)
		self.play(
			cipher2.shift(bottomDiagramPos - topDiagramPos)
		)
		self.wait()


		key2 = Key(
			key.keyString, 
			position = key.position,
		)
		self.play(
			key2.createRectangleKey(noBrace=True),
			run_time = 0.01
		)
		self.play(key2.shiftRec(
			bottomDiagramPos - topDiagramPos,
			noBrace = True
		))



		self.play(key2.createBlueArrow())

		plain2 = Btext(plain.strLines, color = plainColor, position  = plain.position.copy())
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

		# for i in range(len(anim2)):
		# 	self.play(
		# 		anim1[i],
		# 		anim2[i]
		# 	)


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

		self.play(
			Unwrite(decDescription),
			Unwrite(enDescription),
			plain2.remove(),
			cipher2.remove(),
			key2.remove(noBrace = True),
			key.remove()
		)

		self.play(
			plain.shift(midDiagramPos - topDiagramPos),
		)
		self.play(
			plain.addTag("plain text")
		)
		self.wait()

		self.play(
			cipher.shift(midDiagramPos - topDiagramPos),
		)
		self.play(
			cipher.addTag("cipher text")
		)

		self.wait()

		finalkey = Key(unknownKeyString, position = key.position+midDiagramPos-topDiagramPos)
		self.play(
			finalkey.createRectangleKey(noBrace = True)
		)
		self.wait()


class GeneralMITM(ThreeDScene):
	def construct(self):
		"""
		 Srovnání MITM na kostce a na DES. Co je společného. Nalevo kostka,
		napravo nějak vizualizovaný DES. Pak v "tabulce" ukázat čísla
		srovnávající runtime bruteforcu vs MITM.

		Pak ukázat i použité množství paměti, aby byl vidět tradeoff.

		Nakonec někde ukázat zobecnění, že potřebujeme sice jen sqrt(n) času,
		ale zato sqrt(n) paměti místo O(1).

		So again, we are going from both sides and we meet in the middle.
		This trick is analogous to the cube graph of size 10^20 that is too large 
		to be fully explored, but clever application of the meet in the middle trick 
		allowed us to find the best solution that needed around 10^10 steps and around 
		the same number of bytes of memory. 

		"""
		self.camera.set_focal_distance(20000.0)
		self.camera.should_apply_shading = False

		# first split screen
		self.next_section(skip_animations=False)

		backgroundRect = Rectangle(
			height = 8,
			width = 14.2,
			fill_opacity = 1,
			fill_color = BASE02,
			color = BASE02, 	
		) 
		#backgroundRect.z_index = -100
		
		backgroundRect.generate_target()
		# backgroundRect.move_to(
		# 	(14.2 * 1.5 / 2 + 14.2/2)*LEFT + 100*OUT
		# )
		backgroundRect.target.move_to(
			(14.2 / 2)*RIGHT
		)

		self.play(
			MoveToTarget(backgroundRect),
			run_time = 1	
		)
		self.wait()


		halfScreen = 14.2 / 2

		# rubik objects
		
		shft = 2 * UP
		cube = RubiksCube(cubie_size=0.7).move_to(
			shft + halfScreen/2 * LEFT
		)

		# text objects
		cubeTexts = [
			[
				Tex(str, color = textColor)
				for str in strList
			]
			for strList in [
				[r"$10^{20}$", r"$n$", r" configurations"],
				[r"{\it Meet in the Middle} solution:"], 
				[r"$10^{10}$", r"$\sqrt{n}$", r" work"],
				[r"$10^{10}$", r"$\sqrt{n}$", r" memory"],
				[r"$n = 10^{20}$"]
			]
		]
		desTexts = [
			[
				Tex(str, color = textColor)
				for str in strList
			]
			for strList in [
				[r"$2^{112}$", r"$n$", r" possible keys"],
				[r"{\it Meet in the Middle} solution:"], 
				[r"$2^{56}$", r"$\sqrt{n}$", r" work"],
				[r"$2^{56}$", r"$\sqrt{n}$", r" memory"], 
				[r"$n = 2^{112}$"]
			]
		]



		for Texts, pos in zip([cubeTexts, desTexts], [halfScreen*LEFT/2, halfScreen*RIGHT/2]):
			Group(
				Group(Texts[0][0], Texts[0][2]).arrange(RIGHT),
				Texts[1][0],
				Group(Texts[2][0], Texts[2][2]).arrange(RIGHT),
				Group(Texts[3][0], Texts[3][2]).arrange(RIGHT),
				Texts[4][0]
			).arrange(DOWN).move_to(pos + 2*DOWN)

		
			for txtList in Texts[0:1] + Texts[2:4]:
				txtList[2].shift((txtList[2].get_bottom() - txtList[0].get_bottom())[1] * 2 * DOWN)
				txtList[1].move_to(txtList[0].get_center()).align_to(txtList[0], RIGHT)
				


		#cube animations



		self.play(FadeIn(cube))
		self.play(Rotate(cube, 2 * PI, UP), run_time=1)
		self.wait()
		
		for Texts in [cubeTexts]:
			self.play(AnimationGroup(
					Write(Texts[0][0]),
					Write(Texts[0][2])
			))
			self.wait()

			self.play(Write(Texts[1][0]))

			self.wait()
			self.play(AnimationGroup(
				Write(Texts[2][0]),
				Write(Texts[2][2])
			))
			self.wait()
			self.play(AnimationGroup(
				Write(Texts[3][0]),
				Write(Texts[3][2])
			))
			self.wait()

		# des animations


		dist = 3
		sc = 1

		plain = Btext(
			strPlainText, 
			position = midDiagramPos + shft + halfScreen/2 * RIGHT - halfScreen/3 * RIGHT,
			scale = sc,
		)

		inter = Btext(
			constructRandomString(),  
			position = midDiagramPos + shft + halfScreen/2 * RIGHT,
			scale = sc,
			width = plain.width,
			height = plain.height
		)

		cipher = Btext(
			constructRandomString(), 
			position = midDiagramPos + shft + halfScreen/2 * RIGHT + halfScreen/3 * RIGHT,
			scale = sc,
			width = plain.width,
			height = plain.height
		)

		len = 1.2
		key1 = Arrow(
			start = (len / 2.0) * LEFT,
			end = (len / 2.0) * RIGHT ,
			color = encodeColor,
			stroke_width = 8			
		).move_to((plain.position + inter.position)/2)


		key2 = Arrow(
			start = (len / 2.0) * LEFT,
			end = (len / 2.0) * RIGHT,
			color = encodeColor,
			stroke_width = 8
		).move_to((cipher.position + inter.position)/2)

		self.play(
			plain.create(),
			inter.create(),
			cipher.create(),
			Create(key1),
			Create(key2),
		)
		self.wait()

		#des text

		for Texts in [desTexts]:
			self.play(AnimationGroup(
					Write(Texts[0][0]),
					Write(Texts[0][2])
			))
			self.wait()

			self.play(Write(Texts[1][0]))

			self.wait()
			self.play(AnimationGroup(
				Write(Texts[2][0]),
				Write(Texts[2][2])
			))
			self.wait()

			self.play(AnimationGroup(
				Write(Texts[3][0]),
				Write(Texts[3][2])
			))
			self.wait()

		# change numbers to n


		self.play(
			*[
				Write(Texts[4][0])
				for Texts in [desTexts, cubeTexts]
			]	
		)
		self.wait()


		# fix roots that are a bit off
		desTexts[2][1].shift(0.1*DOWN)
		cubeTexts[2][1].shift(0.1*DOWN)

		self.play(
			*[
				Transform(strList[0], strList[1])
				for strList in desTexts[0:1] + desTexts[2:4] + cubeTexts[0:1] + cubeTexts[2:4]
			]
		)
		self.wait()

		# uncreate everything

		anims = []
		for text in desTexts + cubeTexts:
			for t in text:
				anims.append(Unwrite(t))


		self.play(
			*anims,
			*[t.remove() for t in [plain, inter, cipher]],
			*[Uncreate(key) for key in [key1, key2]],
			#cube.animate.rotate(2*PI, UP).shift(14.2 * RIGHT),
			FadeOut(cube)
		)
		self.wait()


		# final thanks
		channel_name = Tex(r"polylog", color=textColor)
		channel_name.scale(3).shift(2 * UP).shift(14.2 * LEFT)

		thanks = [
			Tex(str, color = textColor)
			for str in [
				r"Big thanks to: 3blue1brown \& Manim community for Manim",
				"KingWampy for Rubik's cube library in Manim",
				"people"
			]
		]
		thanks_group = Group(*thanks).arrange(DOWN).shift(14.2 * LEFT)
		for t in thanks:
			t.align_to(thanks[0], LEFT)
		self.add(
			*thanks,
			channel_name
		)
		# shift to the screen
		self.play(
			*[o.animate.shift(14.2 * RIGHT) for o in 
				[
					backgroundRect,
					thanks_group,
					channel_name
				]
			]
		)

		self.wait()
		self.play(
			*[
				Unwrite(t) for t in thanks
			]
		)
		self.wait()

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
