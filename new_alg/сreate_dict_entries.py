import sys


def func1(input_file, tag_file, lang):
	with open(input_file, 'r', encoding='utf-8') as file:
		file = file.read().strip('\n').split('\n')

	with open(tag_file, 'r', encoding='utf-8') as all_tags:
		all_tags = all_tags.read().strip('\n').split('\n')

	tag_dict = {}
	lemmas = []
	tags = []

	for line in all_tags:
		line = line.split('\t')
		tag_dict[line[0]] = line[1]

	if lang == 'rus':
		for line in file:
			#print(line)	
			lemma = line.split('\t')[1]
			tag = line.split('\t')[2]

			lemmas.append(lemma)
			tags.append(tag_dict[tag])

			if len(lemmas) == 10:
				break
	else:
		for line in file:
			if line != '' and line[0] != '#':
				lemma = line.split('\t')[2]
				tag = line.split('\t')[3]
				
				lemmas.append(lemma)
				tags.append(tag_dict[tag])

			if len(lemmas) == 10:
				break

	return lemmas, tags


source = sys.argv[1]
target = sys.argv[2]
source_tags = sys.argv[3]
target_tags = sys.argv[4]
source_lang = sys.argv[5]
target_lang = sys.argv[6]
output_file = sys.argv[7]

source_lemmas, source_tags = func1(source, source_tags, source_lang)
target_lemmas, target_tags = func1(target, target_tags, target_lang)

with open(output_file, 'w', encoding='utf-8') as file:
	for i in range(len(source_lemmas)):
		file.write('%s\t%s\t%s\t%s\n' % (source_lemmas[i], source_tags[i], target_lemmas[i], target_tags[i]))