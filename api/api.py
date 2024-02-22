import sys
from pathlib import Path
import os

sys.path.append(str(Path(__file__).resolve().parent.parent))  # noqa: E402

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from yandex_gpt.yandex_gpt import YandexGPT


app = FastAPI()
# noinspection PyTypeChecker
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv(
        'CORS_ORIGINS',
        'http://localhost:3000'
    ).split(','),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

yandex_gpt = YandexGPT(
    yandex_cloud_config_file_path='config/yandex_cloud.yaml',
    yandex_gpt_key_file_path='keys/yandex_authorization_key.json'
)


class LetterData(BaseModel):
    letter_template: str
    resume: str
    job_description: str


@app.post("/generate_letter/")
async def generate_letter(data: LetterData):
    messages = [
        {
            "role": "system",
            "text": "Замени {***} в шаблоне письма на релевантные значения с учётом резюме и описания вакансии."
                    "В качестве ответа дай ТОЛЬКО модифицированный текст письма, без дополниельных комментариев."
        },
        {
            "role": "user",
            "text": f"Шаблон письма: {data.letter_template}"
                    f"\n"
                    f"Резюме: {data.resume}"
                    f"\n"
                    f"Описание вакансии: {data.job_description}"
        }
    ]
    try:
        response = yandex_gpt.send_completion_request(
            messages=messages,
            temperature=0.0
        )
        generated_text = response['result']['alternatives'][0]['message']['text']
        return {"generated_letter": generated_text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
