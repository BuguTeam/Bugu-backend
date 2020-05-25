## Bugu-backend

这是一个dev分支

Bugu微信小程序后端：使用flask+MySQL

用到的工具

1.需要先安装MySQL，并熟悉相关操作.

2.使用python3, 推荐使用虚拟环境virtualenv，依赖包在`requirements.txt`中列出.



目录结构：

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

`instance\config.py`中是配置文件，包含密钥等信息。

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





#### session管理

微信小程序的登录流程比较复杂，参考： https://developers.weixin.qq.com/miniprogram/dev/framework/open-ability/login.html 

一些参考资料：https://www.cnblogs.com/dashucoding/p/9917371.html 

3rd_session：  http://www.yiyongtong.com/archives/view-5954-1.html 



#### Discussion部分的改动

#### 服务器部署：

现在后端已经部署到了服务器上，服务器ip为39.104.25.65，访问端口是80

服务器后端代码位于~/myGit/Bugu-backend下，如果更新了代码，需要重新运行myGit目录下的run.sh重启后端服务