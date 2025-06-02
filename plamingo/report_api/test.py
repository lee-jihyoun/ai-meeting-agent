import os
from openai import AzureOpenAI
from dotenv import load_dotenv

load_dotenv()

client = AzureOpenAI(
    api_key = os.getenv("AZURE_OPENAI_API_KEY"),   # 키
    azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT"),# https://<리소스>.openai.azure.com
    api_version  = "2024-12-01-preview"                 # 포털에 표기된 버전? 확인
)

response = client.chat.completions.create(
    model       = "plamingo-gpt-4o",      # **배포 이름(Deployment name)**
    temperature = 0.2,
    messages=[
        {"role": "system", "content": "당신은 전문 서기입니다."},
        {"role": "user",   "content": "회의록 원문을 5줄로 요약해줘."}
    ]
)

print(response.choices[0].message.content)
