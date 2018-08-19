import os
import sys
import argparse
import json
from nltk.tokenize import word_tokenize as tokenizer
from collections import Counter


"""
===================== Global arguments section =================================
"""

parser = argparse.ArgumentParser(description='A script for finding a context for grammar/"other" postedits')
parser.add_argument('input_file', help='File with grammar or "other" postedits')
parser.add_argument('postedits', help='File with all postedits')  
parser.add_argument('s_lang', help='Source language')
parser.add_argument('t_lang', help='Target language')
parser.add_argument('pe_type', help='Type of postedits: should be either "grammar" or "other"')

args = parser.parse_args()


"""
===================== Main code section =================================
"""


def create_entries(input_file):
	entries = []

	with open(input_file, 'r', encoding='utf-8') as file:
		file = file.read().strip('\n').split('\n')

	for line in file:
		e = line.split('\t')[:3]

		if e not in entries:
			entries.append(e)

	return entries


def create_lines(postedits):
	lines = []

	with open(postedits, 'r', encoding='utf-8') as file:
		file = file.read().strip('\n').split('\n')

	for i in range(len(file)):
		file[i] = file[i].strip('(\'')
		file[i] = file[i].strip('\')')
		file[i] = file[i].split('\', \'')

		lines.append(file[i])

	return lines


def find_context(entries, lines):
	context = {}

	for e in entries:
		context[tuple(e)] = [[], []]

		for line in lines:
			try:
				s = tokenizer(line[0])
				mt = tokenizer(line[1])
				t = tokenizer(line[2])

				if mt[0] == t[0] and mt[2] == t[2] and e[0] in s and e[1] in mt and e[2] in t:
					context[tuple(e)][0].append([s[0], s[2]])
					context[tuple(e)][1].append([mt[0], mt[2]])
			except:
				pass

	cleaned_context = {}

	for key, value in context.items():
		if value != [[], []]:
			cleaned_context['\t'.join(key)] = value

	#print(cleaned_context)

	return cleaned_context


def main():
	input_file = args.input_file
	postedits = args.postedits
	s_lang = args.s_lang
	t_lang = args.t_lang
	pe_type = args.pe_type

	entries = create_entries(input_file)
	lines = create_lines(postedits)
	cleaned_context = find_context(entries, lines)
	
	with open('%s-%s_%s-pe-context.json' % (s_lang, t_lang, pe_type), 'w') as file:
		json.dump(cleaned_context, file)


if __name__ == '__main__':
	main()