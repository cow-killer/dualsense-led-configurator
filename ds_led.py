# DualSense LED Configurator 0.1
# © 2020-2021 cow_killer


import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk # for GUI
import random # for random RGB colors
import time # for sleep timers
import sys # for exiting the application if there is an error
import os #detects if program is being run as root

# Define the MAC address for your DS here
mac_address = "00:00:00:00:00:00"

icon = "assets/icon.png"
controller = "assets/pad.png"
charging_battery = "assets/charging.png"
full_battery = "assets/full_battery.png"
medium_battery = "assets/medium_battery.png"
low_battery = "assets/low_battery.png"
      
class NotRootBox(Gtk.Dialog):
    def __init__(self, parent):
        Gtk.Dialog.__init__(self, title="Error", transient_for=parent, flags=0)
        self.add_buttons(Gtk.STOCK_OK, Gtk.ResponseType.OK)
        self.set_border_width(15)

        error = Gtk.Label()
        error.set_markup("<b>ERROR:</b> You need to run this program as root in order to modify the LEDs.")
        
        box = self.get_content_area()
        box.add(error)
        self.show_all()

class ErrorBox(Gtk.Dialog):
    def __init__(self, parent):
        Gtk.Dialog.__init__(self, title="Error", transient_for=parent, flags=0)
        self.add_buttons(Gtk.STOCK_OK, Gtk.ResponseType.OK)
        self.set_border_width(15)

        error = Gtk.Label()
        error.set_markup("<b>ERROR:</b> You either entered the wrong MAC address or your device is not connected.")
        
        box = self.get_content_area()
        box.add(error)
        self.show_all()

