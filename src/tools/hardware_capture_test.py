# src/tools/hardware_capture_test.py
"""
RTL-SDR V4 실물 하드웨어 캡처 검증 스크립트.

목적: SDRFactory가 진짜 실물 하드웨어를 열었는지, 아니면 VirtualSDR로
조용히 넘어갔는지 절대 헷갈릴 수 없게 만드는 것.

주의(중요): SDRFactory.get_sdr(mode="real")은 "패키지(pyrtlsdr)는 설치돼
있는데 장치 연결 자체가 실패"한 경우에만 예외를 던집니다. pyrtlsdr 패키지가
아예 설치 안 되어 있으면 mode="real"을 줘도 예외 없이 조용히 VirtualSDR을
반환합니다 (sdr_interface.py의 `if mode in [...] and HAS_REAL_SDR:` 가드
때문). 그래서 이 스크립트는 예외 처리만 믿지 않고, 반환된 객체가 실제로
VirtualSDR의 인스턴스인지 직접 검사하는 걸 진짜 방어선으로 씁니다.

3가지 캡처 시나리오:
  1. 안테나 연결 상태 (기본: 1420.4 MHz, HI 라인 대역)
  2. 안테나 분리/터미네이터 (동일 대역)
  3. FM 방송 대역 (88~108 MHz 사이, 기본 98 MHz)

각 캡처는 평균 스펙트럼(dB)과 통계(평균/표준편차/최대값/최대 위치)를
npz 파일로 저장하고, matplotlib이 있으면 비교 그래프도 남깁니다.
"""
import os
import sys
import time
import numpy as np

# 프로젝트 루트를 sys.path에 추가 (어디서 실행해도 src.* import가 되도록)
_PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from src.signal.sdr_interface import SDRFactory, SignalProcessor, VirtualSDR, HAS_REAL_SDR


def confirm_real_hardware(sample_rate, center_freq):
    """실물 하드웨어를 명시적으로 요구하고, 진짜 실물인지 이중으로 확인.
    실물이 아니면 VirtualSDR로 조용히 넘어가지 않고 여기서 즉시 중단합니다."""
    print("=" * 72)
    print("🔌 [하드웨어 연결 시도] mode='real' 명시 - 실패 시 즉시 중단됩니다")
    print(f"   pyrtlsdr 패키지 설치 여부(HAS_REAL_SDR) = {HAS_REAL_SDR}")
    print("=" * 72)

    try:
        sdr = SDRFactory.get_sdr(mode="real", sample_rate=sample_rate, center_freq=center_freq)
    except Exception as e:
        print()
        print("╔" + "═" * 70 + "╗")
        print("║  ❌ 실물 RTL-SDR 하드웨어 연결 실패 (장치 오픈 중 예외 발생)          ║")
        print("║     VirtualSDR로 넘어가지 않고 여기서 중단합니다.                    ║")
        print("╚" + "═" * 70 + "╝")
        print(f"원인: {e}")
        sys.exit(1)

    # 💡 진짜 방어선: 예외가 안 났어도 VirtualSDR일 수 있음 (pyrtlsdr 미설치 시)
    if isinstance(sdr, VirtualSDR):
        print()
        print("╔" + "═" * 70 + "╗")
        print("║  ⚠️  VirtualSDR이 반환됨 - 실물 하드웨어 아닙니다!                   ║")
        print("║     (예외는 안 났지만 실제로는 가상 SDR로 조용히 폴백된 상태)         ║")
        if not HAS_REAL_SDR:
            print("║     원인: pyrtlsdr 패키지가 설치되어 있지 않습니다.                  ║")
            print("║     -> pip install pyrtlsdr 로 설치 후 다시 시도하세요.              ║")
        else:
            print("║     원인: 패키지는 있으나 장치가 감지되지 않았을 가능성이 높습니다.   ║")
        print("╚" + "═" * 70 + "╝")
        sys.exit(1)

    print()
    print("╔" + "═" * 70 + "╗")
    print(f"║  ✅ 실물 하드웨어 확인됨: {type(sdr).__name__:<44}║")
    print("╚" + "═" * 70 + "╝")
    return sdr


def capture_and_analyze(sdr, label, center_freq, num_samples=8192, avg_count=20):
    """center_freq로 튜닝 후 스펙트럼을 avg_count번 캡처해서 평균/통계 산출"""
    print(f"\n📡 [{label}] 캡처 시작 (중심주파수={center_freq/1e6:.3f} MHz, {avg_count}회 평균)")

    try:
        sdr.center_freq = center_freq
    except Exception as e:
        print(f"  ⚠️ center_freq 설정 실패: {e} (기존 주파수로 계속 진행)")

    time.sleep(0.2)  # 튜닝 안정화 대기

    spectra = []
    for _ in range(avg_count):
        samples = sdr.read_samples(num_samples)
        psd = SignalProcessor.get_power_spectrum(samples)
        db = 10 * np.log10(psd + 1e-12)
        spectra.append(db)

    avg_spectrum = np.mean(spectra, axis=0)
    stats = {
        "label": label,
        "center_freq_mhz": center_freq / 1e6,
        "mean_db": float(np.mean(avg_spectrum)),
        "std_db": float(np.std(avg_spectrum)),
        "max_db": float(np.max(avg_spectrum)),
        "max_db_bin": int(np.argmax(avg_spectrum)),
    }
    print(f"  결과: mean={stats['mean_db']:.2f}dB  std={stats['std_db']:.2f}dB  "
          f"max={stats['max_db']:.2f}dB (bin {stats['max_db_bin']})")

    return avg_spectrum, stats


