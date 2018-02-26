import sys
import json


def write_content(file, dict_elem):
	with open(file, 'a', encoding='utf-8') as file:
		file.write(dict_elem['content'])
		file.write('\n')


def parse_corpora(input_file, source_file, mt_file, target_file):
	full_corpora = json.load(open(input_file))

	for elem in full_corpora:
		if elem['mt'] and elem['mt']['engine'] == 'Apertium':
			write_content(source_file, elem['source'])
			write_content(mt_file, elem['mt'])
			write_content(target_file, elem['target'])

	
def main():
	input_file = sys.argv[1]
	source_file = sys.argv[2]
	mt_file = sys.argv[3]
	target_file = sys.argv[4]

	parse_corpora(input_file, source_file, mt_file, target_file)


if __name__ == '__main__':
	main()