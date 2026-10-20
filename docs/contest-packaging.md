# 组题与整卷交付

用户指定题目顺序，将已有题目组合成省选模拟赛等整场比赛。组题目录与原题目录并列，原题仍保留制作入口、验证工具和进度；组题目录保存交付副本，不替换原题目录。

## 目录结构

```text
day1/
├── statement.pdf
├── editorial.pdf
├── example_a/
│   ├── example_a.md
│   ├── example_a_editorial.md
│   ├── example_a.cpp
│   ├── data/
│   └── down/
├── example_b/
│   ├── example_b.md
│   ├── example_b_editorial.md
│   ├── example_b.cpp
│   ├── data/
│   └── down/
├── example_c/
│   ├── example_c.md
│   ├── example_c_editorial.md
│   ├── example_c.cpp
│   ├── data/
│   └── down/
└── down/
    ├── statement.pdf
    ├── example_a/
    ├── example_b/
    └── example_c/
```

以上为三题比赛的通用示例；按用户指定的输出目录、题目顺序及 BRIEF 中的文件名标签 `[id]` 构建。每题题面命名为 `[id].md`，题解为 `[id]_editorial.md`，标程为 `[id].cpp`。同场题目标签须唯一。

每题 `data/` 只放正式输入与答案，保留对应编号。每题 `down/` 包含全部下载样例，以及该题的公开接口头文件、示例 grader 和编译说明（若有）。总 `down/` 是选手目录，包含合并题面和三个题目子目录，各子目录与相应单题 `down/` 内容一致。标程改名后，公开编译说明必须同步。

总 `down/` 不包含题解、标程、正式数据、私有 grader 或 checker、种子、生成器、制作报告。BRIEF、STATUS、字体和项目脚本不属于交付内容。合并 Typst 源稿、复制清单、检查记录及排版预览可保存在 `.build/`，分发时排除该目录。

## 合并卷排版

合并题面参考[联合省选 2026 第一试原始题面](https://relia.uk/download.php?id=17301&type=statement)的 A4 版心、题名、【分节标题】、页眉横线、连续页码及上下排列的带行号样例。封面列出整场题目和实际文件名、时空限制、评分方式等信息，各题另起一页；不复制参考赛事题目内容、标识或未经验证的评测环境信息。

字体以用户偏好为准：正文、标题和分节使用 **LXGW Bright**；代码、文件名和样例使用 **JetBrains Mono**，其中中文回退到 LXGW Bright；公式使用 **Euler Math**。共用规则集中在根目录 `problem-theme.typ`，原题与合并卷统一使用这套字体。

合并题解使用最新正式 Markdown 题解，转换数学表达式后编译，按同一题序逐题另起一页。转换不改变算法或结论，实质修订仍遵循题解 skill 和验证要求。

## 构建与检查

```sh
python3 scripts/download_fonts.py
python3 scripts/build_contest.py day1 example_a example_b example_c
```

当前封面面向三题 CNOI-style 模拟赛；每题满分 100 分。构建需要 Pandoc 和 Typst，可分别通过 `--pandoc`、`--compiler` 指定程序。封面默认名称为“省选模拟赛”，场次 Day 1，时长 5 小时；可通过 `--title`、`--session`、`--duration` 设置。分数和每题时空限制取自原题，不借组题重新决定部分分。

输出目录须不存在或为空；如需重建，请指定新的输出目录，避免旧产物混入下发文件。题面中标准的 `#let limits = json("limits.json")` 定义会保留为组卷内的独立元信息文件。限制文件支持 `time_seconds` / `time_limit_seconds` / `time_limit_ms`、`memory_mib` / `memory_limit_mib` 和 `test_count` / `test_cases`。

构建器仅复制白名单文件，以 SHA-256 核对副本并记录在 `.build/manifest.json`；总下发目录与单题下发目录均须核对。编译后逐页检查标题、页码、公式、样例及表格分页，并从交付目录编译标程、运行全部公开样例。原题已有完整数据验证且本次没有改变算法时，可用源文件和数据哈希一致性确认正式数据沿用。

对外发布仍按用户授权执行。本地完成组题不等于公开发布。

## 工具自检

运行 `python3 -m unittest discover -s scripts -p test_build_contest.py -v` 检查通用合成题目的复制白名单、排序、限制参数兼容、越界链接拒绝及 Typst 编译。测试中的 Markdown 转换器为桩，不代替真实 Pandoc 转换验证；安装 Typst 时执行 PDF 集成测试。可通过 `CONTEST_TEST_COMPILER` 与 `CONTEST_TEST_FONT_PATH` 指定本地程序及字体。
