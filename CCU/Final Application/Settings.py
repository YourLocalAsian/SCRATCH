from enum import IntEnum
from bluezero import adapter
from bluezero import central

import struct
import threading
import time 
import sys
import random
import cv2
import numpy as np

# HUD Services
HUD_SERVER_SRV = '843b4b1e-a8e9-11ed-afa1-0242ac120002' 
HUD_MODE_CHAR_UUID = '10c4bfee-a8e9-11ed-afa1-0242ac120002'
HUD_POWER_CHAR_UUID = '10c4c44e-a8e9-11ed-afa1-0242ac120002'
HUD_POI_X_CHAR_UUID = '10c4c69c-a8e9-11ed-afa1-0242ac120002'
HUD_POI_Y_CHAR_UUID = '10c4c696-a8e9-11ed-afa1-0242ac120002'
HUD_ANGLE_CHAR_UUID = '10c4c886-a8e9-11ed-afa1-0242ac120002'
HUD_AUDIO_CHAR_UUID = '10c4ce76-a8e9-11ed-afa1-0242ac120002'
HUD_IMAGE_CHAR_UUID = '10c4d3a8-a8e9-11ed-afa1-0242ac120002'
HUD_FSM_CHAR_UUID = '10c4d3a9-a8e9-11ed-afa1-0242ac120002'

# Cue Stick Services
STICK_SERVER_SRV = '91bad492-b950-4226-aa2b-4ede9fa42f59' 
STICK_ACC_CHAR_UUID = 'ca73b3ba-39f6-4ab3-91ae-186dc9577d99'
STICK_ROLL_CHAR_UUID = '1d710a64-929a-11ed-a1eb-0242ac120002'
STICK_PITCH_CHAR_UUID = '1d710d8e-929a-11ed-a1eb-0242ac120002'
STICK_YAW_CHAR_UUID = '1d710f6e-929a-11ed-a1eb-0242ac120002'
STICK_BUTTON_CHAR_UUID = '1d7110c2-929a-11ed-a1eb-0242ac120002'
STICK_FSM_CHAR_UUID = '1d7111da-929a-11ed-a1eb-0242ac120002'

# Glove Services
GLOVE_SERVER_SRV = 'bb9246d2-98fc-11ed-a8fc-0242ac120002' 
GLOVE_YAW_CHAR_UUID = 'bb924d12-98fc-11ed-a8fc-0242ac120002'
GLOVE_DISTANCE_CHAR_UUID = 'bb925050-98fc-11ed-a8fc-0242ac120002'

# VISION Services
VISION_SRV = '' # TODO: Talk to Noah or create these and give it to him
ANGLE_CHAR_UUID = '' # TODO
STRENGTH_CHAR_UUID = '' # TODO

# BLE Connection Flages
HUD_connected = False
stick_connected = False
glove_connected = False
VISION_connected = True # ! Change to False later

#central device
HUD_monitor = None 
glove_monitor = None
stick_monitor = None 
VISION_monitor = None
bt_thread = None

# HUD Characteristics & Variables
HUD_mode_char = None
HUD_power_char = None
HUD_poi_x_char = None
HUD_poi_y_char = None
HUD_angle_char = None
HUD_fsm_char = None
HUD_audio_char = None
HUD_image_char = None
HUD_notification_cb_set = False
image_counter = 0
actual_x = 0
actual_y = 0
received_integers = []

# Glove Characteristics
glove_yaw_char = None
glove_distance_char = None
glove_notification_cb_set = False

# Stick Characteristics
stick_acc_char = None
stick_roll_char = None
stick_pitch_char = None
stick_yaw_char = None
stick_button_char = None
stick_fsm_char = None
stick_notification_cb_set = False
stick_received_acceleration = []

# TODO: make BLE characteristics for VISION communication
VISION_angle_char = None
VISION_strength_char = None
VISION_next_shot_char = None
VISION_notification_cb_set = False

# CCU State Variables
user_impaired = False

class OperatingMode(IntEnum):
    GAME = 0
    TRAINING = 1

operation_mode = OperatingMode.GAME

class ButtonInput(IntEnum):
    UP = 0
    DOWN = 1
    LEFT = 2
    RIGHT = 3
    A = 4
    B = 5
    NONE = 6

class StickStates(IntEnum):
    NOT_READY = 0
    READY = 1
    WAITING = 2
    TAKING_SHOT = 3
    SHOT_TAKEN = 4
    PAUSED = 5
    SET_NON = 6
    SET_BLD = 7

class HudStates(IntEnum):
    INITIAL = 0
    BLIND = 1
    NB_TARGET = 2
    TAKE_PICTURE = 3
    ACTUAL = 4

# Blind Shot Mode Variables
ANGLE_THRESHOLD = 3.0
DESIRED_DISTANCE = 1.0
DISTANCE_THRESHOLD = 1.0

# Prompt Numbers
WELCOME = 0
ASK_IMPAIRED = 1
BLIND_SELECTED = 2
NONBLIND_SELECTED = 3
SELECT_OP = 4
ENTERING_GM = 5
ENTERING_TM = 6

MOVE_FOR_CALIBRATION = 7
ZERO_OUT_GLOVE = 8
GLOVE_ZEROED_OUT = 9
TURN_LEFT = 10
TURN_RIGHT = 11
MOVE_FORWARD = 12
MOVE_BACKWARD = 13
AIM_HIGHER = 14
AIM_LOWER = 15
CHECKING_GLOVE_ANGLE = 16
GLOVE_ANGLE_CORRECT = 17
CHECKING_GLOVE_DISTANCE = 18
GLOVE_DISTANCE_CORRECT = 19
CHECKING_STICK_PITCH = 20
STICK_PITCH_CORRECT = 21
TAKE_SHOT = 22
NICE_SHOT = 23
MEAN_ONE = 24
MEAN_TWO = 25
CALIBRATE_CUE = 26
CUE_CALIBRATED = 27

# Blocking Flags
new_glove_angle_received = False
new_glove_dist_received = False
new_stick_pitch_received = False
new_stick_button_received = False
new_stick_fsm_received = False