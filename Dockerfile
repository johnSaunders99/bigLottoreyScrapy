# 使用官方 Python 3.11 作为基础镜像
FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 复制依赖清单并安装依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制项目代码
COPY ..

# 暴露端口（Flask 默认 5000）
EXPOSE 5000

# 设置环境变量
ENV FLASK_APP=service.py
ENV FLASK_RUN_HOST=0.0.0.0

# 启动命令
CMD ["flask", "run"]