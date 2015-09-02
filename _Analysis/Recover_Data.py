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

#def get_trial_number(line):
#	trial_num = int(line.split("=")[0][2:]) - 1 # get the number that is the trial number 
#	trial_num = str(trial_num) # then make string again
#	return(trial_num)

# THIS WORKS 
def process_vmrk(filedir, filename):
	os.chdir(filedir) # change to file's folder
	basename = os.path.splitext(filename)[0] # get base name 
	participant_id = basename.split("_")[-1]
	newFile = open(basename + "_new" + "_" + participant_id, "w") # open file in which the refined information from the original .vmrk will be put in 
	newFile.write("id\ttrial_num	cue_location	cue_modality	target_location	target_modality	target_type	trial_start_time\ttarget_on_time")
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
			else:
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
						newFile.write("\n") # make new line 
						newFile.write(participant_id) # write down participant id
						trial_num += 1 # get trial number 
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
								 
# THIS WORKS 
# this walks through given directory to find files with given extention to apply to them the given function. NOTE: the filename (output) is of type 'str'
def walk_it_out(directory, extention):
	filepaths = []
	for root, dirnames, filenames in os.walk(directory):
		for filename in fnmatch.filter(filenames, extention): # It will be in multimodal_ior directory
			filepath = os.path.join(root, filename) 
			filepaths.append(filepath)
	return filepaths 

# function to convert all edfs in a directory to asc 
def edf_to_asc(filename):
	subprocess.call('./edf2asc ./'+filename,shell=True)					

# THIS WORKS 
def process_asc(filedir, filename):
	os.chdir(filedir) # change to file's folder 
	dataFile = open(filename,'r')
	lastStart=0
	samples = []
	messages = []
	trials = []
	blinks = []
	saccades = []
	done = False
	dataStarted = False
	while not done:
		line = dataFile.readline()
		if not dataStarted:
			if line[0].isdigit():
				dataStarted = True
		if dataStarted:
			if line == '':
				done = True
			elif line[0].isdigit():
				samples.append(line.replace(' ','').split('\t')[0:4])
			elif line[0:3]=='MSG':
				temp = line[4:-1]
				temp = temp.split(' ')
				if len(temp)==2:
					time = temp[0]
					temp = temp[1].split('\t')
					temp.insert(0,time)
					trials.append(temp)
				else:
					messages.append([temp[0],' '.join(temp[1:])])
			elif line[0:5]=='ESACC':
				saccades.append(line.split()[1:])
			elif line[0:6]=='EBLINK':
				blinks.append(line.split()[1:])
			elif line[0:4] in ['SFIX','EFIX','SSAC','SBLI']:
				pass
			else:
				print line #unaccounted-for line
	
	dataFile.close()
	
	samplesFile = open('samples.txt','w')
	samplesFile.write('\n'.join(['\t'.join(thisSample) for thisSample in samples]))
	samplesFile.close()
	
	messagesFile = open('messages.txt','w')
	messagesFile.write('\n'.join(['\t'.join(thisMessage) for thisMessage in messages]))
	messagesFile.close()
	
	trialsFile = open('trials.txt','w')
	trialsFile.write('\n'.join(['\t'.join(thisTrial) for thisTrial in trials]))
	trialsFile.close()
	
	blinksFile = open('blinks.txt','w')
	blinksFile.write('\n'.join(['\t'.join(thisBlink) for thisBlink in blinks]))
	blinksFile.close()
		
	saccadesFile = open('saccades.txt','w')
	saccadesFile.write('\n'.join(['\t'.join(thisSaccade) for thisSaccade in saccades]))
	saccadesFile.close()

# function to process saccades, blinks, samples, etc. files that were derived from asc files 
def process_EM_files(filedir, filename):
	os.chdir(filedir)
	trialsFile = open('trials.txt','r')
	blinksFile = open('blinks.txt','r')
	saccadesFile = open('saccades.txt','r')
	participant_id = trialsFile.readline().split('\t')[2] # grab id variable from trials file 
	trialsFile.seek(0) # go back to beginning in case it changed 
	basename = os.path.splitext(filename)[0]
	newFile = open(basename + "_new" + "_" + participant_id,'w') # put in file name 
	newFile.write("id\tblock_num\ttrial_num\ttrial_start_time\ttrial_end_time\tsaccade\tblink\tlatest_saccade_start\tlatest_blink_start")
	done = False
	dataStarted = False
	while not done:
		line = trialsFile.readline()
		if not dataStarted: # note first item must be digit  
			if line[0].isdigit():
				dataStarted = True
		if dataStarted:
			if line == '':
				done = True
			else:
				line = line.split("\t")
				if line[1] == "trial_start":		
					newFile.write('\n')
					newFile.write(line[2] + '\t') # id 
					newFile.write(line[3] + '\t') # block number 
					newFile.write(line[4].rstrip("\n") + '\t') # trial number
					newFile.write(line[0] + '\t') # trial start time
					trial_start_time = int(line[0])
				else:
					newFile.write(line[0] + '\t') # trial end time 
					trial_end_time = int(line[0])
					temp_list = []
					saccade = "FALSE"
					saccadesFile.seek(0)
					for sac_line in saccadesFile.readlines():
						sac_line = sac_line.split('\t')
						saccade_start = int(sac_line[1])
						if (trial_start_time <= saccade_start <= trial_end_time): 
							temp_list.append(saccade_start)
							saccade = "TRUE"
						else:
							pass
					if saccade == "TRUE": 
						latest_saccade_start = max(temp_list)
					else: 
						latest_saccade_start = "NA" 
					temp_list = []
					blink = "FALSE"
					blinksFile.seek(0)
					for blk_line in blinksFile.readlines():
						blk_line = blk_line.split('\t')
						blink_start = int(blk_line[1])
						if (trial_start_time <= blink_start <= trial_end_time): 
							temp_list.append(blink_start)
							blink = "TRUE"
						else:
							pass
					if blink == "TRUE": 
						latest_blink_start = max(temp_list)
					else: 
						latest_blink_start = "NA" 
					newFile.write(saccade + '\t') 
					newFile.write(blink + '\t') 
					newFile.write(str(latest_saccade_start) + '\t')  
					newFile.write(str(latest_blink_start) ) 
	trialsFile.close()
	blinksFile.close() 
	saccadesFile.close() 
	newFile.close()

# THIS WORKS 
def deconstruct_filepaths(filepaths):
	filedir_filename_tuples = [] 
	for filepath in filepaths:
		head_tail = os.path.split(filepath)
		filedir = head_tail[0]
		filename = head_tail[1]
		filedir_filename_tuples.append( (filedir, filename) )
	return(filedir_filename_tuples)

# THIS WORKS 
def run_function(directory, extention, function):
	filepaths = walk_it_out(directory, extention)
	filedir_filename_tuples = deconstruct_filepaths(filepaths)
	path_orig = os.getcwd()
	for (filedir, filename) in filedir_filename_tuples:
		function(filedir, filename)
		os.chdir(path_orig)

# convert (does not replace old file) all edfs [ONLY NEED TO DO THIS ONCE]
run_function("..\_Data", "*.edf", edf_to_asc) 

# process asc files - do I want to process them out of _Data? 
run_function("..\_Data", "*.asc", process_asc) 

# create new files with organized relevant data from existing .vmrk files
run_function("..\_EEG", "*.vmrk", process_vmrk)
