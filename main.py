import os, platform, sys, subprocess, shutil, plistlib

#* Checks for the script

# checks if the os running the script is mac os (darwin)
if platform.system() != "Darwin":
	sys.exit("Please use a mac to run this script!")

# checks if script is run as root
if os.geteuid() != 0:
	sys.exit("This script requires root access to work. \n(you also need to disable the SIP if using an version past 10.11)")

# checks if the mac is intel or apple silicon
if platform.mac_ver()[2] != "x86_64":
	sys.exit(f"The mac you are currently using doesn't support bootcamp.")

#* Functions

# function to run a command in the terminal and return it to the program
def getCMDResult(cmd):

	# runs the command provided in the shell terminal
	run = subprocess.run(cmd, stdout=subprocess.PIPE, shell=True, check=True)
	
	# strips the outputed result
	result = run.stdout.strip()

	# returns the result variable
	return result

# function to edit a key in a plist file
def editPlistKey(file, oldKey, newKey):
	
	# opens the plist file as read-bytes
	with open(file, "rb") as f:
		plistData = plistlib.load(f)

	# checks if the key value in the plist file equals the old key value provided
	if oldKey in plistData:
		
		# changes the key value
		value = plistData.pop(oldKey)
		plist_data[new_key] = value

		# writes the key value to the plist file
		with open(file, "wb") as f:
			plistlib.dump(plistData, f)

# function to edit a string in a plist file
def editPlistString(file, key, newValue):

	# opens the plist file as read-bytes
	with open(file, "rb") as f:
		plistData = plistlib.load(f)

		# checks if the new value in the plist file equals the old value
		if key in plistData and isinstance(plistData[key], str):
			
			# changes the value
			plistData[key] = newValue

			# writes the new value to the plist file
			with open(file, "wb") as f:
				plistlib.dump(plistData, f)

# function to edit a array in a plist file
def editPlistArray(file, arrayKey, newValue):

	# opens the plist file as read-bytes
	with open(file, "rb") as f:
		plistData = plistlib.load(f)

	# appends the new value into the existing array
	plistData[arrayKey].append(newValue)

	# writes th new value to the plist file
	with open(file, "wb") as f:
		plistlib.dump(plistData, f)

def editPlist(file):

	# dictionary of edit functions
	edits = {
        'string_key': 'new_string_value',
        'array_key': ['new_element1', 'new_element2'],
        'nested_dict': {'nested_key': 'new_nested_value'}
    }

    # opens the plist file
	with open(file, "rb") as f:

		# loads file data into 'plistData' variable
		plistData = plistlib.load(f)

	# checks what edit needs to be performed
	for key, value in edits.items():

		# executes the edit
		if isinstance(plistData.get(key), list) and isinstance(value, list):
			plistData[key].extend(value)

		# checks if the data already exists
		else:
			plistData[key] = value

	# writes the modified data to the plist file
	with open(file, "wb") as f:
		plistlib.dump(plistData, f)


# function to backup a file
def fileBak(sourceFile):

	# creates a duplicate of the source file and adds .bak as its extention
	shutil.copy(sourceFile, f"{sourceFile}.bak")

#* Pre-defined variables

# bootcamp app location
bootcamp = '/Applications/Utilities/Boot Camp Assistant.app'

# bootcamp Info.plist file location
bootcampPlist = '/Applications/Utilities/Boot Camp Assistant.app/Contents/Info.plist'

#* Main code

# get the macs model identifier
modelID = getCMDResult("system_profiler SPHardwareDataType | awk '/Model Identifier/ {print $3}'").decode("utf-8")

# get the macs boot rom version
bootROMVer = getCMDResult("system_profiler SPHardwareDataType | awk '/Boot ROM Version/ {print $4}'").decode("utf-8")

# backup the original Info.plist file for recovery purposes
fileBak(bootcampPlist)

# add your mac model id to the 'PreUEFIModel' string in the Info.plist file
editPlistArray(bootcampPlist, "PreUEFIModels", modelID)

# add your mac model id to the 'USBBootSupportedModels' string int the Info.plist file
editPlistArray(bootcampPlist, "PreUSBBootSupportedModels", modelID)

# check if the Xcode command line tools are installed
if "version:" in str(getCMDResult("pkgutil --pkg-info=com.apple.pkg.CLTools_Executables | awk '/version/ {print $1}'")) == False:
	print("To procede with the modification of bootcamp you need to install the xcode command line utilities.")
	os.system("xcode-select --install")

# codesign the bootcamp app
os.system("sudo codesign -fs - /Applications/Utilities/Boot\\ Camp\\ Assistant.app")


