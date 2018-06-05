import sys


input_file = sys.argv[1]
output_file = sys.argv[2]

with open(input_file, 'r', encoding='utf-8') as file:
	f = file.read().strip('\n').split('\n')

with open(output_file, 'w', encoding='utf-8') as file:
	for elem in f:
		if len(elem.split('\t')) != 4:
			continue

		if elem.split('\t')[3] == 'keep':
			file.write('%s\n' % (elem))