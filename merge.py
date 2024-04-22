import os
import shutil


def merge_ts(author, title, count):
    if not os.path.isdir(author):
        os.mkdir(author)
    with open(f'seg1\\{title}.ts', 'wb') as merged:
        for ts in range(1, count + 1):
            with open(f'seg1\\segment-{ts}-v1-a1.ts', 'rb') as mergefile:
                shutil.copyfileobj(mergefile, merged)


merge_ts('test', 'first10', 10)
