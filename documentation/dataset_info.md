# '-meta.tsv' columuns
## useful
(therefore contained in `META_COLUMNS`in `environment_constants`, some of them shortened or modified in `dataloader`)

- binarizable data:
  - House: {'Lower house', 'Upper house'} -> 'is_upper_house': True, False
  - Speaker_role: 'Chairperson' or 'Regular' -> 'is_chairperson': True, False
  - Speaker_type *: 'MP', 'notMP' -> 'is_mp': True, False
  - Speaker_gender *: 'F', 'M' -> 'is_female': True, False
- ID -> utterance_id (without 'ParlaMint-GB')
- Speaker_party *: all kinds of different parties
- Party_status *: 'Coalition', 'Opposition', nan -> 'is_coalition': True, False, 'n/a'
    - nan with the following names:
      - 'Armstrong, Hilary Jane',
      - 'Browne, Wallace',
      - 'Campbell, Gregory Lloyd',
      - 'Colville, John Mark Alexander',
      - 'Cotter, Brian Joseph Michael',
      - 'Dodds, Nigel',
      - 'Donaldson, Jeffrey Mark',
      - 'Flight, Howard Emerson',
      - 'Girvan, William Paul',
      - 'Harries, Richard Douglas',
      - 'Hay, William',
      - 'Little Pengelly, Emma',
      - 'McCrea, William',
      - 'Morrow, Maurice',
      - 'Paisley, Ian Richard Kyle',
      - 'Perham, Michael',
      - 'Robinson, Gavin James',
      - 'Scott-Joynt, Michael Charles',
      - 'Shannon, Richard James',
      - 'Simpson, Thomas David',
      - 'Wharton, John Martin',
      - 'Willis, George Philip',
      - 'Wilson, Samuel',
      - 'Wright, Nicholas Thomas'
- Speaker_name *: all the names

\* Speaker_type, Speaker_party, Party_status, Speaker_name, Speaker_gender
all sometimes contain '-', but only all of them together
-> refer to this as 'ghost speaker'
-> those instances are saved in hyphen_data.csv
-> they are discarded from main dataframe in `dataloader`

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
see also:
- https://universaldependencies.org/format.html
- https://stanfordnlp.github.io/CoreNLP/
## useful
(therefore contained in `SENTENCE_COLUMNS` in `environment_constants`)
- form: concrete form of lemma
- upos: universal part of speech tag
- head: index of the word that is the head of this word, caveat: starts at 1, but my DataFrames start at 0!

## not used for any analysis
(therefore discarded in `dataloader`)
- id: index of word in sentence (can also be derived from row, caveat: off by 1!)
- lemma: word which form is an instance of
- xpos: some kind of part of speech tag
- feats: e.g. `{'Tense': 'Past', 'VerbForm': 'Part', 'Voice': 'Pass'}`
- deprel: some sort of relative part of speech tag
- deps: I have no idea what this is
- misc: totally useless