from threading import Thread

import ctypes
from ctypes import wintypes

import time

from pynput.mouse import Button, Controller
mouse = Controller()

from pynput.keyboard import Key, Controller, Listener, KeyCode
keyboard = Controller()

import time
macroActive = False
PROGRAM_RUNNING = True
originallyClipped = False

MACRO_KEYBIND = KeyCode.from_char(input("Enter the key you want to use as your macro keybind: "))

while not MACRO_KEYBIND:
    MACRO_KEYBIND = KeyCode.from_char(input("Enter the key you want to use as your macro keybind: "))

EXIT_KEYBIND = KeyCode.from_char(input("Enter the key you want to use as your exit keybind: "))

while not EXIT_KEYBIND:
    EXIT_KEYBIND = KeyCode.from_char(input("Enter the key you want to use as your macro keybind: "))

targetPosition = (500, 10)
currentPosition = None

user32 = ctypes.WinDLL("user32", use_last_error=True)

class RECT(ctypes.Structure):
    _fields_ = [("left",   wintypes.LONG),
                ("top",    wintypes.LONG),
                ("right",  wintypes.LONG),
                ("bottom", wintypes.LONG)]

def lock_cursor_at(x, y, x2, y2):
    one_px = RECT(x, y, x2, y2)
    user32.ClipCursor(ctypes.byref(one_px))

def unlock_cursor():
    user32.ClipCursor(None)

def is_cursor_clipped():
    current = RECT()
    user32.GetClipCursor(ctypes.byref(current))
    return current.left != targetPosition[0] or current.top != targetPosition[1]

def macroHandler():
    global macroActive, targetPosition, currentPosition, PROGRAM_RUNNING, originallyClipped

    while PROGRAM_RUNNING:
        if macroActive:
            if currentPosition == None:
                currentPosition = mouse.position
                mouse.release(Button.right)
            else:
                if is_cursor_clipped():
                    current = RECT()
                    user32.GetClipCursor(ctypes.byref(current))
                    originallyClipped = (current.left, current.top, current.right, current.bottom)

            lock_cursor_at(targetPosition[0], targetPosition[1], targetPosition[0]+1, targetPosition[1]+1)
            mouse.press(Button.left)

        elif currentPosition != None:
            mouse.release(Button.left)
            unlock_cursor()
            mouse.position = currentPosition
            currentPosition = None

            if originallyClipped:
                lock_cursor_at(originallyClipped[0], originallyClipped[1], originallyClipped[2], originallyClipped[3])
                originallyClipped = None

        if not macroActive:
            time.sleep(1/60)

    return False


def checkKeyPress(key):
    global macroActive, PROGRAM_RUNNING, MACRO_KEYBIND, EXIT_KEYBIND

    if key == MACRO_KEYBIND:
        macroActive = True

    elif key == EXIT_KEYBIND:
        PROGRAM_RUNNING = False
        macroActive = False
        return False

def checkKeyRelease(key):
    global macroActive, MACRO_KEYBIND

    if not PROGRAM_RUNNING:
        return False

    if key == MACRO_KEYBIND:
        macroActive = False

def startListener1():
    with Listener(on_press = checkKeyPress, on_release = checkKeyRelease) as listener:
        listener.join()

thread1 = Thread(target=macroHandler)
thread2 = Thread(target=startListener1)

print("Starting; press {} to exit".format(EXIT_KEYBIND))
thread1.start()
thread2.start()

thread1.join()
thread2.join()
print("Exited")
