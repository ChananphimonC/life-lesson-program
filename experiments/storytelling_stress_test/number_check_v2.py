"""Independent recomputation of every number in the REVISED paper-folding story (v2). Pure arithmetic with exact integers/fractions
where possible; no network. Does not import number_check.py, so it is a second implementation, not a re-run.

    python number_check_v2.py

Status labels used in the output:  [คำนวณ] arithmetic from stated inputs   [สมมติฐาน] assumed input, not verified
                                   [ประมาณ] rounded/approximate           [อ้างอิงรอง] taken from a secondary source
"""

from __future__ import annotations

import math
import sys
from fractions import Fraction

T = Fraction(1, 10_000)            # [สมมติฐาน] sheet thickness 0.1 mm, in metres
ROLL_LEN, ROLL_W = 100, Fraction(3, 10)   # [สมมติฐาน] roll 100 m x 0.30 m, same thickness as A4 sheet
MOON_MIN, MOON_MAX = 356_400, 406_700    # [อ้างอิงรอง] km, reported extremes of centre-to-centre distance
EARTH_EQ_KM = 40_075                     # [อ้างอิงรอง] equatorial circumference
PITCH_M = 105                            # [ประมาณ] common international football-pitch length (rules allow 100-110 m)


def height_m(n):
    return (2 ** n) * T


def gallivan(n):
    """[อ้างอิงรอง] minimum strip length, folding in ONE direction: (pi t / 6)(2^n+4)(2^n-1). pi kept as float."""
    return math.pi * float(T) / 6 * (2 ** n + 4) * (2 ** n - 1)


