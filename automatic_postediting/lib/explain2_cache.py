#!/usr/bin/env python3

import argparse, subprocess, itertools, collections, sys
from streamparser_fixed.streamparser import parse
import pprint
from tinydb import TinyDB, Query


def analyzeText(text, locPair, pair, directory=None):
    print('/usr/local/share/apertium/apertium-{0}-{1}/{2}-{3}.automorf.bin'.format(locPair[0], locPair[1], pair[0], pair[1]))
    print('./{2}-{3}.automorf.bin'.format(locPair[0], locPair[1], pair[0], pair[1]))
    p1 = subprocess.Popen(['echo', text], stdout=subprocess.PIPE)
    if directory:
        p2 = subprocess.Popen(['lt-proc', '-a', './{2}-{3}.automorf.bin'.format(locPair[0], locPair[1], pair[0], pair[1])], stdin=p1.stdout, stdout=subprocess.PIPE, cwd=directory)
    else:
        p2 = subprocess.Popen(['lt-proc', '-a', '/usr/local/share/apertium/apertium-{0}-{1}/{2}-{3}.automorf.bin'.format(locPair[0], locPair[1], pair[0], pair[1])], stdin=p1.stdout, stdout=subprocess.PIPE)
    
    p1.stdout.close()

    return p2.communicate()[0].decode('utf-8').strip()

def translateText(text, pair, directory=None):
    p1 = subprocess.Popen(['echo', text], stdout=subprocess.PIPE)
    if directory:
        p2 = subprocess.Popen(['apertium', '-d', directory, '{0}-{1}'.format(*pair)], stdin=p1.stdout, stdout=subprocess.PIPE)
    else:
        p2 = subprocess.Popen(['apertium', '{0}-{1}'.format(*pair)], stdin=p1.stdout, stdout=subprocess.PIPE)

    p1.stdout.close()

    return p2.communicate()[0].decode('utf-8').strip()


def getCorrespondences(sourceLanguage,targetLanguage,ignoreCase,maxSourceLength,directory,maxTranslationLength, s):

    pair = (sourceLanguage, targetLanguage)
    sourceText = s.lower() if ignoreCase else s #S

    cache_db = TinyDB('cache_db2.json')
    Data = Query()


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


    translatedTextSubsegements = []
    for analyzedSourceUnitsSubsegment, startIndexInUnits, lastIndexInUnits in analyzedSourceUnitsSubsegments:
        sourceTextSubsegment = '' #s
        for i, (analyzedSourceUnitPreceedingText, analyzedSourceLexicalUnit) in enumerate(analyzedSourceUnitsSubsegment):
            sourceTextSubsegment += (analyzedSourceUnitPreceedingText if i != 0 else '') + analyzedSourceLexicalUnit.wordform

        startIndexInSourceText = sum(list(map(lambda x: len(x[0]) + len(x[1].wordform), analyzedSourceUnits[:startIndexInUnits]))) + len(analyzedSourceUnitsSubsegment[0][0]) #i
        lastIndexInSourceText = sum(list(map(lambda x: len(x[0]) + len(x[1].wordform), analyzedSourceUnits[:lastIndexInUnits+1]))) - 1 #j

        if ignoreCase:
            sourceTextSubsegment = sourceTextSubsegment.lower()


        #this stuff translates source text subsegment
        if cache_db.search((Data.type == 'stsb_translation') & (Data.key == sourceTextSubsegment)):
            translatedTextSubsegment = cache_db.search((Data.type == 'stsb_translation') & (Data.key == sourceTextSubsegment))[0]['value']
            #print('ага\n%s\n\n' % (translatedTextSubsegment))
        else:
            translatedTextSubsegment = translateText(sourceTextSubsegment, pair, directory=directory) #t
            cache_db.insert({'type': 'stsb_translation', 'key': sourceTextSubsegment, 'value': translatedTextSubsegment})
        
        if ignoreCase:
            translatedTextSubsegment = translatedTextSubsegment.lower()


        #this stuff analyzes translated text subsegment
        if cache_db.search((Data.type == 'trsb_analysis') & (Data.key == translatedTextSubsegment)):
            analyzedTranslatedTextSubsegment = cache_db.search((Data.type == 'trsb_analysis') & (Data.key == translatedTextSubsegment))[0]['value']
            #print('угу\n%s\n\n' % (analyzedTranslatedTextSubsegment))
        else:
            analyzedTranslatedTextSubsegment = analyzeText(translatedTextSubsegment, pair, pair[::-1], directory=directory)
            cache_db.insert({'type': 'trsb_analysis', 'key': translatedTextSubsegment, 'value': analyzedTranslatedTextSubsegment})
        
        #analyzedTranslatedTextSubsegment = analyzeText(translatedTextSubsegment, pair, pair[::-1], directory=directory)
        
        analyzedTranslatedTextSubsegmentUnits = list(parse(analyzedTranslatedTextSubsegment, withText=True))
        #pprint.pprint(analyzedTranslatedTextSubsegmentUnits)

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
           
    #print('Source text: %s' % repr(sourceText))
    #print('Translated text: %s\n' % repr(translatedText))
    #   pprint.pprint(correspondences)



    return correspondences
#    if table:
#        print('\n')
#        print('\n'.join(list(map(lambda i: '%s: %s %s' % (str(i).ljust(2), sourceText[i] if i < len(sourceText) else ' ', translatedText[i] if i < len(translatedText) else ' '), range(0, max(len(sourceText), len(translatedText)))))))

