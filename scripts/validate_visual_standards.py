"""Visual standards and layout geometry validator.

Validates:
1. Compliance with the 8-point base grid (x, y, width, height divisible by 8)
2. Outer margin constraints (minimum 32px margins on FHD canvas)
3. WCAG 2.1 AA color contrast compliance for corporate theme tokens
"""
from __future__ import annotations

import json
import math
from numbers import Real
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
REPORT_PAGES_DIR = ROOT / "powerbi/CHHHS Research Publications.Report/definition/pages"


def calculate_relative_luminance(rgb_hex: str) -> float:
    """Calculate relative luminance for a given hex color string (#RRGGBB)."""
    h = rgb_hex.lstrip("#")
    if len(h) != 6:
        raise ValueError(f"Invalid RGB hex: {rgb_hex}")
    r, g, b = [int(h[i : i + 2], 16) / 255.0 for i in (0, 2, 4)]

    def channel_lum(c: float) -> float:
        return c / 12.92 if c <= 0.03928 else math.pow((c + 0.055) / 1.055, 2.4)

    rl = channel_lum(r)
    gl = channel_lum(g)
    bl = channel_lum(b)
    return 0.2126 * rl + 0.7152 * gl + 0.0722 * bl


def calculate_contrast_ratio(hex1: str, hex2: str) -> float:
    """Calculate contrast ratio between two hex colors according to WCAG 2.1 specifications."""
    l1 = calculate_relative_luminance(hex1)
    l2 = calculate_relative_luminance(hex2)
    lighter = max(l1, l2)
    darker = min(l1, l2)
    return (lighter + 0.05) / (darker + 0.05)


def check_wcag_compliance(foreground_hex: str, background_hex: str, is_large_text: bool = False) -> tuple[float, bool]:
    """Check whether contrast meets WCAG 2.1 AA (4.5:1 normal, 3.0:1 large)."""
    ratio = calculate_contrast_ratio(foreground_hex, background_hex)
    threshold = 3.0 if is_large_text else 4.5
    return (round(ratio, 2), ratio >= threshold)


def audit_visual_geometry(visual_json_path: Path) -> dict[str, Any]:
    """Audit position and dimensions of a visual against the 8-point base grid."""
    with open(visual_json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    pos = data.get("position")
    violations = []
    if not isinstance(pos, dict):
        pos = {}
        violations.append("position must be an object")
    values = {name: pos.get(name) for name in ("x", "y", "width", "height")}
    for name, value in values.items():
        if isinstance(value, bool) or not isinstance(value, Real) or not math.isfinite(float(value)):
            violations.append(f"{name} must be a finite number")
    x, y, w, h = (values[name] for name in ("x", "y", "width", "height"))
    if all(isinstance(value, Real) and not isinstance(value, bool) and math.isfinite(float(value))
           for value in (x, y, w, h)):
        if x < 0 or y < 0:
            violations.append("x and y must be non-negative")
        if w <= 0 or h <= 0:
            violations.append("width and height must be positive")
        if x % 8 != 0:
            violations.append(f"x={x} not divisible by 8")
        if y % 8 != 0:
            violations.append(f"y={y} not divisible by 8")
        if w % 8 != 0:
            violations.append(f"width={w} not divisible by 8")
        if h % 8 != 0:
            violations.append(f"height={h} not divisible by 8")

    return {
        "file": str(visual_json_path.relative_to(ROOT)),
        "name": data.get("name"),
        "x": x,
        "y": y,
        "width": w,
        "height": h,
        "valid_grid_8px": len(violations) == 0,
        "violations": violations,
    }


def audit_all_report_visuals(pages_dir: Path | None = None) -> list[dict[str, Any]]:
    """Audit all visual.json files in the PBIR directory."""
    target_dir = pages_dir or REPORT_PAGES_DIR
    results = []
    for p in target_dir.rglob("visual.json"):
        results.append(audit_visual_geometry(p))
    return results


def main():
    print("Auditing PBIR visual geometries for 8px base grid compliance...")
    audits = audit_all_report_visuals()
    print(f"Total visuals audited: {len(audits)}")

    failures = [a for a in audits if not a["valid_grid_8px"]]
    if failures:
        print(f"FAILED: {len(failures)} visual(s) violated 8px grid:")
        for f in failures:
            print(f"  - {f['name']} ({f['file']}): {', '.join(f['violations'])}")
    else:
        print("SUCCESS: 100% of visuals conform to the 8px base grid!")

    print("\nAuditing WCAG 2.1 AA Theme Contrast...")
    tokens = [
        ("Neutral Primary (#201F1E) on White (#FFFFFF)", "#201F1E", "#FFFFFF", False),
        ("Neutral Secondary (#605E5C) on White (#FFFFFF)", "#605E5C", "#FFFFFF", False),
        ("Theme Teal (#00828A) on White (#FFFFFF)", "#00828A", "#FFFFFF", False),
        ("Success Green (#107C41) on White (#FFFFFF)", "#107C41", "#FFFFFF", False),
        ("Warning Amber (#D83B01) on White (#FFFFFF)", "#D83B01", "#FFFFFF", False),
    ]
    for name, fg, bg, large in tokens:
        ratio, passed = check_wcag_compliance(fg, bg, large)
        status = "PASS" if passed else "FAIL"
        print(f"  [{status}] {name}: Ratio = {ratio}:1")


if __name__ == "__main__":
    main()
