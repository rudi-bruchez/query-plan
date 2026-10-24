#!/usr/bin/env python3
"""Builds css/qp_icons.png and the icon block of css/qp.css from the operator icons
of the Microsoft documentation (MicrosoftDocs/sql-docs, CC BY 4.0).

Usage: python3 tools/sprite-microsoft.py <sql-docs clone>

Icons are 32 px in the source and shown at 24 px. The warning, parallel and batch
overlays come from the previous sprite (Fat Cow Farm Fresh), which has no equivalent.
"""
import re
import sys
from pathlib import Path
from PIL import Image

SOURCE = "docs/relational-databases/media/showplan-logical-and-physical-operators-reference"
CELL, SHOWN, COLS = 32, 24, 10
SCALE = SHOWN / CELL

# Class name (as computed by renderNodeIcon) -> Microsoft file, when kebab-case does not match.
# Microsoft draws Key Lookup as a page and RID Lookup as an index tree with a magnifier,
# which is backwards: a Key Lookup seeks a clustered index, a RID Lookup reads a heap.
MANUAL = {
    "Catchall": "iterator-catch-all",
    "IteratorCatchall": "iterator-catch-all",
    "CursorCatchall": "cursor-catch-all",
    "LanguageElementCatchall": "language-construct-catch-all",
    "While": "language-construct-catch-all",
    "If": "conditional",
    "StmtCond": "conditional",
    "StmtCursor": "cursor-catch-all",
    "FastForward": "cursor-catch-all",
    "SnapShot": "snapshot",
    "Statement": "result",
    "PopulateQuery": "population-query",
    "UDX": "udx-extended-operator",
    "KeyLookup": "row-id-nonclustered-locate",
    "BookmarkLookup": "row-id-nonclustered-locate",
    "RIDLookup": "key-lookup",
    "GatherStreams": "parallelism",
    "DistributeStreams": "parallelism-distribute-streams",
    "RepartitionStreams": "parallelism-repartition-streams",
    "EagerSpool": "spool",
    "LazySpool": "spool",
    "RowCountSpool": "spool",
    "WindowSpool": "spool",
    "HashMatchRoot": "hash-match",
    "HashMatchTeam": "hash-match",
    "WindowAggregate": "aggregate",
    "IndexScan": "nonclustered-index-scan",
    "IndexSeek": "nonclustered-index-seek",
    "IndexSpool": "nonclustered-index-spool",
    "IndexInsert": "nonclustered-index-insert",
    "OnlineIndexInsert": "nonclustered-index-insert",
    "IndexDelete": "nonclustered-index-delete",
    "IndexUpdate": "nonclustered-index-update",
    "ColumnStoreIndexScan": "columnstore-index-scan",
    "ColumnStoreIndexInsert": "columnstore-index-insert",
    "ColumnStoreIndexDelete": "columnstore-index-delete",
    "ColumnStoreIndexUpdate": "columnstore-index-update",
    "ColumnStoreIndexMerge": "columnstore-index-merge",
}
# Overlays kept from the previous sprite (tools/overlays.png, three 16 px cells in this order)
OVERLAYS = ["qp-iconwarn", "qp-iconpar", "qp-iconbatch"]


def clear_background(im):
    """The Microsoft icons sit on an opaque white or #f6f6f6 square, which shows on a
    hover background and turns black in the dark theme. Make the light pixels reachable
    from the border transparent; light areas enclosed by strokes stay."""
    px, (w, h) = im.load(), im.size
    light = lambda p: p[3] > 0 and min(p[:3]) >= 235
    todo = [(x, y) for x in range(w) for y in (0, h - 1)] + [(x, y) for y in range(h) for x in (0, w - 1)]
    seen = set()
    while todo:
        x, y = todo.pop()
        if (x, y) in seen or not (0 <= x < w and 0 <= y < h) or not light(px[x, y]):
            continue
        seen.add((x, y))
        px[x, y] = (0, 0, 0, 0)
        todo += [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]
    return im


def kebab(name):
    return re.sub(r"(?<!^)(?=[A-Z])", "-", name).lower()


def main():
    root = Path(__file__).resolve().parent.parent
    icons_dir = Path(sys.argv[1]) / SOURCE
    css_path = root / "css" / "qp.css"
    css = css_path.read_text(encoding="utf-8-sig")
    begin, end = "/* icons:start */", "/* icons:end */"
    if begin in css:
        block = css[css.index(begin):css.index(end) + len(end)]
        classes = re.findall(r"\.qp-icon-(\w+)\s*\{", block)
    else:
        classes = re.findall(r"\.qp-icon-(\w+)\{", css)
    classes = [c for c in dict.fromkeys(classes) if c != "RdiLookup"]
    for c in MANUAL:
        if c not in classes:
            classes.append(c)

    files = sorted({MANUAL.get(c, kebab(c)) for c in classes})
    missing = [f for f in files if not (icons_dir / f"icon-{f}.png").exists()]
    if missing:
        sys.exit("icônes introuvables : " + ", ".join(missing))

    strip = Image.open(root / "tools" / "overlays.png").convert("RGBA")
    overlays = {k: strip.crop((j * 16, 0, j * 16 + 16, 16)) for j, k in enumerate(OVERLAYS)}

    cells = files + ["overlays"]
    rows = (len(cells) + COLS - 1) // COLS
    sprite = Image.new("RGBA", (COLS * CELL, rows * CELL), (0, 0, 0, 0))
    position = {}
    for i, f in enumerate(cells):
        x, y = (i % COLS) * CELL, (i // COLS) * CELL
        position[f] = (x, y)
        if f == "overlays":
            for j, im in enumerate(overlays.values()):
                sprite.paste(im, (x + (j % 2) * 16, y + (j // 2) * 16))
        else:
            icon = clear_background(Image.open(icons_dir / f"icon-{f}.png").convert("RGBA"))
            if icon.size != (CELL, CELL):
                # A few sources are 16 px (Filter): drawn as is, they fill a corner of the cell
                icon = icon.resize((CELL, CELL), Image.LANCZOS)
            sprite.alpha_composite(icon, (x, y))
    sprite.save(root / "css" / "qp_icons.png", optimize=True)

    size = f"{COLS * SHOWN:g}px {rows * SHOWN:g}px"
    lines = [begin,
             "/* Operator icons: Microsoft, MicrosoftDocs/sql-docs, CC BY 4.0. Generated by tools/sprite-microsoft.py */",
             f"div[class|='qp-icon'], .qp-iconwarn, .qp-iconpar, .qp-iconbatch {{ background-image: url('qp_icons.png'); background-size: {size}; }}"]
    for c in classes:
        x, y = position[MANUAL.get(c, kebab(c))]
        lines.append(f".qp-icon-{c} {{ background-position: -{x * SCALE:g}px -{y * SCALE:g}px; }}")
    ox, oy = position["overlays"]
    for j, k in enumerate(OVERLAYS):
        x, y = ox + (j % 2) * 16, oy + (j // 2) * 16
        lines.append(f".{k} {{ background-position: -{x * SCALE:g}px -{y * SCALE:g}px; }}")
    lines.append(end)
    generated = "\n".join(lines)

    if begin in css:
        css = css.replace(css[css.index(begin):css.index(end) + len(end)], generated)
    else:
        css = re.sub(r"\.qp-icon-\w+\{[^}]*\}\n?", "", css)
        css = css.rstrip() + "\n\n" + generated + "\n"
    css_path.write_text(css, encoding="utf-8")
    print(f"{len(classes)} classes, {len(files)} icônes, sprite {sprite.size[0]}x{sprite.size[1]}")


if __name__ == "__main__":
    main()
