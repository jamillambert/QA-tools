# Python script to batch rename with a number appended for all files in a directory with the specified extension
# Jamil Lambert 2020
#
# usage:
#    run in directory containing files
#    python rename.py arg1 arg2
#    where arg1 = current file name ending e.g. .xlsx
#           arg2 = new file name stem

import os, sys

if len(sys.argv) != 3 :
	print('Invalid input arguments, example usage: python rename.py .xlsx newFileName')
else:
	i = 0
	for f in os.listdir('.'):
		if f.endswith(str(sys.argv[1])):
			i = i +1
			fileName = str(i) + '_' + str(sys.argv[2]) + str(sys.argv[1])
			os.rename(f, fileName)
	if i == 0:
		print('No files found with extension' + str(sys.argv[1]))
	else:
		print(str(i) + ' files renamed in the format ' + str(sys.argv[2]) + '_x' + str(sys.argv[1]))
