# Main - Buddy Lamp
# get_color():
# -gets server color every 10 minutes
# change_color():
# -sets server color to your color when button is pressed
# button_callback():
# -when button is pressed, calls change_color()

import time
import requests

try:
    import RPi.GPIO as GPIO
except ModuleNotFoundError:
    print("RPi module not found. Are you running on a Raspberry Pi?")

# *---change these---*
api_url = "https://URL"
my_household_name = "Johnson"
my_color = "red"
# ****

current_color = ""
seconds_between_requests = 10

# ---GPIO stuff---
GPIO.setmode(GPIO.BCM)
# Button
button_pin = 2  # GPIO pin connected to the button
GPIO.setup(button_pin, GPIO.IN)  # Set the button pin as an input
button_pressed = False  # Flag to track button state
# LEDs
led_pin_number = 3  # red
GPIO.setup(led_pin_number, GPIO.OUT)  # Set the LED pin as an output
led_pin_number2 = 17  # blue
GPIO.setup(led_pin_number2, GPIO.OUT)


def get_color(color_currently, led_pin, led_pin2):
    """
        Gets the color from the server and adjusts the LEDs.

        Args:
            color_currently (str): The color the server currently has.
            led_pin (int): The first LED GPIO number.
            led_pin2 (int): The second LED GPIO number.

        Returns:
            color_currently (str): The new server color.
    """
    try:
        # HTTP GET request to the server
        response = requests.get(api_url)
        # if the response succeeded (200 code)
        if response.status_code == 200:
            print("200: Request successful!")
            data = response.json()
            server_color = data.get("color")
            print("server_color: " + server_color)
            # if the color is white: turn off RGBs
            if server_color == "white":
                print(f"no server color")
                GPIO.output(led_pin, GPIO.LOW)  # Turn off the 1st LED (yours)
                GPIO.output(led_pin2, GPIO.LOW)  # Turn off the 2nd LED (other)
            # if the color is not your color: turn off your color, turn on the right color
            elif server_color and server_color != my_color:
                color_currently = server_color
                print(f"color updated to {server_color}")
                GPIO.output(led_pin, GPIO.LOW)
                GPIO.output(led_pin2, GPIO.HIGH)
            # if the color is not your color and has not changed: do nothing
            elif server_color and server_color != my_color and server_color == color_currently:
                print(f"server color has not changed")
            # if the color is your color: turn off other LED, turn on your LED
            elif server_color and server_color == my_color:
                print(f"server color is your color")
                GPIO.output(led_pin2, GPIO.LOW)
                GPIO.output(led_pin, GPIO.HIGH)
            # other cases that are not handled
            else:
                print(f"Other case - not yet handled")
        # if code != 200
        else:
            print("Request failed!")
    except requests.exceptions.RequestException as e:
        print(f"Request error: {e}")

    return color_currently


def change_color(household_name, color, led_pin, led_pin2):
    """
        Sends your color to the server and adjusts the LEDs.

        Args:
            household_name (str): Your household name.
            color (str): The color you are sending.
            led_pin (int): The first LED GPIO number.
            led_pin2 (int): The second LED GPIO number.

        Returns:
            Nothing.
    """
    try:
        payload = {
            "household": {
                "name": household_name,
                "color": color
            }
        }
        # HTTP POST request to the server
        response = requests.post(api_url, json=payload)
        # if the request succeeded: Turn other LEDs off, turn your LED on
        if response.status_code == 201:
            GPIO.output(led_pin2, GPIO.LOW)
            GPIO.output(led_pin, GPIO.HIGH)
            print("201: Color change request successful!")
        else:
            print("Color change request failed!")
    except requests.exceptions.RequestException as e:
        print(f"Request error: {e}")


def button_callback(household_name, color, led_pin, led_pin2):
    """
        When button is pressed: Calls change_color().

        Args:
            household_name (str): Your household name.
            color (str): The color you are sending.
            led_pin (int): The first LED GPIO number.
            led_pin2 (int): The second LED GPIO number.

        Returns:
            Nothing.
    """
    # Allows button to be triggered only on release
    global button_pressed
    if not button_pressed:
        button_pressed = True
        change_color(household_name, color, led_pin, led_pin2)
    button_pressed = False  # Reset button state


# Button listener
GPIO.add_event_detect(button_pin, GPIO.FALLING,
                      callback=lambda channel: button_callback(my_household_name, my_color, led_pin_number,
                                                               led_pin_number2), bouncetime=300)

# Loop to keep it listening/requesting
while True:
    # Change the current_color to whatever the server color is
    current_color = get_color(current_color, led_pin_number, led_pin_number2)
    # Wait for x seconds before the next request
    time.sleep(seconds_between_requests)