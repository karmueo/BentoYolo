import requests
import base64
import numpy as np
from PIL import Image
from io import BytesIO
import gradio as gr

# 后端推理服务URL
url_predict = "http://192.168.30.232:5500/process_image"


def encode_image(image: np.ndarray) -> str:
    """
    把图像编码为base64字符串

    Args:
        image (np.ndarray): 输入为numpy格式的图像

    Returns:
        str: 编码后的base64字符串
    """
    if image.dtype != np.uint8:
        image = (image * 255).astype(np.uint8)  # 将图像转换为uint8类型
    pil_image = Image.fromarray(image)
    buffered = BytesIO()
    pil_image.save(buffered, format="JPEG")
    return base64.b64encode(buffered.getvalue()).decode("utf-8")


def decode_image(encoded_image: str) -> np.ndarray:
    """
    解码base64字符串为numpy格式的图像

    Args:
        encoded_image (str): _description_

    Returns:
        np.ndarray: _description_
    """
    image_data = base64.b64decode(encoded_image)
    image = Image.open(BytesIO(image_data))
    return np.array(image)


def perform_task(image: np.ndarray, task: str):
    """
    把图像编码为base64字符串，发送给后端服务，获取处理后的图像

    Args:
        image (np.ndarray): _description_
        task (str): _description_

    Returns:
        _type_: _description_
    """
    encoded_image = encode_image(image)
    request_data = {"encoded_image": encoded_image}
    # request_data = Base64Image(encoded_image=encoded_image).model_dump_json()
    response = requests.post(
        url_predict, json=request_data, headers={"Content-Type": "application/json"}
    )

    if response.status_code == 200:
        try:
            response_json = response.json()
            result_image = decode_image(response_json["encoded_image"])
            return result_image
        except Exception as e:
            print(f"Error processing response: {e}")
            return None
    else:
        print(f"Request failed with status code: {response.status_code}")
        return None


def detect(image):
    return perform_task(image, "detect")


# Gradio界面，删除页面底部的版权信息
with gr.Blocks(css="footer{display:none !important}") as demo:
    with gr.Row():
        with gr.Column():
            input_image = gr.Image(type="numpy", label="输入图片")
            detect_button = gr.Button("检测")
        with gr.Column():
            detect_output_image = gr.Image(type="numpy", label="检测结果")

    # 绑定按钮事件，点击按钮时调用detect和segment函数
    detect_button.click(fn=detect, inputs=input_image, outputs=detect_output_image)

demo.launch(server_name="0.0.0.0", server_port=7860)
