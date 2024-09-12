FROM python:3.12.5-slim

# 設置工作目錄
WORKDIR /app

# 複製項目文件到容器中
COPY . /app

# 安裝項目依賴
RUN pip install --no-cache-dir -r requirements.txt


# 暴露應用程序運行的端口
EXPOSE 5050

# 運行應用程序
CMD ["python", "main.py"]
