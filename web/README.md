# 前端

## Table of Contents

- [About](#about)
- [Usage](#usage)
- [Contributing](../CONTRIBUTING.md)

## About <a name = "about"></a>

使用Gradio搭建了一个前端，用来测试BentoYolo

### Prerequisites

- Python 3.8及以上版本
- 部署的时候需要Docker

### Installing

用pip下载Gradio
```bash
pip install gradio
```

## Usage <a name = "usage"></a>

主要程序为`app.py`，可以通过下面的方式来启动

```bash
python app.py
```

### 部署

1. 参考Dockerfile编写，该 Dockerfile 执行以下步骤：
    - 从 Python 3.8 slim 镜像开始。
    - 设置工作目录并将应用程序复制到容器中。
    - 安装 Gradio（您还应该安装所有其他要求）。
    - 暴露端口 7860（Gradio 的默认端口为7860）。
    - 设置 GRADIO_SERVER_NAME 环境变量以确保 Gradio 侦听所有网络接口。
    - 指定运行应用程序的命令。

2. 构建容器并启动

    ```bash
    docker build -t gradio-app .
    docker run -p 7866:7860 gradio-app
    ```

    现在应该可以通过 http://localhost:7866 访问您的 Gradio 应用程序。