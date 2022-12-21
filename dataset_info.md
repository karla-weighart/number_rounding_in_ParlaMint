# '-meta.tsv' columuns
## useful
(therefore contained in `META_COLUMNS`in `environment_constants.py`, some of them shortened or modified in `dataloader`)

- ID -> utterance_id (without 'ParlaMint-GB')
- House: {'Lower house', 'Upper house'} -> upper_house: True, False
- Speaker_role: 'Chairperson' or 'Regular' -> 'chairperson': True, False
- Speaker_type *: 'MP', 'notMP'
- Speaker_party *: all kinds of different parties
- Party_status *: 'Coalition', 'Opposition', nan
- Speaker_name *: all the names
- Speaker_gender *: 'F', 'M'

`* Speaker_type, Speaker_party, Party_status, Speaker_name, Speaker_gender
all sometimes contain '-', but only all of them together
-> those instances are saved in hyphen_data.csv
-> #TODO: will be discarded from main dataframe

## not used for any analysis
(therefore discarded in `dataloader`)
- Title
- From
- To
- Term
- Session
- Meeting
- Sitting
- Agenda
- Subcorpus
- Speaker_party_name
- Speaker_birth

# .conllu (implied) columns
## useful
(therfore contained in `SENTENCE_COLUMNS`in `environment_constants.py`)
- form: concrete form of lemma
- upos: universal part of speech tag
- head: index of the word that is the head of this word

## not used for any analysis
(therefore discarded in `dataloader`)
- id: index of word in sentence (can also be derived from row, caveat: off by 1!)
- lemma: word which form is an instance of
- xpos: some kind of part of speech tag
- feats: e.g. `{'Tense': 'Past', 'VerbForm': 'Part', 'Voice': 'Pass'}`
- deprel: some sort of relative part of speech tag
- deps: I have no idea what this is
- misc: totally useless