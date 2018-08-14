# Toolbox for automatic postediting (GSoC 2018)

More information about this project can be found here: http://wiki.apertium.org/wiki/Automatic_postediting_at_GSoC_2018

This is a step-by-step guide for extracting postedits and using it for improving an Apertium language pair.

### 0. Prerequisites

While working with this toolbox, you might need to install:

a) Apertium core, bel-rus and rus-ukr language pairs.

b) such Python packages as: nltk, apertium-streamparser, pymystem3.

c) Perl and apertium-eval-translator (you can download it using this link: https://sourceforge.net/projects/apertium/files/apertium-eval-translator/1.2/apertium-eval-translator-1.2.1.tar.gz/download).

d) UDPipe + models for Belarusian and Ukranian.

### 1. Data

You can take data for training and testing in following folders:

* Belarusian - Russian: https://github.com/deltamachine/naive-automatic-postediting/tree/master/data/be (for training: *train.bel, train.mt.rus, train.rus*, for testing: *test.bel, test.mt.rus, test.rus*)
* Russian - Ukranian: https://github.com/deltamachine/naive-automatic-postediting/tree/master/data/be (for training: *train.ru, train.mt.uk, train.uk*, for testing: *test.ru, test.mt.uk, test.uk*)

### 2. Algorithm for operations extraction

The rationale for this algorithm described in *rationale.md*

Run this script on your train data to extract postedits.

##### Usage

```
new_learn_postedits_algorithm.py train.source train.mt train.target source_lang target_lang path_to_language_pair context_window
```

*context_window* parameter - number of words around the word which should be postedited.

Output example for Belarusian - Russian (context window = 1): https://github.com/deltamachine/naive-automatic-postediting/blob/master/new_alg/be_data/bel-rus-postedits.txt


##### Example

```
python3 new_learn_postedits_algorithm.py train.be train.mt.ru train.ru bel rus /home/anna/apertium-bel-rus 1
```

### 3. Classifying postedits

A script for classifying extracted postedits indentifies three types of operations: potential monodix/bidix entries 
(when a pair doesn't have a translation for a given word), grammar mistakes (when Apertium chooses incorrect form of 
translated word) and other mistakes (it can be, for example, a potential lexical selection rule).

This script takes file which was generated on a previous step and generates three output files: one with "potential dictionary entries", one with "grammar mistakes" and one with "other types of mistakes". 

##### Usage

```
extract_types.py postedits.txt lang_pair
```

##### Example

```
python3 extract_types.py bel-rus_postedits.txt bel-rus
```

Output example for Belarusian - Russian:

* bidix entries: https://github.com/deltamachine/naive-automatic-postediting/blob/master/new_alg/be_data/bel-rus-bidix_entries.txt
* grammar mistakes: https://github.com/deltamachine/naive-automatic-postediting/blob/master/new_alg/be_data/bel-rus-grammar_entries.txt
* other mistakes: https://github.com/deltamachine/naive-automatic-postediting/blob/master/new_alg/be_data/bel-rus-other_entries.txt

### 4. Cleaning

The extracting postedits algorithm is not perfect and extracts a lot of garbage along with potentially good triplets. This script filters most of the garbage out.

It may take one of the files which were generated on previous step.

##### Usage

```
clean_postedits.py postedits.txt source_lang target_lang path_to_lang_pair
```

##### Example

```
python3 clean_postedits.py bel-rus_bidix_entries.txt bel rus /home/anna/apertium/apertium-bel-rus
```

Output example for Belarusian - Russian:

* bidix entries: https://github.com/deltamachine/naive-automatic-postediting/blob/master/new_alg/be_data/bel-rus-cleaned_bel-rus-bidix_entries.txt
* grammar mistakes: https://github.com/deltamachine/naive-automatic-postediting/blob/master/new_alg/be_data/bel-rus-cleaned_bel-rus-grammar_entries.txt
* other mistakes: https://github.com/deltamachine/naive-automatic-postediting/blob/master/new_alg/be_data/bel-rus-cleaned_bel-rus-other_entries.txt

### 5. Inserting operations into a language pair: dictionary approach

How to create monodix/bidix entries:

a) Run *create_entries_table.py* on a file with cleaned bidix postedits.

NB: files *ud_tags.txt* and *mystem_tags.txt* should be in the same folder as the script.
NB2: if your source/target language is Russian, type 'mystem' instead of source_ud_model_path/target_ud_model_path

```
create_entries_table.py bidix_postedits.txt source_lang target_lang ud_bin_path source_ud_model_path target_ud_model_path
```

Output example for Belarusian - Russian: https://github.com/deltamachine/naive-automatic-postediting/blob/master/new_alg/examples/bel-rus_table1.txt

##### Example

```
python3 create_entries_table.py bel-rus_bidix_entries.txt bel rus /home/udpipe/src/udpipe /home/udpipe/belarusian-ud-2.0-170801.udpipe mystem

```

b) After that, the created table should be manually checked: UDPipe/Mystem not always determine a correct lemma/tag for a word. Edit lemmas and tags if they are wrong.

Example of manually edited table: https://github.com/deltamachine/naive-automatic-postediting/blob/master/new_alg/examples/bel-rus_table2.txt

c) Run *check_entries.py* on the manually edited table. This script will look for every lemma in monolingual dictionaries and write 'True' (if lemma was found and it shouldn't be added in a monolingual dictionary) and 'False' (if lemma wasn't found) near every word in the table.


```
check_entries.py source_lang target_lang source_dict_path target_dict_path
```

##### Example

```
python3 check_entries.py bel rus /home/anna/apertium-bel/apertium-bel.bel.dix /home/anna/apertium-rus/apertium-rus.rus.dix

```

Output example: https://github.com/deltamachine/naive-automatic-postediting/blob/master/new_alg/examples/bel-rus_table3.txt

d) Manually edit the table: add a stem and a paradigm for every word, which was not found in dictionaries. If this is a 'True' lemma, just write 'none' instead stem and paradigm.

Example of the manually edited table: https://github.com/deltamachine/naive-automatic-postediting/blob/master/new_alg/examples/bel-rus_table4.txt

e) Run *add_new_entries.py* on the edited table.

```
add_new_entries.py table.txt source_path target_path pair_path source_lang target_lang
```

##### Example

```
python3 add_new_entries.py bel-rus_table.txt /home/anna/apertium-bel /home/anna/apertium-rus /home/anna/apertium-bel-rus bel rus

```

### 6. Inserting operations into a language pair: separate module approach (under development)

How to apply postedits: run *new_apply_postedits.py* on your test data.


##### Usage

```
new_apply_postedits.py source_corpus.txt mt_corpus.txt target_corpus.txt postedits.txt source_lang target_lang path_to_lang_pair
```

##### Example

```
python3 new_apply_postedits.py test.bel test.mt.rus test.rus bel-rus_bidix_entries.txt bel rus /home/anna/apertium/apertium-bel-rus
```

Output example for Belarusian - Russian: https://github.com/deltamachine/naive-automatic-postediting/blob/master/new_alg/examples/bel-rus_corrected.txt

How to check WER (run this on the file which was created on the previous step):

##### Usage

```
check_wer.py nap_output.txt path_to_eval_translator
```

##### Example

```
python3 check_wer.py bel-rus_corrected.txt /home/anna/apertium-eval-translator/apertium-eval-translator.pl
```
