from __future__ import annotations

import numpy as np
import os
from pathlib import Path
from typing import List
import json
import base64
from io import BytesIO
from PIL import Image
import bentoml
from pydantic import BaseModel, field_validator, Field
import typing as t


def increment_counter():
    """
    定义一个全局变量counter，用于记录服务调用次数
    """
    global counter
    counter += 1
    with open(counter_file, "w") as f:
        f.write(str(counter))


def decode_image(encoded_image: str) -> np.ndarray:
    """
    将base64编码的图像解码为numpy数组

    Args:
        encoded_image (str): base64编码的图像

    Returns:
        np.ndarray: numpy数组
    """
    print("Decoding image.................")
    image_data = base64.b64decode(encoded_image)
    image = Image.open(BytesIO(image_data))
    return np.array(image)


def encode_image(image: np.ndarray) -> str:
    """
    将numpy数组编码为base64字符串

    Args:
        image (np.ndarray): _description_

    Returns:
        str: _description_
    """
    pil_image = Image.fromarray(image)
    buffered = BytesIO()
    pil_image.save(buffered, format="JPEG")
    return base64.b64encode(buffered.getvalue()).decode("utf-8")


class Base64Image(BaseModel):
    encoded_image: str = Field(description="The input image encoded as base64 string")

    @field_validator("encoded_image")
    def validate_image(cls, v):
        try:
            # 尝试解码并加载图片以验证是否为有效的base64编码图片数据
            image_data = base64.b64decode(v)
            image = Image.open(BytesIO(image_data))
            image.verify()
        except Exception as e:
            raise ValueError(f"无效的图片数据: {e}")
        return v


# 使用装饰器@bentoml.service来注释一个类，表明它是一个BentoML服务
@bentoml.service(
    resources={"gpu": 1},
    http={"port": 5000},
    traffic={"timeout": 10},
)
class YoloV8:
    def __init__(self):
        from ultralytics import YOLO

        current_dir = os.path.dirname(os.path.abspath(__file__))
        detect_model_path = os.path.join(current_dir, "yolov8x.pt")
        print(f"Loading YOLO detect model from {detect_model_path}")
        self.detect_model = YOLO(detect_model_path)

    @bentoml.api(input_spec=Base64Image, output_spec=Base64Image)
    def process_image(self, **params: t.Any) -> str:
        """
        使用pydantic从post请求中解析输入数据，主要是base64编码的图片数据，进行推理并返回结果

        Returns:
            str: base64编码的图片数据
        """
        # 解码图片
        encoded_image = params["encoded_image"]
        image = decode_image(encoded_image)

        # 生成递增的保存目录名称
        increment_counter()
        save_dir = Path(f"runs/detect/predict{counter}")

        rendered_image_path = self.render(image, save_dir, "detect")

        # 读取保存的图像并重新编码为Base64
        with open(rendered_image_path, "rb") as f:
            encoded_rendered_image = base64.b64encode(f.read()).decode("utf-8")

        return Base64Image(encoded_image=encoded_rendered_image)

    def predict(self, images: List[np.ndarray], task: str) -> List[List[dict]]:
        """
        预测服务

        Args:
            images (List[np.ndarray]): _description_
            task (str): _description_

        Raises:
            ValueError: _description_
            e: _description_

        Returns:
            List[List[dict]]: _description_
        """
        try:
            if task == "detect":
                results = self.detect_model(images)
            # elif task == "segment":
            #     results = self.segment_model(images, task="segment")
            else:
                raise ValueError(f"Unknown task: {task}")
            return [json.loads(result.tojson()) for result in results]
        except Exception as e:
            print(f"Error during prediction: {e}")
            raise e

    def render(self, image: np.ndarray, save_dir: Path, task: str) -> Path:
        """
        相比预测服务，render还会绘制结果

        Args:
            image (np.ndarray): _description_
            save_dir (Path): _description_
            task (str): _description_

        Raises:
            ValueError: _description_
            e: _description_

        Returns:
            Path: _description_
        """
        try:
            if task == "detect":
                result = self.detect_model(image)[0]
            # elif task == "segment":
            #     result = self.segment_model(image, task="segment")[0]
            else:
                raise ValueError(f"Unknown task: {task}")

            rendered_image = result.plot()

            # 创建保存目录
            save_dir.mkdir(parents=True, exist_ok=True)
            save_path = save_dir / "rendered_image.jpg"
            rendered_image_pil = Image.fromarray(rendered_image)
            rendered_image_pil.save(save_path)

            return save_path
        except Exception as e:
            print(f"Error during rendering: {e}")
            raise e


# 初始化计数器
counter_file = Path("runs/counter.txt")
counter_file.parent.mkdir(parents=True, exist_ok=True)

# 如果计数器文件存在，则从文件中读取计数器的值，否则初始化为0
if counter_file.exists():
    with open(counter_file, "r") as f:
        counter = int(f.read().strip())
else:
    counter = 0
