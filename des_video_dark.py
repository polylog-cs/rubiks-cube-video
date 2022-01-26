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
config.background_color = BASE02


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
	def __init__(self, keyString, position = np.array([0, 0, 0]), scale = 1.0, clipartWidth = keyWidthLarge, upShift = 0.0*UP, keyTitle ="56 bit key"):
		self.keyString = keyString
		self.clipartWidth = clipartWidth
		self.position = position
		self.upShift = upShift
		self.keyTitle = keyTitle

		self.text = Tex(keyString, color = textColor).move_to(self.position).scale(scale)
		self.brace = Brace(self.text, UP, color = textColor).shift(textPadding * UP).scale(scale)
		self.title = Tex(self.keyTitle, color = textColor).scale(scale)
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
		newTitle = Tex(self.keyTitle, color = textColor).move_to(self.title.get_center())
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


class DesBruteForce(Scene):
	def construct(self):
		"""
		: Animace, kde je vstupní text (něco vtipného), pak šipky nad
		kterými jsou klíče a jde to do cipher textů. Klíč je buď klipart nebo
		občas string bitů. Napravo je cipher text a checkujeme (posouváme ho?)
		zda matchuje naše CipherTexty
		"""

		self.next_section(skip_animations = False)

		DesTextPosition = 3*UP
		DesText = Tex(r"DES", color = textColor).move_to(DesTextPosition)
		self.add(DesText)

		# create plain and cipher text

		plain = Btext(strPlainText, color = plainColor, position = midDiagramPos - diagramWidth * RIGHT /2 )
		self.play(
			plain.create(tag = True, tagStr = "plain text"),
			run_time = 0.01
		)

		cipher = Btext(strCipherText, color = cipherColor, width = plain.width, height = plain.height, position = midDiagramPos + diagramWidth*RIGHT/2)
		self.play(
			cipher.create(tag = True, tagStr = "cipher text"),
			run_time = 0.01
		)

		key = Key(unknownKeyString, position = midDiagramPos)
		# + diagramWidth/3 * LEFT)
		self.play(
			key.createRectangleKey(),
			run_time = 0.01
		)
		
		# shift plain to the left
		self.play(
			key.shiftRec(diagramWidth/3 * LEFT, noBrace = False),
			plain.shift(diagramWidth/3 * LEFT),
			cipher.shift(diagramWidth/3*RIGHT)
		)
		self.wait()


		guess = Btext(
			constructRandomString(), 
			position = 2 * key.position - plain.position, 
			width = plain.width, 
			height = plain.height
		)


		self.play(
			#key.changeText(zeroString),
			guess.create(noText = True),
			key.createRedArrow(),
			#run_time = 1
		)

		self.next_section(skip_animations=False)

		# self.play(
		# 	Succession(
		# 		AnimationGroup(
		# 			guess.changeText(constructRandomString(), empty = True),
		# 		)
		# 	)

		# )


		# first go one by one
		waitingTimes = [] 
		L = 10 # víc 
		for i in range(L):
			waitingTimes.append(
				max((1.0 - (i * 1.0 / L)), minTime)
			)
		for i in range(1000):
			waitingTimes.append(minTime)
		
		cumTimes = np.cumsum(np.array(waitingTimes))
		np.insert(cumTimes, 0, 0)
		
		anims = []

		

		cnt = 0
		actString = "000..." + '{0:05b}'.format((cnt % 32))
		self.play( # first one is done differently due to weird behaviour otherwise
			key.changeText(actString),
			guess.changeText(constructRandomString(), empty = True),
			run_time  = waitingTimes[0]
		)

		for t in waitingTimes[1:L]:
			actString = "000..." + '{0:05b}'.format((cnt % 32))
		
			self.add_sound(random_click_file(), time_offset=cumTimes[cnt]- cumTimes[1])
			anims.append(
				Succession(
					Wait(cumTimes[cnt]- cumTimes[1]), 
					AnimationGroup(
						key.changeText(actString),
 						guess.changeText(constructRandomString()),
						run_time = t
					)
				)
			)
			cnt += 1

		# fast forward

		for big in range(5):
			for _ in range(invMinTime):
				actString = '{0:03b}'.format(big) + "..."
				for _ in range(5):
					actString += random.choice(["0", "1"])

				self.add_sound(random_click_file(), time_offset=cumTimes[cnt]- cumTimes[1])
				anims.append(
					Succession(
						Wait(cumTimes[cnt] - cumTimes[1]), 
						AnimationGroup(
							key.changeText(actString),
							guess.changeText(constructRandomString()),
							run_time = minTime
						)
					)
				)

				cnt += 1


		# we found the correct key

		self.add_sound(random_click_file(), time_offset=cumTimes[cnt]- cumTimes[1])
		anims.append(
			Succession(
				Wait(cumTimes[cnt] - cumTimes[1]),
				AnimationGroup(
					key.changeText(ourKeyString),
					guess.changeText(strCipherText),
					run_time = minTime
				)
			)
		)

		self.play(
			*anims
		)

		self.add_sound("audio/polylog_success.wav")
		self.play(
			Circumscribe(guess.border),
			Circumscribe(cipher.border)
		)

		self.wait()

		self.play(
			plain.remove(),
			plain.removeTag(),
			cipher.removeTag(),
			cipher.remove(),
			guess.remove(),
			key.remove()
		)

