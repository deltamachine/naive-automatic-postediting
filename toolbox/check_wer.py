import re
import os
import argparse


"""
===================== Global arguments section =================================
"""

parser = argparse.ArgumentParser(description='A script for checking WER')
parser.add_argument('input_file', help='Input file, which was created by new_apply_postedits.py')
parser.add_argument('eval_path', help='Path to apertium-eval-translator Perl script')

args = parser.parse_args()


"""
===================== Main code section =================================
"""


def clean_text(input_file):
	with open(input_file, 'r', encoding='utf-8') as file:
		input_file = file.read().strip('\n')

	"""input_file = re.sub(' \.', '.', input_file)
	input_file = re.sub(' ,', ',', input_file)
	input_file = re.sub(' \?', '?', input_file)
	input_file = re.sub(' !', '!', input_file)
	input_file = re.sub(' :', ':', input_file)
	input_file = re.sub(' ;', ';', input_file)
	input_file = re.sub('" ', '"', input_file)
	input_file = re.sub(' "', '"', input_file)
	input_file = re.sub('« ', '«', input_file)
	input_file = re.sub(' »', '»', input_file)
	input_file = re.sub('#', '', input_file)"""
	input_file = re.sub('MT\t', ' ', input_file)
	input_file = re.sub('T\t', ' ', input_file)
	input_file = re.sub('ED\t', ' ', input_file)

	return input_file


def write_hyp_and_ref(input_file):
	cases = input_file.split('\n\n')

	with open('hyp1.txt', 'w', encoding='utf-8') as file1, \
	open('hyp2.txt', 'w', encoding='utf-8') as file2, \
	open('ref.txt', 'w', encoding='utf-8') as file3:
		for elem in cases:
			elem = elem.split('\n')
			mt = elem[1]

			if elem[2] != ' ':
				ed = elem[2]
			else:
				ed = elem[1]

			pe = elem[-1]

			file1.write('%s\n' % (mt.strip(' ')))
			file2.write('%s\n' % (ed.strip(' ')))
			file3.write('%s\n' % (pe.strip(' ')))	


def main():
	input_file = args.input_file
	eval_path = args.eval_path

	input_file = clean_text(input_file)
	write_hyp_and_ref(input_file)

	os.system('perl %s -test hyp1.txt -ref ref.txt' % (eval_path))
	os.system('perl %s -test hyp2.txt -ref ref.txt' % (eval_path))


if __name__ == '__main__':
	main()