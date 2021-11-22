import os
import re
import asyncio
import json
import time
import aiohttp
import random
import hashlib
import hmac
import base64
import binascii
import urllib
from collections import deque
from pipeit import *    # `pip install pipeit` to use

translate_dir = '.\\chinese'
translate_dir = os.path.abspath(translate_dir)

baidu_appid = '2018*************'        # 填写你的baidu_appid
baidu_secretkey = 'ULJ2*************' # 填写你的密钥
tencent_secretid = 'AK*************'
tencent_secretKey = 'Te*************'
speed_limit = 5                          # 每秒钟翻译次数限制
FROM_LANG = 'en'
TO_LANG = 'zh'

async def translator_baidu(session, message):
    salt = random.randint(32768, 65535)
    sign = baidu_appid + message + str(salt) + baidu_secretkey
    sign = hashlib.md5(sign.encode()).hexdigest()
    params = {
        'q': message,
        'from': FROM_LANG,
        'to': TO_LANG,
        'appid': baidu_appid,
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
    except Exception as e:
        raise RuntimeError('百度翻译api通信错误')

async def translator_tencent(session, message):
    timeData = str(int(time.time())) 
    nonceData = random.randint(32768, 65535)
    actionData = "TextTranslate" 
    uriData = "tmt.tencentcloudapi.com"
    signMethod="HmacSHA256"
    requestMethod = "GET"
    regionData = "ap-hongkong"
    versionData = '2018-03-21'

    # message = message.encode('utf-8')

    signDictData = {
        'Action' : actionData,
        'Nonce' : nonceData,
        'ProjectId':0,
        'Region' : regionData,
        'SecretId' : tencent_secretid,
        'SignatureMethod':signMethod,
        'Source': FROM_LANG,
        'SourceText': message,
        'Target': TO_LANG,
        'Timestamp' : int(timeData),
        'Version':versionData ,
    }

    sign_string = f"{requestMethod}{uriData}/?" + '&'.join(f"{key}={value}" for key, value in signDictData.items())
    digestmod = hashlib.sha256
    hashed = hmac.new(tencent_secretKey.encode('utf-8'), sign_string.encode('utf-8'), digestmod)
    hashed_b64 = binascii.b2a_base64(hashed.digest())[:-1]
    signDictData["Signature"] = hashed_b64.decode()

    try:
        fail_count = 0
        while fail_count < 2:
            async with session.get(f'https://{uriData}', params = signDictData) as resp:
                if resp.status == 200:
                    trans_result = json.loads(await resp.text())["Response"]["TargetText"]
                    if trans_result != "":
                        return trans_result
            fail_count += 1
        raise
    except Exception as e:
        raise RuntimeError('腾讯翻译api通信错误')

def treat_paragraph(text):
    src = text.split('\n')
    src_ = src[3]
    eng = src_[src_.index('"') + 1:(len(src_) - src_[::-1].index('"') - 1)]
    return eng, src

class Quest:

    def __init__(self, matched: re.Match, bias: int):
        self.bias = bias
        self.start = matched.start()
        self.end = matched.end()
        self.length = self.end - self.start
        self.text = matched.group()
        self.splited = self.text.split('\n')
        _src = self.splited[3]
        self.eng = _src[_src.index('"') + 1:(len(_src) - _src[::-1].index('"') - 1)]
        self.voicer = _src[_src.index('#') + 2:_src.index('"') - 1]
        self.translates = []

    def __repr__(self):
        return f"Quest({self.bias}, {self.start}, {self.end}, {self.eng})"

    async def update(self, session, translator):
        text = await translator(session, self.eng)
        self.translates.append(text)

    def replace(self, full_text, total_fix):
        if self.translates:
            self.splited.pop()
            spaces = 0
            for _ in self.splited.pop():
                if _ != ' ':
                    break
                spaces += 1
            for _ in self.translates:
                self.splited.append(f'{" " * spaces}{self.voicer}{" " if self.voicer != "" else ""}"{_}"')
            self.splited.append('')
            new_text = '\n'.join(self.splited)
            modified_length = len(new_text) - self.length
            return full_text[:self.bias + self.start + total_fix] + new_text + full_text[self.bias + self.end + total_fix:], modified_length
        else:
            return full_text, 0
        

async def main():
    for files in os.walk(translate_dir):
        files = files[2] | Filter(lambda x: os.path.splitext(x)[1] == '.rpy') | list
        files.sort(); break

    PAT1 = re.compile('# game/[a-zA-Z0-9_.]+?:[\d]+?[\n]translate[\s][\w]+?[\s][a-zA-Z0-9_]+:[\n][\n][\s]+#.+?"\n[\s]+[a-zA-Z0-9_]*?[\s]*""[\n]')

    for file in files:
        file_path = os.path.join(translate_dir, file)
        print(f"Handling {file_path}")
        with open(file_path, 'r', encoding='utf-8') as f:
            orn_text = f.read()

        orn_text_copy = orn_text
        quest_list = deque()
        result = PAT1.search(orn_text)
        bias = 0
        bias_sum = 0
        while result:
            quest = Quest(result, bias_sum)
            quest_list.append(quest)
            bias = quest.end
            bias_sum += bias
            orn_text = orn_text[bias:]
            result = PAT1.search(orn_text)
        orn_text = orn_text_copy
        print(f"Quests: {len(quest_list)}")

        quest_results = []
        async with aiohttp.ClientSession() as session:
            while len(quest_list) != 0:
                pending = []
                for _ in range(min(len(quest_list), speed_limit)):
                    pending.append(quest_list.popleft())

                tasks = [quest.update(session, translator) for quest in pending for translator in (translator_baidu, translator_tencent)]
                await asyncio.gather(*tasks)

                await asyncio.sleep(0.5)
                quest_results.extend(pending)

                print('.', end='')
        print()
        total_fix = 0
        for quest in quest_results:
            orn_text, modified_length = quest.replace(orn_text, total_fix)
            total_fix += modified_length

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(orn_text)

asyncio.get_event_loop().run_until_complete(main())