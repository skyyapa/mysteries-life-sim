# 开发上下文记录（CONTEXT）

> 本文件是项目的**上下文备忘**：记录当前实现状态、架构脉络、关键决策与下一步。
> 任何新会话/协作者先读本文件 + `README.md`，即可无缝接续开发。
> 每完成一个阶段后在本文件追加更新（保持它与代码真实一致）。

最后更新：V0.14 World Tick 2.0 完成时

---

## 一、项目是什么

《诡秘之主·人生模拟器》——规则驱动的叙事人生模拟器。
玩家在第五纪 1348 年的鲁恩王国廷根生活一年，普通生活与异常事件交织。

核心设计原则（源自 `项目架构.md`）：

> **数据库决定世界真相，规则引擎决定能不能发生，叙事层只负责怎么讲。**
> Canon World（原著层）只读，AI 不能改；Simulation World（玩家层）由此演变。
> 当前先做"不依赖 AI 的规则模拟核心"，AI 属未来阶段。

---

## 二、当前实现状态（双版本并存）

| 版本 | 定位 | 入口 |
|---|---|---|
| **Web 版** `web/` | 实际游玩主体 | 打开 `web/index.html` |
| **Python 版** `src/life_sim/` | 规则验证核心 | `python run.py` |

两套版本数据分离：Web 数据内嵌在 `web/app.js`；Python 数据在 `data/*.json`。
**改动事件/NPC 需两边同步**（历史上曾因此脱节；当前已基本对齐）。

## 三、Python 引擎当前结构（V0.14 后）

```
src/life_sim/
├── engine.py            # WorldEngine 总控制器（组装子系统，收敛到 WorldTick）
├── models.py            # Character / GameState / WorldState / NPC / WorldDate / JournalEntry
├── event_system.py      # 事件图系统（池图/链图、条件、冷却、时效）
├── npc_system.py        # NPC 系统（日程、周末差异、失踪）
├── data_loader.py       # 读取 data/*.json
├── save.py              # 存档读/写
├── canon_importer.py    # Canon 导入器（原著层数据）
├── world/               # V0.14 新增
│   ├── tick.py          #   WorldTick 编排器 + TimeSystem（唯一世界推进入口）
│   └── state.py         #   世界状态聚合入口
├── location/system.py   # V0.14 新增：地点状态（人口/活跃度/危险）
├── economy/system.py    # V0.14 新增：轻量经济（收入×支出）
└── relation/system.py   # V0.14 新增：关系系统（信任/友谊/畏惧）
```

### World Tick 2.0 唯一入口（V0.14 核心）

```
WorldEngine.tick_world(state, days/hours)
    └── WorldTick.run(state)
          ├── 1. TimeSystem       时间推进（时分级，快进）
          ├── 2. NPCSystem        NPC 行动（日程/周末/失踪）
          ├── 3. LocationSystem  地点变化（人口/活跃度/危险）
          ├── 4. EconomySystem   经济结算（收入-支出/挨饿伤身）
          ├── 5. RelationSystem  关系演化（友谊/畏惧衰减，信任稳定）
          ├── 6. EventSystem     事件检查（图推进/过期痕迹）
          └── 7. Commit          状态提交
```

**纪律**：一切世界变化必须经过 WorldTick（旧 `tick()`/`update_world()` 保留兼容，新逻辑走新入口）。

---

## 四、已实现功能清单（按实现顺序）

### 基础
- 角色创建（随机姓名/年龄/家庭/职业）、属性系统、行动系统
- 月度结算（工资/房租/生活费）、存款+利息+自动保底、意外支出
- 一年 360 天可玩通，跨年年龄增长，自动生活模式（默认）

### 事件系统
- 事件图：普通生活池图（24 节点）+ 异常失踪链图 + 非凡接触链图 + 廷根暗流主线链图
- 条件：地点/天数/标签/线索/结论/联系人信任门槛/疯狂值/季节/月份/职业
- 机制：冷却、时效窗口（maxDay）、错过痕迹日志、事件一次性（onceTag）
- 核心抉择事件（失踪案选择等）**不设时限**，防主线锁死

### 调查/非凡线（E 级完整）
- 线索→推理→结论链；调查风险/冷却/教会信任
- 初涉非凡 → 第二委托 → 教会声音 → 失控前兆（疯狂≥40）→ 真相抉择（三出口）
- 隐藏疯狂值（madness）：污染驱动、灵性锚压制，UI 只显阶段

