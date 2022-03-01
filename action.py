from typing import Callable, Dict, List
import abc
import time

from control import *

class Action:
  @staticmethod
  @abc.abstractmethod
  def action(self,
    count: Dict[str, int], count_sorted: Dict[str, int], location: Dict[str, List], 
    canSummon: bool, canLevelSp: bool, canLevelDice: List,
    countTotal: int):
    return NotImplemented

import random as rd

class MyAction(Action):
  @staticmethod
  def randomMerge( diceControl: DiceControl, findMergeDice: Callable,
    count, location, mergeDice, exceptDice):
    rdidx = rd.randrange(count[mergeDice])
    srcidx = location[mergeDice][rdidx] + 1

    merge_dice_location = findMergeDice(srcidx, exceptDice)

    if len(merge_dice_location) > 0:
      dstidx = merge_dice_location[rd.randrange(0, len(merge_dice_location))] + 1
      if srcidx != dstidx:
        diceControl.mergeDice(srcidx, dstidx)
        time.sleep(1)

  @staticmethod
  def action(
    diceControl: DiceControl, findMergeDice: Callable,
    count: Dict[str, int], count_sorted: Dict[str, int], location: Dict[str, List], 
    canSummon: bool, canLevelSp: bool, canLevelDice: List,
    countTotal: int):

    # flag
    hasSolar = count['Solar_O'] >= 4
    hasMimic = count['Mimic'] > 0
    hasStone = count['Rock'] > 0
    noBlank = count['Blank'] == 0

    countRock = count['Rock']
    countSolar = count['Solar_O'] + count['Solar_X']
    countBlank = count['Blank']

    earlyGame = countTotal <= 10

    if not hasSolar and hasMimic and not earlyGame:
      MyAction.randomMerge(diceControl, findMergeDice,
        count, location, 'Mimic', (None if countSolar > 4 else ['Solar_X', 'Solar_O'])) 
    if not hasSolar and hasStone and countRock >= 2 and not earlyGame:
      MyAction.randomMerge(diceControl, findMergeDice,
        count, location, 'Rock', ['Mimic'])
    if not hasSolar and countSolar == 6 and not earlyGame:
      MyAction.randomMerge(diceControl, findMergeDice,
        count, location, 'Solar_X', ['Mimic'])
    if not hasSolar and noBlank:
      MyAction.randomMerge(diceControl, findMergeDice,
        count, location, count_sorted[0][0], ['Mimic'])

    if canLevelSp:
      diceControl.levelUpSP()
    elif canSummon and (not hasSolar or countBlank >= 3):
      diceControl.summonDice()
    elif canLevelDice[2]:
      diceControl.levelUpDice(3)
    elif canLevelDice[0]:
      diceControl.levelUpDice(1)
    elif canLevelDice[3]:
      diceControl.levelUpDice(4)