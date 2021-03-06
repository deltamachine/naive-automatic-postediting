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

* Belarusian - Russian: https://github.com/deltamachine/naive-automatic-postediting/tree/master/toolbox/bel-rus_data/train-test (for training: *train.bel, train.mt.rus, train.rus*, for testing: *test.bel, test.mt.rus, test.rus*)
* Russian - Ukranian: https://github.com/deltamachine/naive-automatic-postediting/tree/master/toolbox/rus-ukr_data/train-test (for training: *train.ru, train.mt.uk, train.uk*, for testing: *test.ru, test.mt.uk, test.uk*)
* Spanish - Catalan: https://github.com/deltamachine/naive-automatic-postediting/tree/master/toolbox/spa-cat_data (for training: *train.spa, train.mt.cat, train.cat*, for testing: *test.spa, test.mt.cat, test.cat*)

### 2. Algorithm for operations extraction

The rationale for this algorithm described in *rationale.md*

Run this script on your train data to extract postedits.

##### Usage

```
new_learn_postedits_algorithm.py train.source train.mt train.target source_lang target_lang path_to_language_pair context_window
```

*context_window* parameter - number of words around the word which should be postedited.

Output example for Belarusian - Russian (context window = 1): https://github.com/deltamachine/naive-automatic-postediting/blob/master/toolbox/bel-rus_data/bel-rus-postedits.txt


##### Example

```
python3 new_learn_postedits_algorithm.py bel-rus_data/train-test/train.bel bel-rus_data/train-test/train.mt.rus bel-rus_data/train-test/train.rus bel rus /home/.../apertium-bel-rus 1
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

* bidix entries: https://github.com/deltamachine/naive-automatic-postediting/blob/master/toolbox/bel-rus_data/bel-rus-bidix_entries.txt
* grammar mistakes: https://github.com/deltamachine/naive-automatic-postediting/blob/master/toolbox/bel-rus_data/bel-rus-grammar_entries.txt
* other mistakes: https://github.com/deltamachine/naive-automatic-postediting/blob/master/toolbox/bel-rus_data/bel-rus-other_entries.txt

### 4. Cleaning

The extracting postedits algorithm is not perfect and extracts a lot of garbage along with potentially good triplets. This script filters most of the garbage out.

It may take one of the files which were generated on previous step.

##### Usage

```
clean_postedits.py postedits.txt source_lang target_lang path_to_lang_pair
```

##### Example

```
python3 clean_postedits.py bel-rus_bidix_entries.txt bel rus /home/.../apertium-bel-rus
```

Output example for Belarusian - Russian:

* bidix entries: https://github.com/deltamachine/naive-automatic-postediting/blob/master/toolbox/bel-rus_data/bel-rus-cleaned_bel-rus-bidix_entries.txt
* grammar mistakes: https://github.com/deltamachine/naive-automatic-postediting/blob/master/toolbox/bel-rus_data/bel-rus-cleaned_bel-rus-grammar_entries.txt
* other mistakes: https://github.com/deltamachine/naive-automatic-postediting/blob/master/toolbox/bel-rus_data/bel-rus-cleaned_bel-rus-other_entries.txt

### 5. Inserting operations into a language pair: dictionary approach

##### How to create monodix/bidix entries:

a) Run *create_entries_table.py* on a file with cleaned bidix postedits.

NB: files *ud_tags.txt* and *mystem_tags.txt* should be in the same folder as the script.

NB2: if your source/target language is Russian, type 'mystem' instead of source_ud_model_path/target_ud_model_path

```
create_entries_table.py bidix_postedits.txt source_lang target_lang ud_bin_path source_ud_model_path target_ud_model_path
```

Output example for Belarusian - Russian: https://github.com/deltamachine/naive-automatic-postediting/blob/master/toolbox/examples/bel-rus_table1.txt

##### Example

```
python3 create_entries_table.py bel-rus_bidix_entries.txt bel rus /home/.../udpipe/src/udpipe /home/.../belarusian-ud-2.0-170801.udpipe mystem

