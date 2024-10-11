# 基于python-3.11.10
FROM python:3.11.10-slim

# 工作目录
WORKDIR /musicatri

# 复制项目运行文件
COPY ./langfiles /musicatri/langfiles
COPY ./website /musicatri/website
COPY ./musicatri.py /musicatri/musicatri.py
COPY ./requirements.txt /musicatri/requirements.txt

# 安装项目依赖
RUN ["pip", "install", "--upgrade", "pip"]
RUN ["pip", "install", "-r", "requirements.txt"]

# 安装系统软件
RUN ["apt", "update"]
RUN ["apt", "install", "ffmpeg", "-y"]

# 项目启动入口
ENTRYPOINT ["python", "./musicatri.py"]