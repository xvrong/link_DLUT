# 项目介绍 
大连理工大学新版校园网登录系统 登录脚本 

# 使用方法
1. 克隆项目
2. 安装依赖

   python版本: 3.8及以上
   1. [requests](https://pypi.org/project/requests/)
   2. [PyExecJS2](https://pypi.org/project/PyExecJS2/)
   3. [ping3](https://pypi.org/project/ping3/)

   ```bash
   pip install requests
   pip install PyExecJS2
   pip install ping3
   ```

3. 修改config.ini中的用户名和密码
4. 运行link_dlut.py，执行后脚本会持续检查网络状态，如果网络断开，则尝试重新登录

# 开机自启
## windows 
1. 修改link_dlut.vbs中的项目路径
2. 将link_dlut.vbs复制到C:\Users\用户名\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup下