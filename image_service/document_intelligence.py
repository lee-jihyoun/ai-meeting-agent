import requests
import os
import time

# TODO : .env에서 값을 받아오도록 처리 필요
# Document Intelligence 설정
AZURE_FORM_ENDPOINT = os.getenv("AZURE_FORM_ENDPOINT")  # 예: https://<resource>.cognitiveservices.azure.com/
AZURE_FORM_KEY = os.getenv("AZURE_FORM_KEY")

def analyze_document(blob_url):
    analyze_url = f"{AZURE_FORM_ENDPOINT}/formrecognizer/documentModels/prebuilt-document:analyze?api-version=2023-07-31"
    headers = {
        "Content-Type": "application/json",
        "Ocp-Apim-Subscription-Key": AZURE_FORM_KEY
    }

    data = {
        "urlSource": blob_url
    }

    print(f"📤 문서 분석 요청: {blob_url}")
    response = requests.post(analyze_url, headers=headers, json=data)
    if response.status_code != 202:
        raise Exception(f"❌ 분석 요청 실패: {response.status_code} - {response.text}")
    
    operation_location = response.headers["operation-location"]
    print("⏳ 분석 대기중...")

    # 분석 완료 대기
    while True:
        result = requests.get(operation_location, headers=headers)
        result_json = result.json()
        status = result_json.get("status")

        if status in ["succeeded", "failed"]:
            break
        time.sleep(3)

    if status == "failed":
        raise Exception("❗ 문서 분석 실패")
    
    print("✅ 분석 완료")
    return result_json

def summarize_result(result_json):
    try:
        pages = result_json["analyzeResult"]["pages"]
        summary = []
        for page in pages:
            if "lines" in page:
                lines = [line["content"] for line in page["lines"]]
                summary.extend(lines)
        return "\n".join(summary[:10])  # 상위 10줄 요약
    except Exception as e:
        print(f"⚠️ 요약 실패: {e}")
        return "요약 불가"

def save_summary_to_file(summary, output_path="summary.txt"):
    with open(output_path, "a", encoding="utf-8") as f:
        f.write(f"\n\n📅 {datetime.datetime.now()}\n")
        f.write(summary)
        f.write("\n" + "="*50 + "\n")
    print(f"💾 요약 저장됨: {output_path}")


if __name__ == "__main__":
    test_url = "https://<your-blob-url>.blob.core.windows.net/container/image.png"
    result = analyze_document(test_url)
    print(summarize_result(result))












