import argparse, subprocess, itertools, pprint, sys, re, csv
from collections import Counter, namedtuple
from streamparser_fixed.streamparser import parse


"""
=======================Global arguments section===========================
"""

parser = argparse.ArgumentParser(description='Apertium translation parts')
parser.add_argument('sourceLanguage', help='source language')
parser.add_argument('targetLanguage', help='target language')
parser.add_argument('-m', '--maxSourceLength', help='maximum length of whole-word subsegments (for source text)', type=int, default=5)
parser.add_argument('-M', '--maxTranslationLength', help='maximum length of whole word subsegments (for translated text)', type=int, default=5)
parser.add_argument('-d', '--directory', help='directory of Apertium language pair', default=None)
parser.add_argument('-i', '--ignoreCase', help='ignore case in analyzations (use lower always)', action='store_true', default=False)
parser.add_argument('-o', '--operators', help='Postediting operator file')
parser.add_argument('-f', '--source_texts', help='source file', default=None)
parser.add_argument('-O', '--output_file', help='output file', default=None)

args = parser.parse_args()
operators = args.operators
pair = (args.sourceLanguage, args.targetLanguage)
output_file = args.output_file


"""
=======================Main code section====================================
"""

def analyze_text(text, locPair, pair, directory=None):
    p1 = subprocess.Popen(['echo', text], stdout=subprocess.PIPE)

    if directory:
        p2 = subprocess.Popen(['lt-proc', '-a', './{2}-{3}.automorf.bin'.format(locPair[0], locPair[1], pair[0], pair[1])], stdin=p1.stdout, stdout=subprocess.PIPE, cwd=directory)
    else:
        p2 = subprocess.Popen(['lt-proc', '-a', '/usr/local/share/apertium/apertium-{0}-{1}/{2}-{3}.automorf.bin'.format(locPair[0], locPair[1], pair[0], pair[1])], stdin=p1.stdout, stdout=subprocess.PIPE)
    
    p1.stdout.close()

    return p2.communicate()[0].decode('utf-8').strip()


def translate_text(text, pair, directory=None):
    p1 = subprocess.Popen(['echo', text], stdout=subprocess.PIPE)

    if directory:
        p2 = subprocess.Popen(['apertium', '-d', directory, '{0}-{1}'.format(*pair)], stdin=p1.stdout, stdout=subprocess.PIPE)
    else:
        p2 = subprocess.Popen(['apertium', '{0}-{1}'.format(*pair)], stdin=p1.stdout, stdout=subprocess.PIPE)

    p1.stdout.close()

    return p2.communicate()[0].decode('utf-8').strip()


def prepare_data():
    opC = set()

    with open(operators, 'r', encoding='utf-8') as file:
        reader = csv.reader(file)

        for row in reader:
            opC.add((row[0], row[1], row[2]))

    if args.source_texts == None:
       text_file = sys.stdin
    else: 
       text_file = open(args.source_texts, 'r')

    return opC, text_file


def function2(source_text):
    analyzed_source = analyze_text(source_text, pair, pair, directory=args.directory)
    analyzed_source_units = list(parse(analyzed_source, withText=True))

    correspondence = namedtuple('Correspondence', ['s', 't', 'i', 'j', 'k', 'l'])
    correspondences, analyzed_su_subsegments = [], []

    for length in range(1, args.maxSourceLength + 1):
        for start_ind in range(0, len(analyzed_source_units) - length + 1):
            last_ind = start_ind + length - 1 
            analyzed_su_subsegments.append((analyzed_source_units[start_ind:last_ind + 1], start_ind, last_ind))

    return analyzed_source, analyzed_source_units, correspondence, correspondences, analyzed_su_subsegments


def function3(source_text):
    translation = translate_text(source_text, pair, directory=args.directory)
    
    if args.ignoreCase:
        translation = translation.lower()
    
    analyzed_translation = analyze_text(translation, pair, pair[::-1], directory=args.directory)
    analyzed_translation_units = list(parse(analyzed_translation, withText=True))
    translation = re.sub("\s+", " ", translation)

    analyzed_tu_subsegments = []
        
    for length in range(1, args.maxTranslationLength + 1):
        for start_ind in range(0, len(analyzed_translation_units) - length + 1):
            last_ind = start_ind + length - 1
            analyzed_tu_subsegments.append((analyzed_translation_units[start_ind:last_ind + 1], start_ind, last_ind))


    return translation, analyzed_translation, analyzed_translation_units, analyzed_tu_subsegments