### 社交系统
- 关系分层：生面孔/熟人(20+)/朋友(40+)/密友(60+)/挚友(80+)
- 泛社交封顶 40；点卡片设"深交对象"可突破到 100
- 分层事件：朋友的私事(40+)/深夜倾吐(70+)
- V0.14 升级为三维关系（信任/友谊/畏惧）

### 世界层
- 天气/经济压力/城市紧张逐日演化；组织行动（教会注意度/暗流活跃度）
- 地点状态（V0.14）；NPC 周末日程 + 失踪机制（V0.14 前已完成）

### Canon 层
- `data/canon_src/` → `canon_importer.py` → `canon/*.json`（结构化只读）
- 已导入：黑夜女神教会、值夜者、塔罗会 + 邓恩·史密斯、奥尔森教士
- 注意：塔罗会才是"愚者"相关正确组织名（已修正），1348 年尚未成立，作暗线悬念

---

## 五、测试状态

```
140 passed（0.9s）
tests/
├── test_engine.py        引擎基础
├── test_time.py          时间推进/跨年/年龄
├── test_events.py        事件图/条件/冷却/回归
├── test_save.py          存档往返/旧档兼容
├── test_world_health.py  长跑健康（365/730/1095 天）
├── test_economy.py       存款/利息/意外支出
├── test_social.py        社交分层/深交
├── test_mainline.py      主线+疯狂值
├── test_missed.py        时效/错过痕迹
├── test_world_tick.py    组织/NPC周末失踪/Canon
└── test_world_tick2.py    V0.14 编排/时间/地点/经济/关系
```

---

## 六、关键决策记录（为什么这么设计）

1. **Tick 唯一入口**（V0.14）：禁止散落 `npc.tick()`/`event.trigger()`，全部收敛 WorldTick——保证可测试、可调试、时序一致。
2. **信任稳定原则**：NPC 信任一旦建立不因日子流逝掉分（真实人设），友谊/畏惧才自然衰减——否则"社交+1 当日被回落-1"抵消，社交无意义。
3. **`NPC.trust` 做成 property**：读写都代理到 `relationship["trust"]`，让旧代码直接赋值也能同步新三维结构。
4. **核心抉择不设时限**：事件有时效（maxDay），但主线决策永不过期，避免玩家错过后永久卡关。
5. **泛社交封顶 40**：普通社交最多到"朋友"，挚友必须指定深交对象专门相处（朋友以上要有深度）。
6. **Canon 层 AI 不可写**：原著资料结构化为 canon/，规则引擎只读；importer 负责从外部 skill 导入。
7. **事件链不自我锁死**：曾修过"报纸重叠→墙角符号"边条件要求"符号自身标签"的死锁 bug，加回归测试守护。

---

## 七、下一步计划（路线图）

用户给定的优先级（按顺序）：

1. **V0.15 NPC 系统深化**（下一阶段重点）
   - 目标：`goal` 字段驱动行为——医生钱少会加班、商人会去市场谈生意
   - 日程从固定 7 天模板 → 目标反应式日程（规则驱动，不 AI）
2. **V0.16 事件图分支深化**
   - 图级分支（不同选择走向完全不同的后续节点），而非仅节点内 choice
3. **V0.20 完整廷根模拟**
   - 城市感知层：每日动态摘要（"近日东区煤价上涨""教会加强夜间巡逻"）
4. 长期：途径选择（占卜家/观众/不眠者低序列）；一年人生总结结局

---

## 八、待办/边界/坑

- ⚠️ **线上部署未更新**：本地 20+ 功能（神秘链、主线、存档面板、季节、经济、社交、时效…）都在本地 `web/`，线上 `api.yapasky.dpdns.org/life-simulator/` 仍是旧版。上线需替换 `web/` 三个文件（index.html/app.js/styles.css）。目前无部署脚本。
- ⚠️ **数据双写**：Web 数据在 app.js 内嵌，Python 在 data/；加事件/NPC 需同步两边。避免再次脱节（曾发生 Web 20 NPC vs Python 3 NPC）。
- Windows 终端 GBK 编码：`python -c` 中文输出会乱码（数据本身 UTF-8 正确），测试输出同理——别把显示乱码当成数据错误。
- 修改 JSON 数据后跑 `python -m pytest` 兜底；Web 改动后 `node --check web/app.js`。
- NPC 初始信任在 `data/npcs.json`（`trust` 字段）→ importer 会写进 `relationship.trust`。

---

## 九、快速上手命令

```powershell
python run.py                     # CLI（自动生活模式）
python run.py --auto 30           # 自动模拟 30 天
python -m pytest -q               # 全部测试
node --check web/app.js           # Web JS 语法检查
python -m life_sim.canon_importer # 重跑 canon 导入
```