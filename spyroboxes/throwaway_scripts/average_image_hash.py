import hashlib
from pathlib import Path
from PIL import Image
import imagehash
import json
import csv

'''
https://stackoverflow.com/a/52736785
'''

# this folder contains skies WITHOUT their tetrahedrons, rendered at 512 px
renders_folder = Path(r"I:\Spyro\2025\test_renders_03_md5")
output = Path('spyroboxes/temp/output.json')

everything = {}
NEW_HEADER = 'TOP_DOWN_IMG_AVG'

for i in renders_folder.glob('*.png'):
    img = Image.open(i)
    avg = imagehash.average_hash(img, 32)
    everything[i.name.split('_')[0]] = str(avg)

# for i in renders_folder.glob('*.png'):
#     digest = hashlib.md5(i.read_bytes()).hexdigest()
#     everything.append(digest)

fieldnames = Path('spyroboxes/temp/data.csv').read_text().split('\n')[0].split(',')
print('fieldnames:', fieldnames)
txt = Path('spyroboxes/temp/avg.txt')


with open('spyroboxes/temp/data.csv', 'r') as infile:
    with open('spyroboxes/temp/data_out.csv', 'w') as outfile:
        with open(txt, 'w') as txtfile:
            reader = csv.DictReader(infile)
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)

            writer.writeheader()
            for row in reader:
                if row['DATA_MD5'] in everything:
                    with_avg = {NEW_HEADER: everything[row['DATA_MD5']]}
                    new_row = row | with_avg
                    writer.writerow(new_row)
                    txtfile.write(everything[row['DATA_MD5']] + '\n')
                else:
                    writer.writerow(row)
                    txtfile.write('\n')


# output.write_text('\n'.join(everything))
json.dump(everything, output.open('w'))
