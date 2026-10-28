# 运行依赖
flask>=3.0.0
waitress>=3.0.0
xuri-rpc-websocket>=1.0.0
cbor2>=5.4.0
# xuri-rpc-websocket 使用 websockets.legacy 接口,websockets 15 起已移除,锁定 <14
websockets>=12.0,<14.0
{{SQLALCHEMY_REQUIREMENT}}# 测试依赖(pytest + 覆盖率)
pytest>=8.2.0
pytest-cov>=5.0.0