```

b) After that, the created table should be manually checked: UDPipe/Mystem not always determine a correct lemma/tag for a word. Edit lemmas and tags if they are wrong.

Example of manually edited table: https://github.com/deltamachine/naive-automatic-postediting/blob/master/toolbox/examples/bel-rus_table2.txt

c) Run *check_entries.py* on the manually edited table. This script will look for every lemma in monolingual dictionaries and write 'True' (if lemma was found and it shouldn't be added in a monolingual dictionary) and 'False' (if lemma wasn't found) near every word in the table.


```
check_entries.py source_lang target_lang source_dict_path target_dict_path
```

##### Example

```
python3 check_entries.py bel rus /home/.../apertium-bel/apertium-bel.bel.dix /home/.../apertium-rus/apertium-rus.rus.dix

```

Output example: https://github.com/deltamachine/naive-automatic-postediting/blob/master/toolbox/examples/bel-rus_table3.txt

d) Manually edit the table: add a stem and a paradigm for every word, which was not found in dictionaries. If this is a 'True' lemma, just write 'none' instead stem and paradigm.

Example of the manually edited table: https://github.com/deltamachine/naive-automatic-postediting/blob/master/toolbox/examples/bel-rus_table4.txt

e) Run *add_new_entries.py* on the edited table.

```
add_new_entries.py table.txt source_path target_path pair_path source_lang target_lang
```

##### Example

```
python3 add_new_entries.py bel-rus_table.txt /home/.../apertium-bel /home/.../apertium-rus /home/.../apertium-bel-rus bel rus

```


##### How to create lexical selection rules:

1. Run _find_context.py_ on your file with "other" mistakes.

```
find_context.py other_entries.txt all_postedits.txt source_lang target_lang type_of_postedits
```

##### Example

```
python3 find_context.py bel-rus_data/bel-rus-cleaned_bel-rus-other_entries.txt bel-rus_data/bel-rus-postedits.txt bel rus other

```

2. Run _create_ls_rules.py_ on the file created on the previous step.

```
create_ls_rules.py other_entries_context.txt source_lang target_lang path_to_lang_pair
```

##### Example

```
python3 create_ls_rules.py bel-rus_data/bel-rus_other-pe-context.json bel rus /home/.../apertium-bel-rus

```


This script will create potential lexical selection rules and write them in a file. Note, that tt works not perfectly and still requires some manual correction.

Example of automatically generated lexical selection rules: https://github.com/deltamachine/naive-automatic-postediting/blob/master/toolbox/bel-rus_lex-sel-rules.txt


#### Test lexical selection rules

The script generated few potential selection rules: https://github.com/deltamachine/naive-automatic-postediting/blob/master/toolbox/bel-rus_lex-sel-rules.txt.

This file contains two good lexical selection rules which were manually choosed and edited a bit (missed tags were added, lemma for "кубак" was edited): https://github.com/deltamachine/naive-automatic-postediting/blob/master/toolbox/bel-rus_corrected-rules.txt

If you want to test bel-rus rules:

1. Run _add_ls_rules.py_:

```
python3 add_ls_rules.py bel-rus_corrected-rules.txt bel-rus /home/.../apertium-bel-rus

```

2. Cd into apertium-bel-rus directory.

3. Run examples.

**Example 1**

Run:

```
echo "Я напісаў ліст." | apertium -d . bel-rus-lex

