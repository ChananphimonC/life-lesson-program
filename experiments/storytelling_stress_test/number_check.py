"""Every number used in the paper-folding story, computed (not recalled). Pure arithmetic, no network.

    python number_check.py            -> markdown tables (also what STRESS_TEST_SCRIPTS.md embeds)

Assumption (stated, NOT verified against any source): one sheet is T_MM = 0.1 mm thick, i.e. a 500-sheet ream measures 50 mm.
Moon distances are the figures reported by the pages read on 2026-11-03 (see STRESS_TEST_EVALUATION.md for status):
  mean ~384,400 km; average perigee 363,300 km; average apogee 405,507 km; reported ranges 356,400-370,400 and 404,000-406,700 km.
"""

from __future__ import annotations

import math
import sys

T_MM = 0.1
MOON_MEAN, MOON_PERIGEE_AVG, MOON_APOGEE_AVG = 384_400.0, 363_300.0, 405_507.0
MOON_MIN, MOON_MAX = 356_400.0, 406_700.0
LIGHT_YEAR_M = 9_460_730_472_580.8 * 1000
ROLL_M = 60.0


def height_m(n, t_mm=T_MM):
    return (2 ** n) * t_mm / 1000.0


def min_length_m(n, t_mm=T_MM):
    """Gallivan: L = (pi*t/6)(2^n+4)(2^n-1), folding in one direction, L and t in the same unit."""
    t = t_mm / 1000.0
    return math.pi * t / 6 * (2 ** n + 4) * (2 ** n - 1)


def fmt_len(m):
    if m < 1:
        return f"{m * 1000:.1f} mm"
    if m < 1000:
        return f"{m:,.1f} m"
    return f"{m / 1000:,.1f} km"


def tables():
    out = []
    out.append(f"**สมมติฐานความหนา: {T_MM} มม. ต่อแผ่น** (ปึก 500 แผ่น = 50 มม.) ไม่ได้ตรวจจากแหล่งใด เป็นค่าที่ผู้ผลิตต้องวัดจากปึกจริง\n")
    out.append("| พับกี่ครั้ง | จำนวนชั้น | ความหนา (คำนวณ) | ใช้ในเรื่อง |")
    out.append("|---|---|---|---|")
    uses = {6: "ฉาก 2: ต้นวัดก้อน ~6.4 มม.", 7: "ฉาก 1–2: พับได้แค่นี้ด้วยมือ วัด ~12.8 มม.", 10: "ฉาก 4: ก้อนหนา ~10 ซม.",
            20: "ฉาก 3: สายว่าว 105 ม. ที่ประตูวัด", 30: "ฉาก 3: ต้นคิดว่า 'ร้อยกิโล'", 40: "ฉาก 3: 'แสนกิโล'",
            41: "ฉาก 5: 'สองแสนสองหมื่น'", 42: "คำตอบในซอง"}
    for n in (6, 7, 10, 20, 30, 40, 41, 42):
        out.append(f"| {n} | {2 ** n:,} | {fmt_len(height_m(n))} | {uses[n]} |")
    out.append("")
    h41, h42 = height_m(41) / 1000, height_m(42) / 1000
    out.append("**ตรวจว่า 42 เป็นคำตอบเดียวไม่ว่าดวงจันทร์อยู่ตรงไหน (t = 0.1 มม.):**\n")
    out.append("| เงื่อนไข | ความสูง (กม.) | เทียบกับดวงจันทร์ |")
    out.append("|---|---|---|")
    out.append(f"| 41 ครั้ง | {h41:,.0f} | ต่ำกว่าระยะใกล้สุดที่รายงาน ({MOON_MIN:,.0f}) → ไม่ถึงเสมอ |")
    out.append(f"| 42 ครั้ง | {h42:,.0f} | สูงกว่าระยะไกลสุดที่รายงาน ({MOON_MAX:,.0f}) {100 * (h42 / MOON_MAX - 1):.1f}% → เกินเสมอ |")
    lo = MOON_MAX * 1e6 / (2 ** 42)  # mm: smallest t for which 42 folds clear the farthest moon (1 km = 1e6 mm)
    hi = MOON_MIN * 1e6 / (2 ** 41)  # mm: t at which 41 folds would already reach the nearest moon
    out.append("")
    out.append(f"→ คำตอบคือ 42 เมื่อความหนากระดาษอยู่ระหว่าง **{lo:.4f}–{hi:.4f} มม.** (นอกช่วงนี้คำตอบเปลี่ยน; ที่ 0.08 มม. 42 ครั้งสูง {height_m(42, 0.08) / 1000:,.0f} กม. ไม่ถึงดวงจันทร์ใกล้สุด)\n")
    out.append(f"ความหนาที่ใช้ในเรื่อง ({T_MM} มม.) อยู่ในช่วงนี้ แต่ **ช่วงนี้คำนวณจากค่าระยะดวงจันทร์ที่ตรวจจากแหล่งรอง** ถ้ากระดาษจริงบางกว่า {lo:.3f} มม. เรื่องต้องแก้\n")
    out.append("**การพับจริงด้วยม้วนกระดาษ 60 ม. (สูตรของ Gallivan):**\n")
    out.append("| พับกี่ครั้ง | ความยาวขั้นต่ำที่ต้องใช้ | 60 ม. พอไหม |")
    out.append("|---|---|---|")
    for n in (9, 10, 11, 12):
        L = min_length_m(n)
        out.append(f"| {n} | {fmt_len(L)} | {'พอ' if L <= ROLL_M else 'ไม่พอ'} |")
    out.append("")
    block_len_cm = ROLL_M / (2 ** 10) * 100
    block_th_cm = height_m(10) * 100
    out.append(f"ก้อนหลังพับ 10 ครั้ง (ประมาณอย่างหยาบ ไม่นับกระดาษที่เสียที่รอยพับ): หนา ≈ {block_th_cm:.1f} ซม. ยาว ≈ {block_len_cm:.1f} ซม. → หนากว่ายาว (ตรงกับที่ลุงโชควัดในเรื่อง: 'หนาสิบเซน ยาวหกเซน')\n")
    ratio = min_length_m(11) / min_length_m(10)
    out.append(f"ความยาวที่ต้องใช้พับครั้งที่ 11 เทียบครั้งที่ 10 = ×{ratio:.2f} (≈ ×4 ตามที่ต้นอนุมานในเรื่อง)\n")
    L42 = min_length_m(42)
    out.append(f"**พับ 42 ครั้งจริง ต้องใช้กระดาษยาว ≈ {L42:.2e} ม. ≈ {L42 / LIGHT_YEAR_M:,.0f} ปีแสง** (คำพูดในเรื่อง: 'หนึ่งแสนปี' ปัดจาก ~{L42 / LIGHT_YEAR_M / 1000:.0f} พันปีแสง; ใช้เป็นภาพสั้น ๆ ไม่เทียบกับขนาดดาราจักรในบท)\n")
    out.append("**การตรวจคำพูดในบท:** ป้าเอื้อนคำนวณ 'ห่าง': |1,000,000 − 42| = 999,958 (≈ 'เกือบล้าน' ✓), |500 − 42| = 458 ✓, |80 − 42| = 38 ✓ → ลุงโชคชนะ ✓")
    return "\n".join(out)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    print(tables())
