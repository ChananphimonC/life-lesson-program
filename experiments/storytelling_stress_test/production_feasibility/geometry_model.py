"""Folding-geometry feasibility model for story 2 (standard library + Pillow only; no network).

    python geometry_model.py     -> prints the tables used in MATH_AND_GEOMETRY.md and writes folding_geometry.png

Two length models for a strip folded in half repeatedly in ONE direction (metres; t = sheet thickness):
  GALLIVAN (secondary source, only partly confirmed):  L_n = (pi t / 6)(2^n + 4)(2^n - 1)
  MODEL A  (derived here, transparent, conservative): at fold k the stack has m = 2^(k-1) layers; its 2m layers are joined
           in m semicircular loops with centre-line radii (2j-1)t/2, j = 1..m; their lengths sum to (pi t / 2) m^2.
           Loops made by earlier folds are carried (doubled) by every later fold, so
           L_n = sum_k 2^(n-k) (pi t/2) 4^(k-1) = pi t 2^(n-2) (2^n - 1).
  MODEL A ignores that inner loops might share slack, so it should be >= the true minimum; GALLIVAN is the published minimum.
  Neither model covers stiffness, compression, creasing or fold misalignment. Nothing here was tested on real paper.
"""
import math
import sys

from PIL import Image, ImageDraw, ImageFont

T = 1e-4  # m  (ASSUMPTION: 0.1 mm per sheet)


def gal(n, t=T):
    return math.pi * t / 6 * (2 ** n + 4) * (2 ** n - 1)


def modA(n, t=T):
    return math.pi * t * 2 ** (n - 2) * (2 ** n - 1)


def arcsA(k, t=T):
    """Loop length created by fold k alone (before any later fold copies it)."""
    return math.pi * t / 2 * (2 ** (k - 1)) ** 2


def flat_len(L, n, loss):
    """Straight length per layer left after n folds (negative = impossible)."""
    return (L - loss) / 2 ** n


def tmax(L, n, f):
    """Largest sheet thickness (m) for which n folds fit in length L (f is linear in t)."""
    return L / f(n, 1.0)


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    print("n | layers | thickness(mm) | Gallivan L(m) | ModelA L(m) | A/G")
    for n in range(1, 13):
        print(f"{n:>2} | {2 ** n:>6} | {2 ** n * T * 1000:>9.1f} | {gal(n):>10.3f} | {modA(n):>10.3f} | {modA(n) / gal(n):.2f}")
    print("\nratio L(n+1)/L(n):")
    for n in range(1, 12):
        print(f"  {n}->{n + 1}: Gallivan {gal(n + 1) / gal(n):.3f}  ModelA {modA(n + 1) / modA(n):.3f}  loops-of-one-fold (A) {arcsA(n + 1) / arcsA(n):.1f}")
    print("\nRoll feasibility (t = 0.1 mm):")
    for L in (60, 100):
        for n in (10, 11):
            print(f"  roll {L:>3} m, {n} folds: Gallivan needs {gal(n):7.1f} m ({'OK' if gal(n) <= L else 'NO'}), "
                  f"ModelA needs {modA(n):7.1f} m ({'OK' if modA(n) <= L else 'NO'})")
    print("\nThickness windows (mm): 10 folds fit if t <= x ; 11 folds fail if t > y")
    for L in (60, 100):
        print(f"  L={L:>3} m: Gallivan x={tmax(L, 10, gal) * 1000:.3f} y={tmax(L, 11, gal) * 1000:.4f} | "
              f"ModelA x={tmax(L, 10, modA) * 1000:.3f} y={tmax(L, 11, modA) * 1000:.4f}")
    print(f"  => on a 100 m roll 'fold 10 works, fold 11 fails' needs t in about {tmax(100, 11, gal) * 1000:.3f} to {tmax(100, 10, modA) * 1000:.3f} mm (valid under both models)")
    print("  thin kite tissue (0.04 mm): fold 11 needs", f"{gal(11, 4e-5):.1f} m (Gallivan) / {modA(11, 4e-5):.1f} m (ModelA)", "-> would NOT fail on a 100 m roll")
    print("\nBlock after 10 folds, 100 m x 0.30 m strip, t = 0.1 mm:")
    th = 2 ** 10 * T
    for name, f in (("Gallivan", gal), ("ModelA", modA)):
        fl = flat_len(100, 10, f(10))
        print(f"  {name}: leftover straight length per layer {fl * 100:.1f} cm; thickness {th * 100:.1f} cm; width 30 cm; "
              f"rounded end adds ~half thickness {th * 50:.1f} cm -> plan length ~ {(fl + th / 2) * 100:.1f} cm")
    print(f"  naive 100/2^10 (the 9.8 cm in the v2 notes) = {100 / 1024 * 100:.1f} cm; ignores material used by the loops")
    print("\n42 folds, minimum strip length:")
    ly = 9.4607304725808e15
    for name, f in (("Gallivan", gal), ("ModelA", modA)):
        print(f"  {name}: {f(42):.3e} m = {f(42) / ly:,.0f} light-years")
    print(f"\nloops of fold 11 / loops of fold 10 = {arcsA(11) / arcsA(10):.1f} (exact in Model A)")
    piles = [2 ** k for k in range(8)]
    print("\nBowls:", piles, "sum", sum(piles), "remainder", 410 - sum(piles), "| a 9th doubling pile would be", 2 ** 8)
    print("Weight of 100 m x 0.30 m at 80 g/m2:", 100 * 0.3 * 80 / 1000, "kg (assumes 80 gsm ~ 0.1 mm office paper)")
    print("Human check proposal: strip of 4 taped A4 sheets ~1.19 m x 3 cm; Gallivan needs", f"{gal(7):.3f} m for 7 folds and {gal(8):.2f} m for 8 folds (t=0.1 mm)")
    draw()


