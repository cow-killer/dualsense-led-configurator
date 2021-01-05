# DualSense LED Configurator 0.2
# © 2021 cow_killer

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk # for GUI
import random # for random RGB colors
import time # for sleep timers
import sys # for exiting the application if there is an error
import os #detects if program is being run as root
import select
from tkinter import *
import tkinter.colorchooser # need tkiner for now for color picker and RGB brightness

# Define the MAC address for your DS here
mac_address = "00:00:00:00:00:00"

icon = "assets/icon.png"
controller = "assets/pad.png"
charging_battery = "assets/charging.png"
full_battery = "assets/full_battery.png"
medium_battery = "assets/medium_battery.png"
low_battery = "assets/low_battery.png"

class AboutBox(Gtk.Dialog):
    def __init__(self, parent):
        Gtk.Dialog.__init__(self, title="About", transient_for=parent, flags=0)
        self.add_buttons(Gtk.STOCK_OK, Gtk.ResponseType.OK)
        self.set_border_width(15)

        version = Gtk.Label()
        version.set_markup("<big><b>DualSense LED Configurator 0.2</b></big>")
        author = Gtk.Label()
        author.set_markup("<big><b>© 2021 cow_killer</b></big>\n")
        source = Gtk.Label()
        
        warning = Gtk.Label()
        warning.set_markup("<b>WARNING:</b> This software is currently unstable!\n") 
        
        credits_label = Gtk.Label()
        credits_label.set_markup("Icon image by Martial Red\nDS image by Khairuman\nBattery icons by nadeem\n")       
        
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
		# check to see if user has root privileges, if not exit
		if os.geteuid() != 0: 
			print("ERROR: You need to run this program as root in order to modify the LEDs.")
			sys.exit()
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
		
		# Get battery percentage. Display error if file is not available and exit
		try:
			f = open("/sys/class/power_supply/ps-controller-battery-" + mac_address + "/capacity")
			status_file = open("/sys/class/power_supply/ps-controller-battery-" + mac_address + "/status")
		except FileNotFoundError:
			print("ERROR: You either entered the wrong MAC address or your device is not connected.")
			sys.exit()
		else:
			battery_icon = Gtk.Image()
			battery_percentage_left = f.read();
			status = status_file.readline().strip();
			if status == "Charging":
				battery_label.set_markup("Battery: <b>" + battery_percentage_left + "percent, charging</b>")
				battery_icon.set_from_file(charging_battery)
			elif status == "Full":
				battery_label.set_markup("Battery: <b>Full</b>")
				battery_icon.set_from_file(full_battery)
			else:
				battery_label.set_markup("Battery: <b>" + battery_percentage_left + "percent</b>")
				if battery_percentage_left > "75":
					battery_icon.set_from_file(full_battery)
				elif battery_percentage_left < "75" and battery_percentage_left >= "35":
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
		
		color_picker = Gtk.Button(label="Choose Color")
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
		
		choose_brightness = Gtk.Button(label="Choose Manually")
		choose_brightness.connect("clicked", self.choose_brightness_clicked)
		grid.attach(choose_brightness, 4, 3, 1, 1)
		
		# Bottom LEDs
		pane1 = Gtk.Label()
		pane1.set_markup("<b><big>Bottom LEDs</big></b>")
		grid.attach(pane1, 2, 5, 1, 1)

		led1 = Gtk.Button(label="LED 1 Toggle")
		led1.connect("clicked", self.led1_clicked)
		grid.attach(led1, 0, 6, 1, 1)

		led2 = Gtk.Button(label="LED 2 Toggle")
		led2.connect("clicked", self.led2_clicked)
		grid.attach(led2, 1, 6, 1, 1)

		led3 = Gtk.Button(label="LED 3 Toggle")
		led3.connect("clicked", self.led3_clicked)
		grid.attach(led3, 2, 6, 1, 1)

		led4 = Gtk.Button(label="LED 4 Toggle")
		led4.connect("clicked", self.led4_clicked)
		grid.attach(led4, 3, 6, 1, 1)

		led5 = Gtk.Button(label="LED 5 Toggle")
		led5.connect("clicked", self.led5_clicked)
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
		
	# Beginning of definitions
	def open_color_picker(self, widget): # Color picker for side LEDs
		win = Tk()
		win.title(string = "Choose Color")
		colorDialog = tkinter.colorchooser.Chooser()
		color = colorDialog.show()
		try:
			red = int(color[0][0])
			green = int(color[0][1])
			blue = int(color[0][2])
		except TypeError: # close dialog box if Cancel was clicked
			win.destroy()
		else:
			# Write the RGB value to 'multi-intensity'
			wr = open("/sys/class/leds/playstation::" + mac_address + "::rgb/multi_intensity", "r+")
			wr.write(str(red) + " " + str(green) + " " + str(blue))
			wr.close()
			print("RGB set to " + str(red) + " " + str(green) + " " + str(blue))
			win.destroy()
		
	def rgb_random_clicked(self, widget):
		wr = open("/sys/class/leds/playstation::" + mac_address + "::rgb/multi_intensity", "r+")
		random_red = random.randint(1, 255)
		random_green = random.randint(1, 255)
		random_blue = random.randint(1, 255)
		wr.write(str(random_red) + " " + str(random_green) + " " + str(random_blue))
		wr.close()
		print("RGB set to " + str(random_red) + " " + str(random_green) + " " + str(random_blue))
	
	def rgb_rainbow_clicked(self, widget):
		print("Running, press Enter any time to exit -> ")
		
		# Set RGB to 0 0 0 before we begin
		wr = open("/sys/class/leds/playstation::" + mac_address + "::rgb/multi_intensity", "r+")
		wr.write("0 0 0")
		wr.close()
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
			while red <= max_rgb and green <= max_rgb and blue <= max_rgb: # slowly glow brighter
				wr = open("/sys/class/leds/playstation::" + mac_address + "::rgb/multi_intensity", "r+")
				wr.write(str(red) + " " + str(green) + " " + str(blue))
				wr.close()
				time.sleep(0.05)
				red += random_red_increment
				green += random_green_increment
				blue += random_blue_increment
			while red > min_rgb and green > min_rgb and blue > min_rgb: # die down
				time.sleep(0.05)
				red -= random_red_increment
				green -= random_green_increment
				blue -= random_blue_increment
				wr = open("/sys/class/leds/playstation::" + mac_address + "::rgb/multi_intensity", "r+")
				wr.write(str(red) + " " + str(green) + " " + str(blue))
				wr.close()
			if sys.stdin in select.select([sys.stdin], [], [], 0)[0]: # exit if Enter is pressed
				print("Exiting...")
				sys.exit()
	
	# Side LED brightness
	def no_brightness_clicked(self, widget):
		brightness_off = 0
		wr = open("/sys/class/leds/playstation::" + mac_address + "::rgb/brightness", "r+")
		wr.write(str(brightness_off))
		wr.close()
		print("Brightness set to " + str(brightness_off))
		
	def low_brightness_clicked(self, widget):
		low_brightness_value = 85
		wr = open("/sys/class/leds/playstation::" + mac_address + "::rgb/brightness", "r+")
		wr.write(str(low_brightness_value))
		wr.close()
		print("Brightness set to " + str(low_brightness_value))
		
	def medium_brightness_clicked(self, widget):
		med_brightness_value = 170
		wr = open("/sys/class/leds/playstation::" + mac_address + "::rgb/brightness", "r+")
		wr.write(str(med_brightness_value))
		wr.close()
		print("Brightness set to " + str(med_brightness_value))
	
	def max_brightness_clicked(self, widget):
		max_brightness_value = 255
		wr = open("/sys/class/leds/playstation::" + mac_address + "::rgb/brightness", "r+")
		wr.write(str(max_brightness_value))
		wr.close()
		print("Brightness set to " + str(max_brightness_value))
		
	def choose_brightness_clicked(self, widget):
		def set_value():
			wr = open("/sys/class/leds/playstation::" + mac_address + "::rgb/brightness", "r+")
			wr.write(str(brightness.get()))
			wr.close()
			print("Brightness set to " + str(brightness.get()))
			slider.destroy()
		def cancel_value():
			slider.destroy()
		slider = Tk()
		slider.title(string = "Set Brightness")
		slider.geometry("300x100")
		
		# Retrieve brightness value from file and set this as the default in the slider
		wr = open("/sys/class/leds/playstation::" + mac_address + "::rgb/brightness", 'r+')
		value = wr.readline().strip()
		
		brightness = Scale(slider, from_=0, to=255, orient=HORIZONTAL)
		brightness.set(value)
		brightness.pack()
		Button(slider, text="OK", command=set_value).pack()
		Button(slider, text="Cancel", command=cancel_value).pack()
		slider.mainloop()
		
	# Definitions for turning individual LEDs on/off
	def led1_clicked(self, widget):
		wr = open("/sys/class/leds/playstation::" + mac_address + "::led1/brightness", 'r+')
		value = wr.readline().strip()
		new_value = "1" if value == "0" else "0"
		wr.write(new_value)
		wr.close()
		
	def led2_clicked(self, widget):
		wr = open("/sys/class/leds/playstation::" + mac_address + "::led2/brightness", 'r+')
		value = wr.readline().strip()
		new_value = "1" if value == "0" else "0"
		wr.write(new_value)
		wr.close()
		
	def led3_clicked(self, widget):
		wr = open("/sys/class/leds/playstation::" + mac_address + "::led3/brightness", 'r+')
		value = wr.readline().strip()
		new_value = "1" if value == "0" else "0"
		wr.write(new_value)
		wr.close()

	def led4_clicked(self, widget):
		wr = open("/sys/class/leds/playstation::" + mac_address + "::led4/brightness", 'r+')
		value = wr.readline().strip()
		new_value = "1" if value == "0" else "0"
		wr.write(new_value)
		wr.close()
		
	def led5_clicked(self, widget):
		wr = open("/sys/class/leds/playstation::" + mac_address + "::led5/brightness", 'r+')
		value = wr.readline().strip()
		new_value = "1" if value == "0" else "0"
		wr.write(new_value)
		wr.close()
		
	
	# All LEDs ON/OFF
	def all_leds_clicked(self, widget):
		led_number = 1
		while led_number <= 5:
			wr = open("/sys/class/leds/playstation::" + mac_address + "::led" + str(led_number) + "/brightness", 'r+')
			value = wr.readline().strip()
			new_value = "1" if value == "0" else "0"
			wr.write(new_value)
			wr.close()
			led_number += 1
			
	# Progress bar LEDs
	def prog_bar_clicked(self, widget):
		# Turn off all the LEDs before proceeding
		print("Running, press Enter any time to stop -> ")
		while True:
			led_number = 1
			while led_number <= 5:
				wr = open("/sys/class/leds/playstation::" + mac_address + "::led" + str(led_number) + "/brightness", 'r+')
				wr.write("0")
				wr.close()
				led_number += 1
			led_number = 1
			while led_number <= 5:
				wr = open("/sys/class/leds/playstation::" + mac_address + "::led" + str(led_number) + "/brightness", 'r+')
				wr.write("1")
				wr.close()
				led_number += 1
				time.sleep(0.5)
			if sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
				print("Exiting...")
				sys.exit()
	
	# Disco LEDs
	def disco_leds_clicked(self, widget):
		print("Running, press Enter any time to exit -> ")
		# Turn off all the LEDs before proceeding
		led_number = 1
		while led_number <= 5:
			wr = open("/sys/class/leds/playstation::" + mac_address + "::led" + str(led_number) + "/brightness", 'r+')
			wr.write("0")
			wr.close()
			led_number += 1
			
		# Commence the cycle
		while True:
			random_led = random.randint(1, 5)
			wr = open("/sys/class/leds/playstation::" + mac_address + "::led" + str(random_led) + "/brightness", 'r+')
			value = wr.readline().strip()
			new_value = "1" if value == "0" else "0"
			wr.write(new_value)
			wr.close()
			time.sleep(0.3)
			
			if sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
				print("Exiting...")
				sys.exit()
	
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
