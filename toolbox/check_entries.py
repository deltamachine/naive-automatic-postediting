import re
import argparse


"""
===================== Global arguments section =================================
"""

parser = argparse.ArgumentParser(description='A helper script for checking, if word is in a dictionary')
parser.add_argument('input_file', help='File with a table, created by create_entries_table.py')
parser.add_argument('s_lang', help='Source language')
parser.add_argument('t_lang', help='Target language')
parser.add_argument('source_dict_path', help='Path to source monolingual dictionary, e.g. apertium-bel.bel.dix')
parser.add_argument('target_dict_path', help='Path to target monolingual dictionary, e.g. apertium-rus.rus.dix')

args = parser.parse_args()

"""
===================== Main code section =================================
"""


def find_lemma(word, dict_path):
	with open(dict_path, 'r', encoding='utf-8') as file:
		dictionary = file.read()

	pattern = 'lm=\"' + word + '\"' 
	dict_entrie = re.search(pattern, dictionary)

	if dict_entrie != None:
		return 'True'
	else:
		return 'False'


def main():
	input_file = args.input_file
	source_lang = args.s_lang
	target_lang = args.t_lang
	source_dict_path = args.source_dict_path
	target_dict_path = args.target_dict_path

	with open(input_file, 'r', encoding='utf-8') as file:
		entries = list(set(file.read().strip('\n').split('\n')))

	with open('%s-%s_table3.txt' % (source_lang, target_lang), 'w', encoding='utf-8') as file:
		for line in entries:
			line = line.split('\t')
			source_found = find_lemma(line[0], source_dict_path)
			target_found = find_lemma(line[2], target_dict_path)

			file.write('%s\t%s\t%s\t%s\t%s\t%s\n' % (line[0], line[1], source_found, line[2], line[3], target_found))


if __name__ == '__main__':
	main()
