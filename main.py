from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
import requests
import json
import os

load_dotenv()

ZHIPU_API_KEY = os.getenv("ZHIPU_API_KEY")

# 做一个简单的安全检查，确保成功读取到了 Key
if not ZHIPU_API_KEY:
    raise RuntimeError("未检测到 ZHIPU_API_KEY，请检查 .env 文件配置！")

app = FastAPI(
    title="My Chatbot API",
    description="这是一个使用 Zhipu API 的聊天机器人接口示例",
    version="1.0.0"
)

#定义客户端发送的请求体格式
class ChatRequest(BaseModel):
    message: str
    model: str = "glm-5"  # 默认使用 glm-5 模型


#定义服务器返回的响应体格式
class ChatResponse(BaseModel):
    reply: str

def call_zhipu_api(messages, model="glm-5"):
    url = "https://open.bigmodel.cn/api/paas/v4/chat/completions"

    headers = {
        "Authorization": f"Bearer {ZHIPU_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": model,
        "messages": messages,
        "temperature": 1.0
    }

    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"API调用失败: {response.status_code}, {response.text}")

#创建FastAPI的post接口
@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    try:
        user_message = [
            {"role": "user", "content": request.message}
        ]
        
        api_result = call_zhipu_api(messages=user_message, model=request.model)

        bot_reply = api_result['choices'][0]['message']['content']

        return ChatResponse(reply=bot_reply)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

#根目录健康检查接口
@app.get("/")
async def root():
    return {"status": "healthy", "message": "Chatbot API 服务已成功启动!"}