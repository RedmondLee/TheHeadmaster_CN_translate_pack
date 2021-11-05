# 使用前需要去百度翻译开放平台注册appid和秘钥
# https://fanyi-api.baidu.com/
import random
import hashlib
import os
import asyncio
import json
import time
import aiohttp
from collections import deque
from pipeit import *
from note_translate_global_settings import *

appid = '2018****************' # 填写你的appid
secretkey = 'ULJ2**************' # 填写你的密钥
speed_limit = 10 # 每秒钟翻译次数限制
if appid == '' or secretkey == '':
    raise ValueError('')

FROM_LANG = 'en'
TO_LANG = 'zh'

async def translate_single_line(session, message):
    salt = random.randint(32768, 65535)
    sign = appid + message + str(salt) + secretkey
    sign = hashlib.md5(sign.encode()).hexdigest()
    params = {
        'q': message,
        'from': FROM_LANG,
        'to': TO_LANG,
        'appid': appid,
        'salt': salt,
        'sign': sign
    }
    try:
        fail_count = 0
        while fail_count < 2:
            async with session.get('http://api.fanyi.baidu.com/api/trans/vip/translate', params = params) as resp:
                if resp.status == 200:
                    trans_result = json.loads(await resp.text())["trans_result"][0]["dst"]
                    if trans_result != "":
                        return trans_result
            fail_count += 1
        raise
    except:
        raise RuntimeError('百度翻译api通信错误')

async def main():
    for files in os.walk(store_dir2):
        files = sorted(files[2]);break

    for file in files:
        store_path2 = os.path.join(store_dir2, file)
        with open(store_path2, 'r', encoding='utf-8') as f:
            text = f.read()
        blocks = text.split('>>>>>') | Filter(lambda x:x) | Map(lambda x:x.split('###')) | deque
        blocks_backup = blocks | Map(lambda x:x[0]) | list 
        result_backup = []
        async with aiohttp.ClientSession() as session:
            while blocks:
                pending = []
                start_time = time.time()
                while blocks and len(pending) < speed_limit:
                    pending.append(translate_single_line(session, blocks.popleft()[0].replace('\n',' ')))
                if pending:
                    results = await asyncio.gather(*pending)
                    result_backup.extend(results)
                    print('.',end='')
                took_time = time.time() - start_time
                await asyncio.sleep(max(1.5 - took_time, 0))
        with open(store_path2, 'w', encoding='utf-8') as f:
            for block in zip(blocks_backup,result_backup):
                f.write(f'>>>>>{block[0]}###\n{block[1]}\n')
        print(f'translate finished {file}...')

asyncio.run(main())