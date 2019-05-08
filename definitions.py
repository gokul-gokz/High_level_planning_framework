"""
This is a $(PROJECT_ROOT) level file used to provide resource pathing to all other files in the project.

It is meant to prevent/mitigate any unsustainable hard-coding of file paths.  Note:  this means that any file within
this project is expected to be run from the "." directory containing this file.  Your mileage will vary if you ignore
this advice.

Gunnar Horve <gunnarhorve@gmail.com>
Last Update: 04/30/2018
"""

import os

ROOT_DIR = os.path.dirname(os.path.abspath(__file__)) # This is your Project Root
RES_PATH = ROOT_DIR + "/res"
HERO_PATH = RES_PATH + "/hero.png"
MAP_PATH = RES_PATH + "/map.tmx"

DATA_PATH = ROOT_DIR + "/game/data_generation"
PPDDL_PATH = ROOT_DIR + "/PPDDL_Generation/option_data.p"
DATA_POOLING_DIR = DATA_PATH + "/records"               # used for saving individual data runs to
SPAWN_PATH = DATA_PATH + "/valid_spawns.json"           # used for spawning in hero
TRAINING_DATA = DATA_PATH + "/records.p"                # combination of all data in POOLING_DIR

