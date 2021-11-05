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

for files in os.walk(image_dir):
    files = files[2];break

c = set()
for file in files:
    with open(os.path.join(image_dir, file), 'rb') as f:
        test = f.read()
        c.add(test[:4])
print(c)

