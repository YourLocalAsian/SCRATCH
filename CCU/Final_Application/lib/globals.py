from lib.constants import OperatingMode

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
VISION_simulated = True

# CCU State Variables
user_impaired = False
operation_mode = OperatingMode.GAME

# Blocking Flags
new_glove_angle_received = False
new_glove_dist_received = False
new_stick_pitch_received = False
new_stick_button_received = False
new_stick_fsm_received = False
callbacks_set = 0

# Demo Variables
demo_mode = False
demo_counter = 0