# 默认镜像构建基于基于python-3.11.10，使用Dockerfile.fastbuild作为构建文件来获得更快的构建速度
FROM python:3.11.10-slim

# 工作目录设置为/musicatri
WORKDIR /musicatri

# 复制项目运行文件
COPY ../langfiles /musicatri/langfiles
COPY ../website /musicatri/website
COPY ../musicatri.py /musicatri/musicatri.py
COPY ../config.json /musicatri/config.json
COPY ../requirements.txt /musicatri/requirements.txt

# 安装python第三方依赖
RUN ["pip", "install", "--upgrade", "pip"]
RUN ["pip", "install", "-r", "requirements.txt"]

# 安装程序运行必要依赖
RUN ["apt", "update"]
RUN ["apt", "install", "ffmpeg", "-y"]

# 项目启动入口
ENTRYPOINT ["python", "./musicatri.py"]