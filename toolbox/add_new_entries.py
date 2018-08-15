import re
import os
import argparse


"""
===================== Global arguments section =================================
"""

parser = argparse.ArgumentParser(description='A script for creating monodix/bidix entries and adding them to dictionary')
parser.add_argument('input_file', help='File with a table, created by check_entries.py and manually edited')
parser.add_argument('source_path', help='Path to source language folder, e.g. /home/apertium-bel')
parser.add_argument('target_path', help='Path to target language folder, e.g. /home/apertium-rus')
parser.add_argument('bidix_path', help='Path to language pair folder, e.g. /home/apertium-bel-rus')
parser.add_argument('s_lang', help='Source language')
parser.add_argument('t_lang', help='Target language')

args = parser.parse_args()

"""
===================== Main code section =================================
"""


def add_to_dict(dict_path, entries, prefix):
	dict_path = dict_path + '/apertium-%s.%s.dix' % (prefix, prefix)

	with open(dict_path, 'r', encoding='utf-8') as file:
		dictionary = file.read().strip('\n').split('\n')

	new_dictionary = dictionary[:-3] + ['\n'] + entries + dictionary[-3:]
	new_dictionary = '\n'.join(new_dictionary)

	with open(dict_path, 'w', encoding='utf-8') as file:
		file.write(new_dictionary)


def compile_dicts(source_path, target_path, bidix_path, source_lang, target_lang):
	os.chdir(bidix_path)

	os.system('lt-comp lr %s/apertium-%s.%s.dix %s-%s.automorf.bin' % (source_path, source_lang, source_lang, source_lang, target_lang)) 
	os.system('lt-comp rl %s/apertium-%s.%s.dix %s-%s.autogen.bin' % (source_path, source_lang, source_lang, target_lang, source_lang))

	os.system('lt-comp lr %s/apertium-%s.%s.dix %s-%s.automorf.bin' % (target_path, target_lang, target_lang, source_lang, target_lang))
	os.system('lt-comp rl %s/apertium-%s.%s.dix %s-%s.autogen.bin' % (target_path, target_lang, target_lang, target_lang, source_lang))


	os.system('lt-comp lr %s/apertium-%s.%s.dix %s-%s.automorf.bin' % (source_path, source_lang, source_lang, source_lang, target_lang)) 
	os.system('lt-comp rl %s/apertium-%s.%s.dix %s-%s.autogen.bin' % (source_path, source_lang, source_lang, source_lang, target_lang))
	os.system('lt-comp lr %s/apertium-%s.%s.dix %s-%s.automorf.bin' % (target_path, target_lang, target_lang, target_lang, source_lang))
	os.system('lt-comp rl %s/apertium-%s.%s.dix %s-%s.autogen.bin' % (target_path, target_lang, target_lang, target_lang, source_lang))

	os.system('lt-comp lr apertium-%s-%s.%s-%s.dix %s-%s.autobil.bin' % (source_lang, target_lang, source_lang, target_lang, source_lang, target_lang))
	os.system('lt-comp rl apertium-%s-%s.%s-%s.dix %s-%s.autobil.bin' % (source_lang, target_lang, source_lang, target_lang, target_lang, source_lang))


def create_entries(input_file, source_lang, target_lang):
	with open(input_file, 'r', encoding='utf-8') as file:
		words = file.read().strip('\n').split('\n')

	source_raw, target_raw = [], []
	source_entries, target_entries, bidix_entries = [], [], []

	for line in words:
		line = line.split('\t')
		source_raw.append(line[:5])
		target_raw.append(line[5:])

	for s, t in zip(source_raw, target_raw):
		if 'False' in s:
			if source_lang == 'rus':
				s_entrie = '    <e lm="%s"><p><l>%s</l><r>%s</r></p><par n="%s"/></e>' % (s[0], s[3], s[0], s[4])
			else:
				s_entrie = '    <e lm="%s"><i>%s</i><par n="%s"/></e>' % (s[0], s[3], s[4])
			source_entries.append(s_entrie)
		if 'False' in t:
			if target_lang == 'rus':
				t_entrie = '    <e lm="%s"><p><l>%s</l><r>%s</r></p><par n="%s"/></e>' % (t[0], t[3], t[0], t[4])
			else:
				t_entrie = '    <e lm="%s"><i>%s</i><par n="%s"/></e>' % (t[0], t[3], t[4])
			target_entries.append(t_entrie)

		bd_entrie = '    <e><p><l>%s<s n="%s"/></l><r>%s<s n="%s"/></r></p></e>' % (s[0], s[1], t[0], t[1])
		bidix_entries.append(bd_entrie)

	return source_entries, target_entries, bidix_entries


def main():
	input_file = args.input_file
	source_path = args.source_path
	target_path = args.target_path
	bidix_path = args.bidix_path
	source_lang = args.s_lang
	target_lang = args.t_lang

	source_entries, target_entries, bidix_entries = create_entries(input_file, source_lang, target_lang)

	add_to_dict(source_path, source_entries, source_lang)
	add_to_dict(target_path, target_entries, target_lang)
	add_to_dict(bidix_path, bidix_entries, source_lang + '-' + target_lang)

	compile_dicts(source_path, target_path, bidix_path, source_lang, target_lang)


if __name__ == '__main__':
	main()