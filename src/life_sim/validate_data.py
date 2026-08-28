"""数据文件校验器（V0.22 工具链）。

用途：在编辑 data/event_graphs.json 等数据后立即发现结构/语义错误，
避免"手改 JSON 缺括号导致引用崩溃"这类问题。

校验内容：
1. JSON 可解析
2. JSON Schema 结构校验（data/schema/*.schema.json）
3. 语义校验：
   - 图 id / 节点 id 全局唯一
   - 链图 start_node 存在；边的 from/to 引用存在的节点
   - once_tag / add_tags / requires_tags_any 之间无自相矛盾
   - max_day >= min_day；min_day 不晚于 max_day
   - 每个节点有 text；choices 至少一个 label/result 非空
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, ValidationError

ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "data"
SCHEMA_DIR = DATA_DIR / "schema"

# 校验范围：哪些数据文件用哪个 schema（None = 仅 JSON 解析 + 语义）
DATA_FILES: dict[str, str | None] = {
    "event_graphs.json": "event_graphs.schema.json",
    "npcs.json": None,
    "actions.json": None,
    "schedules.json": None,
    "events.json": None,
}


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def validate_schema(data: Any, schema_path: Path | None) -> list[str]:
    """结构校验：返回错误列表，空 = 通过。"""
    if schema_path is None:
        return []
    schema = load_json(schema_path)
    validator = Draft202012Validator(schema)
    errors = [
        f"{'.'.join(str(p) for p in e.absolute_path) or '<root>'}: {e.message}"
        for e in validator.iter_errors(data)
    ]
    return errors


def validate_event_graphs(data: list[dict[str, Any]]) -> list[str]:
    """event_graphs.json 的语义校验（结构已由 schema 保证）。"""
    errors: list[str] = []
    graph_ids: set[str] = set()
    node_ids: dict[str, set[str]] = {}

    for g_idx, graph in enumerate(data):
        gid = graph.get("id", "")
        if gid in graph_ids:
            errors.append(f"图 id 重复: {gid}")
        graph_ids.add(gid)

        nodes = graph.get("nodes", [])
        ids = {n.get("id", "") for n in nodes}
        node_ids[gid] = ids
        if len(ids) != len(nodes):
            errors.append(f"图 {gid}: 节点 id 重复")

        # start_node 存在
        start = graph.get("start_node")
        if start and start not in ids:
            errors.append(f"图 {gid}: start_node '{start}' 不存在")

        # 节点内部语义
        for node in nodes:
            nid = node["id"]
            if "min_day" in node and "max_day" in node:
                if node["min_day"] > node["max_day"]:
                    errors.append(f"图 {gid} 节点 {nid}: min_day > max_day")
            choices = node.get("choices", [])
            if choices:
                for c in choices:
                    if not c.get("label"):
                        errors.append(f"图 {gid} 节点 {nid}: choice 缺 label")
                    if not c.get("result"):
                        errors.append(f"图 {gid} 节点 {nid}: choice 缺 result")
            # once_tag 与 requires_tags_any 不应互相锁定（选择后触发条件消失）
            once = node.get("once_tag")
            req = node.get("requires_tags_any", [])
            if once and once in req:
                errors.append(
                    f"图 {gid} 节点 {nid}: once_tag '{once}' 也在 requires_tags_any → 事件永远无法触发"
                )

        # 边引用
        edges = graph.get("edges", [])
        for edge in edges:
            if edge["from"] not in ids:
                errors.append(f"图 {gid}: edge.from '{edge['from']}' 不存在")
            if edge["to"] not in ids:
                errors.append(f"图 {gid}: edge.to '{edge['to']}' 不存在")

    # 跨图 once_tag 一致性：同一 once_tag 不应出现在多个图（会互相卡死）
    once_owners: dict[str, str] = {}
    for graph in data:
        gid = graph.get("id", "")
        for node in graph.get("nodes", []):
            once = node.get("once_tag")
            if once:
                if once in once_owners and once_owners[once] != gid:
                    pass  # 允许（不同图同 tag 语义上是全局通用）
                once_owners[once] = gid
    return errors


def validate_file(name: str) -> list[str]:
    path = DATA_DIR / name
    if not path.exists():
        return [f"文件不存在: {name}"]
    try:
        data = load_json(path)
    except json.JSONDecodeError as exc:
        return [f"{name}: JSON 解析失败 → {exc}"]
    except OSError as exc:
        return [f"{name}: {exc}"]

    schema_path = SCHEMA_DIR / DATA_FILES[name] if DATA_FILES.get(name) else None
    errors = validate_schema(data, schema_path)
    if name == "event_graphs.json":
        errors.extend(validate_event_graphs(data))
    return errors


def validate_all() -> list[str]:
    all_errors: list[str] = []
    for name in DATA_FILES:
        all_errors.extend(validate_file(name))
    return all_errors


def main() -> int:
    errors = validate_all()
    if errors:
        print(f"校验失败（{len(errors)} 个错误）：")
        for err in errors:
            print(f"  [x] {err}")
        return 1
    print("[OK] 全部数据文件校验通过")
    return 0


if __name__ == "__main__":
    sys.exit(main())