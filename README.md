# TinyURL 服務

這是一個使用 FastAPI 構建的簡單 TinyURL 服務，用於創建短網址並進行重定向。

## 功能

- 創建短網址
- 重定向短網址到原始 URL
- 速率限制
- 日誌記錄

## 技術棧

- FastAPI
- SQLAlchemy
- Redis
- PostgreSQL

## 安裝

1. 克隆倉庫：
```bash
git clone https://github.com/your-username/system-design-tinyurl.git
cd system-design-tinyurl
```

2. 安裝依賴：
```bash
pip install -r requirements.txt
```

## 配置

設置以下環境變量：

- `DATABASE_URL`：數據庫連接 URL
- `REDIS_HOST`：Redis 主機地址
- `REDIS_PORT`：Redis 端口
- `REDIS_DB`：Redis 數據庫編號
- `RATE_LIMIT_TIMES`: 速率限制次數 (Default 1)
- `RATE_LIMIT_TIME_UNIT`: 速率限制次數 (Default minutes, Options: milliseconds | seconds | minutes | hours)

## 運行

使用以下命令運行服務：
```bash
uvicorn main:app --host 0.0.0.0 --port 5050 --workers 2
```

## API 使用

### 1. 創建短網址

**請求：**

- 方法：POST
- 路徑：`/v1/tinyurl`
- 內容類型：JSON

**請求體：**
```json
{
    "origin": "https://example.com/very/long/url/that/needs/shortening"
}
```

**響應：**
```json
{
    "tiny": "http://yourdomain.com/v1/abcdefgh",
    "expired_date": "2023-12-31",
    "success": true,
    "origin": "https://example.com/very/long/url/that/needs/shortening"
}
```

### 2. 重定向短網址

**請求：**

- 方法：GET
- 路徑：`/v1/{tiny_url}`

**響應：**

- 重定向到原始 URL

## 錯誤處理

服務可能返回以下錯誤：

- 404 Not Found：短網址不存在
- 410 Gone：短網址已過期
- 422 Unprocessable Entity: 資料驗證錯誤
- 429 Too Many Requests：請求頻率超過限制
- 500 Internal Server Error：服務器內部錯誤

錯誤響應格式：

```json
{
  "detail": {
    "reason": "錯誤原因",
    "details": "錯誤詳情",
    "success": false
  }
}
```

## 注意事項

1. API 有速率限制，默認設置為每分鐘 1 次請求。
2. 創建的短網址有效期為 30 天。
3. 原始 URL 最大長度為 2048 字符。

## 開發

項目使用 VSCode 進行開發。建議安裝以下擴展：

- ms-python.python
- ms-python.vscode-pylance
- ms-python.isort
- ms-python.pylint
- sourcery.sourcery
- eamodio.gitlens
- streetsidesoftware.code-spell-checker
- eeyore.yapf

