# Test dimming of three LEDs with TLC59711 while controlling a servo with Raspberry internal PWM
import time

import board
import busio

import adafruit_tlc59711
import wiringpi

# Define SPI bus connected to chip.  You only need the clock and MOSI (output)
# line to use this chip.
spi = busio.SPI(board.SCK, MOSI=board.MOSI)

# Define the TLC59711 instance.
leds = adafruit_tlc59711.TLC59711(spi)

# use 'GPIO naming'
wiringpi.wiringPiSetupGpio()

# set PWM output pin
servo_pin = 18
wiringpi.pinMode(servo_pin, wiringpi.GPIO.PWM_OUTPUT)
# set the PWM mode to milliseconds stype
wiringpi.pwmSetMode(wiringpi.GPIO.PWM_MODE_MS)
# divide down clock
wiringpi.pwmSetClock(192)
wiringpi.pwmSetRange(2000)

step_time = 0.01 # time to sleep each loop
duration = 5 # total time to run

# servo PWM pulse values
pulse_max = 250
pulse_min = 50
pulse_delta = pulse_max - pulse_min

n_steps = int(duration / step_time)

for i in range(0, n_steps):
    led_value = int(65535*i/n_steps)
    leds[0] = (led_value, led_value, led_value)

    pulse = int(pulse_delta*i/n_steps) + pulse_min
    wiringpi.pwmWrite(servo_pin, pulse)

    time.sleep(step_time)

leds[0] = (65535, 65535, 65535) # set all leds full brightness

