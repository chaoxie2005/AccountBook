FROM registry.hub.docker.com/library/python:3.11-slim
# 设置环境变量 - 配置 Python 不生成 .pyc 缓存文件
ENV PYTHONDONTWRITEBYTECODE=1
# 配置 pip 使用国内镜像源（下载更快）
ENV PIP_INDEX_URL=https://mirrors.aliyun.com/pypi/simple/
# 设置工作目录 - 相当于 cd /app
WORKDIR /app
# 复制依赖文件 - 先复制这个，因为 Docker 会缓存这层
COPY requirements.txt .
# 安装依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制整个项目到容器中
COPY . .

# 收集静态文件 - Django 项目生产环境必需
RUN python manage.py collectstatic --noinput

# 暴露端口
EXPOSE 5000
# 启动命令 - 容器启动时运行的命令
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "accountbook.wsgi:application"]

