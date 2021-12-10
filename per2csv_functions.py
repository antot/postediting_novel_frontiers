#!/usr/bin/env python3

def check_annotation_done ( tree ):
#	status = tree.find('./job').attrib['status']
	status = tree.getroot().get('status')
	if status != "FINISHED":
		print("KAPUT") #TODO Avort!
		print(tree.getroot().attrib)
	#print(status)

# converts a time expression from a per file to seconds
# e.g. 1m15s,719 -> 75.719
def time2seconds ( input ):
	hours = 0
	minutes = 0
	seconds = 0
	milliseconds = 0

	if "," in input:
		milliseconds = int(input.split(",")[1])
	if "h" in input:
		hours = int(input.split("h")[0])
		input = input.split("h")[1]
	if "m" in input:
		minutes = int(input.split("m")[0])
	if "s" in input:
		seconds_str = input.split("s")[0]
		if "m" in seconds_str:
			seconds_str = seconds_str.split("m")[1]
		seconds = int(seconds_str)

	#print(minutes,seconds,milliseconds)
	return hours * 3600 + minutes*60 + seconds + milliseconds / 1000

