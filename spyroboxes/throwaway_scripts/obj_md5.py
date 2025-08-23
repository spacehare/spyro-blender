from pathlib import Path
import json
import hashlib

PATH_OBJ_DATA_JSON = Path("obj_data.json")
PATH_OUT_JSON = Path("hashed.json")
PATH_OUT_TXT = Path("hashed.txt")

# key = filename
# value = obj text data
data: dict[str, str] = json.load(PATH_OBJ_DATA_JSON.open('r'))


# gonna assign each unique data a UID
out_list: list = []

for key in data:
    hashed_value = hashlib.md5(data[key].encode()).hexdigest()
    out_list.append(hashed_value)


PATH_OUT_TXT.write_text('\n'.join([str(i) for i in out_list]))
json.dump(out_list, PATH_OUT_JSON.open('w'))
