## Bugu-backend

这是一个testing分支

增加Bugu微信小程序后端（flask+MySQL）的单元测试；工具：Flask-Testing

配置步骤与dev分支相同，若已配置运行过则不必重复执行，只需要注意再次运行：
```
(venv) pip install -r requirements.txt #安装对应的包
```
以安装FlaskTesting等测试扩展。


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
       ├── tests.py
       └── run.py
```

`tests.py`是测试文件。
`instance\config.py`中是配置文件，包含密钥等信息。


1.新建用于测试的MySQL数据库：

```
> mysql -u root

mysql> CREATE DATABASE bugubackend_test;

mysql> GRANT ALL PRIVILEGES ON bugubackend_test . * TO 'buguadmin'@'localhost';

```

2.执行测试。

```
(venv) python tests.py
```

测试代码（```tests.py```）相关注意点：

1.参考：https://scotch.io/tutorials/build-a-crud-web-app-with-python-and-flask-part-three#toc-tests

2.可以看到修改了```app\auth\views.py```中的```gen_openid```函数，目的是使其直接返回测试需要的openid（在addActivity和UserActivityHistory中调用了该函数）；更好的实现方式应该是使用mock替代gen_openid模块

3.测试中使用post向被测模块发送请求时，注意注释掉被测模块中的```db.session.commit()```语句，否则测试报错（原因可参考https://pythonhosted.org/Flask-Testing/ ）。需要执行的commit操作可以放到测试函数post请求之后的语句中（见tests.py中test_addActivity_view等函数）。

#### 服务器部署：

现在后端已经部署到了服务器上，服务器ip为39.104.25.65，访问端口是80

服务器后端代码位于~/myGit/Bugu-backend下，如果更新了代码，需要重新运行myGit目录下的run.sh重启后端服务