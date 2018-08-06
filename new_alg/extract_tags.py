import sys


input_file = sys.argv[1]
output_file = sys.argv[2]
lang = sys.argv[3]

with open(input_file, 'r', encoding='utf-8') as file:
	file = file.read().strip('\n').split('\n')

tags = set()

if lang == 'rus':
	for line in file:
		tag = line.split('\t')[2]
		tags.add(tag)
else:
	for line in file:
		if line != '' and line[0] != '#':
			tag = line.split('\t')[3]
			tags.add(tag)

with open(output_file, 'w', encoding='utf-8') as file:
	for elem in tags:
		file.write('%s\n' % (elem))