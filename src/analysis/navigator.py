# src/analysis/navigator.py

import os
import glob
import shutil
from astropy.io import fits

class AstroDataNavigator:
    def __init__(self, base_dir="observations"):
        self.base_dir = base_dir
        self.sandbox_dir = os.path.join(base_dir, "sandbox")
        
        # 📂 샌드박스 내부 등급별 격리 폴더 자동 생성 (안전장치)
        os.makedirs(os.path.join(self.sandbox_dir, "tier1_clean"), exist_ok=True)
        os.makedirs(os.path.join(self.sandbox_dir, "tier2_warning"), exist_ok=True)
        os.makedirs(os.path.join(self.sandbox_dir, "tier3_rejected"), exist_ok=True)

    def navigate_and_route(self, target_subdir="milkyway"):
        """
        [Day 134 핵심] FITS 파일의 장애 이력(HW_FAILS)과 등급을 심층 분석하여
        데이터의 신뢰도 등급별로 안전하게 샌드박스 라우팅(격리 이동)을 수행합니다.
        """
        search_path = os.path.join(self.base_dir, target_subdir, "*.fits")
        file_list = glob.glob(search_path)
        
        print(f"\n🛰️ [Day 134 Navigator] 장애 감지 데이터 샌드박스 오토-네비게이터 기동")
        print(f" 📂 대상 디렉토리: {os.path.dirname(search_path)}")
        print(f" 📊 스캔 분석 대상: 총 {len(file_list)}개 FITS 파일 타겟팅 완료")
        print("=" * 80)

        if not file_list:
            print("  ⚠️ [안내] 라우팅할 대상 FITS 파일이 디렉토리에 존재하지 않습니다.")
            print("  💡 수집 파이프라인(pipeline.py)을 먼저 기동하여 원천 데이터를 확보하세요.")
            print("-" * 80)
            return

        for file_path in file_list:
            filename = os.path.basename(file_path)
            
            try:
                with fits.open(file_path) as hdul:
                    header = hdul[0].header
                    
                    # 🔍 메타데이터 정밀 추출 (Day 126 품질 & Day 133 장애 이력)
                    grade = str(header.get('QUAL_GRD', 'C')).upper()
                    snr = header.get('QUAL_SNR', 0.0)
                    hw_fails = header.get('HW_FAILS', 0)
                    
                # ----------------------------------------------------
                # 🤖 [지능형 라우팅 트리거 정책 다중 조건 스코어링]
                # ----------------------------------------------------
                if hw_fails >= 3 or 'F' in grade:
                    # 🔴 심각한 장애 과다 혹은 RFI 완전 오염 데이터 -> Tier-3 폐기 격리
                    dest_folder = os.path.join(self.sandbox_dir, "tier3_rejected")
                    tier_label = "🔴 Tier-3 (Rejected/Contaminated RFI Layer)"
                elif hw_fails > 0 or 'C' in grade:
                    # 🟡 관측 중 단선 경력이 있거나, 단순 노이즈 수준의 데이터 -> Tier-2 주의 격리
                    dest_folder = os.path.join(self.sandbox_dir, "tier2_warning")
                    tier_label = "🟡 Tier-2 (Warning/Suspicious Artifact)"
                else:
                    # 🟢 장애 0회 및 고품질 과학 데이터 -> Tier-1 초청정 마스터 백본 패스
                    dest_folder = os.path.join(self.sandbox_dir, "tier1_clean")
                    tier_label = "🟢 Tier-1 (Ultra-Clean Science Master Asset)"
                    
                # 물리적 파일 복사/이동을 통한 샌드박스 격리 수행 (시동)
                dest_path = os.path.join(dest_folder, filename)
                shutil.copy2(file_path, dest_path) # 메타데이터(시간축 등)를 온전히 유지한 채 복사
                
                print(f" 📦 [{filename}] 실시간 전수진단 리포트")
                print(f"  🔹 [품질] 과학 등급: {grade} | 신호 대 잡음비(SNR): {snr:.2f} dB")
                print(f"  🔹 [이력] 관측 중 HW 단선 트리거 횟수: {hw_fails}회")
                print(f"  ➡️  디시전 라우팅: {tier_label}")
                print("-" * 80)
                
            except Exception as e:
                print(f" ❌ [{filename}] 헤더 파싱 및 격리 중 치명적 손상 에러 발생: {e}")
                print("-" * 80)

        print(f"🎯 [네비게이션 완료] 모든 관측 데이터셋이 무결성 자격 요건에 따라 분리 격리되었습니다.")
        print(f" 📂 샌드박스 관제 센터 통합 경로: {self.sandbox_dir}")
        print("=" * 80)

if __name__ == "__main__":
    navigator = AstroDataNavigator()
    navigator.navigate_and_route(target_subdir="milkyway")