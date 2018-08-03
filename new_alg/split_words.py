import sys


def split_words(input_file):
	with open(input_file, 'r', encoding='utf-8') as file:
		file = file.read().strip('\n').split('\n')

	source, target = [], []

	for line in file:
		source.append(line.split('\t')[0])
		target.append(line.split('\t')[2])	

	source = ' '.join(source)
	target = ' '.join(target)

	return source, target


def write_words(output_file, string):
	with open(output_file, 'w', encoding='utf-8') as file:
		file.write(string)


input_file = sys.argv[1]
output_source = sys.argv[2]
output_target = sys.argv[3]

source, target = split_words(input_file)

write_words(output_source, source)
write_words(output_target, target)
