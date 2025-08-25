import hashlib
from pathlib import Path
from PIL import Image
import imagehash
import json

# this folder contains skies WITHOUT their tetrahedrons, rendered at 512 px
renders_folder = Path(r"I:\Spyro\2025\test_renders_03_md5")
output = Path('spyroboxes/temp/output.json')

everything = {}

for i in renders_folder.glob('*.png'):
    img = Image.open(i)
    avg = imagehash.average_hash(img)
    everything[str(i)] = {'avg': str(avg)}

# for i in renders_folder.glob('*.png'):
#     digest = hashlib.md5(i.read_bytes()).hexdigest()
#     everything.append(digest)


# output.write_text('\n'.join(everything))
json.dump(everything, output.open('w'))
