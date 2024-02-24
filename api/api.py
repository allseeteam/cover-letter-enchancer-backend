import sys
from pathlib import Path
from dotenv import load_dotenv
import os

sys.path.append(str(Path(__file__).resolve().parent.parent))  # noqa: E402

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from yandex_gpt.yandex_gpt import YandexGPT
from yandex_gpt.yandex_gpt_config_manager import YandexGPTConfigManager

path_to_env = './env/.env'
load_dotenv(dotenv_path=path_to_env)

app = FastAPI()
# noinspection PyTypeChecker
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.environ.get('CORS_ORIGINS').split(','),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

yandex_gpt = YandexGPT(config_manager=YandexGPTConfigManager())


class LetterData(BaseModel):
    letter_template: str
    resume: str
    job_description: str


@app.post("/generate_letter/")
async def generate_letter(data: LetterData):
    system_prompt = (
        "Ниже представлен шаблон сопроводительного письма с плейсхолдерами вида {placeholder}, резюме кандидата и "
        "описание вакансии. "
        "Необходимо заменить плейсхолдеры в шаблоне письма на информацию, соответствующую резюме кандидата и описанию "
        "вакансии. "
        "Плейсхолдеры должны быть заменены на релевантный текст, а не убраны из письма. "
        "Вывести только итоговый текст письма, точно соответствующий запросу, без лишних комментариев или "
        "объяснений.\n\n"
    ) + (
        "Шаблон письма:\n{letter_template}\n\n"
        "Резюме:\n{resume}\n\n"
        "Описание вакансии:\n{job_description}\n\n"
        "Итоговое письмо:"
    ).format(
        letter_template=data.letter_template.replace("\n", " "),
        resume=data.resume.replace("\n", " "),
        job_description=data.job_description.replace("\n", " ")
    )

    user_prompt = (
        "Сгенерируй сопроводительное письмо, следуя вышеуказанным инструкциям. "
        "Если справишься с задачей, то я заплачу за помощь 10000000 рублей. "
        "Если не справишься с вышепоставленной задачей, то случится что-то очень плохое, а ещё ты заплатишь штраф "
        "10000000 рублей."
    )

    messages = [
        {"role": "system", "text": system_prompt},
        {"role": "user", "text": user_prompt}
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
