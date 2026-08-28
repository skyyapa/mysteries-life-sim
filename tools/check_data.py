"""数据校验便捷入口：改完 data/*.json 后跑 `python tools/check_data.py`。

等价于 pytest -q tests/test_data_schema.py 的校验部分，但无需 pytest。
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from life_sim.validate_data import validate_all


def main() -> int:
    errors = validate_all()
    if errors:
        print(f"[FAIL] 数据校验失败（{len(errors)} 个错误）：")
        for err in errors:
            print(f"  [x] {err}")
        print("\n提示：改完 data/event_graphs.json 等文件后跑本脚本，可避免手改 JSON 崩溃。")
        return 1
    print("[OK] 全部数据文件校验通过")
    return 0


if __name__ == "__main__":
    sys.exit(main())