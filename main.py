# Adapted for MicroPython
# SPDX-FileCopyrightText: 2017 Limor Fried for Adafruit Industries
#
# SPDX-License-Identifier: MIT

import time
import network
from config import *
from func import *

# pylint: disable=broad-except
# https://github.com/pyotp/pyotp example

oled.fill(0)
oled.show()

if TEST:
    print("===========================================")
    print("SHA1 test: ", ubinascii.hexlify(SHA1(b'hello world').digest()))
    # should be 2aae6c35c94fcfb415dbe95f408b9ce91ee846ed

if TEST:
    KEY = b'abcd'
    MESSAGE = b'efgh'
    print("===========================================")
    print("HMAC test: ", ubinascii.hexlify(HMAC(KEY, MESSAGE).digest()))
    # should be e5dbcf9263188f9fce90df572afeb39b66b27198

if TEST:
    print("===========================================")
    print("Base32 test: ", bytes(base32_decode("IFSGCZTSOVUXIIJB")))
    # should be "Adafruit!!"

# Set up networking
sta_if = network.WLAN(network.STA_IF)
oled.fill(0)
oled.text('Connecting to', 0, 0)
oled.text(wifi_config['ssid'], 0, 10)
oled.show()
print('Connecting to', wifi_config['ssid'])

if not sta_if.isconnected():
    print("Connecting to SSID", wifi_config['ssid'])
    sta_if.active(True)
    sta_if.connect(wifi_config['ssid'], wifi_config['password'])
    while not sta_if.isconnected():
        pass
print("Connected! IP:", sta_if.ifconfig()[0])
# Done! Let them know we made it
oled.text("Ok!", 0, 30)
oled.show()
time.sleep(2)


# NTP time is seconds-since-2000
print("NTP time: ", t)

# But we need Unix time, which is seconds-since-1970
t += EPOCH_DELTA
print("Unix time: ", t)

# Instead of using RTC which means converting back and forth
# we'll just keep track of seconds-elapsed-since-NTP-call

print("Monotonic time", mono_time)

countdown = ON_SECONDS  # how long to stay on if not in always_on mode

while ALWAYS_ON or (countdown > 0):
    show_totps(0)
    rem = 0
    while True:
        ut = get_unix_time()
        rem = int(30 - (ut % 30))
        # Display a little bar that 'counts down' how many seconds you have left
        oled.line(0, 63, 128 - rem*4, 63, True)
        oled.show()
        if rem >= 30:
            time.sleep(1)
            break
        time.sleep(1)
            
    # We'll update every 1/4 second, we can hash very fast so its no biggie!
    countdown -= 0.25
#     time.sleep(1)


# All these hashes will be lost in time(), like tears in rain. Time to die
oled.fill(0)
oled.show()
