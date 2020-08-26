# 智能更新deluge的单种securekey
## 依赖
- deluge_client
- requests

（依赖库采用pip安装：控制台/Shell下输入 `pip install 包名`）

## 你需要准备
- 合理的代理/Hosts设置保证API访问
- 在 站点根目录/privatetorrents.php 获取你的API URL
- Deluge后端网址和端口（注意 端口**不是**WEBUI的端口 可以在Connection Manager查看）
- Deluge用户名密码

## 使用方法
- 修改 CHANGE INFO BELOW 下方几行参数为你自己的参数
- 进入控制台/Shell
- `cd`进入所在脚本所在目录
- `python xxxx.py`回车运行

## 免责说明
  测试阶段，已尽量进行debug，但也难免疏漏。
如有还请及时反馈。因滥用造成的任何问题恕不负责。
