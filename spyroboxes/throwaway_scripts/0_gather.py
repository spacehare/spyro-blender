from pathlib import Path
import json

OBJ_PATH = Path("obj/")  # this should be where all the SpyroWorldViewer OBJ files are
DATA_PATH = Path("data.json")
texts = {}

for filename in OBJ_PATH.glob('*'):
    texts[str(filename.name)] = Path(filename).read_text()

DATA_PATH.write_text(json.dumps(texts))
