
# New algorithm: RATIONALE 

This rationale describes new algorithm for learning postediting operations. It is based on the custom alignment algorithm 
which is also described below.

Disclaimer: seems that this algorithm will work okay on close-related languages, but I'm not sure about others.

### Definitions:
 * S : source sentence
 * MT: machine translation system
 * MT(S): machine translation of S
 * PE(MT(S)): post-editing of the machine translation of S, assumed available
 
### Process:
1. Tag S, MT(S) and PE(MT(S)) using Apertium tagger (for example, bel-rus-morph).
2. For S, MT(S) and PE(MT(S)) collect a dictionary, which contains positions of words as keys and tokens + tags as items. 
For example, for a sentence "Цмоки" the dictionary will look like {0: [цмоки, (n, m, aa, sg, nom)]}.
3. Then align S and MT(S) and S and PE(MT(S)) using these dictionaries. Algorithm goes through every word in MT(S) and finds pairs of words (S - MT(S)), where:
    a) word in S is the same as word in MT(S) (for example, Russian and Belarusian both have word "не"). 
    b) words have the highest percent of similar tags
    c) words both have not tags at all
    d) both words have the lowest percent of edits which will make one word from another (Levenshtein distance is used here).
In all cases words are aligned only in those cases if difference between their positions <= 2.
4. After aligning, find aligned triplets where word in MT(S) != PE(MT(S)). This is our potential operation.

### Usage

```
new_learn_postedits_algorithm.py train.source train.mt train.target source_lang target_lang context_window
```

context_window parameter - number of words around the word which should be postedited.


### Example

```
python3 new_learn_postedits_algorithm.py train.be train.mt.ru train.ru bel rus 2
```
