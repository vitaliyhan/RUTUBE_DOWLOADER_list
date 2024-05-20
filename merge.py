import os
import shutil


def merge_ts(author, title, count):
    if not os.path.isdir(author):
        os.mkdir(author)
    if not os.path.isdir(f'{author}\\seg_full'):
        os.mkdir(f'{author}\\seg_full')
    with open(f'{author}\\seg_full\\{title}.ts', 'wb') as merged:
        for ts in range(1, count + 1):
            with open(f'seg_full\\segment-{ts}-v1-a1.ts', 'rb') as mergefile:
                shutil.copyfileobj(mergefile, merged)


merge_ts('test', '10 ser', 2205)
