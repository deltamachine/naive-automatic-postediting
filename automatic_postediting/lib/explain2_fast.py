#!/usr/bin/env python3

import argparse, subprocess, itertools, collections, sys, pipes, re
from streamparser_fixed.streamparser import parse
import pprint


def analyzeText(text, locPair, pair, directory=None):
    p1 = subprocess.Popen(['echo', text], stdout=subprocess.PIPE)
    if directory:
        p2 = subprocess.Popen(['lt-proc', '-a', './{2}-{3}.automorf.bin'.format(locPair[0], locPair[1], pair[0], pair[1])], stdin=p1.stdout, stdout=subprocess.PIPE, cwd=directory)
    else:
        p2 = subprocess.Popen(['lt-proc', '-a', '/usr/local/share/apertium/apertium-{0}-{1}/{2}-{3}.automorf.bin'.format(locPair[0], locPair[1], pair[0], pair[1])], stdin=p1.stdout, stdout=subprocess.PIPE)
    
    p1.stdout.close()

    return p2.communicate()[0].decode('utf-8').strip()


def analyze(input_file, output_file, directory, pair):
    pipe = pipes.Template()
    command = 'lt-proc -a ' + directory + pair[1] + '-' + pair[0] + '.automorf.bin'
    pipe.append(command, '--')
    pipe.copy(input_file, output_file)


def translateText(text, pair, directory=None):
    p1 = subprocess.Popen(['echo', text], stdout=subprocess.PIPE)
    if directory:
        p2 = subprocess.Popen(['apertium', '-d', directory, '{0}-{1}'.format(*pair)], stdin=p1.stdout, stdout=subprocess.PIPE)
    else:
        p2 = subprocess.Popen(['apertium', '{0}-{1}'.format(*pair)], stdin=p1.stdout, stdout=subprocess.PIPE)

    p1.stdout.close()

    return p2.communicate()[0].decode('utf-8').strip()


def translate(input_file, output_file, directory, pair):
    pipe = pipes.Template()
    command = 'apertium -d ' + directory + ' ' + pair[0] + '-' + pair[1]
    pipe.append(command, '--')
    pipe.copy(input_file, output_file)


