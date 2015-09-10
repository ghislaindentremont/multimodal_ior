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
# this walks through given directory to find files with given extention to append them to a list. 
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

# THIS WORKS 
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
def walk_and_deconstruct(directory, extention):
	filepaths = walk_it_out(directory, extention)
	filedir_filename_tuples = deconstruct_filepaths(filepaths)
	return filedir_filename_tuples

# THIS WORKS 
def run_function(directory, extention, function):
	filendir_filename_tuples = walk_and_deconstruct(directory, extention)
	path_orig = os.getcwd()
	for (filedir, filename) in filedir_filename_tuples:
		function(filedir, filename)
		os.chdir(path_orig)

# THIS WORKS 
def find_missing_files(filedir, filename):
	list = ["e03", "e04", "e05", "e06", "e07", "e08", "e09", "e10"]
	participant_tuple= []
	for participant in list:
		if fnmatch.fnmatch(filename, "*"+participant+"*"):  
			participant_tuple.append( (filedir, filename) )
			break # might have misused break 
	return participant_tuple

# THIS WORKS 
def get_relevant_tuples(directory, extention):
	filedir_filename_tuples = walk_and_deconstruct(directory, extention)
	relevant_tuples = []
	for (filedir, filename) in filedir_filename_tuples:
		relevant_tuple = find_missing_files(filedir, filename)
		if not relevant_tuple:
			pass
		else:
			relevant_tuples.append(relevant_tuple[0])
	return relevant_tuples

# THIS WORKS 
# make list for each column 
def get_column_lists(filedir, filename):
	os.chdir(filedir)
	newFile = open(filename, "r")
	first_line = newFile.readline()
	first_line = first_line.split("\t")
	length_line = len(first_line)
	big_list = [] # list within lists 
	for i in range(length_line): # this should create a list with a list within it with just one item (header) for each column.
		temp_list = []
		temp_list.append(first_line[i])
		big_list.append(temp_list)
	lines = newFile.readlines()
	for line in lines:
		line = line.strip("\n")
		line = line.split("\t")
		for i in range(length_line):
			big_list[i].append(line[i])
	return big_list

# THIS WORKS
def rid_practice(big_list):
	for i in range(len(big_list) ):
		a_list = []
		header = big_list[i][0]
		body = big_list[i][41:]
		a_list.append(header)
		for item in body:
			a_list.append(item)
		big_list[i] = a_list 

def ignore_NA(list, change): 
	for item in list:
		if item == "NA":
			pass
		else:
			item2 = item - change
			list[list.index(item)] = item2 

# want to match .vmrk with _new EM file - assuming two big lists  
def match_vmrk_EM_files(vmrk_big_list, EM_big_list):
	length_list_EM = len(EM_big_list)
	length_list_vmrk = len(vmrk_big_list)
	if EM_big_list[1][1] == "practice":
		rid_practice(EM_big_list)
	else:
		pass
	EM = len(EM_big_list[0])
	vmrk = len(vmrk_big_list[0])
	if vmrk - EM == 40: # assume, same number prior to removing practice trials for EM, EM should now have 40 less 
		for i in range(length_list_vmrk):
			rid_practice(vmrk_big_list)
		EM = len(EM_big_list[0])
		vmrk = len(vmrk_big_list[0])
		if vmrk - EM != 0:
			return "ERROR: getting rid of practice trials did not solve the problem"
		else:
			pass 
	elif vmrk - EM == 0: # case where vmrk already was missing practice trials 
		pass 
	elif vmrk - EM < 40: # I should check before hand for the cases where the EEG may have timed out - I don't think there are any of the lost participants 
		return "ERROR: vmrk file is missing some files at the end of the experiment."
	else:
		return "ERROR: vmrk should not be more than practice trials of EM at this point, but is..."
	EM_time_start = EM_big_list[3][1]
	vmrk_time_start = vmrk_big_list[6][1]
	time_diff = EM_time_start - vmrk_time_start  # assuming that eeg was always started after Eyetracker
	if time_diff < 0:
		return "vmrk time start is greater than EM time start - should always be opposite given experimental design"
	else:
		pass
	EM_big_list[3][1:] = EM_big_list[3][1:] - time_diff # change trial start time 
	EM_big_list[4][1:] = EM_big_list[4][1:] - time_diff # change trial end time 
	ignore_NA(EM_big_list[7][1:], time_diff) # change latest saccade time
	ignore_NA(EM_big_list[8][1:], time_diff) # change latest blink time 
	return EM_big_list[3][1:] - vmrk_big_list[6][1:] # now check to be sure that trial start times match


# get relevant tuples then get biglist for each, then match?




# convert (does not replace old file) all edfs [ONLY NEED TO DO THIS ONCE]
run_function("..\_Data", "*.edf", edf_to_asc) 

# process asc files - do I want to process them out of _Data? 
run_function("..\_Data", "*.asc", process_asc) 

# create new files with organized relevant data from existing .vmrk files
run_function("..\_EEG", "*.vmrk", process_vmrk)

# create single file with relevant data from all asc-derived EM files 
run_Funtion("..\_Data", "*asc", process_EM_files)

# get relevant tuples then create big list 