from enum import IntEnum

class ControlMode(IntEnum):
  WIN32API = 0
  ADB = 1

class Emulator(IntEnum):
  BLUESTACKS = 0
  NOX = 1

class ExtractMode(IntEnum):
  LEFTTOP = 0
  CENTER = 1

class DetectDiceMode(IntEnum):
  HIST = 0
  TEMPLATE = 1
  DHASH = 2
  MSSSIM = 3
  COMBINE = 4

class BattleMode(IntEnum):
  BATTLE_1V1 = 0
  BATTLE_2V2 = 1