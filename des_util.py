from os import wait
import string
from manim import *
from manim.utils import tex
import numpy as np
import math
import textwrap
import random
from solarized import *

# Use our fork of manim_rubikscube!
from manim_rubikscube import *
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
	r"funny text",
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
oneString = "000...00001"
ourKeyString = "101...01110"
randKeyString = constructRandomKeyString()
unknownKeyString = "???...?????"



# text object
class Btext:
	def __init__(self, strLines, position = np.array([0, 0, 0]), width = None, height = None, scale = 1.0, fill_color = None, fill_opacity = 0.0):
		self.position = position
		self.width = width
		self.height = height
		self.strLines = strLines
		self.fill_color = fill_color
		self.fill_opacity = fill_opacity
		self.tag = False

		self.lines = Group(*[
			Tex(
				str, 
				color = textColor, 
				font_size = smallFontSize,
			).scale(scale) for str in strLines
		]).arrange(DOWN, center = False, aligned_edge = LEFT, buff = textPadding)

		self.border = constructTextBorder(
			insideObject = self.lines,
			width = self.width,
			height = self.height, 
			fill_color = self.fill_color,
			fill_opacity = self.fill_opacity,
		).scale(scale)

		# self.lines = Group(*[
		# 	Tex(
		# 		str, 
		# 		color = textColor, 
		# 		font_size = smallFontSize,
		# 	) for str in strLines
		# ]).arrange(DOWN, center = False, aligned_edge = LEFT, buff = textPadding)


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

	def create(self, position = None, noText = False, tag = False, tagStr = ""):
		if position is not None:
			self.position = position.copy()
		
		self.border.move_to(self.position)
		self.lines.move_to(self.position)
		
		anim = []

		if noText == False:
			anim.append(AnimationGroup(
					*[Write(text) for text in self.lines],
					lag_ratio = 0.2
				)
			)

		if tag == True:
			self.tag = True
			self.tagText = Tex(
				tagStr,
				color = textColor,
				font_size = fontSize
			).move_to(
				self.border.get_center()
			).next_to(self.border, DOWN)

			anim.append(
				Write(self.tagText)
			)

		return AnimationGroup(

			AnimationGroup(
				Create(self.border),
				run_time = 10
			),

			*anim, 
		)

	def highlight(self):
		animl = [
			self.border.animate().set_z_index(9999999)#.set_color(RED) # TODO zmenit
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
			color = textColor,
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
		self.title = Tex("56 bits", color = textColor).scale(scale)
		self.braceTitle = Group(self.brace, self.title).arrange(UP)

		self.border = Rectangle(
			width = self.text.get_right()[0] - self.text.get_left()[0] + padding, 
			height = self.text.get_top()[1] - self.text.get_bottom()[1] + padding, 
			color = keyColor
		).scale(scale)
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
		newTitle = Tex("56 bits", color = textColor).move_to(self.title.get_center())
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

