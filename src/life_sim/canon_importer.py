"""Canon 世界观导入器。

设计原则（源自项目架构.md）：
- Canon World（原著层）只读，不允许 AI 修改。
- 导入源（如 lord-of-mysteries-skill）→ importer → canon/ 结构化数据。
- 查询层只读 canon，规则引擎据此判断"能否发生"，叙事层据此"怎么讲"。

用法：
    from life_sim.canon_importer import import_canon, load_canon
    canon = import_canon("data/canon_src/", out_dir="canon")
    org = load_canon("canon/organizations.json")["黑夜女神教会"]
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


CANON_ROOT = Path(__file__).resolve().parents[2] / "canon"


# ---- 规范化函数：把"自由文本"转成结构化 canon ----

def _slugify(name: str) -> str:
    """生成稳定 ascii id；中文名无法拉丁化时用 'cn_<名>' 兜底。"""
    base = re.sub(r"[^a-zA-Z0-9]+", "_", name).strip("_").lower()
    if not base:
        base = f"cn_{name}"  # 中文名兜底（调用方应尽量提供 id）
    return base


def _normalize_organization(raw: dict[str, Any]) -> dict[str, Any]:
    """规范化组织条目。"""

    return {
        "id": raw.get("id") or _slugify(raw["name"]),
        "name": raw["name"],
        "type": raw.get("type", "organization"),
        "era": raw.get("era", "第五纪"),
        "location": list(raw.get("location", [])),
        "faith": raw.get("faith"),
        "leader": raw.get("leader"),
        "notes": raw.get("notes", ""),
    }


def _normalize_character(raw: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": raw.get("id") or _slugify(raw["name"]),
        "name": raw["name"],
        "type": "character",
        "era": raw.get("era", "第五纪"),
        "location": raw.get("location"),
        "organization": raw.get("organization"),
        "roles": list(raw.get("roles", [])),
        "notes": raw.get("notes", ""),
    }


_NORMALIZERS = {
    "organizations": _normalize_organization,
    "characters": _normalize_character,
}


def import_canon(source_dir: str | Path, out_dir: str | Path = CANON_ROOT) -> Path:
    """把 source_dir 下的原始数据文件导入到 canon/ 输出目录。

    source_dir 中按类型分文件：organizations.json / characters.json / ...
    输出到 out_dir 的对应文件，去重并稳定 id。
    """
    source = Path(source_dir)
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)

    imported: dict[str, list[dict[str, Any]]] = {}
    for filename, normalize in _NORMALIZERS.items():
        src_path = source / f"{filename}.json"
        if not src_path.exists():
            continue
        items = json.loads(src_path.read_text(encoding="utf-8"))
        normalized = [normalize(item) for item in items]

        # 合并进已有 canon（按 id 去重，新条目优先保留原有 id）
        out_path = out / f"{filename}.json"
        existing = load_json_file(out_path)
        by_id = {item["id"]: item for item in existing}
        for item in normalized:
            by_id[item["id"]] = item  # 源数据覆盖（开发者可控，非 AI）
        imported[filename] = list(by_id.values())

        (out / f"{filename}.json").write_text(
            json.dumps(imported[filename], ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
    return out


def load_canon(name: str, root: str | Path = CANON_ROOT) -> list[dict[str, Any]]:
    """只读加载 canon 数据。"""
    return load_json_file(Path(root) / f"{name}.json")


def load_json_file(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    return json.loads(path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    import sys

    src = sys.argv[1] if len(sys.argv) > 1 else "data/canon_src"
    out = import_canon(src)
    print(f"Canon 已导入到 {out}")
    for name in ("organizations", "characters"):
        items = load_canon(f"{name}.json", root=out)
        print(f"- {name}: {len(items)} 条")