class AboutBox(Gtk.Dialog):
    def __init__(self, parent):
        Gtk.Dialog.__init__(self, title="About", transient_for=parent, flags=0)
        self.add_buttons(Gtk.STOCK_OK, Gtk.ResponseType.OK)
        self.set_border_width(15)

        version = Gtk.Label()
        version.set_markup("<big><b>DualSense LED Configurator 0.1</b></big>")
        author = Gtk.Label()
        author.set_markup("<big><b>© 2020-2021 cow_killer</b></big>\n")
        source = Gtk.Label()
        
        warning = Gtk.Label()
        warning.set_markup("<b>WARNING:</b> This software is currently unstable!\n") 
        
        credits_label = Gtk.Label()
        credits_label.set_markup("Icon image by Martial Red\nController image by Khairuman\nBattery icons by nadeem\n")       
        
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
			dialog = NotRootBox(self)
			dialog.run()
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

		# Get battery percentage. Display error if file is not available and exit
		try:
			f = open("/sys/class/power_supply/ps-controller-battery-" + mac_address + "/capacity")
			status_file = open("/sys/class/power_supply/ps-controller-battery-" + mac_address + "/status")
		except FileNotFoundError:
			dialog = ErrorBox(self)
			dialog.run()
			sys.exit()
		else:
			battery_label = Gtk.Label()
			battery_icon = Gtk.Image()
			battery_percentage_left = f.read();
			status = status_file.readline().strip();
			if status == "Charging":
				battery_label.set_markup("Battery: <b>" + battery_percentage_left + "percent, charging</b>")
				battery_icon.set_from_file(charging_battery)
			else:
				battery_label.set_markup("Battery: <b>" + battery_percentage_left + "percent</b>")
				if battery_percentage_left >= "75":
					battery_icon.set_from_file(full_battery)
				elif battery_percentage_left < "75" and battery_percentage_left >= "30":
					battery_icon.set_from_file(medium_battery)
				elif battery_percentage_left < "30":
					battery_icon.set_from_file(low_battery)
			f.close()
			status_file.close()
			grid.attach(battery_label, 5, 5, 1, 1)
			grid.attach(battery_icon, 5, 6, 1, 1)
			
		# Set RGB
		pane2 = Gtk.Label()
		pane2.set_markup("<big><b>Side LEDs</b></big>")
		grid.attach(pane2, 2, 0, 1, 1)
		
		rgb_red = Gtk.Button(label="Red")
		rgb_red.connect("clicked", self.rgb_red_clicked)
		grid.attach(rgb_red, 0, 1, 1, 1)
		
		rgb_green = Gtk.Button(label="Green")
		rgb_green.connect("clicked", self.rgb_green_clicked)
		grid.attach(rgb_green, 1, 1, 1, 1)
		
		rgb_blue = Gtk.Button(label="Blue")
		rgb_blue.connect("clicked", self.rgb_blue_clicked)
		grid.attach(rgb_blue, 2, 1, 1, 1)
		
		rgb_random = Gtk.Button(label="Random")
		rgb_random.connect("clicked", self.rgb_random_clicked)
		grid.attach(rgb_random, 3, 1, 1, 1)
		
		rgb_rainbow = Gtk.Button(label="Rainbow (UNSTABLE!)")
		rgb_rainbow.connect("clicked", self.rgb_rainbow_clicked)
		grid.attach(rgb_rainbow, 4, 1, 1, 1)
		
		# RGB brightness
		pane3 = Gtk.Label()
		pane3.set_markup("<big><b>Brightness</b></big>")
		grid.attach(pane3, 2, 2, 1, 1)
		
		no_brightness = Gtk.Button(label="None")
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
		
		# Turn on/off all LEDs
		all_leds = Gtk.Button(label="Opposite LEDs Toggle")
		all_leds.connect("clicked", self.all_leds_clicked)
		grid.attach(all_leds, 2, 7, 1, 1)
		
		# Progress-bar like LED display
		prog_bar = Gtk.Button(label="Progress Bar (UNSTABLE!)")
		prog_bar.connect("clicked", self.prog_bar_clicked)
		grid.attach(prog_bar, 0, 7, 1, 1)
		
		# Random array of LEDs
		disco_leds = Gtk.Button(label="Disco! (UNSTABLE!)")
		disco_leds.connect("clicked", self.disco_leds_clicked)
		grid.attach(disco_leds, 3, 7, 1, 1)
		
		# About
		about_button = Gtk.Button(label="About")
		about_button.connect("clicked", self.about_button_clicked)
		grid.attach(about_button, 0, 100, 1, 1)
		
		# Rainbow AND Disco
		rainbow_disco = Gtk.Button(label="Rainbow AND Disco (UNSTABLE!)")
		rainbow_disco.connect("clicked", self.rainbow_disco_clicked)
		grid.attach(rainbow_disco, 2, 100, 1, 1)

		# Quit
		quit_button = Gtk.Button(label="Close")
		quit_button.connect("clicked", self.quit_button_clicked)
		grid.attach(quit_button, 5, 100, 1, 1)

		self.connect("destroy", Gtk.main_quit)
		
	# RGBs
	def rgb_red_clicked(self, widget):
		wr = open("/sys/class/leds/playstation::" + mac_address + "::rgb/multi_intensity", "r+")
		wr.write("255 0 0")
		wr.close()
		
	def rgb_green_clicked(self, widget):
		wr = open("/sys/class/leds/playstation::" + mac_address + "::rgb/multi_intensity", "r+")
		wr.write("0 255 0")
		wr.close()
		
	def rgb_blue_clicked(self, widget):
		wr = open("/sys/class/leds/playstation::" + mac_address + "::rgb/multi_intensity", "r+")
		wr.write("0 0 255")
		wr.close()
		
	def rgb_random_clicked(self, widget):
		wr = open("/sys/class/leds/playstation::" + mac_address + "::rgb/multi_intensity", "r+")
		random_red = random.randint(1, 255)
		random_green = random.randint(1, 255)
		random_blue = random.randint(1, 255)
		wr.write(str(random_red) + " " + str(random_green) + " " + str(random_blue))
		wr.close()
	
	def rgb_rainbow_clicked(self, widget):
		# Set RGB to 0 0 0 before we begin
		wr = open("/sys/class/leds/playstation::" + mac_address + "::rgb/multi_intensity", "r+")
		wr.write("0 0 0")
		wr.close()
		
		max_rgb = 255
		min_rgb = 0
		while True: # Dangerous loop, need to find a clean way to exit the program when this is on
			red = 0
			green = 0
			blue = 0
			
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
			while red != min_rgb and green != min_rgb and blue != min_rgb: # die down
				time.sleep(0.05)
				red -= random_red_increment
				green -= random_green_increment
				blue -= random_blue_increment
				wr = open("/sys/class/leds/playstation::" + mac_address + "::rgb/multi_intensity", "r+")
				wr.write(str(red) + " " + str(green) + " " + str(blue))
				wr.close()
	
	# Side LED brightness
	def no_brightness_clicked(self, widget):
		wr = open("/sys/class/leds/playstation::" + mac_address + "::rgb/brightness", "r+")
		wr.write("0")
		wr.close()
		
	def low_brightness_clicked(self, widget):
		wr = open("/sys/class/leds/playstation::" + mac_address + "::rgb/brightness", "r+")
		wr.write("85")
		wr.close()
		
	def medium_brightness_clicked(self, widget):
		wr = open("/sys/class/leds/playstation::" + mac_address + "::rgb/brightness", "r+")
		wr.write("170")
		wr.close()
	
	def max_brightness_clicked(self, widget):
		wr = open("/sys/class/leds/playstation::" + mac_address + "::rgb/brightness", "r+")
		wr.write("255")
		wr.close()
		
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
	
	# Disco LEDs
	def disco_leds_clicked(self, widget):
		# Turn off all the LEDs before proceeding
		led_number = 1
		while led_number <= 5:
			wr = open("/sys/class/leds/playstation::" + mac_address + "::led" + str(led_number) + "/brightness", 'r+')
			wr.write("0")
			wr.close()
			led_number += 1
		while True:
			random_led = random.randint(1, 5)
			wr = open("/sys/class/leds/playstation::" + mac_address + "::led" + str(random_led) + "/brightness", 'r+')
			value = wr.readline().strip()
			new_value = "1" if value == "0" else "0"
			wr.write(new_value)
			wr.close()
			time.sleep(0.3)
	
	# About box	
	def about_button_clicked(self, widget):
		dialog = AboutBox(self)
		dialog.run()
		dialog.destroy()

	def rainbow_disco_clicked(self, widget):
		# Set RGB to 0 0 0 before we begin
		wr = open("/sys/class/leds/playstation::" + mac_address + "::rgb/multi_intensity", "r+")
		wr.write("0 0 0")
		wr.close()
		
		max_rgb = 255
		min_rgb = 0
		
		# Turn off all bottom LEDs before proceeding
		led_number = 1
		while led_number <= 5:
			wr = open("/sys/class/leds/playstation::" + mac_address + "::led" + str(led_number) + "/brightness", 'r+')
			wr.write("0")
			wr.close()
			led_number += 1
		
		while True: 
			# Bottom LEDs
			random_led = random.randint(1, 5)
			wr = open("/sys/class/leds/playstation::" + mac_address + "::led" + str(random_led) + "/brightness", 'r+')
			value = wr.readline().strip()
			new_value = "1" if value == "0" else "0"
			wr.write(new_value)
			wr.close()
			time.sleep(0.3)
			
			# Side LEDs
			red = 0
			green = 0
			blue = 0
			
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
			while red != min_rgb and green != min_rgb and blue != min_rgb: # die down
				time.sleep(0.05)
				red -= random_red_increment
				green -= random_green_increment
				blue -= random_blue_increment
				wr = open("/sys/class/leds/playstation::" + mac_address + "::rgb/multi_intensity", "r+")
				wr.write(str(red) + " " + str(green) + " " + str(blue))
				wr.close()

	# Exit
	def quit_button_clicked(self, widget):
		Gtk.main_quit()

window = MainWindow()
window.show_all()
Gtk.main()
