import sys
import os
from nltk.tokenize import word_tokenize as tokenizer
from collections import Counter
from pymystem3 import Mystem


def process_mystem(words):
	m = Mystem()

	words = ' '.join(list(words.keys()))
	analysis = m.analyze(words)
	info = {}

	for elem in analysis:
		if elem['text'] != ' ' and elem['text'] != '\n':
			try:
				token = elem['text']
				lemma = elem['analysis'][0]['lex']

				if lemma not in info.keys():
					info[lemma] = []

				info[lemma].append(token)
			except:
				pass

	return info
	

def distance(a, b):
	"""Calculates the Levenshtein distance between string a and string b."""

	n, m = len(a), len(b)

	if n > m:
		a, b = b, a
		n, m = m, n

	current_row = range(n + 1)

	for i in range(1, m + 1):
		previous_row, current_row = current_row, [i] + [0] * n

		for j in range(1, n + 1):
			add, delete, change = previous_row[j] + 1, current_row[j - 1] + 1, previous_row[j - 1]
			
			if a[j - 1] != b[i - 1]:
				change += 1

			current_row[j] = min(add, delete, change)

	return current_row[n]


def process_levenshtein(old_words):
	words = list(old_words.keys())
	info = {}

	for i in range(len(words)):
		info[words[i]] = [[words[i], old_words[words[i]]]]
		for j in range(i+1, len(words)):
			dis = distance(words[i], words[j])
			letters1 = len(words[i])
			letters2 = len(words[j])
			percent1 = (letters1 - dis) / letters1 * 100
			percent2 = (letters2 - dis) / letters2 * 100

			if percent1 >= 40 or percent2 >= 40:
				info[words[i]].append([words[j], old_words[words[j]]])

	return info

other_entries = sys.argv[1]
postedits = sys.argv[2]

entries = []
lines = []

with open(other_entries, 'r', encoding='utf-8') as file:
	file = file.read().strip('\n').split('\n')

for line in file:
	e = line.split('\t')[:3]

	if e not in entries:
		entries.append(e)

with open(postedits, 'r', encoding='utf-8') as file:
	file = file.read().strip('\n').split('\n')

for i in range(len(file)):
	file[i] = file[i].strip('(\'')
	file[i] = file[i].strip('\')')
	file[i] = file[i].split('\', \'')

	lines.append(file[i])

context = {}

for e in entries:
	context[tuple(e)] = [[], []]
	for line in lines:
		try:
			s = tokenizer(line[0])
			mt = tokenizer(line[1])
			t = tokenizer(line[2])

			if e[0] in s and e[1] in mt and e[2] in t:
				context[tuple(e)][0] += s
				context[tuple(e)][1] += mt
		except:
			pass


for key, value in context.items():
	value[0] = Counter(value[0])
	del value[0][key[0]]
	del value[0][',']
	del value[0]['.']

	value[1] = Counter(value[1])
	del value[1][key[1]]
	del value[1][',']
	del value[1]['.']

	s_info = process_levenshtein(value[0])
	mt_info = process_mystem(value[1])
	print(s_info, '\n\n')
	print(mt_info, '\n\n')