def function4(analyzed_su_preceeding_text, analyzed_source_lu, analyzed_source_units, analyzed_su_subsegment, units_start_ind, units_last_ind, i):
    st_subsegment = ''
    st_subsegment += (analyzed_su_preceeding_text if i != 0 else '') + analyzed_source_lu.wordform

    st_start_ind = sum(list(map(lambda x: len(x[0]) + len(x[1].wordform),analyzed_source_units[:units_start_ind]))) + len(analyzed_su_subsegment[0][0])
    st_last_ind = sum(list(map(lambda x: len(x[0]) + len(x[1].wordform), analyzed_source_units[:units_last_ind + 1]))) - 1 #j

    if args.ignoreCase:
        st_subsegment = st_subsegment.lower()

    return st_subsegment, st_start_ind, st_last_ind
    #тут можно сохранить все возвращаемое в файлик


def function5(st_subsegment):
    tt_subsegment = translate_text(st_subsegment, pair, directory=args.directory) #t
    
    if args.ignoreCase:
        tt_subsegment = tt_subsegment.lower()
    
    analyzed_tt_subsegment = analyze_text(tt_subsegment, pair, pair[::-1], directory=args.directory)
    analyzed_tts_units = list(parse(analyzed_tt_subsegment, withText=True))

    return tt_subsegment, analyzed_tt_subsegment, analyzed_tts_units


def function6(analyzed_tts_units, analyzed_tu_subsegments, analyzed_translation_units):
    subsegment_matches = list(filter(lambda x: list(map(lambda y: str(y[1]), x[0])) == list(map(lambda z: str(z[1]), analyzed_tts_units)) , analyzed_tu_subsegments))
                
    if subsegment_matches:
        tt_start_ind = sum(list(map(lambda x: len(x[0]) + len(x[1].wordform), analyzed_translation_units[:subsegment_matches[0][1]]))) + len(subsegment_matches[0][0][0][0])
        tt_last_ind = sum(list(map(lambda x: len(x[0]) + len(x[1].wordform), analyzed_translation_units[:subsegment_matches[0][2]+1]))) - 1

    return tt_start_ind, tt_last_ind


def function7(correspondences, opC):
    opB = set()
    
    for s, t, i, j, k, l in correspondences:
        t = re.sub("\s+", " ", t)
        opB.add((s, t))

    opD = set()

    for s, t in opB:
        for source, hyp, ref in opC:
            if s == source:
                opD.add((s, t, ref))

    return opD


def function8(translation, opD):
    tokT = translation.split()
    results = Counter()

    for s, t, ref in opD:
        toktprime = ref.split()
        tokt = t.split()       
        res = [(tokt,i) for i in range(len(tokT)) if tokT[i:i + len(tokt)] == tokt]

        for (x, j) in res:
           posteditedlist = tokT[0:j] + toktprime + tokT[j + len(tokt):]
           postedited = ""

           for element in posteditedlist:
              postedited = postedited+ " " + element
           
           results[postedited.strip()] += 1

    return results


def function9(results, sen_num, source_text, translation):
    with open(output_file, 'a', encoding='utf-8') as file:
        if results != {}:
            file.write('[%s] %s\n@ %s\n' % (sen_num, source_text, translation))

            for p in results:
                file.write('$ %s\n' % (p))

            file.write('\n')


def main():
    opC, text_file = function1()
  
    sen_num = 0
    
    for source_text in text_file:
        sen_num += 1
        source_text = source_text.strip()

        analyzed_source, analyzed_source_units, correspondence, correspondences, analyzed_su_subsegments = function2(source_text)
        translation, analyzed_translation, analyzed_translation_units, analyzed_tu_subsegments = function3(source_text)

        translated_text_subsegments = []
        
        for analyzed_su_subsegment, units_start_ind, units_last_ind in analyzed_su_subsegments:
            for i, (analyzed_su_preceeding_text, analyzed_source_lu) in enumerate(analyzed_su_subsegment):
                st_subsegment, st_start_ind, st_last_ind = function4(analyzed_su_preceeding_text, analyzed_source_lu, 
                                                                     analyzed_source_units, analyzed_su_subsegment, 
                                                                     units_start_ind, units_last_ind, i)

                tt_subsegment, analyzed_tt_subsegment, analyzed_tts_units = function5(st_subsegment)
                #print(analyzed_tts_units)
                tt_start_ind, tt_last_ind = function6(analyzed_tts_units, analyzed_tu_subsegments, analyzed_translation_units)

                correspondences.append(correspondence(
                    s=st_subsegment, 
                    t=tt_subsegment,
                    i=st_start_ind, 
                    j=st_last_ind, 
                    k=tt_start_ind, 
                    l=tt_last_ind
                ))

            opD = function7(correspondences, opC)
            results = function8(translation, opD)

        function9(results, sen_num, source_text, translation)


if __name__ == '__main__':
    main()