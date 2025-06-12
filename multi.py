import digitalio
import board
import usb_hid
import time
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.mouse import Mouse
from adafruit_hid.keycode import Keycode
from adafruit_hid.consumer_control import ConsumerControl
from adafruit_hid.consumer_control_code import ConsumerControlCode

print("== Pi Pico Multifunction Knob with Windows Shortcuts Buttons ==")

# Pin Definitions
CLK_PIN = board.GP4
DT_PIN = board.GP3
SW_PIN = board.GP2
BTN1_PIN = board.GP9
BTN2_PIN = board.GP8
BTN3_PIN = board.GP7
BTN4_PIN = board.GP19
BTN5_PIN = board.GP20
BTN6_PIN = board.GP21
BTN7_PIN = board.GP22
BTN8_PIN = board.GP26
BTN9_PIN = board.GP27

# Variables
clk_last = None
currentMode = 0
totalMode = 3

# HID Devices
cc = ConsumerControl(usb_hid.devices)
mouse = Mouse(usb_hid.devices)
keyboard = Keyboard(usb_hid.devices)

# Rotary Encoder Pins
clk = digitalio.DigitalInOut(CLK_PIN)
clk.direction = digitalio.Direction.INPUT

dt = digitalio.DigitalInOut(DT_PIN)
dt.direction = digitalio.Direction.INPUT

sw = digitalio.DigitalInOut(SW_PIN)
sw.direction = digitalio.Direction.INPUT
sw.pull = digitalio.Pull.UP

# Buttons Pins
btn_pins = [BTN1_PIN, BTN2_PIN, BTN3_PIN, BTN4_PIN, BTN5_PIN, BTN6_PIN, BTN7_PIN, BTN8_PIN, BTN9_PIN]
buttons = []
for pin in btn_pins:
    button = digitalio.DigitalInOut(pin)
    button.direction = digitalio.Direction.INPUT
    button.pull = digitalio.Pull.DOWN
    buttons.append(button)

# Onboard LED for Feedback
led = digitalio.DigitalInOut(board.LED)
led.direction = digitalio.Direction.OUTPUT

# Helper Functions
def millis():
    return time.monotonic() * 1000

def ccw():
    print("CCW")
    if currentMode == 0:  # Volume decrement
        cc.send(ConsumerControlCode.VOLUME_DECREMENT)
    elif currentMode == 1:  # Horizontal scroll right
        keyboard.press(Keycode.SHIFT)
        mouse.move(wheel=-1)
        keyboard.release(Keycode.SHIFT)
    elif currentMode == 2:  # Brightness decrement
        cc.send(ConsumerControlCode.BRIGHTNESS_DECREMENT)

def cw():
    print("CW")
    if currentMode == 0:  # Volume increment
        cc.send(ConsumerControlCode.VOLUME_INCREMENT)
    elif currentMode == 1:  # Horizontal scroll left
        keyboard.press(Keycode.SHIFT)
        mouse.move(wheel=1)
        keyboard.release(Keycode.SHIFT)
    elif currentMode == 2:  # Brightness increment
        cc.send(ConsumerControlCode.BRIGHTNESS_INCREMENT)

def long_press():
    print("Entering Sleep Mode")
    led.value = True
    keyboard.press(Keycode.ALT)
    keyboard.press(Keycode.F4)
    keyboard.release_all()
    time.sleep(0.5)
    led.value = False

def indicate_mode_change():
    print(f"Mode: {currentMode}")
    for _ in range(currentMode + 1):
        led.value = True
        time.sleep(0.2)
        led.value = False
        time.sleep(0.2)

def handle_button_actions():
    for i, btn in enumerate(buttons):
        if btn.value:
            print(f"Button {i + 1} pressed")
            # Windows shortcuts for each button
            if i == 0:  # Button 1: Open File Explorer (Win + E)
                keyboard.send(Keycode.WINDOWS, Keycode.E)
            elif i == 1:  # Button 2: Minimize All Windows (Win + M)
                keyboard.send(Keycode.WINDOWS, Keycode.M)
            elif i == 2:  # Button 3: Lock the Screen (Win + L)
                keyboard.send(Keycode.WINDOWS, Keycode.L)
            elif i == 3:  # Button 4: Open Task Manager (Ctrl + Shift + Esc)
                keyboard.send(Keycode.CONTROL, Keycode.SHIFT, Keycode.ESCAPE)
            elif i == 4:  # Button 5: Screenshot (Win + Print Screen)
                keyboard.send(Keycode.WINDOWS, Keycode.PRINT_SCREEN)
            elif i == 5:  # Button 6: Open Settings (Win + I)
                keyboard.send(Keycode.WINDOWS, Keycode.I)
            elif i == 6:  # Button 7: Copy (Ctrl + C)
                keyboard.send(Keycode.CONTROL, Keycode.C)
            elif i == 7:  # Button 8: Paste (Ctrl + V)
                keyboard.send(Keycode.CONTROL, Keycode.V)
            elif i == 8:  # Button 9: Cut (Ctrl + X)
                keyboard.send(Keycode.CONTROL, Keycode.X)
            time.sleep(0.2)  # Debounce delay

# Main Loop
while True:
    # Rotary Encoder Handling
    clkState = clk.value
    if clk_last != clkState:
        if dt.value != clkState:
            cw()  # Clockwise
        else:
            ccw()  # Counterclockwise
        clk_last = clkState

    # Handle buttons
    handle_button_actions()

    # Mode Switching with rotary push button
    if sw.value == 0:  # Button pressed
        pressTime = millis()
        time.sleep(0.2)  # Debounce delay
        longPress = False

        while sw.value == 0:  # Check if still pressed
            if millis() - pressTime > 1000 and not longPress:  # Long press detected
                print("Long Press Detected")
                longPress = True
                long_press()

        if not longPress:  # Short press cycles mode
            currentMode += 1
            currentMode %= totalMode
            indicate_mode_change()
