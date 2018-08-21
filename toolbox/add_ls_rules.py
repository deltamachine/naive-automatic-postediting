import os
import re
import argparse


"""
===================== Global arguments section =================================
"""

parser = argparse.ArgumentParser(description='A script for creating lexical selection rules')
parser.add_argument('input_file', help='File with automatically generated lexical selection rules')
parser.add_argument('lang_pair', help='For example, bel-rus')
parser.add_argument('path', help='Path to Apertium language pair') 

args = parser.parse_args()


"""
===================== Main code section =================================
"""


def add_entries(dictionary, entries):
    with open(dictionary, 'r', encoding='utf-8') as file:
        old_dictionary = file.read().strip('\n').split('\n')

    for key, value in entries.items():
        l1, t1 = key[0], key[1]

        for i in range(len(old_dictionary)):
            m = re.search('<e><p><l>%s<s n="%s"/>.*?<r>(.*?)<s n="(.*?)"/>.*?</e>' % (l1, t1), old_dictionary[i])

            if m != None:
                l3 = m.group(1)
                t3 = m.group(2)
                old_dictionary[i] = '    <e><p><l>%s<s n="%s"/></l><r>%s<s n="%s"/></r></p></e>' % (l1, t1, l3, t3)

    new_dictionary = old_dictionary[:-3] + ['\n'] + list(entries.values()) + old_dictionary[-3:]
    new_dictionary = '\n'.join(new_dictionary)

    with open(dictionary, 'w', encoding='utf-8') as file:
        file.write(new_dictionary)


def create_entries(raw_rules):
    bd_entries = {}

    for rule in raw_rules:
        pair = re.search('\<match lemma=\"(.*?)\" tags=\"(.*?)\.?\*\".*?\>\n +?\<select lemma=\"(.*?)\" tags=\"(.*?)\.?\*\".*?\>', rule)

        l1 = pair.group(1)
        t1 = pair.group(2)
        l2 = pair.group(3)
        t2 = pair.group(4)

        entrie = '    <e><p><l>%s<s n="%s"/></l><r>%s<s n="%s"/></r></p></e>' % (l1, t1, l2, t2)
        bd_entries[tuple([l1, t1, l2, t2])] = entrie

    return bd_entries


def compile_dict(dictionary, autobil1, autobil2):
    os.system('lt-comp lr %s %s' % (dictionary, autobil1))
    os.system('lt-comp rl %s %s' % (dictionary, autobil2))


def add_and_compile_rules(apertium_path, ready_rules):
    with open(apertium_path + '/rules.xml', 'w', encoding='utf-8') as file:
        file.write('<rules>\n')
        file.write(ready_rules)
        file.write('\n</rules>\n')

    os.system('lrx-comp %s/rules.xml %s/rules.fst' % (apertium_path, apertium_path))    


def main():
    input_file = args.input_file
    lang_pair = args.lang_pair
    apertium_path = args.path

    reverse_lang_pair = lang_pair.split('-')[1] + '-' + lang_pair.split('-')[0]

    if apertium_path[-1] == '/':
        apertium_path = apertium_path[:-1]

    dictionary = apertium_path + '/apertium-%s.%s.dix' % (lang_pair, lang_pair)
    autobil1 = apertium_path + '/%s.autobil.bin' % (lang_pair)
    autobil2 = apertium_path + '/%s.autobil.bin' % (reverse_lang_pair)

    with open(input_file, 'r', encoding='utf-8') as file:
        ready_rules = file.read().strip('\n')

    raw_rules = ready_rules.split('\n\n')
    bidix_entries = create_entries(raw_rules)

    add_entries(dictionary, bidix_entries)
    compile_dict(dictionary, autobil1, autobil2)
    add_and_compile_rules(apertium_path, ready_rules)


if __name__ == '__main__':
    main()