def draw():
    W, H = 1500, 900
    im = Image.new("RGB", (W, H), "white")
    d = ImageDraw.Draw(im)
    f, fs, fb = ImageFont.load_default(18), ImageFont.load_default(14), ImageFont.load_default(24)
    d.text((30, 20), "Story 2 folding geometry (idealised; NOT tested on real paper)", fill="black", font=fb)
    d.text((60, 80), "A. One fold of a stack with m=4 layers: 4 nested semicircular loops (side view)", fill="black", font=f)
    t, cx, cy = 14, 360, 300
    for j in range(1, 5):
        r = (2 * j - 1) * t / 2
        d.arc([cx - r, cy - r, cx + r, cy + r], 270, 90, fill=(200, 60, 40), width=3)
        d.line([cx - 230, cy - r, cx, cy - r], fill=(60, 90, 200), width=3)
        d.line([cx - 230, cy + r, cx, cy + r], fill=(60, 90, 200), width=3)
    d.text((60, 400), "loop j: centre-line radius (2j-1)t/2, length pi(2j-1)t/2", fill="black", font=fs)
    d.text((60, 420), "sum over m loops = (pi t/2) m^2 -> loops of the next fold are exactly 4x larger", fill="black", font=fs)
    px, py, pw, ph = 760, 110, 640, 330
    d.text((px, py - 30), "B. Minimum strip length vs folds (t = 0.1 mm, log scale)", fill="black", font=f)
    d.rectangle([px, py, px + pw, py + ph], outline="black")
    lo, hi = math.log10(0.001), math.log10(2000)

    def Y(v):
        return py + ph - (math.log10(v) - lo) / (hi - lo) * ph

    def X(n):
        return px + (n - 1) / 11 * pw

    for v in (0.01, 0.1, 1, 10, 100, 1000):
        d.line([px, Y(v), px + pw, Y(v)], fill=(225, 225, 225))
        d.text((px - 52, Y(v) - 8), f"{v:g} m", fill="black", font=fs)
    for L, c in ((60, (230, 150, 0)), (100, (0, 150, 80))):
        d.line([px, Y(L), px + pw, Y(L)], fill=c, width=3)
        d.text((px + 8 + (0 if L == 100 else 90), Y(L) - 20 if L == 100 else Y(L) + 4), f"roll {L} m", fill=c, font=fs)
    for fn, c, lab in ((gal, (60, 90, 200), "Gallivan"), (modA, (200, 60, 40), "Model A")):
        pts = [(X(n), Y(fn(n))) for n in range(1, 13)]
        d.line(pts, fill=c, width=3)
        for p in pts:
            d.ellipse([p[0] - 3, p[1] - 3, p[0] + 3, p[1] + 3], fill=c)
        d.text((pts[-2][0] - 20 + (0 if lab == "Gallivan" else -60), pts[-2][1] + (10 if lab == "Gallivan" else -34)), lab, fill=c, font=fs)
    for n in range(1, 13):
        d.text((X(n) - 6, py + ph + 6), str(n), fill="black", font=fs)
    d.text((px + pw // 2 - 50, py + ph + 28), "number of folds n", fill="black", font=fs)
    d.text((60, 520), "C. Stack after n folds, 100 m x 0.30 m strip, t = 0.1 mm (Gallivan model; 1 px = 1 mm thick, 2 px = 1 cm long)", fill="black", font=f)
    base_y, x = 820, 60
    for n in (6, 8, 10):
        th = 2 ** n * T * 1000
        length_cm = max(0.0, (100 - gal(n)) / 2 ** n) * 100
        wpx, hpx = max(3, int(length_cm * 2)), max(2, int(th))
        d.rectangle([x, base_y - hpx, x + wpx, base_y], fill=(170, 190, 235), outline="black")
        d.text((x, base_y + 6), f"n={n}: {th:.1f} mm thick", fill="black", font=fs)
        d.text((x, base_y + 24), f"{length_cm:.1f} cm straight length left", fill="black", font=fs)
        x += max(wpx, 230) + 80
    d.text((60, 600), "(100 m strip: n=10 leaves only a few cm of straight paper per layer, 10 cm thick -> a squat block; see MATH_AND_GEOMETRY.md)", fill="black", font=fs)
    im.save("folding_geometry.png")
    print("wrote folding_geometry.png")


if __name__ == "__main__":
    main()
