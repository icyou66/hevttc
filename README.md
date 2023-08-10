# 河北科技师范学院抢课脚本
> - 本作品出自一名大四的老学长。代码写得不规范，还需努力，各路英雄豪侠手下留情(╥╯^╰╥)
> - 本项目供学习交流使用，切勿用于非法用途。使用本项目造成的一切后果自行承担。
> - 之前写好的正方教务系统代码还没有提交便被通知学校换了新系统，呜呜┭┮﹏┭┮
## 功能
- **直接进行选课**
- **已经选过的课程进行退课**
- **持续化监控课程**

## 使用方法
- **进行选课和退课时，均为鼠标右击课程后进行操作**
- **登录后将会自动将账号密码保存至同目录下info.json文件中**
- **其他功能软件中均有提示与说明，不过多赘述，这里着重说明一下监控课程**
- **监控课程可空变量为延迟时间和搜索的课程，延迟时间默认为1秒，可以设置小于1秒的时间例如0.5秒。搜索的课程可以是关键词例如想搜索龙椅上的那些人，你可以直接输入：龙椅。若课程列表中有多个包含：龙椅的课程，默认选择的是第一个课程。因此尽量保证关键词只能匹配到一条课程为最优解。开发测试期间没有测试过持续1天的监控，因此关于监控课程含有诸多不可控因素，如发现有问题可提交issue。** 

#### 安装依赖
```bash
pip install -r requirements.txt
```
#### 依赖说明
- **本代码仅使用了beautifulsoup和requests两个拓展模块，其它均为内置模块，如果你拥有这两个模块可直接运行**
- **尽量使用最新版本的python**

## 可执行文件运行
> 仅支持windows平台。
> 解压至任意目录
> 双击`qk.exe`即可运行
