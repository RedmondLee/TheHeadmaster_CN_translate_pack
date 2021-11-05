# 使用方法参考readme.md
current_version = '0.11.1'
compare_version = None

import os
import shutil
import json
import hashlib
from note_translate_global_settings import *
from collections import deque
from pipeit import *

if os.path.exists(image_dir3):
    shutil.rmtree(image_dir3)

WATCH_LIST = ['.png','.jpg','jpeg','bmp','webp']

def getmd5(file):
    m = hashlib.md5()
    with open(file,'rb') as f:
        for line in f:
            m.update(line)
    md5code = m.hexdigest()
    return md5code

tree_struct = {}
tree_pointer = tree_struct
working_stack = deque([(image_dir, tree_pointer), ])

while working_stack:
    _main_dir, parent_pointer = working_stack.popleft()
    for _path in os.walk(_main_dir):
        _sub_dirs = _path[1]
        _files = _path[2]
        break
    for _ in _sub_dirs:
        parent_pointer[_] = {}
    working_stack.extend(_sub_dirs | Map(lambda x:(os.path.join(_main_dir , x), parent_pointer[x])) | list)
    _files = _files | Filter(lambda x:os.path.splitext(x)[1].lower() in WATCH_LIST) | Filter(lambda x:len(os.path.split(os.path.splitext(x)[0])[1]) != 32) | Map(lambda x:os.path.join(_main_dir , x)) | list
    if len(_files) > 0:
        for _file in _files:
            parent_pointer[os.path.split(_file)[1]] = getmd5(_file) 

print("扫描中，根据硬盘读取速度不同，此过程将持续几秒至几分钟不等...")

if not os.path.exists('image_history.json'):
    with open('image_history.json','w', encoding='utf-8') as f:
        f.write('{}')

with open('image_history.json', 'r', encoding='utf-8') as f:
    history = json.load(f)

# 储存当前版本图片信息
history[current_version] = tree_struct
with open('image_history.json', 'w', encoding='utf-8') as f:
    json.dump(history, f)

if compare_version:
    diff_append = {}
    diff_remove = {}
    old = history[compare_version]
    new = history[current_version]
    pointer_stack = deque([(new,old,diff_append),])
    while pointer_stack:
        new_pointer, old_pointer, apd_pointer = pointer_stack.popleft()
        for name, cont in new_pointer.items():
            if isinstance(cont, str):
                # 对于图片文件
                if name in old_pointer:
                    if new_pointer[name] == old_pointer[name]:
                        # 文件未改变
                        ...
                    else:
                        # 修改
                        apd_pointer[name] = new_pointer[name]
                else:
                    # 新增
                    apd_pointer[name] = new_pointer[name]
            else:
                # 对于文件夹
                if name in old_pointer:
                    # 既有
                    diff_append[name] = {}
                    pointer_stack.append((new_pointer[name], old_pointer[name], apd_pointer[name]))
                    ...
                else:
                    # 新增
                    apd_pointer[name] = new_pointer[name]

    # 复制新增文件到新文件夹
    if diff_append:
        flag = [True, ]
        def copy_dir(_from, _to, files):
            for name in list(files.keys()):
                cont = files[name]
                if isinstance(cont, dict):
                    if len(cont) == 0:
                        del files[name]
                    else:
                        os.mkdir(os.path.join(_to, name))
                        copy_dir(os.path.join(_from, name), os.path.join(_to, name), files[name])
                else:
                    flag[0] = False 
                    shutil.copyfile(os.path.join(_from, name), os.path.join(_to, name))
        os.mkdir(image_dir3)
        copy_dir(image_dir, image_dir3, diff_append)
        if flag[0]:
            print('完成，文件无差异。')
        else:
            print('完成，差异文件：')
            print(diff_append)
else:
    print('完成')
        