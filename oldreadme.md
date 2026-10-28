创建一个项目初始化模板
需要支持简单(simple)和复杂(complex)模式
简单模式支持 pnpm/vue3/vite/flask/waitress/xuri-rpc-websocket
复杂模式在此基础上需要额外支持 element-ui,SQLAlchemy
其他要求:
项目顶层需要存在gitignore,不需要创建git
项目目录首先分为`frontend`,`backend`
项目在初始化的时候需要用户提供的参数包括项目名称,前端开发端口号,后端开发端口号(http/ws),后端部署端口号(http/ws),simple/complex.所有端口号非必填,如果留空则随机,随机方法需要是一独立的函数,以后可能会扩展
后端需要有独立的配置文件,并支持dev/release模式
使用python来实现此程序,注意代码注释和类型注解,注意代码简洁,注意严禁静默异常处理
项目需要在后端配置pytest 并带有覆盖率测试
存在命令:
  1,dev启动
  2,编译
  3,编译并复制到flask
  4,覆盖率测试
  5,release启动
  6,无打包编译,即,不包括elementUI和vue3的编译,编译产物会被引用,在新引用环境中提供vue和elementUI
  
  
simple/complex 这块,支持单字符s,c