import sys
import kenlm


def score_sentences(postedited_set, lang_model):
	model = kenlm.Model(lang_model)

	with open(postedited_set, 'r', encoding='utf-8') as file:
		postedited_set = file.read().split('\n\n')[:-1]

	for elem in postedited_set:
		sentences = elem.split('\n')
		original_sentence = sentences[1].strip('@ ')
		postedited_sentences = sentences[2:]

		with open('scores.txt', 'a', encoding='utf-8') as file:
			original_score = model.score(original_sentence, bos = True, eos = True)
			file.write('%s\t%s\n' % (original_sentence, original_score))

			for variant in postedited_sentences:
				variant = variant.strip('$ ')
				pe_score = model.score(variant, bos = True, eos = True)
				file.write('%s\t%s\n' % (variant, pe_score))

			file.write('\n')


def main():
	postedited_set = sys.argv[1]
	lang_model = sys.argv[2]

	score_sentences(postedited_set, lang_model)


if __name__ == '__main__':
	main()