class TripleDes(Scene):
	def construct(self):
		"""
		: animace k tomuhle:
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
		DesText = Tex(r"{{ }}{{DES}}", color = textColor).move_to(DesTextPosition)
		TripleDes = Tex(r"{{Triple }}{{DES}}", color = textColor).move_to(DesTextPosition)
		
		self.add(DesText)


		keyStrings = [
			constructRandomKeyString(len1 = 2, len2 = 2),
			constructRandomKeyString(len1 = 2, len2 = 2),
			constructRandomKeyString(len1 = 2, len2 = 2)
		]

		plain = Btext(
			strPlainText, 
			position = 2*DOWN + 6*LEFT, 
			color = plainColor
		)

		self.play(Transform(DesText,TripleDes))

		self.wait()

		self.play(
			plain.create(tag = True, tagStr= "plain text")
		)

		self.wait()


		ciphers = [
			Btext(
				constructRandomString(), 
				position = pos.copy(), 
				width = plain.width,
				height = plain.height,
				color = col
			) for pos, col in zip(cipherPositions, [textColor, textColor, cipherColor])
		]

		keys = [
			Key(
				str, 
				position = pos.copy(), 
                keyTitle = "56 bits"
			) for (pos, str) in zip(keyPositions, keyStrings)
		]

		self.play(
			ciphers[0].create(),
			keys[0].createRectangleKey(),
			keys[0].createRedArrow(),
		)
		self.wait()

		self.play(
			ciphers[1].create(),
			keys[1].createRectangleKey(),
			keys[1].createRedArrow(),
		)
		self.wait()

		self.play(
			ciphers[2].create(tag = True, tagStr= "cipher text"),
			keys[2].createRectangleKey(),
			keys[2].createRedArrow(),
		)
		self.wait()

		topKeys = [
			Key(
				str, 
				position = pos.copy(),
                keyTitle = "56 bits"
			) for (pos, str) in zip(keyPositions, keyStrings)
		]
		self.play(*[key.createRectangleKey(noBrace=True) for key in topKeys], run_time = 0.01)
		
		self.wait()

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
		self.wait()
		
		newTitle = Tex(r"168 bit key", color = textColor).move_to(topKeys[1].title.get_center())
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

		DoubleDes = Tex("{{Double }}{{DES}}", color = textColor).move_to(DesText.get_center()+0.05*UP)

		txtShift = ciphers[1].border.get_center()[0]*RIGHT
		recShift = topKeys[1].border.get_center() - topKeys[1].border.get_left()


		newKeys = [[key.border.copy().shift(recShift), key.text.copy().shift(recShift)] for key in topKeys]
		newKeys[2][0].color = RED 
		newKeys[2][1].color = RED

		newTitle = Tex(r"112 bit key", color = textColor).move_to(topKeys[1].title.get_center())
		newBrace = Brace(Group(newKeys[0][1], newKeys[1][1]), UP, color = textColor).move_to(topKeys[1].brace)
		

		self.next_section(skip_animations= False)
		# change from triple to double
		self.play(
			keys[1].remove(),
			ciphers[1].remove(),
			FadeOut(topKeys[1].border),
			Unwrite(topKeys[1].text),
			Transform(DesText, DoubleDes),
		)
		self.wait()

		shft = ciphers[1].border.get_center()[0] * LEFT
		shft2 = topKeys[0].border.get_center()[0]*LEFT

		self.play(
			ciphers[0].shift(-shft),
			keys[0].shiftRec(-shft/2),
			keys[2].shiftRec(shft/2),
			topKeys[0].shiftRec(shft2/2, noBrace = True),
			topKeys[2].shiftRec(-shft2/2, noBrace = True),
			Transform(topKeys[1].brace, newBrace),
			Transform(topKeys[1].title, newTitle),
		)
		self.wait()

		# return 

		# self.play(
		# 	FadeOut(ciphers[2].border), *[FadeOut(txt) for txt in ciphers[2].lines], 
		# 	FadeOut(topKeys[2].border), FadeOut(topKeys[2].text),
		# 	FadeOut(keys[2].border), FadeOut(keys[2].text), FadeOut(keys[2].redArrow), FadeOut(keys[2].braceTitle),
		# 	Transform(topKeys[1].title, newTitle),
		# 	Transform(topKeys[1].brace, newBrace),
		# )
		# return

		# # shift to the right
		# self.play(
		# 	*[txt.shift(txtShift) for txt in ciphers+[plain]],
		# 	*[key.shiftRec(txtShift) for key in keys],
		# 	*flatten([
		# 		[Transform(key.border, border), 
		# 		Transform(key.text,text)]
		# 		for (key, [border, text]) in zip(topKeys, newKeys)
		# 	]),
		# 	ciphers[2].tagText.animate().shift(-txtShift)
		# )
		# self.play(
		# 	FadeOut(ciphers[2].tagText),
		# 	ciphers[1].addTag("cipher text"),
		# 	run_time = 0.001
		# )

		# self.wait()



		# highlight arrows

		self.remove(
			keys[0].redArrow,
			keys[2].redArrow
		)
		self.play(
			keys[0].createRedArrow(), 
			Circumscribe(ciphers[0].border),
		)
		self.wait()

		self.play(
			Circumscribe(ciphers[2].border),
			keys[2].createRedArrow()
		)
		self.wait()

		# write down the calculation

		# txt = Group(
		# 	Tex(
		# 		r"$2 \cdot 56 = 112$ bits",
		# 		color = textColor
		# 	),
		txt = Tex(
			r"$2^{112} \approx 10^{34}$",
			color = textColor
		).move_to(5*RIGHT + 2*UP)
		
		self.play(
			Write(txt)
		) 
		self.wait()

		# move to the middle

		self.play(
			Unwrite(txt),
			plain.move_to(posPlain.copy()+midDiagramPos - bottomDiagramPos),
			ciphers[2].move_to(posFinal+midDiagramPos - bottomDiagramPos),
			keys[0].remove(),
			keys[2].remove(),
			topKeys[0].removeRec(noBrace=True),
			topKeys[2].removeRec(noBrace=True),
			ciphers[0].remove(),
			Uncreate(topKeys[1].brace),
			Unwrite(topKeys[1].title),
		)
		self.wait()

		# self.play(
		# 	Unwrite(txt),
		# 	topKeys[0].removeRec(noBrace=True),
		# 	topKeys[1].removeRec(),
		# 	keys[0].changeTextandSize(zeroString, shift = midDiagramPos - bottomDiagramPos + 0.5 * LEFT),
		# 	keys[1].changeTextandSize(zeroString, shift = midDiagramPos - bottomDiagramPos + 0.5 * RIGHT),
		# 	plain.shift(midDiagramPos - bottomDiagramPos + 1 * LEFT),
		# 	ciphers[0].shift(midDiagramPos - bottomDiagramPos),
		# 	ciphers[1].shift(midDiagramPos - bottomDiagramPos + 1 * RIGHT),			
		# )


		# # bruteforce animation
		# self.next_section(skip_animations=False)

		# for i in range(1):
		# 	for big in range(4):
		# 		for _ in range(invMinTime):
		# 			actString = '{0:03b}'.format(big) + "..."
		# 			for _ in range(5):
		# 				actString += random.choice(["0", "1"])
		# 			self.play(
		# 				keys[1].changeText(actString),
		# 				ciphers[1].changeText(constructRandomString()),
		# 				run_time = minTime/2
		# 			)
		# 			self.wait(minTime/2)
		# 	self.play(
		# 		keys[0].changeText("000..." + '{0:05b}'.format(i+1)),
		# 		ciphers[0].changeText(constructRandomString()),
		# 		run_time = 0.01
		# 	)


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
			color = plainColor
		)
		self.play(
			plain.create(tag = True, tagStr="plain text"),
		)
		self.wait()

		cipher = Btext(
			constructRandomString(), 
			position = posFinal,
			width = plain.width,
			height = plain.height,
			color = cipherColor
		)
		self.play(
			cipher.create(tag = True, tagStr="cipher text"),
		)		
		self.wait()

		# generating all intermediate strings in a table


		key = Key(zeroString, position = posKey)

		self.play(
			key.createRectangleKey(),
			key.createRedArrow()
		)
		self.wait()

		topLeft = topDiagramPos + 1*RIGHT
		databasePositions = []
		databaseInters = []
		keyStrings = []
		
		w = 10
		h = 6

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
		cum_time = 0

		for it, (pos, keyString) in tqdm(list(enumerate(zip(databasePositions, keyStrings)))):
			curInter = Btext( 
				#strPlainText,
				constructRandomString(),
				position = posInter, 
				width = plain.width,
				height = plain.height,
				fill_color = config.background_color,
				fill_opacity = 1
			)
			databaseInters.append(curInter)

			anim = Succession(
				AnimationGroup(
					curInter.create(),
					run_time = 0.01
				),
				# AnimationGroup(
				# 	Wait()
				# ),
				AnimationGroup(
					AnimationGroup(
						curInter.move_to(pos),
						run_time = 0.3
					),
					AnimationGroup(
						key.changeText(keyString),
						run_time = minTime 
					),
					lag_ratio = 0.0
				)
			)
			anims.append(anim)

			self.add_sound(random_click_file(), time_offset=cum_time)
			cum_time += minTime * anim.run_time

		self.play(AnimationGroup(
			*anims, 
			lag_ratio = minTime
		))
		self.wait()

		self.next_section(skip_animations=False)

		# key disappears and database shifts

		shft = 5*LEFT
		self.play(
			key.remove()
		)
		self.play(
			*[
				bt.shift(shft) 
				for bt in databaseInters
			],
		)
		self.wait()

		# add brace

		databaseBrace = Brace(Group(databaseInters[-1].border, databaseInters[-1-w].border),RIGHT,color = textColor )
		#databaseBrace = Brace(databaseInters[w*h-1].border, RIGHT),
		databaseBraceText = Tex(r"$2^{56} \approx 10^{17}$ intermediate texts", color = textColor, font_size = fontSize).move_to(databaseBrace.get_center()).next_to(databaseBrace, RIGHT)
		databaseBraceGroup = Group(databaseBrace, databaseBraceText)
		
		self.play(
			Create(databaseBrace),
			Write(databaseBraceText)
		)
		self.wait()

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
		self.wait()
		
		# trying blue keys
		# first go one by one
		waitingTimes = []
		L = 0 
		for i in range(L):
			waitingTimes.append(
				max((1.0 - (i * 1.0 / L)), minTime)
			)
		for i in range(1000):
			waitingTimes.append(minTime)
		
		cumTimes = np.cumsum(np.array(waitingTimes))
		np.insert(cumTimes, 0, 0)
		
		anims = []

		cnt = 0
		for t in waitingTimes[:L]:
			actString = "000..." + '{0:05b}'.format((cnt % 32))

			self.add_sound(random_click_file(), time_offset=cumTimes[cnt])
			anims.append(
				Succession(
					Wait(cumTimes[cnt]), 
					AnimationGroup(
						key2.changeText(actString),
						inter.changeText(constructRandomString()),
						run_time = t
					)
				)
			)
			cnt += 1

		# fast forward

		for big in range(6):
			for _ in range(invMinTime):
				actString = '{0:03b}'.format(big) + "..."
				for _ in range(5):
					actString += random.choice(["0", "1"])
				
				self.add_sound(random_click_file(), time_offset=cumTimes[cnt])
				anims.append(
					Succession(
						Wait(cumTimes[cnt]), 
						AnimationGroup(
							key2.changeText(actString),
							inter.changeText(constructRandomString()),
							run_time = minTime
						)
					)
				)

				cnt += 1


		# we found the correct key



		hit = (2*w*h) // 3 + 2
		strLinesHit = databaseInters[hit].strLines.copy()
		inter2 = databaseInters[hit]

		# inter2 = Btext(
		# 	strLinesHit,
		# 	position = databaseInters[hit].position,
		# 	width = databaseInters[hit].width,
		# 	height = databaseInters[hit].height,
		# 	fill_color = config.background_color,
		# 	fill_opacity = 1
		# )

		anims.append(
			Succession(
				Wait(cumTimes[cnt]),
				AnimationGroup(
					key2.changeText("110...10010"),
					inter.changeText(strLinesHit),
					run_time = minTime
				)
			)
		)

		self.play(*anims)
		self.wait()

		#fade in the correct text

		inter2.position = databaseInters[hit].position
		inter2.border.move_to(inter2.position)
		inter2.lines.move_to(inter2.position)

		# self.play(
		# 	FadeIn(inter2.border),
		# 	AnimationGroup(
		# 		*[FadeIn(text) for text in inter2.lines],
		# 		#lag_ratio = 0.2
		# 	),
		# 	run_time = 1
		# )

		self.next_section(skip_animations=False)


		anims = []
		for it, inte in enumerate(databaseInters):
			if it == hit:
				anims.append(
					inte.shift(2.4*UP)
				)
			else:
				anims.append(
					inte.shift(0*UP)
				)

		self.play(
			*anims
		)
		self.wait()


		self.add_sound("audio/polylog_success.wav")
		self.play(
			Circumscribe(inter.border),
			Circumscribe(inter2.border)
		)
		self.wait()

		# remove all other texts
		self.play(
			*[datInter.remove() for datInter in databaseInters],
			inter2.move_to(inter2.position),
			Unwrite(databaseBraceText),
			Uncreate(databaseBrace)
		)

		self.play(
			inter.move_to((plain.position + cipher.position)/2),
			key2.moveRec(plain.position/4 + cipher.position*3.0/4),
			inter2.move_to((plain.position + cipher.position)/2 ),
		)
		self.wait()

		key = Key(
			constructRandomKeyString(),
			position = plain.position*3.0/4 + cipher.position/4
		)
		self.play(
			key.createRectangleKey(),
			key.createRedArrow()
		)
		self.wait()

		self.play(
			key2.removeBlueArrow(),
			key.removeRedArrow()
		)

		self.wait()

		# remove everything

		self.play(
			plain.remove(),
			plain.removeTag(),
			inter.remove(),
			inter2.remove(),
			cipher.remove(),
			cipher.removeTag(),
			key.remove(),
			key2.remove(),
			Unwrite(DesText)
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
