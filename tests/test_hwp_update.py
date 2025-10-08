import win32com.client as win32
from PIL import Image
import os
import time

# -------------------------
# 1. 이미지 리사이징 함수
# -------------------------
def resize_image(input_path, output_path, width_mm):
    """
    mm 단위를 픽셀로 변환해 이미지 크기 조정 (96dpi 기준)
    """
    mm_to_inch = 0.0393701
    dpi = 96  # 한글 기본 해상도
    width_px = int(width_mm * mm_to_inch * dpi)

    with Image.open(input_path) as img:
        # 비율 유지한 높이 계산
        w_percent = (width_px / float(img.size[0]))
        height_px = int((float(img.size[1]) * w_percent))
        resized_img = img.resize((width_px, height_px), Image.LANCZOS)
        resized_img.save(output_path, dpi=(96, 96))



# -------------------------
# 2. HWP 업데이트 함수
# -------------------------
def update_hwp_report():
    hwp = None
    try:
        hwp = win32.gencache.EnsureDispatch("HWPFrame.HwpObject")
        hwp.XHwpWindows.Item(0).Visible = True

        try:
            hwp.RegisterModule("FilePathCheckDLL", "FilePathCheckerModule")
        except:
            pass

        # 경로 설정
        current_dir = os.getcwd()
        hwp_file_path = os.path.join(current_dir, "report_sample.hwp")
        original_image = os.path.join(current_dir, "image_sample.jpg")
        resized_image = os.path.join(current_dir, "image_resized.jpg")
        output_path = os.path.join(current_dir, "report_updated.hwp")

        if not os.path.exists(hwp_file_path):
            print(f"[오류] HWP 파일 없음: {hwp_file_path}")
            return False
        if not os.path.exists(original_image):
            print(f"[오류] 이미지 파일 없음: {original_image}")
            return False

        # 이미지 리사이즈
        resize_image(original_image, resized_image, width_mm=32)
        print("[완료] 이미지 리사이즈 완료")

        # HWP 파일 열기
        hwp.Open(hwp_file_path)
        time.sleep(1)

        # 텍스트 삽입
        if hwp.PutFieldText("text1", "안녕하세요. 테스트 성공!"):
            print("[완료] text1 필드에 텍스트 입력")
        else:
            print("[경고] text1 필드를 찾을 수 없음")

        # 이미지 삽입
        if hwp.MoveToField("image1"):
            hwp.InsertPicture(resized_image, Embedded=True)
            print("[완료] image1 필드에 이미지 삽입됨")
        else:
            print("[경고] image1 필드를 찾을 수 없음")

        # 저장
        try:
            hwp.SaveAs(output_path)
            print(f"[완료] 저장됨: {output_path}")
        except:
            hwp.Save()
            print("[주의] 저장 실패, 원본에 덮어씀")

        return True

    except Exception as e:
        print(f"[오류] 작업 실패: {e}")
        return False

    finally:
        if hwp:
            try:
                hwp.Quit()
            except:
                pass


# -------------------------
# 3. 필드 존재 확인
# -------------------------
def check_hwp_fields():
    hwp = None
    try:
        hwp = win32.gencache.EnsureDispatch("HWPFrame.HwpObject")
        try:
            hwp.RegisterModule("FilePathCheckDLL", "FilePathCheckerModule")
        except:
            pass

        hwp_file_path = os.path.join(os.getcwd(), "report_sample.hwp")
        hwp.Open(hwp_file_path)
        time.sleep(1)

        print("=== 필드 확인 ===")
        if hwp.MoveToField("text1"):
            print("✓ text1 필드 찾음")
        else:
            print("✗ text1 필드 없음")

        if hwp.MoveToField("image1"):
            print("✓ image1 필드 찾음")
        else:
            print("✗ image1 필드 없음")

    except Exception as e:
        print(f"[오류] 필드 확인 실패: {e}")
    finally:
        if hwp:
            try:
                hwp.Quit()
            except:
                pass


# -------------------------
# 4. 실행
# -------------------------
if __name__ == "__main__":
    print("HWP 필드 확인")
    check_hwp_fields()

    print("\nHWP 보고서 자동 업데이트 시작")
    success = update_hwp_report()

    if success:
        print("✅ 모든 작업 완료")
    else:
        print("❌ 작업 중 오류 발생")
