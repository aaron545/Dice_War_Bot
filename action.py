from typing import Callable, Dict, List
import abc
import time

from control import *

class Action:
  @staticmethod
  @abc.abstractmethod
  def action(self,
    count: Dict[str, int], count_sorted: Dict[str, int], location: Dict[str, List], boardDice: list, 
    canSummon: bool, canLevelSp: bool, canLevelDice: List,
    countTotal: int, boardDiceStar: list):
    return NotImplemented

import random as rd

class MyAction(Action):
  @staticmethod
  def randomMerge(diceControl: DiceControl, findMergeDice: Callable,
    count, location, mergeDice, exceptDice):
    if count[mergeDice] <= 0: return
    rdidx = rd.randrange(count[mergeDice])
    srcidx = location[mergeDice][rdidx] + 1

    merge_dice_location = findMergeDice(srcidx, exceptDice)

    if len(merge_dice_location) > 0:
      dstidx = merge_dice_location[rd.randrange(0, len(merge_dice_location))] + 1
      if srcidx != dstidx:
        diceControl.mergeDice(srcidx, dstidx)
        time.sleep(1)

  @staticmethod
  def orderMerge(diceControl: DiceControl, findMergeDice: Callable,
    count, location, boardDice, mergeDice, exceptDice, order):
    if count[mergeDice] <= 0: return
    rdidx = rd.randrange(count[mergeDice])
    srcidx = location[mergeDice][rdidx] + 1

    merge_dice_location = findMergeDice(srcidx, exceptDice)
    
    if len(merge_dice_location) > 0:
      merge_dice_location = sorted(merge_dice_location, key= lambda x: 99999 if boardDice[x] not in order else order.index(boardDice[x]))
      dstidx = merge_dice_location[0] + 1
      if srcidx != dstidx:
        diceControl.mergeDice(srcidx, dstidx)
        time.sleep(1)

  hasSummonFirstDice = False
  hasLevelUpFirstSp = False
  hasLevelUpSecondThirdSp = 0
  
  @staticmethod
  def init():
    MyAction.hasSummonFirstDice = False
    MyAction.hasLevelUpFirstSp = False
    MyAction.hasLevelUpSecondThirdSp = 0

  @staticmethod
  def action(
    diceControl: DiceControl, findMergeDice: Callable,
    count: Dict[str, int], count_sorted: Dict[str, int], location: Dict[str, List], boardDice: list,
    canSummon: bool, canLevelSp: bool, canLevelDice: List,
    countTotal: int, boardDiceStar: list):

    # flag
    muchPop_Gun = count['Pop_Gun'] >= 5
    # hasMimic = count['Mimic'] > 0
    hasFire = count['Fire'] > 0
    noBlank = count['Blank'] == 0
    hasSupplement = count['Supplement'] > 0

    countFire = count['Fire']
    countHealing = count['Healing']
    countIce = count['Ice']
    # countElectric = count['Electric']
    # countSummoner = count['Summoner']
    # countSlingshot = count['Slingshot']
    # countGun = count['Gun']
    countBlank = count['Blank']
    countTotal = sum([v for k, v in count.items() if k != 'Blank'])
    earlyGame = countTotal <= 12
    
    team = ['Fire','Healing','Ice','Pop_Gun','Supplement']
    # star_1_Pop_Gun_Loc = []
    # Pop_Gun_Loc = location["Pop_Gun"]
    
    def findStarCount(dice:str, star: int):
      star_Loc = []
      dice_Loc = location[dice] 
      for loc in dice_Loc:
            if boardDiceStar[loc] == star:
              star_Loc.append(loc)
      return star_Loc
    # if not hasSolar and hasMimic and not earlyGame:
    #   MyAction.orderMerge(diceControl, findMergeDice,
    #     count, location, boardDice, 'Mimic', (None if countSolar > 4 else ['Solar_X', 'Solar_O']),
    #     ['Rock', 'Mimic']) 
    # if not hasSolar and hasStone and countRock >= 2 and not earlyGame:
    #   MyAction.randomMerge(diceControl, findMergeDice,
    #     count, location, 'Rock', ['Mimic'])
    # if not hasSolar and countSolar == 6 and not earlyGame:
    #   MyAction.randomMerge(diceControl, findMergeDice,
    #     count, location, 'Solar_X', ['Mimic'])
    # if not hasSolar and noBlank:
    #   MyAction.randomMerge(diceControl, findMergeDice,
    #     count, location, count_sorted[0][0], ['Mimic'])
    
    if not MyAction.hasSummonFirstDice:
      if canSummon:
        diceControl.summonDice()
        MyAction.hasSummonFirstDice = True
    elif not MyAction.hasLevelUpFirstSp :
      if canLevelSp:
        diceControl.levelUpSP()
        MyAction.hasLevelUpFirstSp = True    
    else:
      if canLevelSp:
        diceControl.levelUpSP()
      if canLevelDice[0] and muchPop_Gun:
        diceControl.levelUpDice(1)
      if canSummon:
        diceControl.summonDice()
      if noBlank and MyAction.hasLevelUpSecondThirdSp < 2:
        if canLevelSp:
          diceControl.levelUpSP()
          MyAction.hasLevelUpSecondThirdSp += 1
      else:
        # if hasMimic and not earlyGame:
        #   MyAction.randomMerge(diceControl, findMergeDice, count, location, 'Mimic', ['Pop_Gun'])
        if hasSupplement:
          MyAction.orderMerge(diceControl, findMergeDice,count, location, boardDice, 'Supplement', team[0:3], team[3:5])
        if hasFire and countFire >= 2 and noBlank:
          MyAction.randomMerge(diceControl, findMergeDice, count, location, 'Fire', ['Mimic'])
        if countIce >= 2 and noBlank:
          MyAction.randomMerge(diceControl, findMergeDice, count, location, 'Ice', ['Mimic'])

        # if countGun >= 2 and noBlank:
        #   star_1_Gun_Loc = findStarCount("Gun", 1)
        #   if len(star_1_Gun_Loc) >= 2:
        #     diceControl.mergeDice(star_1_Gun_Loc[0] + 1, star_1_Gun_Loc[1] + 1)
        #   star_2_Gun_Loc = findStarCount("Gun", 2)
        #   if len(star_2_Gun_Loc) >= 2:
        #     diceControl.mergeDice(star_2_Gun_Loc[0] + 1, star_2_Gun_Loc[1] + 1)

        if countHealing >= 2 and noBlank:
          MyAction.randomMerge(diceControl, findMergeDice, count, location, 'Healing', ['Mimic'])
        if countBlank == 0:         
          star_1_Pop_Gun_Loc = findStarCount("Pop_Gun", 1)
          if len(star_1_Pop_Gun_Loc) >= 2:
            diceControl.mergeDice(star_1_Pop_Gun_Loc[0] + 1, star_1_Pop_Gun_Loc[1] + 1)
    
    time.sleep(1)