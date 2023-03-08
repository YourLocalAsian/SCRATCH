from enum import Enum

# HUD Services
HUD_SRV = '843b4b1e-a8e9-11ed-afa1-0242ac120002' 
MODE_CHAR_HUD_UUID = '10c4bfee-a8e9-11ed-afa1-0242ac120002'
POWER_CHAR_HUD_UUID = '10c4c44e-a8e9-11ed-afa1-0242ac120002'
POI_X_CHAR_HUD_UUID = '10c4c69c-a8e9-11ed-afa1-0242ac120002'
POI_Y_CHAR_HUD_UUID = '10c4c696-a8e9-11ed-afa1-0242ac120002'
ANGLE_CHAR_HUD_UUID = '10c4c886-a8e9-11ed-afa1-0242ac120002'
AUDIO_CHAR_HUD_UUID = '10c4ce76-a8e9-11ed-afa1-0242ac120002'
IMAGE_CHAR_HUD_UUID = '10c4d3a8-a8e9-11ed-afa1-0242ac120002'
FSM_CHAR_HUD_UUID = '10c4d3a9-a8e9-11ed-afa1-0242ac120002'

# Cue Stick Services
STICK_SRV = '91bad492-b950-4226-aa2b-4ede9fa42f59' 
ACC_CHAR_STICK_UUID = 'ca73b3ba-39f6-4ab3-91ae-186dc9577d99'
ROLL_CHAR_STICK_UUID = '1d710a64-929a-11ed-a1eb-0242ac120002'
PITCH_CHAR_STICK_UUID = '1d710d8e-929a-11ed-a1eb-0242ac120002'
YAW_CHAR_STICK_UUID = '1d710f6e-929a-11ed-a1eb-0242ac120002'
BUTTON_CHAR_STICK_UUID = '1d7110c2-929a-11ed-a1eb-0242ac120002'
FSM_CHAR_STICK_UUID = '1d7111da-929a-11ed-a1eb-0242ac120002'

# Glove Services
GLOVE_SRV = 'bb9246d2-98fc-11ed-a8fc-0242ac120002'
YAW_CHAR_GLOVE_UUID = 'bb924d12-98fc-11ed-a8fc-0242ac120002'
DIST_CHAR_GLOVE_UUID = 'bb925050-98fc-11ed-a8fc-0242ac120002'

# VISION Services
VISION_SRV = '' # TODO
ANGLE_CHAR_UUID = '' # TODO
STRENGTH_CHAR_UUID = '' # TODO

# BLE Connection Variables
hud_connected = False
stick_connected = False
glove_connected = False
vision_connected = False

# CCU State Variables
user_impaired = False

class OperatingMode(Enum):
    GAME = 0
    TRAINING = 1

operation_mode = OperatingMode.GAME

class ButtonInput(Enum):
    UP = 0
    DOWN = 1
    LEFT = 2
    RIGHT = 3
    A = 4
    B = 5
    NONE = 6