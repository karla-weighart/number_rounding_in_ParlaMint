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

    table_data = []

    for line_index in range(len(lines)):
        items = lines[line_index].split()

        # get rid of unnecessary columns
        for i in (2, 3, 3, 4, 4, 4):
            items.pop(i)

        # add macro for UPOS column
        items[2] = f"\\upos{{{items[2]}}}"

        # add color
        if colors and line_index + 1 in colors.keys():
            items[-1] = colors[line_index + 1] + items[-1]

        # merge the items into one line and adjust whitespace
        line = '&\t'.join(item.ljust(16) for item in items)
        table_data.append(line)

    # merge the lines into a single string
    table = '\\\\\n\t'.join(table_data) + '\\\\'

    latex = f"\\begin{{tabularx}}{{\\textwidth}}{{cllc}}\n\t\\toprule\n\t\\texttt{{INDEX}}\t&\t\\texttt{{" \
            f"FORM}}\t&\t\\texttt{{UPOS}}\t&\t\\texttt{{HEAD}}\\\\\n\t\\mid" \
            f"rule\n\t{table}\n\t\\bottomrule\n\\end{{tabularx}}"

    return latex


def subtable(table_content: str,
             caption: str,
             colors: dict[int: str] = None) \
        -> str:
    # adjust indentation
    tabularx = tsv2upos_tabularx(table_content, colors=colors).replace('\n', '\n\t')

    return f"\\begin{{subtable}}[h]{{0.48\\textwidth}}\n\t\\centering\n\t" \
           f"{tabularx}\n\t\\" \
           f"caption{caption}\n\t\\label{{}}\n\t\\end{{subtable}}"


def comparison_table(text_incorrect: str,
                     text_correct: str,
                     corrected_indices: list[int],
                     caption: str,
                     label: str = None) \
        -> str:
    tabular_incorrect = tsv2upos_tabularx(text_incorrect,
                                          colors={index: '\\clrincorrect' for index in corrected_indices})
    tabular_incorrect_caption = 'Original Version from the Dataset',

    tabular_correct = tsv2upos_tabularx(text_correct, colors={index: '\\clrcorrect' for index in corrected_indices})
    tabular_correct_caption = 'Manually Corrected Version'

    latex = f"\\begin{{table}}[]\n\t{subtable(tabular_incorrect)}\n%\n\t\\hfill\n%\t"

    return latex


if __name__ == '__main__':
    print(subtable("""1	What	what	DET	WDT	PronType=Int	2	det	_	NER=O
2	assessment	assessment	NOUN	NN	Number=Sing	5	obj	_	NER=O
3	he	he	PRON	PRP	Case=Nom|Gender=Masc|Number=Sing|Person=3|PronType=Prs	5	nsubj	_	NER=O
4	has	have	VERB	VBZ	Mood=Ind|Number=Sing|Person=3|Tense=Pres|VerbForm=Fin	5	aux	_	NER=O
5	made	make	VERB	VBN	Tense=Past|VerbForm=Part	0	root	_	NER=O
6	of	of	ADP	IN	_	14	mark	_	NER=O
7	whether	whether	ADP	IN	_	14	mark	_	NER=O
8	Zimbabwe	Zimbabwe	PROPN	NNP	Number=Sing	11	nmod:poss	_	NER=O|SpaceAfter=No
9	’s	’s	PART	POS	_	8	case	_	NER=O
10	next	next	ADJ	JJ	Degree=Pos	11	amod	_	NER=O
11	election	election	NOUN	NN	Number=Sing	14	nsubj:pass	_	NER=O
12	will	will	VERB	MD	VerbForm=Fin	14	aux	_	NER=O
13	be	be	VERB	VB	VerbForm=Inf	14	aux:pass	_	NER=O
14	conducted	conduct	VERB	VBN	Tense=Past|VerbForm=Part|Voice=Pass	5	advcl	_	NER=O
15	freely	freely	ADV	RB	_	14	advmod	_	NER=O
16	and	and	CCONJ	CC	_	17	cc	_	NER=O
17	fairly	fairly	ADV	RB	_	14	conj	_	NER=O|SpaceAfter=No
18	.	.	PUNCT	.	_	5	punct	_	NER=O
""", 'Original Version from the Dataset'))
