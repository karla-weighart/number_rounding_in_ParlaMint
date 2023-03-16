def tsv2upos_tabularx(table_content: str,
                      colors: dict[int: str] = None) \
        -> str:
    """

    Parameters
    ----------
    table_content: tsv of a single sentence from .conllu file
    colors: indices of lines to color, colorvalues as strings (e.g. '\\clrincorrect')

    Returns
    -------
    latex tabularx as str
    """
    lines = table_content.rstrip().split('\n')

    for line_index in range(len(lines)):
        items = lines[line_index].split()

        # get rid of unnecessary columns. work from right to left to avoid index shifts after every pop
        for i in (9, 8, 7, 5, 4, 2):
            items.pop(i)

        # add macro for UPOS column
        items[2] = f"\\upos{{{items[2]}}}"

        # add color
        if colors and line_index + 1 in colors.keys():
            items[-1] = colors[line_index + 1] + items[-1]

        # merge the items into one line and adjust whitespace
        lines[line_index] = '&\t'.join(item.ljust(16) for item in items)

    # merge the lines into a single string
    table_data = '\\\\\n\t'.join(lines) + '\\\\'

    latex = f"\\begin{{tabularx}}{{\\textwidth}}{{cllc}}\n\t\\toprule\n\t\\texttt{{INDEX}}\t&\t\\texttt{{" \
            f"FORM}}\t&\t\\texttt{{UPOS}}\t&\t\\texttt{{HEAD}}\t\\\\\n\t\\mid" \
            f"rule\n\t{table_data}\n\t\\bottomrule\n\\end{{tabularx}}"

    return latex


def tsv2subtable(table_content: str,
                 caption: str,
                 label: str,
                 colors: dict[int: str] = None) \
        -> str:
    """

    Parameters
    ----------
    table_content: tsv of a single sentence from .conllu file
    caption: caption for the latex subtable
    label: label for the latex subtable
    colors: indices of lines to color, colorvalues as strings (e.g. '\\clrincorrect')

    Returns
    -------
    latex subtable as str
    """
    # generate tabularx and adjust indentation
    tabularx = tsv2upos_tabularx(table_content, colors=colors).replace('\n', '\n\t')

    return f"\\begin{{subtable}}[h]{{0.48\\textwidth}}\n\t\\centering\n\t" \
           f"{tabularx}\n\t\\" \
           f"caption{{{caption}}}\n\t\\label{{tab:{label}}}\n\t\\end{{subtable}}"


def comparison_table(text_incorrect: str,
                     text_correct: str,
                     corrected_indices: list[int],
                     caption: str,
                     label: str) \
        -> str:
    """

    Parameters
    ----------
    text_incorrect: tsv of a single sentence from .conllu file - incorrect version
    text_correct: tsv of a single sentence from .conllu file - correct version
    corrected_indices: indices of corrected dependencies
    caption: caption for the whole table (captions for subtables will be generated automatically!)
    label: label for the whole table

    Returns
    -------
    latex table with two subtables comparing the version before with the version after the corrections

    """
    # generate subtables and adjust indentation
    subtable_incorrect = tsv2subtable(text_incorrect,
                                      caption='Original Version',
                                      label=f"{label}-incorrect",
                                      colors={index: '\\clrincorrect' for index in corrected_indices}
                                      ).replace('\n', '\n\t')

    subtable_correct = tsv2subtable(text_correct,
                                    caption='Corrected Version',
                                    label=f"{label}-correct",
                                    colors={index: '\\clrcorrect' for index in corrected_indices}
                                    ).replace('\n', '\n\t')

    # put everything together
    latex = f"\\begin{{table}}[H]\n\t" \
            f"{subtable_incorrect}" \
            f"\n%\n\t\\hfill\n%\t\n" \
            f"{subtable_correct}" \
            f"\n\t\\caption{{{caption}}}\n\t\\label{{tab:{label}}}\n\\end{{table}}"

    return latex


