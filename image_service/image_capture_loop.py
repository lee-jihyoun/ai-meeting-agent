import time, datetime
import pyautogui
from document_intelligence import analyze_document
from blob_uploader import upload_to_blob

def capture_and_process():
    now = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"meeting_screen_{now}.png"

    # 화면 전체 캡처
    screenshot = pyautogui.screenshot()
    screenshot.save(filename)
    print(f"📸 화면 캡처: {filename}")

    # Blob 업로드
    upload_to_blob(filename)

    # Document Intelligence 분석
    analyze_document(filename)

def start_image_capture_loop(interval=60):
    print("🖼️ 이미지 캡처 루프 시작...")
    while True:
        capture_and_process()
        time.sleep(interval)

if __name__ == '__main__':
    start_image_capture_loop()
