import os
import argparse
from pymystem3 import Mystem


"""
===================== Global arguments section =================================
"""

parser = argparse.ArgumentParser(description='A script for creating table with potentional dictionary entries')
parser.add_argument('input_file', help='File with bidix postedits')
parser.add_argument('s_lang', help='Source language')
parser.add_argument('t_lang', help='Target language')
parser.add_argument('ud_bin', help='Path to UDPipe binary file')
parser.add_argument('source_ud_model', help='Path to source language sUDPipe model file')
parser.add_argument('target_ud_model', help='Path to target language UDPipe model file')

args = parser.parse_args()

"""
===================== Main code section =================================
"""


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


def process_mystem(words, lang):
	m = Mystem()
	analysis = m.analyze(words)

	with open(lang + '_processed.txt', 'w', encoding='utf-8') as file:
		for elem in analysis:
			if elem['text'] != ' ' and elem['text'] != '\n':
				try:
					token = elem['text']
					lemma = elem['analysis'][0]['lex']
					pos_tag = elem['analysis'][0]['gr'].split(',')[0].split('=')[0]
					info = '%s\t%s\t%s\n' % (token, lemma, pos_tag)
					file.write(info)
				except:
					pass	


def process_udpipe(words, lang, bin_path, model_path):
	output_file = lang + '_processed.txt'
	command = 'echo "%s" | %s --tokenize --tag %s > %s' % (words, bin_path, model_path, output_file)
	os.system(command)


def extract_tags(lang):
	with open(lang + '_processed.txt', 'r', encoding='utf-8') as file:
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

	with open(lang + '_tags.txt', 'w', encoding='utf-8') as file:
		for elem in tags:
			file.write('%s\n' % (elem))


def collect_tag_dict(lang):
	if lang == 'rus':
		filename = 'mystem_tags.txt'
	else:
		filename = 'ud_tags.txt'

	with open(filename, 'r', encoding='utf-8') as all_tags:
		all_tags = all_tags.read().strip('\n').split('\n')

	tag_dict = {}

	for line in all_tags:
		line = line.split('\t')
		tag_dict[line[0]] = line[1]

	return tag_dict


def write_table(lang):
	with open(lang + '_processed.txt', 'r', encoding='utf-8') as file:
		processed_words = file.read().strip('\n').split('\n')

	lemmas, tags = [], []
	tag_dict = collect_tag_dict(lang)

	if lang == 'rus':
		for line in processed_words:	
			lemma = line.split('\t')[1]
			tag = line.split('\t')[2]

			lemmas.append(lemma)
			tags.append(tag_dict[tag])

			#dev mode
			if len(lemmas) == 10:
				break
	else:
		for line in processed_words:
			if line != '' and line[0] != '#':
				lemma = line.split('\t')[2]
				tag = line.split('\t')[3]
				
				lemmas.append(lemma)
				tags.append(tag_dict[tag])

			#dev mode
			if len(lemmas) == 10:
				break

	return lemmas, tags


def main():
	input_file = args.input_file
	source_lang = args.s_lang
	target_lang = args.t_lang
	ud_bin = args.ud_bin
	source_ud_model = args.source_ud_model
	target_ud_model = args.target_ud_model

	source, target = split_words(input_file)

	for s, l, u in zip([source, target], [source_lang, target_lang], [source_ud_model, target_ud_model]):
		if l == 'rus':
			process_mystem(s, l)
		else:
			process_udpipe(s, l, ud_bin, u)

	extract_tags(source_lang)
	extract_tags(target_lang)

	source_lemmas, source_tags = write_table(source_lang)
	target_lemmas, target_tags = write_table(target_lang)

	with open('%s-%s_table1.txt' % (source_lang, target_lang), 'w', encoding='utf-8') as file:
		for i in range(len(source_lemmas)):
			 file.write('%s\t%s\t%s\t%s\n' % (source_lemmas[i], source_tags[i], target_lemmas[i], target_tags[i]))


if __name__ == '__main__':
	main()