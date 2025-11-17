# Repeater Note Client

这是 Repeater Bot 的每日日记本客户端
它使用相同的 Python 3.11 环境运行

## 配置数据
配置文件位于`/config`目录下
文件格式为`json`或`yaml`
每个配置文件都会启动一个Worker协程定时器
示例：
```json
{
    "server": {
        "host": "127.0.0.1",
        "port": 7645,
        "protocol": "http", // http or https
        "timeout": 3600
    },
    "namespace": "Notes_Plugins",
    "prompt_file": "./prompt/repeater.txt", // Prompt file path
    "output_dir": "./output/repeater",
    "output_file_suffix": ".txt",
    "output_format": "text", // text/json/yaml
    "retry_times": 3,
    "retry_interval": 0.5
}
```

## 使用
像后端一样，这个客户端使用相同的`run.py`文件来运行
运行`python run.py`即可启动

## 配置
配置文件位于`/config`目录下
每个配置文件都会启动一个Worker协程定时器

## License
这个项目基于[MIT License](LICENSE)发布。

## 使用到的后端接口
| 请求 | URL | 使用到的参数 | 描述 |
| :---: | :---: | :---: | :---: | :---: |
| `POST` | `/chat/completion/{user_id:str}` | `message`, `reference_context_id`, `save_context` | 获取AI生成内容 |
| `GET` | `/userdata/context/userlist` | | 获取Context类型的用户列表 |

## 相关仓库
- [Repeater Backend](https://github.com/qeggs-dev/repeater-ai-chatbot-backend)