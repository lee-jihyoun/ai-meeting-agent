# 외부 API 호출용 모듈
import requests
# 환경변수 사용을 위한 os 모듈
import os
# 분석 상태 확인을 위한 대기 시간 처리
import time
# datetime 사용을 위한 모듈 (파일에 저장 시 날짜 기록용)
import datetime

# TODO : .env에서 값을 받아오도록 처리 필요 
# Azure Document Intelligence 설정 (엔드포인트와 키)
AZURE_FORM_ENDPOINT = os.getenv("AZURE_FORM_ENDPOINT")  # 예: https://<resource>.cognitiveservices.azure.com/
AZURE_FORM_KEY = os.getenv("AZURE_FORM_KEY")

# 문서 분석 요청 함수 (Blob Storage에 저장된 이미지의 URL을 분석)
def analyze_document(blob_url):
    # 문서 분석 요청 URL 구성 (prebuilt-document 모델 사용)
    analyze_url = f"{AZURE_FORM_ENDPOINT}/formrecognizer/documentModels/prebuilt-document:analyze?api-version=2023-07-31"
    # 요청 헤더 (API 키 포함)
    headers = {
        "Content-Type": "application/json",
        "Ocp-Apim-Subscription-Key": AZURE_FORM_KEY
    }
    # 요청 바디 (분석할 Blob 이미지의 URL)
    data = {
        "urlSource": blob_url
    }

    print(f"📤 문서 분석 요청: {blob_url}")
    # 분석 요청 전송 (비동기 방식, 202 Accepted 응답 예상)
    response = requests.post(analyze_url, headers=headers, json=data)
    if response.status_code != 202:
        raise Exception(f"❌ 분석 요청 실패: {response.status_code} - {response.text}")
    
    # 응답 헤더에서 작업 상태 확인 URL 추출
    operation_location = response.headers["operation-location"]
    print("⏳ 분석 대기중...")

    # 분석 완료 대기(분석이 완료될 때까지 주기적으로 상태 확인)
    while True:
        result = requests.get(operation_location, headers=headers)
        result_json = result.json()
        status = result_json.get("status")

        # 분석이 성공 또는 실패하면 반복 종료
        if status in ["succeeded", "failed"]:
            break
        # 아직 분석 중이면 3초 대기 후 재시도
        time.sleep(3)

    # 실패한 경우 예외 발생
    if status == "failed":
        raise Exception("❗ 문서 분석 실패")
    
    print("✅ 분석 완료")
    # 성공한 분석 결과 반환
    return result_json

# 분석 결과에서 텍스트 요약 추출
def summarize_result(result_json):
    try:
        # 분석 결과에서 페이지 단위 추출
        pages = result_json["analyzeResult"]["pages"]
        summary = []
        # 각 페이지의 텍스트 라인 추출
        for page in pages:
            if "lines" in page:
                lines = [line["content"] for line in page["lines"]]
                summary.extend(lines)
        # 상위 10줄을 요약으로 반환
        return "\n".join(summary[:10])  # 상위 10줄 요약
    except Exception as e:
        print(f"⚠️ 요약 실패: {e}")
        return "요약 불가"
    
# 요약 결과를 파일로 저장하고 서버에 알리는 함수
def save_summary_to_file(summary, output_path="summary.txt"):
    # 요약 내용을 파일에 저장
    with open(output_path, "a", encoding="utf-8") as f:
        # 날짜 기록
        f.write(f"\n\n📅 {datetime.datetime.now()}\n")
        # 요약 내용 저장
        f.write(summary)
        # 구분선 추가
        f.write("\n" + "="*50 + "\n")
    print(f"💾 요약 저장됨: {output_path}")

    # Flask 서버에 run_summary API 호출 (자동 이메일 발송 등 처리)
    try:
        response = requests.post("http://localhost:5000/run_summary", json={
            "filename": output_path
        })
        if response.status_code == 200:
            print("📨 서버에 요약 전송 및 이메일 발송 완료!")
        else:
            print(f"⚠️ 서버 응답 오류: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ 서버 통신 실패: {e}")


# 테스트 실행 (직접 실행 시)
if __name__ == "__main__":
    # 테스트용 이미지 파일 URL (실제 Blob Storage URL로 변경 필요)
    test_url = "https://<your-blob-url>.blob.core.windows.net/container/image.png"
    # 문서 분석 수행
    result = analyze_document(test_url)
    # 요약 결과 출력
    print(summarize_result(result))












