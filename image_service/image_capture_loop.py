import time
import datetime
import pyautogui
from blob_uploader import upload_to_blob
from document_intelligence import analyze_document, summarize_result, save_summary_to_file

CAPTURE_INTERVAL = 60  # 초

def capture_screen():
    now = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"screenshot_{now}.png"
    image = pyautogui.screenshot()
    image.save(filename)
    print(f"📸 이미지 캡처됨: {filename}")
    return filename

def run_capture_loop():
    while True:
        filename = capture_screen()
        # 1. Blob 업로드 후 URL 반환(업로드 후 blob_url 반환받는 방식이어야 함)
        blob_url = upload_to_blob(filename)  # → 업로드 함수 수정 필요

        # 2. 문서 분석 → 요약
        result_json = analyze_document(blob_url)
        summary = summarize_result(result_json)

        # 3. 저장
        save_summary_to_file(summary)
        
        # 4. 다음 캡처까지 대기
        time.sleep(CAPTURE_INTERVAL)


if __name__ == '__main__':
    run_capture_loop()
