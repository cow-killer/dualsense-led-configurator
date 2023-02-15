# DualSense LED Configurator 0.4
# © 2021, 2022 cow_killer, thats-the-joke, ivanbratovic

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib  # for GUI
import random  # for random RGB colors
import time  # for sleep timers
import sys  # for exiting the application if there is an error
import os  # detects if program is being run as root
import select
import tkinter.colorchooser  # need tkiner for now for color picker and RGB brightness
import subprocess  # for running Linux commands

# find the path to the ps-controller-battery directory
device_path = subprocess.check_output(["find", "/sys/devices/","-name","ps-controller-battery*"])
# extract the MAC address from the filepath
mac_address = device_path.decode().split("/")[-1].split("-")[-1].strip()
# extract the main controller directory
device_path = "/".join(device_path.decode().split("/")[0:-2])

# get the random number assigned to the controller
input_num = subprocess.check_output(["find", "/sys/devices/", "-name", "input*:white:player-1"])
input_num = input_num.decode().split("/")[-1].split(":")[0][5:]

# create useful variables for other controller subsystems
battery_path = f"{device_path}/power_supply/ps-controller-battery-{mac_address}"
player_leds_path = f"{device_path}/leds/input{input_num}:white:player"
rgb_leds_path = f"{device_path}/leds/input{input_num}:rgb:indicator"

icon = "assets/icon.png"
controller = "assets/pad.png"
charging_battery = "assets/charging.png"
full_battery = "assets/full_battery.png"
medium_battery = "assets/medium_battery.png"
low_battery = "assets/low_battery.png"

version_number = "0.4"

# check to see if user has root privileges, if not exit
if os.geteuid() != 0:
    print("ERROR: You need to run this program as root in order to modify the LEDs.")
    sys.exit()

class AboutBox(Gtk.Dialog):
    def __init__(self, parent):
        Gtk.Dialog.__init__(self, title="About", transient_for=parent, flags=0)
        self.add_buttons(Gtk.STOCK_OK, Gtk.ResponseType.OK)
        self.set_border_width(15)

        version = Gtk.Label()
        version.set_markup("<big><b>DualSense LED Configurator " + version_number + "</b></big>")
        author = Gtk.Label()
        author.set_markup("<big><b>© 2021, 2022 cow_killer</b></big>\n")
        source = Gtk.Label()

        warning = Gtk.Label()
        warning.set_markup("<b>WARNING:</b> This software is currently unstable!\n")

        credits_label = Gtk.Label()
        credits_label.set_markup(
            "Icon image by Martial Red\nDS image by Khairuman\nBattery icons by nadeem\nSpecial thanks to thats-the-joke and ivanbratovic for PRs\n"
        )

        box = self.get_content_area()
        box.add(version)
        box.add(author)
        box.add(warning)
        box.add(credits_label)
        self.show_all()