def getCorrespondences(sourceLanguage,targetLanguage,ignoreCase,maxSourceLength,directory,maxTranslationLength, s):
    pair = (sourceLanguage, targetLanguage)
    sourceText = s.lower() if ignoreCase else s #S

    #this stuff analyzes source text
    analyzedSourceText = analyzeText(sourceText, pair, pair, directory=directory)

    analyzedSourceUnits = list(parse(analyzedSourceText, withText=True))

    Correspondence = collections.namedtuple('Correspondence', ['s', 't', 'i', 'j', 'k', 'l'])

    correspondences = []

    analyzedSourceUnitsSubsegments = []

    for length in range(1, maxSourceLength + 1):
        for startIndex in range(0, len(analyzedSourceUnits) - length + 1):
            lastIndex = startIndex + length - 1 
            analyzedSourceUnitsSubsegments.append((analyzedSourceUnits[startIndex:lastIndex+1], startIndex, lastIndex)) #s, i, j (analyzed units forms of them)


    #this stuff translates source text
    translatedText = translateText(sourceText, pair, directory=directory)

    if ignoreCase:
        translatedText = translatedText.lower()

    #this stuff analyzes translated text    
    analyzedTranslation = analyzeText(translatedText, pair, pair[::-1], directory=directory)
    analyzedTranslationUnits = list(parse(analyzedTranslation, withText=True))

    analyzedTranslationUnitsSubsegments = []

    for length in range(1, maxTranslationLength + 1):
        for startIndex in range(0, len(analyzedTranslationUnits) - length + 1):
            lastIndex = startIndex + length - 1
            analyzedTranslationUnitsSubsegments.append((analyzedTranslationUnits[startIndex:lastIndex+1], startIndex, lastIndex))

    #translatedTextSubsegements = []

    startIndexes = []
    lastIndexes = []
    sourceTextSubsegments = []

    for analyzedSourceUnitsSubsegment, startIndexInUnits, lastIndexInUnits in analyzedSourceUnitsSubsegments:
        sourceTextSubsegment = '' #s

        for i, (analyzedSourceUnitPreceedingText, analyzedSourceLexicalUnit) in enumerate(analyzedSourceUnitsSubsegment):
            sourceTextSubsegment += (analyzedSourceUnitPreceedingText if i != 0 else '') + analyzedSourceLexicalUnit.wordform

        startIndexInSourceText = sum(list(map(lambda x: len(x[0]) + len(x[1].wordform), analyzedSourceUnits[:startIndexInUnits]))) + len(analyzedSourceUnitsSubsegment[0][0]) #i
        lastIndexInSourceText = sum(list(map(lambda x: len(x[0]) + len(x[1].wordform), analyzedSourceUnits[:lastIndexInUnits+1]))) - 1 #j

        startIndexes.append(startIndexInSourceText)
        lastIndexes.append(lastIndexInSourceText)        

        if ignoreCase:
            sourceTextSubsegment = sourceTextSubsegment.lower()

        sourceTextSubsegments.append(sourceTextSubsegment)

    with open('source_text_subsegments.txt', 'w', encoding='utf-8') as file:
        for s in sourceTextSubsegments:
            file.write(('(( %s ))\n\n') % (s))

    translate('source_text_subsegments.txt', 'translated_text_subsegments.txt', directory, pair)
    analyze('translated_text_subsegments.txt', 'analyzed_translations.txt', directory, pair)

    """with open('source_text_subsegments.txt', 'r', encoding='utf-8') as file:
        sourceTextSubsegments = file.read().strip('\n').split('\n\n')  """

    with open('translated_text_subsegments.txt', 'r', encoding='utf-8') as file:
        translatedTextSubsegments = file.read().strip('\n').split('\n\n')  

    """for i in range(len(sourceTextSubsegments)):
        sourceTextSubsegments[i] = sourceTextSubsegments[i].strip('(( ')
        sourceTextSubsegments[i] = sourceTextSubsegments[i].strip(' ))')

        if ignoreCase:
            sourceTextSubsegments[i] = sourceTextSubsegments[i].lower()"""

    for i in range(len(translatedTextSubsegments)):
        translatedTextSubsegments[i] = translatedTextSubsegments[i].strip('(( ')
        translatedTextSubsegments[i] = translatedTextSubsegments[i].strip(' ))')

        if ignoreCase:
            translatedTextSubsegments[i] = translatedTextSubsegments[i].lower()

    with open('analyzed_translations.txt', 'r', encoding='utf-8') as file:
        analyzedTranslatedTextSubsegments = file.read().strip('\n').split('\n\n')    
        #analyzedTranslatedTextSubsegment = analyzeText(translatedTextSubsegment, pair, pair[::-1], directory=directory)

    #print(len(startIndexes))
    #print(len(sourceTextSubsegments))
    
    for i in range(len(analyzedTranslatedTextSubsegments)):
        analyzedTranslatedTextSubsegment = analyzedTranslatedTextSubsegments[i]
        translatedTextSubsegment = translatedTextSubsegments[i]
        sourceTextSubsegment = sourceTextSubsegments[i]
        startIndexInSourceText = startIndexes[i]
        lastIndexInSourceText = lastIndexes[i]

        analyzedTranslatedTextSubsegment = re.sub('\^\(\/\(\<lpar\>\$\^\(\/\(\<lpar\>\$ ', '', analyzedTranslatedTextSubsegment)
        analyzedTranslatedTextSubsegment = re.sub(' \^\)\/\)\<rpar\>\$\^\)\/\)\<rpar\>\$', '', analyzedTranslatedTextSubsegment)

        #print('meh', analyzedTranslatedTextSubsegment)    
        analyzedTranslatedTextSubsegmentUnits = list(parse(analyzedTranslatedTextSubsegment, withText=True))
        #pprint.pprint(analyzedTranslatedTextSubsegmentUnits)

        #print('meh', analyzedTranslatedTextSubsegmentUnits)
        #print('suka', analyzedTranslationUnitsSubsegments[0])

        subsegmentMatches = list(filter(lambda x: list(map(lambda y: str(y[1]), x[0])) == list(map(lambda z: str(z[1]), analyzedTranslatedTextSubsegmentUnits)) , analyzedTranslationUnitsSubsegments))
        
        if subsegmentMatches:
            startIndexInTranslatedText = sum(list(map(lambda x: len(x[0]) + len(x[1].wordform), analyzedTranslationUnits[:subsegmentMatches[0][1]]))) + len(subsegmentMatches[0][0][0][0]) #k
            lastIndexInTranslatedText = sum(list(map(lambda x: len(x[0]) + len(x[1].wordform), analyzedTranslationUnits[:subsegmentMatches[0][2]+1]))) - 1 #l

            correspondences.append(Correspondence(
                s=sourceTextSubsegment, 
                t=translatedTextSubsegment,
                i=startIndexInSourceText, 
                j=lastIndexInSourceText, 
                k=startIndexInTranslatedText, 
                l=lastIndexInTranslatedText
            ))

            #print(correspondences)
           
    return correspondences