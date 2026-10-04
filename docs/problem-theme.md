# 共用 Typst 题面

所有题目的 `statement.typ` 导入根目录 `problem-theme.typ`。样式集中在主题中，题目只保留内容与元信息；不使用远程包或在线编译服务。

## 编译

```sh
python3 scripts/build_statement.py example
# 等价的 CLI 命令，从项目根目录执行：
typst compile --root . --font-path fonts example/statement.typ example/statement.pdf
# 逐页导出 PNG，用于检查实际排版：
typst compile --root . --font-path fonts --format png example/statement.typ 'example/review/statement-preview-{p}.png'
```

主题使用 Typst 0.14.2 官方模板、page、table、raw 接口；本机实际编译器为 0.15.1。兼容 0.14.2 的目标基于 bundled 官方参考，未在 0.14.2 二进制上编译，不应写成已验证。正文、标题、分节和歌词使用 LXGW Bright（Regular / Medium），运行 `python3 scripts/download_fonts.py` 下载字体，OFL 许可证存放在 `fonts/lxgw-bright/`，来源为 [字体作者仓库](https://github.com/lxgw/LxgwBright)，固定提交见该目录 SOURCE.md，文件哈希见 manifest.json。构建脚本自动传入 `--font-path fonts`，无需安装到系统。样例数据仍使用 Noto Sans Mono CJK SC，数学使用 Typst 自带 New Computer Modern。

## 最小入口

```typst
#import "../problem-theme.typ": problem, sample
#show: problem.with(
  title: "题名", id: "problem", style: "ICPC-style", kind: "batch",
  time-limit: 2, memory-limit: 512,
)

题目描述。

= 输入格式
输入说明。

= 输出格式
输出说明。

#sample(read("down/problem1.in"), read("down/problem1.ans"))
```

`problem` 支持比赛名 `contest`、题号 `problem-id`、语言 `lang`、题型 `kind`（batch/interactive/communication）。`time-limit` 单位秒，`memory-limit` 单位 MiB。ICPC 不显示总分或部分分说明；CNOI 普通题须传入 `test-count: 10/20/25`，通信题会被主题拒绝。

## 排版

- A4、19 mm 左右页边距、10.5 pt 正文、正文 leading 为 1em、黑白印刷；ICPC 采用左侧题名与四行文件/限制信息，页底细线与总页码；CNOI 保留居中题名和页眉。
- CNOI 使用带【】的分节标题；正文每段（含标题后的首段）统一首行缩进 2em。标题、页眉页脚、文件元信息、歌词、样例框、下载文件说明和表格单元格不缩进。IOI、ICPC 使用简洁分节，正文不缩进。
- `epigraph[...]` 使用右侧窄栏，文字左对齐、底部细横线；排两行时用 Typst 的 `\` 显式换行，不使用 HTML。
- `sample` 默认短行左右并列，长于 42 字符则上下排列；不会压缩 128 位十六进制样例到半页宽。可以指定 `layout: "stack"`。保留全部字符，长于整页可容纳宽度时应调整样例排版并重新检查。
- 采用自然分页，不在样例前强制换页，也不要求全部样例同页；单个输入/输出框保持完整。
- 样例文字直接读取 `.in/.ans`，时限和内存建议从 `limits.json` 读取，避免两份题面不同步。

## CNOI 下载样例

`down/` 就是下发文件包，即“选手目录”。整套样例（小样例、大样例）在 `down/` 按标签连续命名，小样例仍由 `sample` 展示文件内容。大样例使用 `sample-reference`，只输出路径和最紧测试点约束，避免把大文件内容载入题面：

```typst
#import "../problem-theme.typ": sample, sample-reference
#sample(read("down/example1.in"), read("down/example1.ans"), number: 1)
#sample-reference(2, "example", (3, 4, 5, 6))
```

文件引用相对于选手目录，不重复添加 `down/` 前缀。第二个调用输出「见选手目录下的 example2.in 与 example2.ans」及「该样例满足测试点 3 ~ 6 的约束条件」。`tests` 可传实际最紧一档的编号数组，由主题统一简写；也可传不可比较约束组合的说明内容，组件不替代输入 validator 或人工语义审查。每档限制的覆盖、手调样例及不泄露特殊构造的规则见 [workflow](problem-workflow.md#cnoi-style-样例与下载文件)。

交互题下载样例可传 `unit: "测试包"`，例如 `sample-reference(2, "example", (1,), unit: "测试包")`；默认单位仍为“测试点”。

## 评分表

赛制与评分规则以 [工作流](problem-workflow.md) 为准；主题组件负责排版和基本完整性检查，不能代替用户对部分分设计的确认。

### CNOI 非交互

```typst
#import "../problem-theme.typ": problem, cnoi-data-table
#show: problem.with(title: "示例", id: "example", style: "CNOI-style", test-count: 10)
= 数据范围
#cnoi-data-table(10, (
  (tests: (1, 2), ranges: (n: [$<=10$]), constraints: [无]),
  (tests: (3, 4, 5, 6, 7, 8, 9, 10), ranges: (n: [$<=1000$]), constraints: [无]),
), range-columns: ((key: "n", label: [$n$]),))
```

数值范围按变量单独成列，“特殊性质”只写结构或其他特殊条件。`range-columns` 指定每列的字段名和显示标题，每行在 `ranges` 中提供对应值；多个变量配置多列。表格检查编号完整、不重复，每点等分；同一行仍按数据点独立评分。编号由 `test-point-label` 格式化：连续两个写作 `1, 2`，连续三个及以上写作 `3 ~ 10`，非连续段用逗号分隔；可用此函数统一其他说明中的测试点编号。

### IOI / CNOI 交互

```typst
#import "../problem-theme.typ": subtask-table
#subtask-table((
  (score: 17, constraints: [$n <= 10$]),
  (score: 83, constraints: [无额外约束]),
))
```

约束与得分公式写入题面正文。离散包需要全部点通过；效率评分的函数、正确性条件及聚合方式必须明确。CNOI 交互的整数分值表传入 `integer-scores: true`，最终整数取整规则仍需在正文与 checker 中写明。ICPC 题面不调用评分表组件。

## 参考边界

公开样式参考：[EC-Final 2025 Hangzhou 的 Problem A 原始题面](https://qoj.ac/download.php?id=16328&type=statement)，采用其可读的标题/时限/输入输出/样例结构，不使用赛事 Logo 或复制题目内容。该参考用于结构设计，主题不承诺精确复刻官方版式。

[NOI 2026 官方资料页](https://www.noi.cn/zxzy/lnzl/jszl/2026-07-27/918389.shtml)已查阅，但 Day1 题面下载接口返回“ID传入错误”，未取得可检视 PDF。CNOI 的中文标题、分节和评分表目前按本项目约定设计，未冒充已复刻 NOI 2026 题面；可在取得原文件后再校准。

## 题名、标签与文件输入输出

`title` 是题目全名，`id` 是文件名标签，不是唯一编号，不能直接用目录名代替题目全名。例如，题目全名为「题目全名」，标签 example，目录 example。文件标签可以重复；同标签的新题可用另一个目录存放，创建脚本默认对目录名加后缀而不更改标签。

CNOI 普通题的 `io-mode: "auto"` 默认 `files`，顶部显示 `[id].in` 和 `[id].out`；其他普通题默认 `stdio`。明确采用标准输入输出的 CNOI 比赛可以指定 `io-mode: "stdio"`。正文输入/输出节调用 `io-note("input", "arena")`、`io-note("output", "arena")` 添加同一套文件说明，标程与评测运行方式也必须同步。交互/通信按接口约定。

下面的 `arena` 仅为示例，需要替换成新题的文件标签；脚本没有默认标签。

```sh
python3 new_problem.py arena --title "题目全名" --style CNOI-style
# 同标签另一个目录：
python3 new_problem.py arena --title "另一道题" --directory arena-other
```

右侧引用、左侧题名和元信息、底部细线页码还参考了 [CCPC Final 2024 / QOJ 2036](https://qoj.ac/contest/2036) 的公开题面。仓库不附带参考 PDF 或题目内容。

文件约定还参考了 QOJ 的 [NOIP 2025 糖果店](https://qoj.ac/download.php?id=15457&type=statement)（candy.in/out）和 [联合省选 2026 找寻者](https://qoj.ac/download.php?id=17301&type=statement)（recollector.in/out）题面文字。

## 交付题面

`python3 scripts/package_problem.py example` 在交付 ZIP 的 statement.typ 中内联共用主题和 limits.json 元信息，保留 down 文件读取（兼容旧题 samples）；工作目录中的原文件不变。全部下载样例随 ZIP 交付，可用 `--samples-only` 另打样例包。ZIP 不附带字体或根目录脚本。解包后安装相同字体，并在题目目录执行 `typst compile statement.typ statement.pdf`，或用 `--font-path` 指向字体目录。

交互题的公开头文件、示例 grader 和编译说明放在 `down/`，打包时逐个指定 `--participant-file down/example.h --participant-file down/grader.cpp --participant-file down/README.md`。该选项也适用于 `--samples-only`；不会自动收录目录内其他源码或私有评测器。
