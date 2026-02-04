# Repeater Note Client

这是 Repeater Bot 的每日日记本客户端
它使用相同的 Python 3.11 环境运行

---

## 配置数据

配置文件位于`./config`目录下
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

---

## 使用

像后端一样，这个客户端使用相同的`run.py`文件来运行
运行`python run.py`即可启动

---

## 生成格式：

### text:

``` PlainText
# Repeater Note
- Note ID: {request_id}
- Time: {time}
- Model ID: {model_id}
- Reference Context User ID: {reference_context_user_id}

## CoT: 
{reasoning_content}

## Answer: 
{answer}
```

### json:

```json
{
  "Note ID": "{note_id}",
  "Time": "{time}",
  "Model ID": "{model_id}",
  "Reference Context User ID": "{reference_context_user_id}",
  "CoT": "{reasoning_content}",
  "Answer": "{answer}"
}
```

### yaml:

```yaml
Note ID: {note_id}
Time: {time}
Model ID: {model_id}
Reference Context User ID: {reference_context_user_id}
CoT: {reasoning_content}
Answer: {answer}
```

---

## Worker

每在`./config`中定义一个配置文件，就会启动一个对应的 Worker 协程
Note Client 专门为多 Server 做了一定优化
所以即使你创建了超多的配置项，它也是轻量的协程调度
首次启动时，它会直接访问目标 API
从用户列表中随机挑选一个用户
以它作为引用上下文，访问 API 生成并保存内容
然后进入等待模式，等待到第二天的一个随机时间
再次访问目标 API 并保存内容

---

## 配置

配置文件位于`./config`目录下
每个配置文件都会启动一个Worker协程定时器

---

## License

这个项目基于[MIT License](LICENSE)发布。

---

## 使用到的后端接口
| 请求 | URL | 使用到的参数 | 描述 |
| :---: | :---: | :---: | :---: |
| `POST` | `/chat/completion/{user_id:str}` | `message`, `cross_user_data_routing`, `save_context` | 获取AI生成内容 |
| `GET` | `/userdata/context/userlist` | | 获取Context类型的用户列表 |

---

## 相关仓库
- [Repeater Server](https://github.com/qeggs-dev/repeater-ai-chatbot)