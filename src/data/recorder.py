from astropy.io import fits
import numpy as np
import datetime
import os

class FitsRecorder:
    def __init__(self, output_dir="observations"):
        self.output_dir = output_dir
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

    def save_observation(self, data, metadata):
        """
        data: 2D Waterfall Array (Time x Frequency)
        metadata: 망원경 상태 정보 (Az, El, Center Freq 등)
        """
        # 1. 파일명 생성 (타임스탬프 기반)
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.join(self.output_dir, f"obs_{timestamp}.fits")

        # 2. HDU(Header Data Unit) 생성
        hdu = fits.PrimaryHDU(data)
        
        # 3. 헤더에 과학적 정보 주입 (나중에 분석할 때 필수!)
        hdr = hdu.header
        hdr['DATE-OBS'] = (datetime.datetime.now().isoformat(), 'Observation start time')
        hdr['INSTRUME'] = ('GEMINI-SIM-V1', 'Radio Telescope Simulator')
        hdr['FREQ-MHZ'] = (metadata.get('center_freq', 1420.4), 'Center Frequency')
        hdr['SAMPRATE'] = (metadata.get('sample_rate', 2.4e6), 'Sample Rate in Hz')
        hdr['AZIMUTH'] = (metadata.get('az', 0.0), 'Telescope Azimuth')
        hdr['ELEVATIO'] = (metadata.get('el', 0.0), 'Telescope Elevation')
        hdr['UNIT'] = ('dB', 'Power unit in decibels')

        # 4. 저장
        hdu.writeto(filename, overwrite=True)
        print(f"\n[RECORDER] Data archived: {filename}")
        return filename