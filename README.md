# Project Title

## Table of Contents

- [About](#about)
- [Getting Started](#getting_started)
- [Usage](#usage)
- [Contributing](../CONTRIBUTING.md)

## About <a name = "about"></a>

Write about 1-2 paragraphs describing the purpose of your project.

## Getting Started <a name = "getting_started"></a>

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See [deployment](#deployment) for notes on how to deploy the project on a live system.

### Prerequisites

- 已经安装了 Python 3.8+ 和 `pip`.
- 对 BentoML 中的关键概念（例如服务）有基本的了解. 可以先学习 [Quickstart](https://docs.bentoml.com/en/latest/get-started/quickstart.html).
- (可选) 建议为此项目创建一个虚拟环境以进行依赖隔离.

### Installing

```
pip install -r requirements.txt
```


## Usage <a name = "usage"></a>

### 运行BentoML服务

在`service.py`中定义了一个 BentoML 服务。在项目目录中运行`bentoml serve`以启动服务。

```bash
bentoml serve service:YoloV8
```

### 部署

要部署 BentoML 服务代码，请首先创建一个 bentofile.yaml 文件来定义其依赖项和环境。在[此处](https://docs.bentoml.com/en/latest/guides/build-options.html)查找 Bentofile 选项的完整列表。
运行 `Bentoml build` 将必要的代码、模型、依赖项配置打包到 Bento 中 - BentoML 中的标准化可部署工件。该命令所有创建的Bentos默认存储在 `/home/user/bentoml/bentos/` 中。


```bash
bentoml build
```

查看所有可用的Bentos

```bash
bentoml list
```

确保 Docker 在运行。生成用于部署的 Docker 容器。由于需要通过外网下载，通常需要配置代理才能正常生成容器，可以通过参数`--opt build-arg=http_proxy=http://xxx.xxx.xxx.xxx:xxxx`指定构建容器时的额外参数

```bash
bentoml containerize yolo_v8:latest
# 如需要添加代理用下面的方式构建,替换实际的代理地址
# bentoml containerize yolo_v8:latest --opt build-arg=http_proxy=http://192.168.30.184:7890 --opt build-arg=https_proxy=http://192.168.30.184:7890
```

运行生成的容器镜像：

```bash
# latest可能需要修改为实际的id，注意打印输出内容
docker run --rm -p 5500:5200 yolo_v8:latest
```
