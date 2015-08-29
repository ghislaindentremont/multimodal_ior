import fnmatch
import os

# execute file in _Analysis, then go back one directory 
os.chdir('..')

# look at all files in the walk through _Data 
for root, dirnames, filenames in os.walk('_Data'):
  for filename in fnmatch.filter(filenames, '*.edf'):
	   subprocess.call('./edf2asc ./'+filename,shell=True) # I will be in multimodal_ior directory 
    