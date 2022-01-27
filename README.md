# DualSense LED Configurator
![DS LED Config Screenshot](https://i.imgur.com/sVz4LCD.png)
This program allows the user to adjust color and brightness to the various LEDs found throughout the DualSense (DS). Rainbow, disco, or otherwise random effects can be applied, though these are unstable. Also fetches battery percentage and displays this.

## Prerequisites (besides your DS, obviously)
* Linux-based operating system with kernel 5.12 or later
* Access to root privileges (the program modifies the values found in `/sys/devices/pci0000:00/(long string followed by a bunch of folders/`)
* Python 3
* GTK 3
* Tkinter

## What You Should Know
The program is highly unstable depending on what button you press, in particular:
* Rainbow LED colors
* Disco/Progress bar LED patterns

Clicking any of those buttons (which have been labeled as unstable accordingly) will cause the program to loop indefinitely. You'll need to one of the following:
* Press `Enter` in the terminal window to either close the application or keep it from looping
* force exit the application through your system monitor 
* disconnect your DS

Other tasks going on on your computer will still run regardless.

## How To Use
1. Clone the repository:<br>
`git clone https://github.com/cow-killer/dualsense-led-configurator.git`
2. Change into the `dualsense-led-configurator` folder and run the script as root:<br>
`sudo python ds_led.py`

## To-Do
* Much-needed UI polish
* Find a way to get rainbow LEDs, disco, etc. to work without hanging the application 
* Update UI if controller is plugged/unplugged and if the percentage of the battery has changed

Pull requests welcomed!
