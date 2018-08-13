import re
import sys


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
	input_file = sys.argv[1]
	source_lang = sys.argv[2]
	target_lang = sys.argv[3]
	source_dict_path = sys.argv[4]
	target_dict_path = sys.argv[5]

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
