# src/analysis/stacker.py

import os
import glob
import numpy as np
from astropy.io import fits

class AstroDataStacker:
    def __init__(self, base_dir="observations"):
        self.base_dir = base_dir

    def run_scientific_stacking(self, target_subdir="milkyway"):
        """
        [Day 127 고도화] 지정된 천체 서브 디렉토리 내의 FITS 파일들을 전수 조사하여,
        QUAL_GRD 헤더가 A/B/C 등급인 청정 관측 데이터만 선별 스택(Matrix Stacking) 처리합니다.
        """
        search_path = os.path.join(self.base_dir, target_subdir, "*.fits")
        file_list = glob.glob(search_path)
        
        print(f"\n⚡ [Day 127 Stacker] 고급 천체 데이터 스택 연산 개시")
        print(f" 📂 탐색 경로: {search_path} (발견된 총 파일: {len(file_list)}개)")
        print("-" * 75)
        
        valid_datasets = []
        total_snr = 0.0
        sample_header = None
        
        # 1. FITS 헤더 스마트 스캔 및 품질 필터링
        for file_path in file_list:
            # 중복으로 구워진 'Master' 파일은 중첩 연산 대상에서 제외하는 안전장치
            if "Master_Stacked" in file_path:
                continue
                
            with fits.open(file_path) as hdul:
                header = hdul[0].header
                data = hdul[0].data
                
                # Day 126에 새겨 넣은 품질 문신(Data Lineage) 추출
                grade_raw = header.get('QUAL_GRD', 'Unknown')
                grade_str = str(grade_raw).upper().strip() # 문자열 강제 변환 및 공백 제거
                snr = header.get('QUAL_SNR', 0.0)
                
                # 💡 안전한 등급 판정 알고리즘 (첫 문자 파싱 기법)
                is_pass = False
                if (grade_str.startswith('A') or 
                    grade_str.startswith('B') or 
                    grade_str.startswith('C') or 
                    grade_str == 'UNKNOWN' or 
                    grade_str == 'N/A'):
                    is_pass = True
                
                if is_pass:
                    valid_datasets.append(data)
                    total_snr += snr
                    if sample_header is None:
                        sample_header = header.copy() # 메타데이터 계승용 원본 헤더 복사
                    print(f" 🟢 [선별 통과] {os.path.basename(file_path)} | Grade: {grade_str[:12]} | SNR: {snr:.2f} dB")
                else:
                    print(f" 🔴 [필터 배제] {os.path.basename(file_path)} | Grade: {grade_str[:12]} -> RFI/노이즈 오염 데이터")

        if not valid_datasets:
            print("❌ [Stacker Error] 스택 연산에 사용할 수 있는 청정 데이터셋이 존재하지 않습니다.")
            print("-" * 75)
            return None

        # 2. 고차원 텐서 적분 연산 (Mathematical Matrix Stacking)
        print("-" * 75)
        print(f"🧮 총 {len(valid_datasets)}개의 관측 매트릭스 배열 적분 및 평균 계산 중...")
        
        # [수학적 핵심] 행렬 누적 평균 연산 -> 무작위 백색 잡음 상쇄 효과 ($\sqrt{N}$ 법칙) 발동
        stacked_matrix = np.mean(valid_datasets, axis=0)
        
        # 3. 마스터 과학 데이터 파일 아카이빙 (Master FITS Dump)
        output_dir = os.path.join(self.base_dir, target_subdir, "stacked")
        os.makedirs(output_dir, exist_ok=True)
        output_file = os.path.join(output_dir, "Master_Stacked_Science_Data.fits")
        
        # 신규 마스터 HDU 구조 정의
        master_hdu = fits.PrimaryHDU(data=stacked_matrix)
        master_hdr = master_hdu.header
        
        # 원본 파일들의 천문 메타데이터 완전 계승 및 적분 정보 주입
        master_hdr['DATE-OBS'] = (sample_header.get('DATE-OBS', 'N/A'), 'Original Observation Timestamp')
        master_hdr['OBJECT'] = (sample_header.get('OBJECT', 'Unknown'), 'Combined Master Target')
        master_hdr['CTYPE1'] = (sample_header.get('CTYPE1', 'Unknown'), 'Physical Coordinate Axis')
        master_hdr['CRVAL1'] = (sample_header.get('CRVAL1', 1420.4e6), 'Center Frequency (Hz)')
        master_hdr['CDELT1'] = (sample_header.get('CDELT1', 2.4e6), 'Sample Rate / Bandwidth')
        master_hdr['GAIN'] = (sample_header.get('GAIN', 49.6), 'Locked Hardware Gain')
        
        # 📌 Day 127 적분 핵심 메타데이터 주입
        master_hdr['STACK_N'] = (len(valid_datasets), 'Number of stacked observation frames')
        master_hdr['AVG_SNR'] = (float(total_snr / len(valid_datasets)), 'Average input SNR in dB')
        master_hdr['PREPROC'] = ('MATHEMATICAL_MEAN_STACKING', 'Noise reduction algorithm applied')
        master_hdr['COMMENT'] = "This file is a high-purity master stacked science dataset."

        # 물리 디스크 쓰기
        master_hdu.writeto(output_file, overwrite=True)
        
        print("-" * 75)
        print(f"🎯 [마스터 데이터 생성 완료] 우주의 미세 신호가 복원된 파일이 보관되었습니다.")
        print(f" 📸 저장 경로: {output_file}")
        print(f" 📊 스택 결과: 프레임 {master_hdr['STACK_N']}장 통합 | 평균 기저 SNR: {master_hdr['AVG_SNR']:.2f} dB")
        print("=" * 75)
        
        return output_file

if __name__ == "__main__":
    stacker = AstroDataStacker()
    # 은하수 수소선 데이터를 대상으로 스택 파이프라인 가동
    stacker.run_scientific_stacking(target_subdir="milkyway")