def main():
    out = sys.stdout
    out.reconfigure(encoding="utf-8")
    p = lambda s="": print(s)

    p("== 1. ความหนาหลังพับ n ครั้ง = 2^n x 0.1 mm  [คำนวณ จากสมมติฐาน 0.1 mm]")
    for n in (6, 7, 10, 20, 30, 40, 41, 42):
        h = height_m(n)
        p(f"  n={n:>2}  layers={2 ** n:>16,}  height={float(h):>16,.4f} m  ({float(h) / 1000:,.3f} km)")
    p()
    p("== 2. เปรียบเทียบภาพ (ใช้ในฉาก 3 แทนการพูดตัวเลข)")
    h20 = float(height_m(20))
    p(f"  n=20: {h20:.1f} m  vs สนามฟุตบอล {PITCH_M} m  -> {h20 / PITCH_M:.2f} เท่า [ประมาณ] 'เกือบเท่าความยาวสนามฟุตบอล'")
    for n in (30, 40, 41):
        km = float(height_m(n)) / 1000
        p(f"  n={n}: {km:,.1f} km = {km / EARTH_EQ_KM:.2f} รอบเส้นศูนย์สูตรโลก [ประมาณ]")
    p(f"  10 ครั้งขึ้นไป x1000 ทุก 10 ครั้ง: 2^10 = {2 ** 10} (1,000 ปัดจาก 1,024 -> คลาดเคลื่อน 2.4%) [ประมาณ] ใช้คำว่า 'ราวพันเท่า'")
    p()
    p("== 3. คำตอบ 42 เทียบระยะดวงจันทร์ [อ้างอิงรอง ของระยะ]")
    h41, h42 = float(height_m(41)) / 1000, float(height_m(42)) / 1000
    p(f"  41 ครั้ง {h41:,.0f} km  < ใกล้สุด {MOON_MIN:,}  -> {'ไม่ถึงเสมอ' if h41 < MOON_MIN else 'ผิด!'}")
    p(f"  42 ครั้ง {h42:,.0f} km  > ไกลสุด {MOON_MAX:,}  -> {'เกินเสมอ' if h42 > MOON_MAX else 'ผิด!'}")
    lo = MOON_MAX * 1e3 / 2 ** 42 * 1e3     # mm
    hi = MOON_MIN * 1e3 / 2 ** 41 * 1e3
    p(f"  42 เป็นคำตอบเดียวเมื่อความหนา {lo:.4f}-{hi:.4f} mm   (0.1 mm อยู่ในช่วง: {lo < 0.1 < hi})")
    p()
    p("== 4. ม้วนกระดาษ 100 m x 0.30 m พับทางเดียว [สูตร = อ้างอิงรอง; เลขคำนวณซ้ำ]")
    for n in range(8, 13):
        L = gallivan(n)
        p(f"  n={n:>2}  ต้องการอย่างน้อย {L:>8.1f} m   100 m {'พอ' if L <= ROLL_LEN else 'ไม่พอ'}"
          f"   (ส่วนเผื่อ {ROLL_LEN / L:.2f}x)" if L <= ROLL_LEN else f"  n={n:>2}  ต้องการอย่างน้อย {L:>8.1f} m   100 m ไม่พอ (ขาด {L - ROLL_LEN:.1f} m)")
    p(f"  อัตราส่วน L11/L10 = {gallivan(11) / gallivan(10):.3f}  (ต้นอนุมาน 'สี่เท่า' ถูกในทิศทาง; ค่าแท้ -> 4 เมื่อ n มาก)")
    p(f"  ความจุทฤษฎี: ที่ t=0.1mm, n=10 เหลือเผื่อ {(ROLL_LEN - gallivan(10)):.1f} m ({100 * (ROLL_LEN / gallivan(10) - 1):.1f}%) -> เผื่อน้อย ใช้ได้เฉพาะ"
      " 'ถ้ากระดาษหนา <= {:.3f} mm' ".format(0.1 * ROLL_LEN / gallivan(10)))
    t_max = 0.1 * ROLL_LEN / gallivan(10)
    p(f"  ถ้ากระดาษจริงหนากว่า {t_max:.3f} mm ม้วน 100 m จะพับไม่ถึง 10 ครั้งแม้ในอุดมคติ  [คำนวณ]")
    p(f"  ก้อนหลังพับ 10 ครั้ง (ประมาณหยาบ ไม่นับความยาวที่ใช้ที่รอยพับ): ยาว {ROLL_LEN / 2 ** 10 * 100:.1f} cm x กว้าง {float(ROLL_W) * 100:.0f} cm x หนา {float(height_m(10)) * 100:.1f} cm [ประมาณ]")
    p(f"  จำนวนชั้นกระดาษที่ผู้คนต้องช่วยยกตอนพับแรก: ความยาวพับแรก {ROLL_LEN / 2} m ต่อชั้น [คำนวณ]")
    p()
    p("== 5. พับ 42 ครั้งจริง [อ้างอิงรอง ของสูตร]")
    L42 = gallivan(42)
    ly = 9_460_730_472_580.8 * 1000
    p(f"  ต้องการอย่างน้อย {L42:.3e} m = {L42 / ly:,.0f} ปีแสง  -> 'แสนปีกว่า' (แสงเดินทางตามกระดาษ) ถูกตามลำดับขนาด [ประมาณ]")
    p()
    p("== 6. เดิมพันและฉากจบ")
    guesses = {"ต้น": 1_000_000, "ป้าเอื้อน": 500, "ลุงโชค": 80}
    for k, v in guesses.items():
        p(f"  {k:<10} ทาย {v:>9,}  ห่างจาก 42 = {abs(v - 42):,}")
    p(f"  ผู้ชนะ (ห่างน้อยสุด): {min(guesses, key=lambda k: abs(guesses[k] - 42))}   ผู้แพ้: {max(guesses, key=lambda k: abs(guesses[k] - 42))}")
    piles = [2 ** k for k in range(8)]
    p(f"  กองชามฉากจบ 1,2,4,...,128 รวม {sum(piles)} ใบ; เหลือจาก 410: {410 - sum(piles)} ใบ (< กองถัดไป {2 ** 8}) -> กองสุดท้ายเล็กกว่ากองคู่ "
      f"[คำนวณ]")
    p(f"  กอง 1..64 รวม {sum(piles[:7])} ใบ ต้นเรียงชามที่ล้างแล้วเป็นหอ")
    p()
    p("== 7. ไทม์ไลน์เรื่อง 2 (นาที)")
    p("  16:00 เริ่ม  ..  ~16:40 ลงมือพับม้วน  ..  ~17:25 พับครั้งที่ 10 สำเร็จ  ..  18:00 เปิดซอง  (ตัวเลขเวลาเป็นเรื่องแต่ง)")


if __name__ == "__main__":
    main()
