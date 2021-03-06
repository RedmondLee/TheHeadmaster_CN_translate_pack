import os 
import re
import json
from pipeit import *
from note_translate_global_settings import *

for files in os.walk(working_dir):
    files = sorted(files[2])
    files = files | Filter(lambda x:os.path.splitext(x)[1] == '.rpy') | list
    break

patterns = [
    '\$[ ][a-zA-Z0-9_]+?\.note[s]*[a-zA-Z0-9_]*?[ ]*?=[ ]*?".+?"[\n]', #notes
    '\$[ ][a-zA-Z0-9_]+?\.weakness[ ]*?=[ ]*?".+?"[\n]', #weakness
    # 'q_name[ ]*?=[ ]*?".+?",', # qname
    'description[ ]*?=[ ]*?".+?",', # description
    'note[1-9][ ]*?=[ ]*?".+?",', # note1-9
    'notes[1-9]*?[ ]*?=[ ]*?".+?",', # note1-9
    'occupation[ ]*?=[ ]*?".+?",', # description
]
# 修正：qname似乎联动牵扯比较多，非手动的话不宜修改
patterns = '|'.join(patterns | Map(lambda x:f"({x})"))

# 一个问题是文本中有没有转义换行符，识别时以行为单位是否合适
def post_split_text(search_result):
    full_text = search_result.group()
    full_start, full_end = search_result.start(), search_result.end()
    fixed_start_t = len(full_text[:full_text.index('"')]) + 1
    fixed_end_t = -2
    fixed_start = full_start + fixed_start_t
    fixed_end = full_end + fixed_end_t
    fixed_text = full_text[fixed_start_t:fixed_end_t]
    return fixed_text, fixed_start, fixed_end, full_text, full_start, full_end

reduction_map = {}
for file in files:
    file_path = os.path.join(working_dir, file)
    new_file_name = os.path.splitext(file)[0] + '.txt'
    store_path = os.path.join(store_dir, new_file_name)
    reduction_map[file] = []
    # 清空已有文件
    if os.path.exists(store_path):
        with open(store_path,'w') as f:
            ...

    with open(file_path, 'r', encoding='utf-8') as f:
        text = f.read()
    regx_srch_fix = 0
    regx_srch_count = 0
    search_result = re.search(patterns, text[regx_srch_fix:])
    while search_result:
        fixed_text, fixed_start, fixed_end, _, _, full_end = post_split_text(search_result)
        with open(store_path,'a',encoding='utf-8') as f:
            f.write(f'>>>>>\n{fixed_text}\n###\n\n')
        reduction_map[file].append((regx_srch_fix + fixed_start, regx_srch_fix + fixed_end))
        regx_srch_fix += full_end
        search_result = re.search(patterns, text[regx_srch_fix:])

with open('reduction_map.json','w',encoding='utf-8') as f:
    json.dump(reduction_map, f)

# 清空空文件
for files in os.walk(store_dir):
    files = sorted(files[2]);break
for file in files:
    file_path = os.path.join(store_dir, file)
    if os.path.getsize(file_path) <= 0:
        os.remove(file_path)

# 复制到副本
import shutil
if os.path.exists(store_dir2):
    shutil.rmtree(store_dir2)
shutil.copytree(store_dir, store_dir2)
