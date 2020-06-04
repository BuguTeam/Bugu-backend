## Bugu-backend

这是Bugu微信小程序后端服务器的一个稳定版本。实现了所有功能，以及在服务器上的部署和与前端的连接。

## 技术框架

使用flask+MySQL

### 用到的工具

1.需要先安装MySQL，并熟悉相关操作.

2.使用python3, 推荐使用虚拟环境virtualenv，依赖包在`requirements.txt`中列出.



## 目录结构

```
├── web
       ├── app
       ├── instance
           ├── config.py
       ├── migrations
       ├── venv
       ├── config.py
       ├── requirements.txt
       └── run.py
```

`instance\config.py`中是配置文件，包含密钥等信息。这一部分由开发组成员保留，没有上传到当前的仓库。

## 运行

1.配置virtualenv环境

```
# cd <my_path>\Bugu-Backend
> virtualenv venv #新建环境，名字为venv
> .\venv\Scripts\activate #激活环境 
(venv) pip install -r requirements.txt #安装对应的包
```

注意！

我们使用virtualenv来做python环境隔离和迁移，那么以后所有pip等操作都需要在这个名叫venv的虚拟环境下进行（也就是前面有一个venv的提示符）。

如果安装了新的包，在提交代码时需要更新`requirements.txt`，可以手动添加，也可以自动导出当前环境：

到`\venv\Scripts`目录下，导出此环境下安装的包的版本信息 

```
(venv) pip freeze > requirements.txt
```

2.新建MySQL数据库：

```
> mysql -u root -p
mysql> CREATE USER 'buguadmin'@'localhost' IDENTIFIED WITH mysql_native_password BY 'bugu2020';

mysql> CREATE DATABASE bugudb;

mysql> GRANT ALL PRIVILEGES ON bugudb . * TO 'buguadmin'@'localhost';

mysql> flush privileges;

```

这里buguadmin是管理员账户，bugu2020是密码，bududb是数据库名字。

现在数据库里面什么都没有，可以通过运行前端，并在addActivity中添加活动，也可以在命令行中通过mysql语句添加。添加完数据之后，可以导出数据库到文件

```
mysqldump -u root -p database_name > database_dump.sql
```

导入数据库：

```
mysql -u root -p new_databast_name < database_dump.sql
```

3.启动。

如果是Windows系统，打开cmd，依次执行：

```
(venv) set FLASK_CONFIG=development
(venv) set FLASK_APP=run.py
```

如果是Linux/Mac系统，打开bash按如下操作

```
$export FLASK_CONFIG=development
$export FLASK_APP=run.py
```

然后运行

```
(venv) flask db init
(venv) flask db migrate
(venv) flask db upgrade

```

如果在Migrate阶段报错`ERROR [root] Error: Can't locate revision identified by '0066c544c2f8'           `, 那么需要把bududb中的版本信息删除。

```
>mysql -u root -p
mysql> use bugudb;
mysql> drop table alembic_version;
```

对数据库模型的任何修改，都要再执行flask db migrate, flask db upgrade. 

最后，运行

```
flask run
```

在浏览器打开`localhost:5000`可以使用GET访问网页。在上面的命令行中可以看到flask的输出.





#### 往数据库里面写入

现在数据库里面什么都没有，可以通过

1.推荐下载微信开发者工具，运行前端[[link](https://github.com/BuguTeam/Bugu)]（dev分支）来交互。运行前端，并在addActivity页面中添加活动

2.也可以在命令行中通过mysql语句添加。

```
>mysql -u root -p
mysql> use bugudb;
mysql> ...
```

3.可以在python中添加管理员账户以及添加任意User/Activity数据。下面是一个例子：

```
>flask shell

from app.models import User
from app import db
admin = User(username="admin",is_admin=True)
db.session.add(admin)
db.session.commit()
```





## 其他说明

### session管理

微信小程序的登录流程比较复杂，后端服务器需要与小程序前端，和微信服务器进行交互。参考官方的说明[[link](https://developers.weixin.qq.com/miniprogram/dev/framework/open-ability/login.html )] 。

一些参考资料：[[link1](https://www.cnblogs.com/dashucoding/p/9917371.html )] [[3rd_session](http://www.yiyongtong.com/archives/view-5954-1.html )]

##### 主要流程

1. 微信小程序端调用wx.login，获取登录凭证（code），并调用接口，将code发送到第三方客户端
2. 小程序端将code传给第三方服务器端，第三方服务器端调用接口，用code换取session_key 和openid (用户唯一身份标识)
3. 第三方服务器端拿到请求回来的session_key和openid，但是不能把Openid直接给客户端；而是生成一个新的session，叫3rd_session (临时登录态，每一次都生成不同的session key，可以由3rd_session解码出openid，临时登录态会过期，过期后不能正确解码)
4. 第三方服务端建立openid和用户信息的对应关系，保存起来
5. 第三方服务端将3rd_session发送到客户端；客户端只拿到3rd_session就够了，小程序不需要知道session_key和openid
6. 正常请求：小程序每次请求都将3rd_session放在请求头里，第三方服务端解析3rd_session得到openid，判断合法性，并进行正常的逻辑处理。

##### third_session相关实现

比如判断用户是否加入活动，只能用用户的Openid来建立关联，不能用3rdsession。

因为，3rdsession只是一个**临时** **会话**的标识

- 观察一下后端的输出，可以发现同一个用户每一次会话的3rdsession都是不一样的，这是因为同一个 gen_3rd_session(u.openid) 的多次执行结果是不一样的。
- 3rdsession是**临时**的！ 3rdsession在一定时间内（可以自己设置）可以解码出原来的openid，但是一段时间过后就不行了。这就是为什么前端开发工具运行很长一段时间之后有时会报错，这是因为一开始申请的临时会话过期了，3rdsession不能正确的解码出openid；重新编译之后就正常了。过期的问题是每一次申请新的3rdsession，还是请求失败之后重新申请，之后有待解决，不过目前短时间内的访问是没有问题的。

目前3rdsession用 itsdangerous库的`TimedJSONWebSignatureSerializer`实现。



#### Discussion部分的改动

#### 服务器部署：

现在后端已经部署到了服务器上，服务器ip为39.104.25.65，访问端口是80

服务器后端代码位于~/myGit/Bugu-backend下，如果更新了代码，需要重新运行myGit目录下的run.sh重启后端服务