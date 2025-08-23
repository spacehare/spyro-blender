from pathlib import Path
import json

PATH_DATA = Path('data.json')
PATH_RESULTS_TSV = Path('list_results.tsv')
DATA_DICT: dict[str, str] = json.loads(PATH_DATA.read_text())
out_value_bools: list[bool] = []  # first occurences of OBJ strings
out_value_counts: list[int] = []  # if the OBJ string only occurs once
values_stack: list[str] = []  # add to this when i find a value
values: list[str] = list(DATA_DICT.values())

for key in DATA_DICT:
    out_value_bools.append(DATA_DICT[key] not in values_stack)
    out_value_counts.append(values.count(DATA_DICT[key]))
    values_stack.append(DATA_DICT[key])

output_str = 'FILENAME\tCOUNT\tFIRST_OCCURRENCE\n'

for i in zip(DATA_DICT.keys(), out_value_counts, out_value_bools):
    output_str += f"{i[0]}\t{i[1]}\t{i[2]}\n"

PATH_RESULTS_TSV.write_text(output_str)
