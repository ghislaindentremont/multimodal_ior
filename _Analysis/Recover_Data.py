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

# THIS WORKS 
def integer_to_binary(number_string): 
	number_interger = int(number_string)
	number_binary = bin(number_interger)[2:] 
	if len(number_binary) < 8:
		number_binary = number_binary.zfill(8)
	return(number_binary)	

# THIS WORKS (implicit)
def get_basename(filename):
	base = os.path.basename(filename)
	basename = os.path.splitext(base)[0]
	return(basename)

#def get_trial_number(line):
#	trial_num = int(line.split("=")[0][2:]) - 1 # get the number that is the trial number 
#	trial_num = str(trial_num) # then make string again
#	return(trial_num)

# 
def get_relevant_data(filename):
	basename = get_basename(filename)
	newFile = open(basename + "_new", "w") # open file in which the refined information from the original .vmrk will be put in 
	newFile.write("trial_num	cue_location	cue_modality	target_location	target_modality	target_type	trial_start_time\ttarget_on_time")
	oldFile = open(filename, 'r')
	done = False
	dataStarted = False
	trial_num = 0
	while not done:
		line = oldFile.readline()
		if not dataStarted:
			if line[0:2] == "Mk":
				dataStarted = True
		if dataStarted:
			if line == '':
				done = True
			elif line[0:2] == "Mk":
				# I want to get binary derived variables
				number_string = line.replace(' ','').split(',')[1].strip().strip('S') # this takes the number to be converted into binary
				if number_string == '':
					pass
				else:
					number_binary = integer_to_binary(number_string)
					line_original = line # make copy for get_trial_num section
					line = line.split(',')
					line[1] = number_binary[::-1]
					# and now extract parameters from binary and put into newFile 
					for_label = line[1]		
					# start of trial or target on
					if for_label[6] == "0":
						newFile.write("\n") #make new line 
						trial_num += 1 #
						trial_num_str = str(trial_num)
						newFile.write(trial_num_str)
						newFile.write("\t")
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
						# trial start time 
						trial_start_time = line[2]
						newFile.write(trial_start_time + "\t") 
					else:
						# target on time
						target_on_time = line[2]
						newFile.write(target_on_time + "\t")
	newFile.close()
	oldFile.close()
								 



def walk_it_out():
	# execute file in _Analysis, then go back one directory 
	os.chdir('..')

	# look at all .vmrk files in the walk through _Data 
	for root, dirnames, filenames in os.walk('_EEG'):
	    for filename in fnmatch.filter(filenames, '*.vmrk'): # It will be in multimodal_ior directory
	    	get_relevant_data(filename)
					
 
    

walk_it_out()
