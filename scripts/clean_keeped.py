import sys


input_file = sys.argv[1]
output_file = sys.argv[2]

with open(input_file, 'r', encoding='utf-8') as file:
	f = file.read().strip('\n').split('\n')

with open(output_file, 'w', encoding='utf-8') as file:
	for elem in f:
		elem = elem.split('\t')
		s1 = elem[0].split(' ')
		s2 = elem[1].split(' ')

		if len(s1) == len(s2):
			to_write = elem[0] + '\t' + elem[1]
			file.write('%s\n' % (to_write))