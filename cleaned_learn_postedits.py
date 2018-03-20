import argparse
from lib.edwf2 import EDWF  # Modified version of Pankaj's library
# code lifted from
# http://stackoverflow.com/questions/25109001/phrase-extraction-algorithm-for-statistical-machine-translation
from lib.phr_ex import phrase_extraction
from lib.explain2 import getCorrespondences
import pprint  # for pretty printing of correspondences
import re  # regular expressions
import csv

"""
===================== Global arguments section =================================
"""

parser = argparse.ArgumentParser(description='Apertium translation parts')
parser.add_argument('sourceLanguage', help='source language')
parser.add_argument('targetLanguage', help='target language')

parser.add_argument('source_input_file', help='Source text, input') 
parser.add_argument('mt_input_file', help='Hypothesis file, input')
parser.add_argument('pe_input_file', help='Postedited output file, input')
parser.add_argument('fmt', help='Fuzzy Match Threshold', type=float)

parser.add_argument('-m', '--maxSourceLength', help='maximum length of whole-word subsegments (for source text)', type=int, default=5)
parser.add_argument('-M', '--maxTranslationLength', help='maximum length of whole word subsegments (for translated text)', type=int, default=5)
parser.add_argument('-d', '--directory', help='directory of Apertium language pair', default=None)
parser.add_argument('-t', '--table', help='prints reference table of characters', action='store_true', default=False)
parser.add_argument('-i', '--ignoreCase', help='ignore case in analyses (use lower always)', action='store_true', default=False)
parser.add_argument('-o', '--output', help='output file', default=None)

args = parser.parse_args()

"""
===================== Main code section =================================
"""


def calculate_distance(source, mt, pe):
    source_tuple = tuple((source.strip()).split())
    mt_tuple = tuple((mt.strip()).split())
    pe_tuple = tuple((pe.strip()).split())

    ed_algorithm = EDWF(mt_tuple, pe_tuple)
    distance = ed_algorithm.get_distance() * 1.0

    return ed_algorithm, distance, mt_tuple, pe_tuple


def create_opA(mt, pe, alignment):
    opA = set()

    for pair, mt, pe in phrase_extraction(mt.strip(), pe.strip(), alignment):
        opA.add((mt.strip(), pe.strip()))

    return opA


def create_opB(correspondences):
    opB = set()

    for s, t, i, j, k, l in correspondences:
        t = re.sub("\s+", " ", t)
        opB.add((s, t))

    """for s, t in correspondences:
        t = re.sub("\s+", " ", t)
        opB.add((s, t))"""

    return opB


def find_intersection(opA, opB):
    posteditops = []

    for s, t in opB:
        for hyp, ref in opA:
            if t == hyp:
                posteditops.append((s, t, ref))

    return posteditops


def extract_operations(ed_algorithm, source, mt, pe):
    alignment = ed_algorithm.get_alignment()

    opA = create_opA(mt, pe, alignment)

    correspondences = getCorrespondences(
        args.sourceLanguage,
        args.targetLanguage,
        args.ignoreCase,
        args.maxSourceLength,
        args.directory,
        args.maxTranslationLength,
        source.strip())

    with open('cor.txt', 'a', encoding='utf-8') as file:
        for s, t, i, j, k, l in correspondences:
            file.write('%s\t%s\n' % (s, t))

    """correspondences = []

    with open('cor.txt', 'r', encoding='utf-8') as file:
        for line in file.readlines():
            line = line.strip('\n')
            cor = line.split('\t')
            correspondences.append(cor)"""

    opB = create_opB(correspondences)

    posteditops = find_intersection(opA, opB)

    return posteditops


def write_operations(posteditops):
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as file:
            for source, mt, pe in posteditops:
                file.write("\"%s\",\"%s\",\"%s\"\n" % (source, mt, pe))
    else:
        print("\"%s\",\"%s\",\"%s\"\n" % (source, mt, pe))


def main():
    posteditops = []

    source_input = open(args.source_input_file, "r")
    mt_input = open(args.mt_input_file, "r")
    pe_input = open(args.pe_input_file, "r")

    for source, mt, pe in zip(source_input, mt_input, pe_input):
        ed_algorithm, distance, mt_tuple, pe_tuple = calculate_distance(source, mt, pe)

        if 1.0 - distance / max(len(mt_tuple), len(pe_tuple)) > 1.0 * args.fmt:
            posteditops += extract_operations(ed_algorithm, source, mt, pe)
    
    write_operations(posteditops)

    source_input.close()
    mt_input.close()
    pe_input.close()


if __name__ == '__main__':
    main()
