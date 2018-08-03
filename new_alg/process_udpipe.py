import os
import sys


def main():
	input_file = sys.argv[1]
	bin_path = sys.argv[2]
	model_path = sys.argv[3]
	output_file = sys.argv[4]

	with open(input_file, 'r', encoding='utf-8') as file:
		words = file.read().strip('\n')

	command = 'echo "%s" | %s --tokenize --tag %s > %s' % (words, bin_path, model_path, output_file)
	os.system(command)


if __name__ == '__main__':
	main()