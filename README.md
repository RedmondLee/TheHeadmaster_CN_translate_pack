# The_Headmaster_CN_translate_pack
P站游戏 The Headmaster(Altos and Herdone) 的翻译工具包.

### 正确的翻译脚本使用流程
```
0. pip install -r requirements.txt
安装依赖，需要python版本大于3.7

1. python note_translate_1_generate.py
提取行内文本

2. 备份
提取文本后，可以选择上传至github仓库，在面临版本更新时，可以使用git工具查看新增文档与原有文档的差异。

3. python note_translate_2_baiduapi.py
运行百度翻译api，将提取出的文本进行自动机翻。运行前需要先注册并填写自己的百度翻译权限key

4. 润色
改正看起来不像人类说出的话。

5. python note_translate_3_reduction.py
将翻译后的文本贴回脚本。
```

### 当前更新版本号
0.11.1
