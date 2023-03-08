# Import Statements

# Constant Definitions

# Global Variable Declarations

# BLE STUFF
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
GLOVE_SRV = ''
YAW_CHAR_GLOVE_UUID = ''
BUTTON_CHAR_GLOVE_UUID = ''

# VISION Services
VISION_SRV = ''
ANGLE_CHAR_UUID = ''
STRENGTH_CHAR_UUID = ''

# Function Prototypes

# Overall CCU Functions
def scan_for_devices():
    return 0

def on_disconnect():
    return 0

# HUD Interactions
def connect_to_hud():
    return 0

def receive_image():
    return 0

def computer_vision():
    return 0

# Cue Stick
def connect_to_stick():
    return 0

def on_new_acc_stick():
    return 0

def on_new_roll_stick():
    return 0

def on_new_pitch_stick():
    return 0

def on_new_yaw_stick():
    return 0

def on_new_button_stick():
    return 0

def on_new_fms():
    return 0

# Glove
def connect_to_glove():
    return 0

def on_new_dist_glove():
    return 0

def on_new_yaw_glove():
    return 0

if __name__ == '__main__':
    print("Hello World!")