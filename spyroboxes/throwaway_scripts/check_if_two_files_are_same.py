from pathlib import Path
import json

A = "s1-1_011_2-n.S.obj"
B = "s1-1_019-n.S.obj"

if __name__ == '__main__':
    PATH_DATA = Path('data.json')
    DATA = json.loads(PATH_DATA.read_text())

    is_same = Path(f'obj/{A}').read_text() == Path(f'obj/{B}').read_text()
    is_same2 = DATA[A] == DATA[B]

    print(is_same)
    print(is_same2)
