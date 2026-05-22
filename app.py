import os
import torch
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from transformers import pipeline

# Создаем сервер на FastAPI
app = FastAPI(title="Cortana Llama Cloud Server")

class ChatRequest(BaseModel):
    text: str

print("Инициализация локальной модели TinyLlama на сервере...")
try:
    chatbot = pipeline(
        "text-generation",
        model="TinyLlama/TinyLlama-1.1B-Chat-v1.0",
        torch_dtype=torch.float32,
        device_map={"": "cpu"} # Работа на бесплатном CPU-сервере
    )
    # Полностью сбрасываем старый конфиг модели, чтобы убрать конфликты
    chatbot.model.generation_config = None
    print("Нейросеть успешно загружена в облако!")
except Exception as e:
    print(f"Критическая ошибка при запуске ИИ: {e}")
    chatbot = None

@app.get("/")
def read_root():
    return {"status": "online", "message": "Сервер Кортаны работает идеально!"}

@app.post("/chat")
def chat_endpoint(request_data: ChatRequest):
    if not chatbot:
        raise HTTPException(status_code=500, detail="Модель ИИ не инициализирована на сервере.")
    
    user_text = request_data.text.strip()
    if not user_text:
        raise HTTPException(status_code=400, detail="Текст запроса не может быть пустым.")

    # Промпт для ИИ
    messages = [
        {
            "role": "system",
            "content": "You are Cortana, a helpful, polite, intelligent AI assistant. Always respond in Russian brief.",
        },
        {"role": "user", "content": user_text},
    ]
    prompt = chatbot.tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)

    # Генерация ответа в облаке
    outputs = chatbot(
        prompt,
        max_new_tokens=100, 
        do_sample=True,
        temperature=0.6,
        top_p=0.9,
        pad_token_id=chatbot.tokenizer.eos_token_id
    )

    full_text = outputs["generated_text"]
    response = full_text.split("<|assistant|>")[-1].strip()

    return {"response": response}

if __name__ == "__main__":
    import uvicorn
    # Автоматически берем порт от Render
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
