# 额外说明

## 提交Bug（与修正错误）的方法

游戏汉化过程中，因为汉化疏漏（比如新增某些标点符号，不被程序识别），或者原作者本身疏漏，游戏可能会产生Bug。通常表现为游戏中弹出灰色界面，使游戏无法运行。

当出现该问题时，这个界面显示的是错误的位置和原因，由于原游戏中的字体替换未覆盖到debug信息，您在游戏内的debug界面可能看到方块乱码，这是由字体不全导致的。当发生错误后，游戏目录下会产生名为traceback.txt文件，记录错误内容发生具体位置，直接打开该文件查看就不会被乱码困扰了。

如果您没有能力自行修正Bug，欢迎在本仓库提交错误，或者在您看到资源的任何平台提交错误，不过除了sstm外大概率不会得到反馈，所以还是统一汇总到本仓库比较好。如果您从未使用过github，只需花费简短时间注册一个账号即可参与讨论（不需要验证手机，注册很轻松）。

提交错误的方法是：点击屏幕左上角标题下方一行字中，从左到右分别是code，issues，pull requests等等，请点击第二项issues(事务)，而后点击绿色按钮new issue，即可按照类似发帖的格式发表主题。主题中直接贴入traceback.txt的内容即可。

如果您不愿意等待修正，您大可以自行修正bug，通常这并不耗费很多时间，也不需要多高的技术。

### 比如下面我们以一个人工模拟的bug举例，如何自己修正bug

假设我们将游戏最开始的旁白部分的文本中的一句：
```
    # mt "I'll head into the office first and check in with my PA Samantha."
    mt "我先去办公室和我的助理萨曼莎报到."
```
在译文中添加一个百分比符号`%`变成`我先去办公室和我的助理萨曼莎报到%.`，这种情况通常可能由机翻产生，比如原文用percent表示百分比，而机器翻译后可能直接将其替换成百分比符号，但这个符号在renpy编程中有特殊含义，如果不加人工修正就会被误读。

我们修改后重新打开游戏，运行到指定位置后果然报错，查看错误的产生原因：traceback.txt
```
I'm sorry, but an uncaught exception occurred.

While running game code:
  File "game/monday.rpy", line 851, in script call
    call day2_thoughts from _call_day2_thoughts
  File "game/tl/chinese/staff_conversations.rpy", line 43, in script
    mt "我先去办公室和我的助理萨曼莎报到%."
ValueError: incomplete format

-- Full Traceback ------------------------------------------------------------

Full traceback:
  File "game/monday.rpy", line 851, in script call
    call day2_thoughts from _call_day2_thoughts
  File "game/tl/chinese/staff_conversations.rpy", line 43, in script
    mt "我先去办公室和我的助理萨曼莎报到%."
  File "renpy/ast.py", line 721, in execute
    renpy.exports.say(who, what, *args, **kwargs)
  File "renpy/exports.py", line 1406, in say
    what = what % tag_quoting_dict
ValueError: incomplete format

Windows-10-10.0.19041
Ren'Py 7.4.10.2178
The Headmaster 0.11.1Public
Fri Nov 19 13:20:03 2021
```
该报错内容应从下往上看，越下方的内容越重要。最下方四行是运行环境记录，暂且忽略。在网上一行提示错误原因
```
what = what % tag_quoting_dict
ValueError: incomplete format
```
可知道错误提示是未识别到应该量化的数值，这是出现了占位符%但没有出现被量化数所导致的。

再往上我们可以看到出问题的代码逐级往上的调用链分别定位于四个文件的xx行：
```
  File "game/monday.rpy", line 851, in script call
    call day2_thoughts from _call_day2_thoughts
  File "game/tl/chinese/staff_conversations.rpy", line 43, in script
    mt "我先去办公室和我的助理萨曼莎报到%."
  File "renpy/ast.py", line 721, in execute
    renpy.exports.say(who, what, *args, **kwargs)
  File "renpy/exports.py", line 1406, in say
    what = what % tag_quoting_dict
```
其中刨除我们看不懂的部分，可以看到那句中文我们还是能看懂的。再加之我们知道bug发生原因，基本上只要把该句中文修改通顺即可规避错误，使程序继续运行。而删除的位置在报错信息中心也被完整的提示了，在game/tl/chinese/staff_conversations.rpy这个文件的第43行。

所以如果你有基础的编程知识，你应该知道这里需要进行转义，即将`%`改成`\%`使得该特殊符号不会被程序解释，或者如果你对于计算机程序没有任何了解的话，单纯地删除这个符号（虽然有可能造成原文词不达意，不过无伤大雅），也能够阻止bug产生。

以上是一个面向完全0基础玩家的debug范例，如果你有一定程度的程序基础/计算机使用经验，这对你也许会更加轻松。

## 玩家如何下载最新汉化补丁

这部分是完全新手向的教学，假定您完全不熟悉github和编程技术。

在您打开本项目首页后[https://github.com/RedmondLee/TheHeadmaster_CN_translate_pack](https://github.com/RedmondLee/TheHeadmaster_CN_translate_pack) 点击屏幕中唯一的绿色按钮code，再点击download zip，即可下载最新的源码（汉化文本）包。当然，在您熟练使用后，您也可以下载某一历史版本的包。

下载后解压，将所有文件对应地复制到game文件夹下，覆盖image和tl文件夹的内容，重新运行游戏，即可覆盖使用最新的汉化补丁。