class MainWindow(Gtk.Window):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.init_ui()

    # GUI
    def init_ui(self):
        self.set_icon_from_file(icon)
        self.set_title("DualSense LED Configurator")
        self.set_border_width(15)

        grid = Gtk.Grid()
        grid.set_column_spacing(10)
        grid.set_row_spacing(10)
        self.add(grid)

        pad_image = Gtk.Image()
        pad_image.set_from_file(controller)
        grid.attach(pad_image, 5, 4, 1, 1)

        battery_label = Gtk.Label()
        battery_icon = Gtk.Image()

        # Get battery percentage. Display error if file is not available and exit
        try:
            f = open(
                f"{battery_path}/capacity"
            )
            status_file = open(
                f"{battery_path}/status"
            )
        except FileNotFoundError:
            print(
                "ERROR: Your controller can't be detected."
            )
            sys.exit()
        else:
            battery_percentage_left = f.readline().strip()
            status = status_file.readline().strip()
            if status == "Charging":
                battery_label.set_markup(
                    "Battery: <b>" + battery_percentage_left + " percent, charging</b>"
                )
                battery_icon.set_from_file(charging_battery)
            elif status == "Full":
                battery_label.set_markup("Battery: <b>Full</b>")
                battery_icon.set_from_file(full_battery)
            else:
                battery_label.set_markup(
                    "Battery: <b>" + battery_percentage_left + " percent</b>"
                )
                if (
                    battery_percentage_left <= "100" or battery_percentage_left >= "85"
                ):  # unlike the DS4, the battery value ends with a 5 (i.e. 95, 85, 75, etc.), unless it's 100%
                    battery_icon.set_from_file(full_battery)
                elif battery_percentage_left < "85" and battery_percentage_left >= "35":
                    battery_icon.set_from_file(medium_battery)
                elif battery_percentage_left < "35":
                    battery_icon.set_from_file(low_battery)
            f.close()
            status_file.close()
        grid.attach(battery_icon, 5, 6, 1, 1)
        grid.attach(battery_label, 5, 5, 1, 1)

        # Set RGB
        pane2 = Gtk.Label()
        pane2.set_markup("<big><b>Side LEDs</b></big>")
        grid.attach(pane2, 2, 0, 1, 1)

        # Color picker
        rgb_random = Gtk.Button(label="Random")
        rgb_random.connect("clicked", self.rgb_random_clicked)
        grid.attach(rgb_random, 1, 1, 1, 1)

        color_picker = Gtk.Button(label="Choose Color...")
        color_picker.connect("clicked", self.open_color_picker)
        grid.attach(color_picker, 2, 1, 1, 1)

        rgb_rainbow = Gtk.Button(label="Rainbow (UNSTABLE!)")
        rgb_rainbow.connect("clicked", self.rgb_rainbow_clicked)
        grid.attach(rgb_rainbow, 3, 1, 1, 1)

        # RGB brightness
        pane3 = Gtk.Label()
        pane3.set_markup("<big><b>Brightness</b></big>")
        grid.attach(pane3, 2, 2, 1, 1)

        no_brightness = Gtk.Button(label="Off")
        no_brightness.connect("clicked", self.no_brightness_clicked)
        grid.attach(no_brightness, 0, 3, 1, 1)

        low_brightness = Gtk.Button(label="Low")
        low_brightness.connect("clicked", self.low_brightness_clicked)
        grid.attach(low_brightness, 1, 3, 1, 1)

        medium_brightness = Gtk.Button(label="Medium")
        medium_brightness.connect("clicked", self.medium_brightness_clicked)
        grid.attach(medium_brightness, 2, 3, 1, 1)

        max_brightness = Gtk.Button(label="Max")
        max_brightness.connect("clicked", self.max_brightness_clicked)
        grid.attach(max_brightness, 3, 3, 1, 1)

        choose_brightness = Gtk.Button(label="Set Manually...")
        choose_brightness.connect("clicked", self.choose_brightness_clicked)
        grid.attach(choose_brightness, 4, 3, 1, 1)

        # Bottom LEDs
        pane1 = Gtk.Label()
        pane1.set_markup("<b><big>Bottom LEDs</big></b>")
        grid.attach(pane1, 2, 5, 1, 1)

        led1 = Gtk.Button(label="LED 1 Toggle")
        led1.connect("clicked", self.led_clicked, 1)
        grid.attach(led1, 0, 6, 1, 1)

        led2 = Gtk.Button(label="LED 2 Toggle")
        led2.connect("clicked", self.led_clicked, 2)
        grid.attach(led2, 1, 6, 1, 1)

        led3 = Gtk.Button(label="LED 3 Toggle")
        led3.connect("clicked", self.led_clicked, 3)
        grid.attach(led3, 2, 6, 1, 1)

        led4 = Gtk.Button(label="LED 4 Toggle")
        led4.connect("clicked", self.led_clicked, 4)
        grid.attach(led4, 3, 6, 1, 1)

        led5 = Gtk.Button(label="LED 5 Toggle")
        led5.connect("clicked", self.led_clicked, 5)
        grid.attach(led5, 4, 6, 1, 1)

        # Progress-bar like LED display
        prog_bar = Gtk.Button(label="Progress Bar (UNSTABLE!)")
        prog_bar.connect("clicked", self.prog_bar_clicked)
        grid.attach(prog_bar, 1, 7, 1, 1)

        # Turn on/off all LEDs
        all_leds = Gtk.Button(label="Opposite LEDs Toggle")
        all_leds.connect("clicked", self.all_leds_clicked)
        grid.attach(all_leds, 2, 7, 1, 1)

        # Random array of LEDs
        disco_leds = Gtk.Button(label="Disco! (UNSTABLE!)")
        disco_leds.connect("clicked", self.disco_leds_clicked)
        grid.attach(disco_leds, 3, 7, 1, 1)

        # About
        about_button = Gtk.Button(label="About")
        about_button.connect("clicked", self.about_button_clicked)
        grid.attach(about_button, 0, 100, 1, 1)

        # Quit
        quit_button = Gtk.Button(label="Close")
        quit_button.connect("clicked", self.quit_button_clicked)
        grid.attach(quit_button, 5, 100, 1, 1)

        self.connect("destroy", Gtk.main_quit)

    def toggle_individual_led(self, led_num):
        with open(f"{player_leds_path}-{led_num}/brightness", "r+") as wr:
            value = wr.readline().strip()
            new_value = "1" if value == "0" else "0"
            wr.write(new_value)

    def enable_individual_led(self, led_num):
        with open(f"{player_leds_path}-{led_num}/brightness", "w") as wr:
            wr.write("1")

    def disable_individual_led(self, led_num):
        with open(f"{player_leds_path}-{led_num}/brightness", "w") as wr:
            wr.write("0")

    def open_color_picker(self, widget):  # Color picker for side LEDs
        win = tkinter.Tk()
        win.title(string="Choose Color")
        colorDialog = tkinter.colorchooser.Chooser()
        color = colorDialog.show()
        try:
            red = int(
                color[0][0]
            )  # convert the floating point values to a whole number
            green = int(color[0][1])
            blue = int(color[0][2])
        except TypeError:  # close dialog box if Cancel was clicked
            win.destroy()
        else:
            # Write the RGB value to 'multi-intensity'
            with open(
                f"{rgb_leds_path}/multi_intensity",
                "r+",
            ) as wr:
                wr.write(str(red) + " " + str(green) + " " + str(blue))
            print("RGB set to " + str(red) + " " + str(green) + " " + str(blue))
            win.destroy()

    def rgb_random_clicked(self, widget):
        random_red = random.randint(1, 255)
        random_green = random.randint(1, 255)
        random_blue = random.randint(1, 255)
        with open(
            f"{rgb_leds_path}/multi_intensity",
            "r+",
        ) as wr:
            wr.write(f"{random_red} {random_green} {random_blue}")
        print(
            "RGB set to "
            + str(random_red)
            + " "
            + str(random_green)
            + " "
            + str(random_blue)
        )

    def rgb_rainbow_clicked(self, widget):
        print("Running rainbow, press Enter any time to exit -> ")

        # Set RGB to 0 0 0 before we begin
        with open(
            f"{rgb_leds_path}/multi_intensity",
            "r+",
        ) as wr:
            wr.write("0 0 0")
        max_rgb = 255
        min_rgb = 0

        red = 0
        green = 0
        blue = 0

        # Commence the cycle
        while True:
            random_red_increment = random.randint(1, 10)
            random_green_increment = random.randint(1, 10)
            random_blue_increment = random.randint(1, 10)
            while (
                red <= max_rgb and green <= max_rgb and blue <= max_rgb
            ):  # slowly glow brighter
                time.sleep(0.05)
                red += random_red_increment
                green += random_green_increment
                blue += random_blue_increment
                with open(
                    f"{rgb_leds_path}/multi_intensity",
                    "r+",
                ) as wr:
                    wr.write(str(red) + " " + str(green) + " " + str(blue))
            while red > min_rgb and green > min_rgb and blue > min_rgb:  # die down
                time.sleep(0.05)
                red -= random_red_increment
                green -= random_green_increment
                blue -= random_blue_increment
                with open(
                    f"{rgb_leds_path}/multi_intensity",
                    "r+",
                ) as wr:
                    wr.write(str(red) + " " + str(green) + " " + str(blue))
            if (
                sys.stdin in select.select([sys.stdin], [], [], 0)[0]
            ):  # exit if Enter is pressed
                print("Exiting...")
                sys.exit()

    # Side LED brightness
    def no_brightness_clicked(self, widget):
        brightness_off = 0
        with open(f"{rgb_leds_path}/brightness", "r+") as wr:
            wr.write(str(brightness_off))
        print("Brightness set to " + str(brightness_off))

    def low_brightness_clicked(self, widget):
        low_brightness_value = 85
        with open(f"{rgb_leds_path}/brightness", "r+") as wr:
            wr.write(str(low_brightness_value))
        print("Brightness set to " + str(low_brightness_value))

    def medium_brightness_clicked(self, widget):
        med_brightness_value = 170
        with open(f"{rgb_leds_path}/brightness", "r+") as wr:
            wr.write(str(med_brightness_value))
        print("Brightness set to " + str(med_brightness_value))

    def max_brightness_clicked(self, widget):
        max_brightness_value = 255
        with open(f"{rgb_leds_path}/brightness", "r+") as wr:
            wr.write(str(max_brightness_value))
        print("Brightness set to " + str(max_brightness_value))

    def choose_brightness_clicked(self, widget):
        def set_value():
            with open(f"{rgb_leds_path}/brightness", "r+") as wr:
                wr.write(str(brightness.get()))
            print("Brightness set to " + str(brightness.get()))
            slider.destroy()

        def cancel():
            slider.destroy()

        slider = tkinter.Tk()
        slider.title(string="Set Brightness")
        slider.geometry("300x100")

        # Retrieve brightness value from file and set this as the default in the slider
        with open(f"{rgb_leds_path}/brightness", "r+") as wr:
            value = wr.readline().strip()

        brightness = tkinter.Scale(slider, from_=0, to=255, orient=tkinter.HORIZONTAL)
        brightness.set(value)
        brightness.pack()
        tkinter.Button(slider, text="OK", command=set_value).pack()
        tkinter.Button(slider, text="Cancel", command=cancel).pack()
        slider.mainloop()

    # Definition for turning individual LEDs on/off
    def led_clicked(self, widget, *data):
        self.toggle_individual_led(data[0])

    # All LEDs ON/OFF
    def all_leds_clicked(self, widget):
        for i in range(1, 6):
            self.toggle_individual_led(i)

    # Progress bar LEDs
    def prog_bar_clicked(self, widget):
        print("Running progress bar, press Enter any time to stop -> ")
        while True:
            # Turn off all the LEDs before proceeding
            for i in range(1, 6):
                self.disable_individual_led(i)

            # Commence the cycle
            for i in range(1, 6):
                self.enable_individual_led(i)
                time.sleep(0.5)

            # break if Enter is pressed
            if sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
                input()
                print("Stopping...")
                break

    # Disco LEDs
    def disco_leds_clicked(self, widget):
        print("Running disco, press Enter any time to stop -> ")
        # Turn off all the LEDs before proceeding
        for i in range(1, 6):
            self.disable_individual_led(i)

        # Commence the cycle
        while True:
            random_led = random.randint(1, 5)
            self.toggle_individual_led(random_led)
            time.sleep(0.3)

            # break if Enter is pressed
            if sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
                input()
                print("Stopping...")
                break

    # About box
    def about_button_clicked(self, widget):
        dialog = AboutBox(self)
        dialog.run()
        dialog.destroy()

    # Exit
    def quit_button_clicked(self, widget):
        Gtk.main_quit()


window = MainWindow()
window.show_all()
Gtk.main()
