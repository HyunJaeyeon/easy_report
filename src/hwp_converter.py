import win32com.client as win32
import os
import time
from typing import Dict, List, Tuple, Optional
from datetime import datetime


class HWPConverter:
    """HWP 파일 변환 및 필드 매핑 처리"""

    def __init__(self):
        self.hwp = None
        self.hwp_file_path = ""
        self.output_path = ""

    def detect_hwp_fields(self, hwp_file_path: str) -> List[str]:
        """HWP 파일의 모든 필드를 감지하여 리스트로 반환"""
        fields = []
        hwp = None
        
        try:
            hwp = win32.gencache.EnsureDispatch("HWPFrame.HwpObject")
            hwp.XHwpWindows.Item(0).Visible = False  # 화면에 표시하지 않음
            
            try:
                hwp.RegisterModule("FilePathCheckDLL", "FilePathCheckerModule")
            except:
                pass

            if not os.path.exists(hwp_file_path):
                raise FileNotFoundError(f"HWP 파일을 찾을 수 없습니다: {hwp_file_path}")

            hwp.Open(hwp_file_path)
            time.sleep(0.5)

            # HWP에서 필드 목록을 가져오는 방법
            # 일반적으로 사용되는 필드명들을 체크
            common_field_names = [
                # checklist.json의 id들과 매칭 가능한 필드명들
                "summary", "please_do_this", "current_status_of_company",
                "please_do_this_manager", "please_do_this_worker",
                "current_status_of_company_strengths", "current_status_of_company_improvements",
                "risk_assessment", "pre_preparation", "identify_factors", 
                "implement_countermeasures", "share_results",
                "pre_preparation_issues_and_improvements", "pre_preparation_consulting_contents",
                "identify_factors_issues_and_improvements", "identify_factors_consulting_contents",
                "implement_countermeasures_issues_and_improvements", "implement_countermeasures_consulting_contents",
                "share_results_issues_and_improvements", "share_results_consulting_contents",
                # 기타 가능한 필드들
                "company_name", "report_date", "consultant_name"
            ]

            for field_name in common_field_names:
                if hwp.MoveToField(field_name):
                    fields.append(field_name)
                    print(f"✓ 필드 발견: {field_name}")

            return fields

        except Exception as e:
            print(f"[오류] HWP 필드 감지 실패: {e}")
            return []

        finally:
            if hwp:
                try:
                    hwp.Quit()
                except:
                    pass

    def validate_field_mapping(self, hwp_file_path: str, checklist_ids: List[str]) -> Dict[str, bool]:
        """체크리스트 ID와 HWP 필드 매핑 검증"""
        hwp_fields = self.detect_hwp_fields(hwp_file_path)
        mapping_result = {}

        print("\n=== 필드 매핑 검증 ===")
        for checklist_id in checklist_ids:
            if checklist_id in hwp_fields:
                mapping_result[checklist_id] = True
                print(f"✓ {checklist_id} → HWP 필드 매칭됨")
            else:
                mapping_result[checklist_id] = False
                print(f"✗ {checklist_id} → HWP 필드 없음")

        return mapping_result

    def convert_checklist_to_hwp(self, hwp_file_path: str, company_name: str, 
                                checked_items: Dict[str, List[str]], 
                                title1_nodes: List) -> Tuple[bool, str]:
        """체크리스트 내용을 HWP 파일로 변환"""
        self.hwp = None
        
        try:
            self.hwp = win32.gencache.EnsureDispatch("HWPFrame.HwpObject")
            self.hwp.XHwpWindows.Item(0).Visible = True  # 변환 중 표시
            
            try:
                self.hwp.RegisterModule("FilePathCheckDLL", "FilePathCheckerModule")
            except:
                pass

            if not os.path.exists(hwp_file_path):
                return False, f"HWP 파일을 찾을 수 없습니다: {hwp_file_path}"

            # HWP 파일 열기
            self.hwp.Open(hwp_file_path)
            time.sleep(1)

            # 회사명 입력
            if self.hwp.MoveToField("company_name"):
                self.hwp.PutFieldText("company_name", company_name)
                print(f"✓ 회사명 입력: {company_name}")

            # 보고서 생성 날짜 입력
            if self.hwp.MoveToField("report_date"):
                current_date = datetime.now().strftime("%Y년 %m월 %d일")
                self.hwp.PutFieldText("report_date", current_date)
                print(f"✓ 보고서 날짜 입력: {current_date}")

            # 체크리스트 내용을 HWP 필드에 매핑
            success_count = 0
            total_fields = 0

            for title1 in title1_nodes:
                for title2 in title1.get_title2_children():
                    for section in title2.get_sections():
                        total_fields += 1
                        
                        # 해당 섹션의 체크된 항목들 수집
                        section_checked_items = []
                        for item in section.items:
                            item_key = f"{section.id}::{item}"
                            if item_key in checked_items.get('checked_items', []):
                                section_checked_items.append(item)

                        # HWP 필드에 내용 입력 (각 항목을 개별적으로 삽입하여 줄바꿈 보장)
                        if self.hwp.MoveToField(section.id):
                            # 필드 내용 초기화
                            self.hwp.PutFieldText(section.id, "")

                            if section_checked_items:
                                # 필드로 다시 이동하여 텍스트 삽입
                                self.hwp.MoveToField(section.id)

                                # 각 항목을 삽입하고 줄바꿈 추가
                                for idx, item in enumerate(section_checked_items):
                                    self.hwp.HAction.GetDefault("InsertText", self.hwp.HParameterSet.HInsertText.HSet)
                                    self.hwp.HParameterSet.HInsertText.Text = f"- {item}"
                                    self.hwp.HAction.Execute("InsertText", self.hwp.HParameterSet.HInsertText.HSet)

                                    # 마지막 항목이 아니면 줄바꿈 추가
                                    if idx < len(section_checked_items) - 1:
                                        self.hwp.HAction.Run("BreakPara")  # Enter 키 입력 (한 번만)

                                success_count += 1
                                print(f"✓ {section.id} 필드 업데이트 완료 ({len(section_checked_items)}개 항목)")
                            else:
                                # 체크된 항목이 없을 때
                                self.hwp.PutFieldText(section.id, "(체크된 항목 없음)")
                                success_count += 1

            # 출력 파일명 생성
            base_name = os.path.splitext(os.path.basename(hwp_file_path))[0]
            output_dir = os.path.dirname(hwp_file_path)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            self.output_path = os.path.join(output_dir, f"{base_name}_{company_name}_{timestamp}.hwp")

            # 파일 저장
            try:
                self.hwp.SaveAs(self.output_path)
                message = f"성공적으로 변환되었습니다!\n\n" \
                         f"변환된 필드: {success_count}/{total_fields}\n" \
                         f"저장 위치: {self.output_path}"
                return True, message

            except Exception as save_error:
                self.hwp.Save()  # 원본에 저장
                message = f"변환 완료 (원본 파일에 저장됨)\n\n" \
                         f"변환된 필드: {success_count}/{total_fields}\n" \
                         f"저장 실패 오류: {save_error}"
                return True, message

        except Exception as e:
            error_message = f"HWP 변환 중 오류가 발생했습니다:\n{str(e)}"
            return False, error_message

        finally:
            if self.hwp:
                try:
                    self.hwp.Quit()
                except:
                    pass

    def get_all_section_ids(self, title1_nodes: List) -> List[str]:
        """모든 섹션 ID를 추출"""
        section_ids = []
        for title1 in title1_nodes:
            for title2 in title1.get_title2_children():
                for section in title2.get_sections():
                    section_ids.append(section.id)
        return section_ids


# HWP 변환 유틸리티 함수들
def check_hwp_available() -> bool:
    """한글(HWP) 프로그램이 설치되어 있는지 확인"""
    try:
        hwp = win32.gencache.EnsureDispatch("HWPFrame.HwpObject")
        hwp.Quit()
        return True
    except:
        return False


def format_checklist_summary(title1_nodes: List, state_manager) -> str:
    """체크리스트 요약을 텍스트로 포맷팅"""
    summary_lines = []
    
    for title1 in title1_nodes:
        summary_lines.append(f"\n■ {title1.label}")
        
        for title2 in title1.get_title2_children():
            summary_lines.append(f"\n  ▶ {title2.label}")
            
            for section in title2.get_sections():
                checked_items = []
                for item in section.items:
                    if state_manager.is_item_checked(section.id, item):
                        checked_items.append(item)
                
                if checked_items:
                    summary_lines.append(f"\n    ● {section.label}")
                    for item in checked_items:
                        summary_lines.append(f"      - {item}")
    
    return "\n".join(summary_lines)