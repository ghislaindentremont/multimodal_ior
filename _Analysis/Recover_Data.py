# IS there synchrony between vmrk files and asc files? NO

""" I want:
-id
-trial_num
-cue_location
-cue_modality
-target_location
-target_modality 
-target_response_rt
	-target_on
	-* get trialDone from asc files
"""

import fnmatch
import os

def integer_to_binary(number_string): 
	number_interger = int(number_string)
	number_binary = bin(number_interger)[2:] 
	if len(number_binary) < 8:
		number_binary = number_binary.zfill(8)

	return(number_binary)	

def get_relevant_data(filename):
	    newFile = open(filename + "_new", "w") # open file in which the refined information from the original .vmrk will be put in 
		newFile.write("trial_num	cue_location	cue_modality	target_location	target_modality	target_type	target_on_time\ttrial_start_time")

		oldFile = open(filename, 'r')
    	
    	done = False
		dataStarted = False

		while not done:
			newFile.write("\n")

			line = oldFile.readline()
			if not dataStarted:
				if line[0:2] == "Mk":
					dataStarted = True
			if dataStarted:
				if line == '':
					done = True
				elif line[0:2] == "Mk":
					# first I want to get the trial variable 
					i = 5
					trial_num = line[2:i]
					while not type(trial) == int:
						i -= 1
						trial_num = line[2:i] 
					newFile.write(trial_num + "\t")
					
					# second I want to get binary derived variables
					number_string = line.replace(' ','').split(',')[1].strip().strip('S')
					if number_string == '':
						pass
					else:
						integer_to_binary(number_string)

						line = line.split(',')
						line[1] = number_binary[::-1]

						# and now extract parameters from binary and put into newFile 
						for_label = line[1]		
					
						# start of trial or target on
						if for_label[6] == "0":
							
							# cue location
							if for_label[1] == "0":
								newFile.write("left" + "\t")
							else:
								newFile.write("right" + "\t")
							
							# cue modality
							if for_label[2] == "0":
								newFile.write("visual" + "\t")
							else:
								newFile.write("auditory" + "\t")
							
							# target location
							if for_label[3] == "0":
								newFile.write("left" + "\t")
							else:
								newFile.write("right" + "\t")
							
							# target modality 
							if for_label[4] == "0":
								newFile.write("visual" + "\t")
							else:
								newFile.write("auditory" + "\t")
							
							# target type	
							if for_label[5] == "0":
								newFile.write("catch" + "\t")
							else:
								newFile.write("target" + "\t")

							# NOW GET WHEN TARGET IS ON
							
						else:
							labels.append("trial start")

							# NOW GET WHEN TRIAL HAS STARTED 



def walk_it_out():
	# execute file in _Analysis, then go back one directory 
	os.chdir('..')

	# look at all .vmrk files in the walk through _Data 
	for root, dirnames, filenames in os.walk('_EEG'):
	    for filename in fnmatch.filter(filenames, '*.vmrk'): # It will be in multimodal_ior directory
	    	get_relevant_data(filename)
					
 
    

################## LOOKING AT PREVIOUS CODE BELOW 

import os 
os.chdir("C:\Users\ghislaindentremont\Documents\R\MultiIOR\VMRK")
file = "multimodal_ior_forAlex.vmrk"
dataFile = open(file,'r')
with_binary = open("with_binary","w")
with_labels = open("with_labels", "w")
#		markers = []
done = False
dataStarted = False
while not done:
	line = dataFile.readline()
	if not dataStarted:
		if line[0:2] == "Mk":
			dataStarted = True
	if dataStarted:
		if line == '':
			done = True
		elif line[0:2] == "Mk":
			number_string = line.replace(' ','').split(',')[1].strip().strip('S')
#					print number_string
			if number_string == '':
				with_binary.write(line) 
#						markers.append(number_string)	
			else:
				number_interger = int(number_string)
#						print number_interger
				number_binary = bin(number_interger)[2:] 
				if len(number_binary) < 8:
					number_binary = number_binary.zfill(8)
#						print number_binary
#						markers.append(number_binary)
				line = line.split(',')
				line[1] = number_binary[::-1]
				# grab for label 
				line2 = line
				line = ",".join(line)
				print line
				with_binary.write(line)
				# and now I wanna label binary
				for_label = line2[1]
				labels = []
				if for_label[1] == "0":
					labels.append("left cue")
				else:
					labels.append("right cue")
				if for_label[2] == "0":
					labels.append("visual cue")
				else:
					labels.append("auditory cue")
				if for_label[3] == "0":
					labels.append("left target")
				else:
					labels.append("right target")
				if for_label[4] == "0":
					labels.append("visual target")
				else:
					labels.append("auditory target")
				if for_label[5] == "0":
					labels.append("catch")
				else:
					labels.append("target")
				if for_label[6] == "0":
					pass
				else:
					labels.append("trial start")
#						labels = ",".join(labels)
#						labels = labels.strip(",")
				labels = ",".join(labels)
				line2[1] = labels 
				# HERE to change what is in between each label
				line2 = ",".join(line2)
				with_labels.write(line2)


with_labels.close()
with_binary.close()				
dataFile.close()