def main():
    OUTPUT_DIR = r"D:\radio-telescope-simulator설명\hardware_test_results"
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    timestamp = time.strftime("%Y%m%d_%H%M%S")

    HI_FREQ = 1420.4e6
    FM_FREQ = 98.0e6  # 88~108MHz FM 대역 사이 값
    SAMPLE_RATE = 2.4e6

    sdr = confirm_real_hardware(sample_rate=SAMPLE_RATE, center_freq=HI_FREQ)

    # 명시적 게인 고정 (프로젝트 관례값)
    try:
        sdr.gain = "auto"
    except Exception:
        pass

    results = {}

    input("\n👉 [1/3] 안테나를 연결한 상태로 준비하고 Enter를 누르세요...")
    spec1, stats1 = capture_and_analyze(sdr, "1_ANTENNA_CONNECTED", HI_FREQ)
    results["1_ANTENNA_CONNECTED"] = (spec1, stats1)

    input("\n👉 [2/3] 안테나를 뽑거나 터미네이터로 막고 Enter를 누르세요...")
    spec2, stats2 = capture_and_analyze(sdr, "2_ANTENNA_DISCONNECTED", HI_FREQ)
    results["2_ANTENNA_DISCONNECTED"] = (spec2, stats2)

    input("\n👉 [3/3] FM 대역(88-108MHz) 테스트입니다. 안테나 연결 상태에서 Enter를 누르세요...")
    spec3, stats3 = capture_and_analyze(sdr, "3_FM_BAND", FM_FREQ)
    results["3_FM_BAND"] = (spec3, stats3)

    # 1. 원본 데이터 저장
    npz_path = os.path.join(OUTPUT_DIR, f"hw_capture_test_{timestamp}.npz")
    np.savez(
        npz_path,
        spec_antenna=spec1, spec_terminated=spec2, spec_fm=spec3,
        stats_antenna=stats1, stats_terminated=stats2, stats_fm=stats3,
    )
    print(f"\n💾 원본 스펙트럼 저장: {npz_path}")

    # 2. 비교 요약 콘솔 출력
    print("\n" + "=" * 72)
    print("📊 [비교 요약]")
    print("=" * 72)
    print(f"{'시나리오':<28} {'평균(dB)':>10} {'표준편차':>10} {'최대(dB)':>10}")
    for key, (_, s) in results.items():
        print(f"{key:<28} {s['mean_db']:>10.2f} {s['std_db']:>10.2f} {s['max_db']:>10.2f}")

    diff = stats1["mean_db"] - stats2["mean_db"]
    print(f"\n안테나 연결 vs 미연결 평균 dB 차이: {diff:+.2f} dB")
    if abs(diff) < 0.5:
        print("⚠️ 차이가 거의 없습니다 - 안테나가 실제로 신호에 영향을 주는지 재확인 필요")
    else:
        print("✅ 안테나 연결 여부에 따라 유의미한 차이가 관측됩니다")

    # 3. 그래프 저장 (matplotlib 있을 때만)
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        plt.figure(figsize=(12, 6))
        plt.plot(spec1, label="1. Antenna Connected", alpha=0.85)
        plt.plot(spec2, label="2. Antenna Disconnected/Terminated", alpha=0.85)
        plt.xlabel("FFT bin")
        plt.ylabel("Power (dB)")
        plt.title(f"RTL-SDR V4 Real Hardware Capture Comparison ({HI_FREQ/1e6:.1f} MHz)")
        plt.legend()
        plt.grid(alpha=0.3)
        cmp_path = os.path.join(OUTPUT_DIR, f"hw_capture_compare_{timestamp}.png")
        plt.savefig(cmp_path, dpi=150)
        plt.close()
        print(f"💾 비교 그래프 저장: {cmp_path}")

        plt.figure(figsize=(12, 6))
        plt.plot(spec3, color="orange")
        plt.xlabel("FFT bin")
        plt.ylabel("Power (dB)")
        plt.title(f"FM Band Capture ({FM_FREQ/1e6:.1f} MHz)")
        plt.grid(alpha=0.3)
        fm_path = os.path.join(OUTPUT_DIR, f"hw_capture_fm_{timestamp}.png")
        plt.savefig(fm_path, dpi=150)
        plt.close()
        print(f"💾 FM 대역 그래프 저장: {fm_path}")
    except ImportError:
        print("(matplotlib 없어서 그래프는 건너뜁니다 - npz 파일엔 데이터가 남아있습니다)")


if __name__ == "__main__":
    main()