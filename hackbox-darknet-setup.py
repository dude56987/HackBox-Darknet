#! /usr/bin/python
########################################################################
# Setup privoxy,tor,and i2p to work together to run for entire system
# Copyright (C) 2014  Carl J Smith
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
########################################################################
import os,sys
########################################################################
def loadFile(fileName):
	try:
		print "Loading :",fileName
		fileObject=open(fileName,'r');
	except:
		print "Failed to load :",fileName
		return False
	fileText=''
	lineCount = 0
	for line in fileObject:
		fileText += line
		sys.stdout.write('Loading line '+str(lineCount)+'...\r')
		lineCount += 1
	print "Finished Loading :",fileName
	fileObject.close()
	if fileText == None:
		return False
	else:
		return fileText
	#if somehow everything fails return fail
	return False
########################################################################
def appendFile(fileName,infoToAppend):
	try:
		# append file
		temp = loadFile(fileName)
		# if file exists append, if not write
		if temp != False:
			temp += infoToAppend+'\n'
		else:
			temp = infoToAppend+'\n'
		writeFile(fileName,temp)
	except:
		# if above code fails return false
		return False
########################################################################
def replaceLineInFile(fileName,stringToSearchForInLine,replacementText):
	# open file
	temp = loadFile(fileName).split('\n')
	# if file exists append, if not write
	newFileText = ''
	if temp != False:
		for line in temp:
			if line.find(stringToSearchForInLine) == -1:
				newFileText += line+'\n'
			else:
				if replacementText != '':
					print 'Replacing line:',line
					print 'With:',replacementText
					newFileText += replacementText+'\n'
				else:
					print 'Deleting line:',line
	else:
		return False
	writeFile(fileName,newFileText)
########################################################################
def deleteLineFromFile(fileName,stringFromLineToDelete):
	replaceLineInFile(fileName,stringFromLineToDelete,'');
########################################################################
def writeFile(fileName,contentToWrite):
	try:
		fileObject = open(fileName,'w')
		fileObject.write(contentToWrite)
		fileObject.close()
		print 'Wrote file to:',fileName
	except:
		print 'ERROR: Could not write file to ',fileName
		return False
########################################################################
# check to see if the program is being run as root
if os.geteuid() != 0:
	print 'ERROR: setupTor must be run as root!'
	exit()
# setting up i2p deepweb protocall though ppa ##########################
os.system('apt-add-repository ppa:i2p-maintainers/i2p')
os.system('apt-fast update')
os.system('apt-fast install i2p')
os.system('dpkg-reconfigure i2p')
# install tor + privoxy
os.system('apt-get install tor privoxy macchanger')
# build the macchanger boot script #####################################
#  changing the mac address at boot ensures connections appear from a
#  diffrent machine each time user reboots, this is not on a timer since
#  the interface needs brought down each time the mac is changed
macChangerBootScript = ''
macChangerBootScript += "#! /usr/bin/python\n"
macChangerBootScript += "from os import system\n"
macChangerBootScript += "for index in range(51):\n"
macChangerBootScript += "\tsystem(('sudo macchanger --another eth'+str(index)))\n"
macChangerBootScript += "\tsystem(('sudo macchanger --another wlan'+str(index)))\n"
writeFile('/usr/bin/macRandomizer',macChangerBootScript)
os.system('chmod +x /usr/bin/macRandomizer')
# if rc.local is already edited remove old before writing (lazy I know)
deleteLineFromFile('/etc/rc.local','macRandomizer')
# set macRandomizer to launch at boot though rc.local file
replaceLineInFile('/etc/rc.local','exit 0','macRandomizer\nexit 0')
########################################################################
# edit privoxy config to forward tor and i2p web links #################
# remove lines if they exist already
deleteLineFromFile('/etc/privoxy/config','forward-socks4a / localhost:9050 .')
deleteLineFromFile('/etc/privoxy/config','forward .i2p localhost:4444')
# add lines to end of file
appendFile('/etc/privoxy/config','forward-socks4a / localhost:9050 .')
appendFile('/etc/privoxy/config','forward .i2p localhost:4444')
# remove logging by privoxy done by default to improve security
deleteLineFromFile('/etc/privoxy/config','logfile logfile')
# restart privoxy for changes to take place
os.system('service privoxy restart')
if '--setup-firefox' in sys.argv:
	# edit users firefox config files to turn on privoxy+tor+i2p ###########
	print 'Editing users settings...'
	# edit firefox user prefs.js file for these values
	# first you must kill firefox or the prefs will be overwritten when ff closes
	os.system('killall firefox') # should be ran as root to kill all instances on system
	# build parallel arrays of data for loop that will edit prefs data
	newSettingsSearchString = []# string will be searched for
	newSettings = []# line containing above string will be replaced with new value
	newSettingsSearchString.append("network.proxy.socks")
	newSettings.append('user_pref("network.proxy.socks", "127.0.0.1");')
	newSettingsSearchString.append("network.proxy.socks_port")
	newSettings.append('user_pref("network.proxy.socks_port", 9050);')
	newSettingsSearchString.append('network.proxy.socks_remote_dns')
	newSettings.append('user_pref("network.proxy.socks_remote_dns", true);')
	newSettingsSearchString.append('network.proxy.http')
	newSettings.append('user_pref("network.proxy.http_port", "::1");')
	newSettingsSearchString.append('network.proxy.http')
	newSettings.append('user_pref("network.proxy.http_port", 8118);')
	newSettingsSearchString.append('network.proxy.ssl')
	newSettings.append('user_pref("network.proxy.ssl", "::1");')
	newSettingsSearchString.append('network.proxy.ssl_port')
	newSettings.append('user_pref("network.proxy.ssl_port", 8118);')
	# then search though all users home directorys and firefox profiles and edit config
	for folder in os.listdir('/home'):
		if os.path.exists(os.path.join('/home',folder,'.mozilla','firefox')):
			for subfolder in os.listdir(os.path.join('/home',folder,'.mozilla','firefox')):
				if os.path.exists(os.path.join('/home',folder,'.mozilla','firefox',subfolder,'prefs.js')):
					#~ tempConfig=loadFile(os.path.join('/home',folder,'.mozilla','firefox',subfolder,'prefs.js')).split('\n')
					newConfig = ''
					for index in range(len(newSettings)):
						# replace each setting in the file
						replaceLineInFile(os.path.join('/home',folder,'.mozilla','firefox',subfolder,'prefs.js'),newSettingsSearchString[index],newSettings[index])
					# after editing file write the new version of the file
					# make user the owner of this file once more since root is editing the files
					print ('chown '+folder+' '+os.path.join('/home',folder,'.mozilla','firefox',subfolder,'prefs.js'))
					os.system(('chown '+folder+' '+os.path.join('/home',folder,'.mozilla','firefox',subfolder,'prefs.js')))
else:
	print 'Use --setup-firefox to configure firefox to work with proxys.'
print 'Install of Tor, I2P, and privoxy as well as configuration of firefox complete, you now have access to the deepweb!'
print 'To make anything else go though tor set the proxy server ip to ::1 and the port to 8118'
