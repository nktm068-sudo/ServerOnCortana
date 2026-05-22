import os
import shutil
import torch
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from transformers import pipeline, AutoModelForCausalLM, AutoTokenizer

app = FastAPI(title="Nova Cloud Server")

MODEL_ID = "Qwen/Qwen2.5-0.5B-Instruct"
CACHE_DIR = "./model_cache"
ZIP_PATH = "./nova_model.zip"

class ChatRequest(BaseModel):
    text: str

print("Инициализация легкой модели Qwen на сервере...")
try:
    tokenizer = AutoTokenizer.from_pretrained(MODEL_ID, cache_dir=CACHE_DIR)
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_ID, 
        torch_dtype=torch.float32, 
        device_map={"": "cpu"},
        cache_dir=CACHE_DIR
    )
    
    chatbot = pipeline("text-generation", model=model, tokenizer=tokenizer)
    print("Нейросеть успешно загружена в облако Render!")
    
    if not os.path.exists(ZIP_PATH):
        print("Создаю архив модели для скачивания клиентами...")
        shutil.make_archive("./nova_model", 'zip', CACHE_DIR)
        print("Архив успешно создан!")
        
except Exception as e:
    print(f"Критическая ошибка при запуске ИИ: {e}")
    chatbot = None

@app.get("/")
def read_root():
    return {"status": "online", "message": "Сервер Новы на Qwen работает!"}

@app.post("/chat")
def chat_endpoint(request_data: ChatRequest):
    if not chatbot:
        raise HTTPException(status_code=500, detail="Модель ИИ не инициализирована на сервере.")
    
    user_text = request_data.text.strip()
    if not user_text:
        raise HTTPException(status_code=400, detail="Текст запроса не может быть пустым.")

    messages = [
        {"role": "system", "content": "You are Nova, a helpful, polite, intelligent AI assistant. Always respond in Russian brief. Never call yourself Cortana."},
        {"role": "user", "content": user_text},
    ]
    prompt = chatbot.tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)

    outputs = chatbot(
        prompt,
        max_new_tokens=100, 
        do_sample=True,
        temperature=0.6,
        top_p=0.9,
        pad_token_id=chatbot.tokenizer.eos_token_id
    )

    full_text = outputs["generated_text"]
    response = full_text.split("<|im_start|>assistant\n")[-1].replace("<|im_end|>", "").strip()

    return {"response": response}

@app.get("/download-model")
def download_model():
    if not os.path.exists(ZIP_PATH):
        raise HTTPException(status_code=404, detail="Архив модели еще генерируется сервером.")
    return FileResponse(
        path=ZIP_PATH, 
        filename="nova_model.zip", 
        media_type="application/zip"
    )

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
