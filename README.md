# 环境要求
- Python 3.5 +

# 如何使用
第一次使用请安装依赖：`pip install -r requirements.txt` 或使用发布版
- 从配置文件加载

启动时会首先尝试读取目录下的 `config.yaml` 文件，若成功读取则使用配置文件中的参数，参数含义见 `config.yaml` 中注释

- 手动输入

若配置文件不存在则要求手动输入账号、密码等参数