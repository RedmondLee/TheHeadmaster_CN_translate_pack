import json
from collections import deque
from pipeit import *
from note_translate_global_settings import *

with open('reduction_map.json','r',encoding='utf-8') as f:
    reduction_map = json.load(f)

for file, block_indexs in reduction_map.items():
    if block_indexs:
        block_indexs = deque(block_indexs)
        source_file_path = os.path.join(working_dir, file)
        text_file_path = os.path.join(store_dir2, os.path.splitext(file)[0] + '.txt')
        with open(text_file_path, 'r', encoding='utf-8') as f:
            text = f.read()
        block_contents = text.split('>>>>>') | Filter(lambda x:x) | Map(lambda x:x.split('###')) | deque
        with open(source_file_path, 'r', encoding='utf-8') as f:
            source = f.read()
        while block_indexs:
            index_start, index_end = block_indexs.popleft()
            content = block_contents.popleft()[1]
            if content[0] == '\n':
                content = content[1:]
            content = content.replace('\n', ' ')
            index_diff = len(content) - (index_end - index_start)
            for _ in block_indexs:
                _[0] = _[0] + index_diff
                _[1] = _[1] + index_diff
            source = source[:index_start] + content + source[index_end:]
        with open(source_file_path, 'w', encoding='utf-8') as f:
            f.write(source)
    