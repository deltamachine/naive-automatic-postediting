import os
import re
import sys
import argparse
from shutil import copyfile


"""
===================== Global arguments section =================================
"""

parser = argparse.ArgumentParser(description='Postediting module for Apertium pipeline')
parser.add_argument('work_mode', help='Should be either \'pe\' or \'raw\'')
parser.add_argument('lang_pair', help='For example, bel-rus')
parser.add_argument('path', help='Path to Apertium language pair') 

args = parser.parse_args()


"""
===================== Main code section =================================
"""


def copy_files(lang_pair, apertium_path):
    bd = lang_pair + '_bidix-entries.txt'
    gram = lang_pair + '_grammar-context.json'
    other = lang_pair + '_other-context.json'

    list_of_files = [bd, gram, other]

    for file in list_of_files:
        copyfile(file, apertium_path + '/' + file)


def change_module(apertium_path, lang_pair):
    with open(apertium_path + '/posteditor.py', 'r', encoding='utf-8') as file:
        f = file.read()

    f = re.sub('_bidix-entries.txt', '%s/%s_bidix-entries.txt' % (apertium_path, lang_pair), f)
    f = re.sub('_grammar-context.json', '%s/%s_grammar-context.json' % (apertium_path, lang_pair), f)
    f = re.sub('_other-context.json', '%s/%s_other-context.json' % (apertium_path, lang_pair), f)

    with open(apertium_path + '/posteditor.py', 'w', encoding='utf-8') as file:
        file.write(f)


def change_main_modes(apertium_path, main_changes, lang_pair, work_mode):
    main_modes = apertium_path + '/modes.xml'

    with open(main_modes, 'r', encoding='utf-8') as file:
        f = file.read()

    rev_lang_pair = lang_pair.split('-')[1] + '-' + lang_pair.split('-')[0]
    

    if work_mode == 'pe':
        f_splitted = f.split('\n')
        ind = None

        for i in range(len(f_splitted)):
            if '<!--' in f_splitted[i]:
                ind = i
            if rev_lang_pair in f_splitted[i]:
                break

        f = ['\n'.join(f_splitted[:ind]), main_changes, '\n'.join(f_splitted[ind:])]
        f = '\n'.join(f)

    else:
        f = re.sub(main_changes, '', f) 

    with open(main_modes, 'w', encoding='utf-8') as file:
        file.write(f)


def change_other_modes(apertium_path, other_changes, lang_pair, work_mode):
    main_mode = apertium_path + '/modes/%s.mode' % (lang_pair)
    pe_mode = apertium_path + '/modes/%s-posteditor.mode' % (lang_pair)

    with open(main_mode, 'r', encoding='utf-8') as file:
        f = file.read().strip(' \n')

    """if work_mode == 'pe':
        f = f + other_changes
    else:
        f = '|'.join(f.split('|')[:-1])"""

    f = f + other_changes

    #with open(main_mode, 'w', encoding='utf-8') as file:
        #file.write(f)

    with open(pe_mode, 'w', encoding='utf-8') as file:
        file.write(f)


def main():
    work_mode = args.work_mode
    lang_pair = args.lang_pair
    apertium_path = args.path

    python_path = 'python3'

    if apertium_path[-1] == '/':
        apertium_path = apertium_path[:-1]

    main_changes = '  <mode name="%s-posteditor" install="no">\n    <pipeline>\n        <program name="%s">\n            <file name="posteditor.py"/>\n        </program>\n    </pipeline>\n  </mode>\n\n' % (lang_pair, python_path)
    other_changes = ' | %s \'%s/posteditor.py\'' % (python_path, apertium_path)

    copyfile('posteditor.py', apertium_path + '/posteditor.py')
    copy_files(lang_pair, apertium_path)
    change_module(apertium_path, lang_pair)

    change_main_modes(apertium_path, main_changes, lang_pair, work_mode)
    change_other_modes(apertium_path, other_changes, lang_pair, work_mode)


if __name__ == '__main__':
    main()