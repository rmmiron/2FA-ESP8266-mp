import time
import ntptime
import ubinascii
import uhashlib
from machine import Pin, I2C
from config import totp
import ssd1306

i2c = I2C(sda=Pin(4), scl=Pin(5))
oled = ssd1306.SSD1306_I2C(128, 64, i2c)

# Constants
SHA1 = uhashlib.sha1
EPOCH_DELTA = 946684800  # seconds between year 2000 and year 1970
SECS_DAY = 86400
TEST = False  # if you want to print out the tests the hashers
ALWAYS_ON = True  # Set to true if you never want to go to sleep!
ON_SECONDS = 60  # how long to stay on if not in always_on mode

# HMAC implementation, as hashlib/hmac wouldn't fit
# From https://en.wikipedia.org/wiki/Hash-based_message_authentication_code
def HMAC(k, m):
    SHA1_BLOCK_SIZE = 64
    KEY_BLOCK = k + (b'\0' * (SHA1_BLOCK_SIZE - len(k)))
    KEY_INNER = bytes((x ^ 0x36) for x in KEY_BLOCK)
    KEY_OUTER = bytes((x ^ 0x5C) for x in KEY_BLOCK)
    inner_message = KEY_INNER + m
    outer_message = KEY_OUTER + SHA1(inner_message).digest()
    return SHA1(outer_message)

# Base32 decoder, since base64 lib wouldnt fit
def base32_decode(encoded):
    missing_padding = len(encoded) % 8
    if missing_padding != 0:
        encoded += '=' * (8 - missing_padding)
    encoded = encoded.upper()
    chunks = [encoded[i:i + 8] for i in range(0, len(encoded), 8)]

    out = []
    for chunk in chunks:
        bits = 0
        bitbuff = 0
        for c in chunk:
            if 'A' <= c <= 'Z':
                n = ord(c) - ord('A')
            elif '2' <= c <= '7':
                n = ord(c) - ord('2') + 26
            elif c == '=':
                continue
            else:
                raise ValueError("Not base32")
            # 5 bits per 8 chars of base32
            bits += 5
            # shift down and add the current value
            bitbuff <<= 5
            bitbuff |= n
            # great! we have enough to extract a byte
            if bits >= 8:
                bits -= 8
                byte = bitbuff >> bits  # grab top 8 bits
                bitbuff &= ~(0xFF << bits)  # and clear them
                out.append(byte)  # store what we got
    return out

# Turns an integer into a padded-with-0x0 bytestr
def int_to_bytestring(i, padding=8):
    result = []
    while i != 0:
        result.insert(0, i & 0xFF)
        i >>= 8
    result = [0] * (padding - len(result)) + result
    return bytes(result)


# HMAC -> OTP generator, pretty much same as
# https://github.com/pyotp/pyotp/blob/master/src/pyotp/otp.py
def generate_otp(int_input, secret_key, digits=6):
    if int_input < 0:
        raise ValueError('input must be positive integer')
    hmac_hash = bytearray(
        HMAC(bytes(base32_decode(secret_key)),
             int_to_bytestring(int_input)).digest()
    )
    offset = hmac_hash[-1] & 0xf
    code = ((hmac_hash[offset] & 0x7f) << 24 |
            (hmac_hash[offset + 1] & 0xff) << 16 |
            (hmac_hash[offset + 2] & 0xff) << 8 |
            (hmac_hash[offset + 3] & 0xff))
    str_code = str(code % 10 ** digits)
    while len(str_code) < digits:
        str_code = '0' + str_code

    return str_code


def get_unix_time():
    return t - mono_time + int(time.time())

def show_totps(first=0):
    oled.fill(0)
    y = 0
    untime = get_unix_time()
    ttotp = totp[first:]
    for name, secret in ttotp:
        # Calculate current time based on NTP + monotonic
        otp = generate_otp(untime // 30, secret)
#         print(name + ":", otp) 		# serial debugging output
        oled.text(name[:9], 0, y)	# display name 9chars 
        oled.text(str(otp), 81, y)  # display OTP right aligned
        y += 10  # Go to next line on OLED
        if y >= 60:
            break

    oled.show()

# Get the latest time from NTP
def get_NTP_time():
    t = None
    while not t:
        try:
            t = ntptime.time()
        except Exception:
            pass
        time.sleep(0.1)
    return t

t = get_NTP_time()
mono_time = int(time.time())