# Toolbox for automatic postediting (GSoC 2018)

More information about this project can be found here: http://wiki.apertium.org/wiki/Automatic_postediting_at_GSoC_2018

### 0. Prerequisites

While working with this toolbox, you might need to install:
a) Apertium core, bel-rus and rus-ukr language pairs.
b) such Python packages as: nltk, streamparser, ufal.udpipe, pymystem3, numpy, pandas, sklearn.
c) Perl and apertium-eval-translator (http://wiki.apertium.org/wiki/Apertium-eval-translator)

### 1. Algorithm for operations extraction

The rationale for this algorithm described in *rationale.md*

##### Usage

```
new_learn_postedits_algorithm.py train.source train.mt train.target source_lang target_lang path_to_language_pair context_window
```

*context_window* parameter - number of words around the word which should be postedited.


##### Example

```
python3 new_learn_postedits_algorithm.py train.be train.mt.ru train.ru bel rus /home/anna/apertium-bel-rus 2
```

### 2. Classifying postedits

A script for classifying extracted postedits indentifies three types of operations: potential monodix/bidix entries 
(when a pair doesn't have a translation for a given word), grammar mistakes (when Apertium chooses incorrect form of 
translated word) and other mistakes (it can be, for example, a potential lexical selection rule).

##### Usage

```
extract_types.py postedits.txt lang_pair
```

##### Example

```
python3 extract_types.py bel-rus_postedits.txt bel-rus
```

### 3. Cleaning

The extracting postedits algorithm is not perfect and extracts a lot of garbage along with potentially good triplets. This script
filters most of the garbage out.

##### Usage

```
clean_postedits.py postedits.txt source_lang target_lang path_to_lang_pair
```

##### Example

```
python3 clean_postedits.py bel-rus_bidix_entries.txt bel rus /home/anna/apertium/apertium-bel-rus
```

### 4. Inserting operations into a language pair: dictionary approach

How to create monodix/bidix entries:

a) Run *create_entries_table.py*

```
create_entries_table.py bidix_postedits.txt source_lang target_lang ud_bin_path ud_model_path
```

##### Example

```
python3 create_entries_table.py bel-rus_bidix_entries.txt bel rus /home/udpipe/src/udpipe /home/udpipe/belarusian-ud-2.0-170801.udpipe

```

b) After that, the created table should be manually checked: UDPipe/Mystem not always determine a correct/lemma for a word.

c) Run *check_entries.py* on the table.


```
check_entries.py source_lang target_lang source_dict_path target_dict_path
```

##### Example

```
python3 *check_entries.py* bel rus /home/anna/apertium-bel/apertium-bel.bel.dix /home/anna/apertium-rus/apertium-rus.rus.dix

```

d) Manually edit the table: add a stem and a paradigm for every word, which was not found in dictionaries.

e) Run *add_new_entries.py* on the edited table.


```
add_new_entries.py table.txt source_path target_path pair_path source_lang target_lang
```

##### Example

```
python3 add_new_entries.py bel-rus_table.txt /home/anna/apertium-bel /home/anna/apertium-rus /home/anna/apertium-bel-rus bel rus

```

### 5. Inserting operations into a language pair: separate module approach (under development)

How to apply postedits to a test file:

##### Usage

```
new_apply_postedits.py source_corpus.txt mt_corpus.txt target_corpus.txt postedits.txt source_lang target_lang path_to_lang_pair
```

##### Example

```
python3 new_apply_postedits.py test.bel test.mt.rus test.rus bel-rus_bidix_entries.txt bel rus /home/anna/apertium/apertium-bel-rus
```

How to check WER (run this on the file which was created on the previous step):

##### Usage

```
check_wer.py nap_output.txt path_to_eval_translator
```

##### Example

```
python3 check_wer.py bel-rus_corrected.txt /home/anna/apertium-eval-translator/apertium-eval-translator.pl
```