```

Output you should get:

```
^Я<prn><pers><p1><mf><sg><nom>/Я<prn><pers><p1><mf><sg><nom>$ ^напісаць<vblex><perf><past><m><sg>/написать¹<vblex><perf><tv><past><m><sg>$ ^ліст<n><m><nn><sg><nom>/лист<n><m><nn><sg><nom>/письмо<n><m><nn><sg><nom>$^..<sent>/..<sent>$
```

Then run:

```
echo "^Я<prn><pers><p1><mf><sg><nom>/Я<prn><pers><p1><mf><sg><nom>$ ^напісаць<vblex><perf><past><m><sg>/написать¹<vblex><perf><tv><past><m><sg>$ ^ліст<n><m><nn><sg><nom>/лист<n><m><nn><sg><nom>/письмо<n><m><nn><sg><nom>$^..<sent>/..<sent>$" | lrx-proc -t rules.fst
```

Output you should get:

```
1:SELECT<1>:ліст<n><m><nn><sg><nom>:<select>письмо<n><ANY_TAG>
^Я<prn><pers><p1><mf><sg><nom>/Я<prn><pers><p1><mf><sg><nom>$ ^напісаць<vblex><perf><past><m><sg>/написать¹<vblex><perf><tv><past><m><sg>$ ^ліст<n><m><nn><sg><nom>/письмо<n><m><nn><sg><nom>$^..<sent>/..<sent>$
```

**Example 2**

Run:

```
echo "Ён выпіў тры кубкі кавы" | apertium -d . bel-rus-lex
```

Output you should get:

```
^Ён<prn><pers><p3><m><sg><nom>/Он<prn><pers><p3><m><sg><nom>$ ^выпіць<vblex><perf><past><m><sg>/выпить<vblex><perf><tv><past><m><sg>$ ^тры<num><mfn><an><pl><nom>/три<num><mfn><an><pl><nom>$ ^кубак<n><m><nn><pl><nom>/кубок<n><m><nn><pl><nom>/чашка<n><m><nn><pl><nom>$ ^кава<n><f><nn><sg><gen>/кофе<n><m><nn><sg><gen>$^.<sent>/.<sent>$
```

Then run:

```
echo "^Ён<prn><pers><p3><m><sg><nom>/Он<prn><pers><p3><m><sg><nom>$ ^выпіць<vblex><perf><past><m><sg>/выпить<vblex><perf><tv><past><m><sg>$ ^тры<num><mfn><an><pl><nom>/три<num><mfn><an><pl><nom>$ ^кубак<n><m><nn><pl><nom>/кубок<n><m><nn><pl><nom>/чашка<n><m><nn><pl><nom>$ ^кава<n><f><nn><sg><gen>/кофе<n><m><nn><sg><gen>$^.<sent>/.<sent>$" | lrx-proc -t rules.fst
```

Output you should get:

```
1:SELECT<3>:кубак<n><m><nn><pl><nom>:<select>чашка<n><ANY_TAG>
^Ён<prn><pers><p3><m><sg><nom>/Он<prn><pers><p3><m><sg><nom>$ ^выпіць<vblex><perf><past><m><sg>/выпить<vblex><perf><tv><past><m><sg>$ ^тры<num><mfn><an><pl><nom>/три<num><mfn><an><pl><nom>$ ^кубак<n><m><nn><pl><nom>/чашка<n><m><nn><pl><nom>$ ^кава<n><f><nn><sg><gen>/кофе<n><m><nn><sg><gen>$^.<sent>/.<sent>$
```

### 6. Inserting operations into a language pair: separate module approach (under development)

How to apply postedits: run *new_apply_postedits.py* on your test data.


##### Usage

```
new_apply_postedits.py source_corpus.txt mt_corpus.txt target_corpus.txt postedits.txt source_lang target_lang path_to_lang_pair
```

##### Example

```
python3 new_apply_postedits.py bel-rus_data/train-test/test.bel bel-rus_data/train-test/test.mt.rus bel-rus_data/train-test/test.rus bel-rus_bidix_entries.txt bel rus /home/.../apertium-bel-rus
```

Output example for Belarusian - Russian: https://github.com/deltamachine/naive-automatic-postediting/blob/master/toolbox/examples/bel-rus_corrected.txt

How to check WER (run this on the file which was created on the previous step):

##### Usage

```
check_wer.py nap_output.txt path_to_eval_translator
```

##### Example

```
python3 check_wer.py bel-rus_corrected.txt /home/.../apertium-eval-translator/apertium-eval-translator.pl
```
