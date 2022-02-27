import sys
import random as rd

from screen import *
from control import *
from detect import *
from ui import *

class Task:
  def __init__(self):
    self.getWindowID()
    self.diceControl = DiceControl(self.hwndChild)
    self.detect = Detect("./image")

    self.board_dice = []
    self.detect_board_dice_img = []
    self.board_dice_lu = []
    self.merge_dice = []
    self.merge_dice_location = []

    self.targetDice = ["Healing", "Solar_O", "Rock", "Flash", "Mimic", "Blank", "Solar_X"]

    self.x = 90
    self.y = 477
    self.size = 49

  def getWindowID(self):
    self.hwnd = win32gui.FindWindow(None, "BlueStacks")
    self.hwndChild = win32gui.GetWindow(self.hwnd, win32con.GW_CHILD)

  def forAllDiceOnBoard(self, function):
    for i in range(3*5):
      row = i // 5
      col = i % 5
      function(i, row, col)

  def findMergeDice(self, count, location, orig_lu, mergeDice, exceptDice):
    rdidx = rd.randrange(count[mergeDice])
    srcidx = location[mergeDice][rdidx] + 1
    self.diceControl.dragPressDice(srcidx)
    time.sleep(0.2)
    _, canMergeImage = getScreenShot(self.hwndChild)
    time.sleep(0.2)
    canMergeImage = self.detect.Image2OpenCV(canMergeImage)
    self.diceControl.dragUpDice(srcidx)

    self.merge_dice = []
    self.merge_dice_location = []
    def detectMerge(i, row, col):
      img = self.detect.extractImage(canMergeImage, (self.x+col*self.size, self.y+row*self.size, 40, 40), ExtractMode.CENTER)
      img_lu = self.detect.getAverageLuminance(img)
      lu_offset = orig_lu[i] - img_lu
      canMerge = self.detect.canMergeDice(lu_offset)
      self.merge_dice.append(canMerge)
      if canMerge and self.board_dice[i] != 'Blank':
        if exceptDice is None or self.board_dice[i] not in exceptDice:
          self.merge_dice_location.append(i)
      if i != 0 and i % 5 == 0 :
        print("")
      print(f"{'O' if canMerge else 'X'} {orig_lu[i]:4.1f} / {img_lu:4.1f}  ", end="")

    self.forAllDiceOnBoard(detectMerge)
    print("")
    
    if len(self.merge_dice_location) > 0:
      dstidx = self.merge_dice_location[rd.randrange(0, len(self.merge_dice_location))] + 1
      if srcidx != dstidx:
        self.diceControl.mergeDice(srcidx, dstidx)
        time.sleep(1)
      
  def task(self):
    
    r, im = getScreenShot(self.hwndChild)
    im = self.detect.Image2OpenCV(im)

    self.board_dice = []
    self.detect_board_dice_img = []
    self.board_dice_lu = []
    def detectDice(i, row, col):
      dice_xy = (self.x+col*self.size, self.y+row*self.size)
      img = self.detect.extractImage(im, (dice_xy[0], dice_xy[1], 50, 50), ExtractMode.CENTER)
      res = self.detect.detectDice(img, self.targetDice)

      dice_lu = self.detect.getAverageLuminance(self.detect.extractImage(im, (dice_xy[0], dice_xy[1], 40, 40), ExtractMode.CENTER))

      self.detect_board_dice_img.append(img)
      self.board_dice.append(res[0])
      self.board_dice_lu.append(dice_lu)

      if i != 0 and i % 5 == 0 :
        print("")
      print(f"{res[0]:10}", end="")

    self.forAllDiceOnBoard(detectDice)
    print("")

    summon_lu = self.detect.getAverageLuminance(self.detect.extractImage(im, (340, 580, 3, 3), ExtractMode.CENTER))
    sp_lu = self.detect.getAverageLuminance(self.detect.extractImage(im, (40, 580, 3, 3), ExtractMode.CENTER))
    level_1_lu = self.detect.getAverageLuminance(self.detect.extractImage(im, (70, 645, 5, 5), ExtractMode.CENTER))
    level_2_lu = self.detect.getAverageLuminance(self.detect.extractImage(im, (130, 645, 5, 5), ExtractMode.CENTER))
    level_3_lu = self.detect.getAverageLuminance(self.detect.extractImage(im, (190, 645, 5, 5), ExtractMode.CENTER))
    level_4_lu = self.detect.getAverageLuminance(self.detect.extractImage(im, (250, 645, 5, 5), ExtractMode.CENTER))
    level_5_lu = self.detect.getAverageLuminance(self.detect.extractImage(im, (310, 645, 5, 5), ExtractMode.CENTER))

    count = {}
    for dice in self.targetDice:
      count[dice] = 0
    for dice in self.board_dice:
      count[dice] += 1
    location = {}
    for type in count:
      location[type] = []
    for idx, dice in enumerate(self.board_dice):
      location[dice].append(idx)
    count_sorted = sorted(count.items(), key=lambda x : x[1], reverse=True)

    # flag
    hasSolar = count['Solar_O'] >= 4
    hasMimic = count['Mimic'] > 0
    hasStone = count['Rock'] > 0
    noBlank = count['Blank'] == 0

    countRock = count['Rock']
    countSolar = count['Solar_O'] + count['Solar_X']
    countBlank = count['Blank']
    countTotal = sum([x[1] for x in count.items() if x[0] != 'Blank'])

    earlyGame = countTotal <= 10

    if not hasSolar and hasMimic and not earlyGame:
      self.findMergeDice(count, location, self.board_dice_lu, 'Mimic', (None if countSolar > 4 else ['Solar_X', 'Solar_O']))
    if not hasSolar and hasStone and countRock >= 2 and not earlyGame:
      self.findMergeDice(count, location, self.board_dice_lu, 'Rock', ['Mimic'])
    if not hasSolar and countSolar == 6 and not earlyGame:
      self.findMergeDice(count, location, self.board_dice_lu, 'Solar_X', ['Mimic'])
    if not hasSolar and noBlank:
      self.findMergeDice(count, location, self.board_dice_lu, count_sorted[0][0], ['Mimic'])

    if self.detect.canLevelSP(sp_lu):
      self.diceControl.levelUpSP()
    elif self.detect.canSummon(summon_lu) and (not hasSolar or countBlank >= 3):
      self.diceControl.summonDice()
    elif self.detect.canLevelDice(level_3_lu):
      self.diceControl.levelUpDice(3)
    elif self.detect.canLevelDice(level_1_lu):
      self.diceControl.levelUpDice(1)
    elif self.detect.canLevelDice(level_4_lu):
      self.diceControl.levelUpDice(4)

    print(f'Summon: {summon_lu} --- {self.detect.canSummon(summon_lu)}')
    print(f'SP: {sp_lu} --- {self.detect.canLevelSP(sp_lu)}')
    print(f'Level_1: {level_1_lu} --- {self.detect.canLevelDice(level_1_lu)}')
    print(f'Level_2: {level_2_lu} --- {self.detect.canLevelDice(level_2_lu)}')
    print(f'Level_3: {level_3_lu} --- {self.detect.canLevelDice(level_3_lu)}')
    print(f'Level_4: {level_4_lu} --- {self.detect.canLevelDice(level_4_lu)}')
    print(f'Level_5: {level_5_lu} --- {self.detect.canLevelDice(level_5_lu)}')

    sys.stdout.flush()
    print("\n================")