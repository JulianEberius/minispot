#-*- coding: utf-8 -*-
#
#  hotkeys.py
#  minispot
#
#  Created by Julian Eberius on 28.01.14.
#  Copyright (c) 2014 Julian Eberius. All rights reserved.
#

import os
import objc
from Foundation import NSClassFromString
from AppKit import NSBundle, NSAlternateKeyMask, NSCommandKeyMask,\
    NSControlKeyMask, NSFunctionKeyMask, NSShiftKeyMask, NSDeviceIndependentModifierFlagsMask,\
    NSEvent

GLOBAL_HANDLERS = {}

mod_map = {
    "alt": NSAlternateKeyMask,
    "cmd": NSCommandKeyMask,
    "command": NSCommandKeyMask,
    "control": NSControlKeyMask,
    "ctrl": NSControlKeyMask,
    "shift": NSShiftKeyMask
}
cmdKeyBit = 8
shiftKeyBit = 9
optionKeyBit = 11
controlKeyBit = 12

cmdKey = 1 << cmdKeyBit
shiftKey = 1 << shiftKeyBit
optionKey = 1 << optionKeyBit
controlKey = 1 << controlKeyBit

mod_map = {
    "alt": optionKey,
    "cmd": cmdKey,
    "command": cmdKey,
    "control": controlKey,
    "ctrl": controlKey,
    "shift": shiftKey
}
key_map = {
    "left": 123,
    "right": 124,
    "down": 125,
    "up": 126,
    "help": 114, "mute": 74, "comma": 43, "volumedown": 73, "1": 18, "0": 29, "4": 21, "8": 28, "return": 36, "enter": 36, "slash": 44, "downarrow": 125, "d": 2, "h": 4, "l": 37, "p": 35, "t": 17, "x": 7, "forwarddelete": 117, "rightbracket": 30, "right": 124, "escape": 53, "home": 115, "5": 23, "space": 49, "3": 20, "f20": 90, "pagedown": 121, "7": 26, "keypadequals": 81, "keypadplus": 69, "c": 8, "f11": 103, "keypadclear": 71, "g": 5, "k": 40, "equal": 24, "o": 31, "minus": 27, "s": 1, "w": 13, "f15": 113, "rightshift": 60, "period": 47, "down": 125, "capslock": 57, "f6": 97, "2": 19, "keypadmultiply": 67, "6": 22, "function": 63, "option": 58, "leftbracket": 33, "f19": 80, "b": 11, "f": 3, "j": 38, "pageup": 116, "up": 126, "n": 45, "f18": 79, "r": 15, "rightoption": 61, "v": 9, "f12": 111, "f13": 105, "f10": 109, "z": 6, "f16": 106, "f17": 64, "f14": 107, "delete": 51, "f1": 122, "f2": 120, "f3": 99, "f4": 118, "f5": 96, "semicolon": 41, "f7": 98, "f8": 100, "f9": 101, "backslash": 42, "keypaddivide": 75, "tab": 48, "rightarrow": 124, "end": 119, "leftarrow": 123, "keypad7": 89, "keypad6": 88, "keypad5": 87, "keypad4": 86, "keypad3": 85, "keypad2": 84, "keypad1": 83, "keypad0": 82, "9": 25, "u": 32, "keypad9": 92, "keypad8": 91, "quote": 39, "volumeup": 72, "grave": 50, "<": 50, ">": 62, "keypaddecimal": 65, "e": 14, "i": 34, "keypadminus": 78, "m": 46, "uparrow": 126, "q": 12, "y": 16, "keypadenter": 76, "left": 123
}


base_path = os.path.join(NSBundle.mainBundle().bundlePath(), "Contents", "Frameworks")
bundle_path = os.path.abspath(os.path.join(base_path, "PTHotkey.framework"))
objc.loadBundle("PTHotKey", globals(), bundle_path=objc.pathForFramework(bundle_path))

PTHotKey = NSClassFromString("PTHotKey")
PTKeyCombo = NSClassFromString("PTKeyCombo")
PTHotKeyCenter = NSClassFromString("PTHotKeyCenter")

def register_key_from_string(key_str, target, signal):
    elems = key_str.split("+")
    modifiers = 0
    keycode = -1
    for e in elems:
        if e in mod_map:
            modifiers |= mod_map[e]
        elif e in key_map:
            keycode = key_map[e]

    combo = PTKeyCombo.keyComboWithKeyCode_modifiers_(keycode, modifiers)
    hotkey = PTHotKey.alloc().initWithIdentifier_keyCombo_(signal, combo)
    hotkey.setTarget_(target)
    hotkey.setAction_(signal)
    PTHotKeyCenter.sharedCenter().registerHotKey_(hotkey)

    return hotkey
