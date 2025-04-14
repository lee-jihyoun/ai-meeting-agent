import os
from dotenv import load_dotenv
from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential

# 환경 변수 로딩
load_dotenv()
key = os.getenv("AI_SERVICE_KEY")
endpoint = os.getenv("AI_SERVICE_ENDPOINT")

# DocumentAnalysisClient 초기화
document_client = DocumentAnalysisClient(
    endpoint=endpoint,
    credential=AzureKeyCredential(key)
)

# 이미지 폴더 경로 지정
image_folder = "./docs/images"  # OCR할 이미지가 들어 있는 로컬 폴더
supported_formats = [".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".pdf"]

# 폴더 내 모든 이미지 처리
for filename in os.listdir(image_folder):
    if any(filename.lower().endswith(ext) for ext in supported_formats):
        file_path = os.path.join(image_folder, filename)
        print(f"\n📄 처리 중: {filename}")

        with open(file_path, "rb") as image_file:
            poller = document_client.begin_analyze_document(
                model_id="prebuilt-read",  # OCR 모델
                document=image_file
            )
            result = poller.result()

            for page_idx, page in enumerate(result.pages):
                print(f"📄 페이지 {page_idx + 1}:")
                for line in page.lines:
                    print("🔹", line.content)
