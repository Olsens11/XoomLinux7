#!/usr/bin/env python3
"""Validate full-document BCM4329 page index and requirement IDs.

Checks source docs only; no PDF binary or hardware access.
"""
from pathlib import Path
import re
root=Path(__file__).resolve().parents[2]
page=(root/"docs/research/BCM4329_DATASHEET_PAGE_INDEX.md").read_text()
matrix=(root/"docs/research/BCM4329_DATASHEET_REQUIREMENT_AUDIT.md").read_text()
pages=[]
for line in page.splitlines():
    m=re.match(r"^\|\s*(\d{1,3})\s*\|\s*([HML])\s*\|",line)
    if m:
        pages.append((int(m.group(1)),m.group(2)))
expected=list(range(1,150))
found=[x[0] for x in pages]
assert found==expected,f"Missing, duplicate or misordered datasheet PDF page(s): {sorted(set(expected)-set(found))}; {len(found)} entries"
requirements=[]
for line in matrix.splitlines():
    m=re.match(r"^\|\s*R(\d{2})\s*\|",line)
    if m:requirements.append(int(m.group(1)))
assert requirements==list(range(1,37)),f"Expected 36 unique requirement IDs, got {requirements}"
print("BCM4329_INDEX_VERIFIED",len(pages),"OF_149_PAGES")
print("BCM4329_REQUIREMENT_MATRIX_VERIFIED",len(requirements),"ROWS")
print("No PDF bytes read, no device access")