if __name__ == '__main__':

    seg = 'ParlaMint-GB_2016-04-27-commons.seg22.1'

    corrected_indices_ = [1]

    text_incorrect_ = """1	Two	two	NUM	CD	NumType=Card	3	compound	_	NER=O
2	hundred	hundred	NUM	CD	NumType=Card	3	compound	_	NER=O
3	thousand	thousand	NUM	CD	NumType=Card	5	nummod	_	NER=O
4	young	young	ADJ	JJ	Degree=Pos	5	amod	_	NER=O
5	people	people	NOUN	NNS	Number=Plur	11	nsubj	_	NER=O
6	have	have	VERB	VBP	Mood=Ind|Tense=Pres|VerbForm=Fin	11	aux	_	NER=O
7	been	be	VERB	VBN	Tense=Past|VerbForm=Part	11	cop	_	NER=O
8	through	through	ADP	IN	_	11	case	_	NER=O
9	the	the	DET	DT	Definite=Def|PronType=Art	11	det	_	NER=O
10	NCS	ncs	NOUN	NN	Number=Sing	11	compound	_	NER=B-ORG
11	programme	programme	NOUN	NN	Number=Sing	0	root	_	NER=O
12	so	so	ADV	RB	_	13	advmod	_	NER=O
13	far	far	ADV	RB	Degree=Pos	11	advmod	_	NER=O
14	and	and	CCONJ	CC	_	17	cc	_	NER=O
15	we	we	PRON	PRP	Case=Nom|Number=Plur|Person=1|PronType=Prs	17	nsubj	_	NER=O
16	are	be	VERB	VBP	Mood=Ind|Tense=Pres|VerbForm=Fin	17	aux	_	NER=O
17	aiming	aim	VERB	VBG	Tense=Pres|VerbForm=Part	11	conj	_	NER=O
18	to	to	PART	TO	_	19	mark	_	NER=O
19	increase	increase	VERB	VB	VerbForm=Inf	17	xcomp	_	NER=O
20	that	that	DET	DT	Number=Sing|PronType=Dem	21	det	_	NER=O
21	number	number	NOUN	NN	Number=Sing	19	obj	_	NER=O
22	significantly	significantly	ADV	RB	_	19	advmod	_	NER=O
23	by	by	ADP	IN	_	24	case	_	NER=O
24	2020	2020	NUM	CD	NumType=Card	19	obl	_	NER=O|SpaceAfter=No
25	.	.	PUNCT	.	_	11	punct	_	NER=O
"""

    text_correct_ = """1	Two	two	NUM	CD	NumType=Card	2	compound	_	NER=O
2	hundred	hundred	NUM	CD	NumType=Card	3	compound	_	NER=O
3	thousand	thousand	NUM	CD	NumType=Card	5	nummod	_	NER=O
4	young	young	ADJ	JJ	Degree=Pos	5	amod	_	NER=O
5	people	people	NOUN	NNS	Number=Plur	11	nsubj	_	NER=O
6	have	have	VERB	VBP	Mood=Ind|Tense=Pres|VerbForm=Fin	11	aux	_	NER=O
7	been	be	VERB	VBN	Tense=Past|VerbForm=Part	11	cop	_	NER=O
8	through	through	ADP	IN	_	11	case	_	NER=O
9	the	the	DET	DT	Definite=Def|PronType=Art	11	det	_	NER=O
10	NCS	ncs	NOUN	NN	Number=Sing	11	compound	_	NER=B-ORG
11	programme	programme	NOUN	NN	Number=Sing	0	root	_	NER=O
12	so	so	ADV	RB	_	13	advmod	_	NER=O
13	far	far	ADV	RB	Degree=Pos	11	advmod	_	NER=O
14	and	and	CCONJ	CC	_	17	cc	_	NER=O
15	we	we	PRON	PRP	Case=Nom|Number=Plur|Person=1|PronType=Prs	17	nsubj	_	NER=O
16	are	be	VERB	VBP	Mood=Ind|Tense=Pres|VerbForm=Fin	17	aux	_	NER=O
17	aiming	aim	VERB	VBG	Tense=Pres|VerbForm=Part	11	conj	_	NER=O
18	to	to	PART	TO	_	19	mark	_	NER=O
19	increase	increase	VERB	VB	VerbForm=Inf	17	xcomp	_	NER=O
20	that	that	DET	DT	Number=Sing|PronType=Dem	21	det	_	NER=O
21	number	number	NOUN	NN	Number=Sing	19	obj	_	NER=O
22	significantly	significantly	ADV	RB	_	19	advmod	_	NER=O
23	by	by	ADP	IN	_	24	case	_	NER=O
24	2020	2020	NUM	CD	NumType=Card	19	obl	_	NER=O|SpaceAfter=No
25	.	.	PUNCT	.	_	11	punct	_	NER=O
"""



###################

    caption_ = f'Original and Corrected Version of Sentence \\texttt{{{seg}}}'.replace('_', '\_')

    label_ = f"appendixWrongDependencies{seg[len('ParlaMint-GB_'):]}"

    print(comparison_table(text_incorrect=text_incorrect_,
                           text_correct=text_correct_,
                           corrected_indices=corrected_indices_,
                           caption=caption_,
                           label=label_))
