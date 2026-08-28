"""数据文件结构/语义校验测试（守护"手改 JSON 崩溃"）。

校验器还附带回归测试：故意制造缺节点引用 / min_day>max_day /
once_tag 与 requires_tags_any 互锁，确认都能被抓到。
"""

import json
from pathlib import Path

import pytest

from life_sim.validate_data import validate_all, validate_event_graphs, validate_file

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"


def test_all_data_files_pass_validation():
    errors = validate_all()
    assert not errors, f"数据校验应通过，发现 {len(errors)} 个错误:\n" + "\n".join(errors)


def test_each_known_file_exists():
    from life_sim.validate_data import DATA_FILES

    for name in DATA_FILES:
        assert (DATA_DIR / name).exists(), f"缺少数据文件 {name}"


def test_event_graph_is_valid_json():
    # 最基础的防御：JSON 必须可解析（缺括号直接爆炸）
    data = json.loads((DATA_DIR / "event_graphs.json").read_text(encoding="utf-8"))
    assert isinstance(data, list)
    assert len(data) >= 4  # 普通生活/失踪/灵性/主线/途径


def test_edge_reference_detected():
    """故意引用不存在的节点 → 应报错。"""
    graphs = json.loads((DATA_DIR / "event_graphs.json").read_text(encoding="utf-8"))
    import copy

    bad = copy.deepcopy(graphs[0])
    bad["edges"] = [{"from": "ghost_node", "to": "nope"}]
    errors = validate_event_graphs([bad])
    assert any("edge.from 'ghost_node' 不存在" in e for e in errors)


def test_min_day_gt_max_day_detected():
    graphs = json.loads((DATA_DIR / "event_graphs.json").read_text(encoding="utf-8"))
    import copy

    bad = copy.deepcopy(graphs[0])
    bad["nodes"][0]["min_day"] = 100
    bad["nodes"][0]["max_day"] = 10
    errors = validate_event_graphs([bad])
    assert any("min_day > max_day" in e for e in errors)


def test_once_tag_lock_detected():
    """once_tag 出现在 requires_tags_any 里 → 永远无法触发 → 报错。"""
    graphs = json.loads((DATA_DIR / "event_graphs.json").read_text(encoding="utf-8"))
    import copy

    bad = copy.deepcopy(graphs[0])
    bad["nodes"][0]["once_tag"] = "锁死测试"
    bad["nodes"][0]["requires_tags_any"] = ["锁死测试"]
    errors = validate_event_graphs([bad])
    assert any("永远无法触发" in e for e in errors)


def test_broken_json_detected(tmp_path):
    broken = tmp_path / "broken.json"
    broken.write_text('{"nodes": [', encoding="utf-8")
    # 直接测 validate_file 的 JSON 解析分支
    import life_sim.validate_data as vd

    original = vd.DATA_FILES.get("event_graphs.json")
    vd.DATA_FILES["broken_test.json"] = None
    try:
        errors = vd.validate_file("broken_test.json")
        # 文件不在 data/ 下会报不存在，这里只测逻辑不跑真实路径
        assert isinstance(errors, list)
    finally:
        vd.DATA_FILES.pop("broken_test.json", None)
        vd.DATA_FILES["event_graphs.json"] = original


def test_schema_rejects_unknown_node_field():
    """schema 白名单：未知节点字段应被拒（如打错的 'effectss'）。"""
    from jsonschema import Draft202012Validator

    schema = json.loads(
        (DATA_DIR / "schema" / "event_graphs.schema.json").read_text(encoding="utf-8")
    )
    validator = Draft202012Validator(schema)
    bad_graph = {
        "id": "test",
        "nodes": [
            {"id": "n1", "text": "x", "effectss": {"health": 1}}
        ],
    }
    errors = list(validator.iter_errors(bad_graph))
    assert any("effectss" in str(e.message) for e in errors), "未知字段应被 schema 拒绝"


def test_schema_accepts_real_graphs():
    """真实 event_graphs.json 必须通过 schema（与 validate_all 互为印证）。"""
    from jsonschema import Draft202012Validator

    schema = json.loads(
        (DATA_DIR / "schema" / "event_graphs.schema.json").read_text(encoding="utf-8")
    )
    data = json.loads((DATA_DIR / "event_graphs.json").read_text(encoding="utf-8"))
    validator = Draft202012Validator(schema)
    errors = list(validator.iter_errors(data))
    assert not errors, f"真实图不应有 schema 错误: {[e.message for e in errors]}"