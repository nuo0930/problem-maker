# problem-maker

由出题人提供题目构思，AI 协助完成算法竞赛题目的查重、解法审查、题面、题解、程序、数据和交付。

这套工具包含工作流约定、AI 项目指令、BRIEF 模板、题目创建脚本和共用 Typst 主题。具体题目的算法、数据生成器和评测程序由出题人与 AI 在各题目录中制作。

## 快速开始

需要 Python 3.9 或更新版本。编译题面还需要 Typst 与 Noto Sans Mono CJK SC 字体；算法程序所需的编译器按题目选择。

```sh
git clone https://github.com/nuo0930/problem-maker.git
cd problem-maker

# 下载并校验共用主题使用的 LXGW Bright 字体
python3 scripts/download_fonts.py

# 创建题目目录，复制 BRIEF 模板
python3 new_problem.py example --title "题目全名" --style CNOI-style
```

`example` 只是示例，请换成新题的文件名标签 `[id]`。它没有预设值，也不代表题目全名。标签用于 `example.cpp`、`example.in`、`example.out` 等文件名。

打开生成的 `example/BRIEF.md`，填写题目大意、简要解法、约束和设计意图，然后让 AI 从该文件开始工作。例如：

> 请先阅读 AGENTS.md 和 docs/problem-workflow.md，再阅读 example/BRIEF.md，按工作流开始制作。发现更好的可行做法时先向我说明；未经确认不要改变题目核心设计。

## 新建题目

```sh
python3 new_problem.py example --title "题目全名" --style ICPC-style
python3 new_problem.py example --title "另一道题" --style IOI-style --kind interactive --directory example-other
```

| 参数 | 用途 |
| --- | --- |
| 第一个参数 | 必填的文件名标签，只含英文字母、数字、下划线或连字符，以字母开头 |
| `--title` | 展示用的题目全名；省略则在 BRIEF 中留待填写 |
| `--style` | `CNOI-style`、`IOI-style` 或 `ICPC-style`；省略则留待填写 |
| `--kind` | `batch`（默认）、`interactive` 或 `communication` |
| `--directory` | 指定一级目录名；省略时采用标签，同名目录存在则加 `-2`、`-3` 等后缀 |

标签可以重复。默认目录加后缀时，BRIEF 中的标签保持不变；显式指定的目录已存在时拒绝覆盖。脚本只创建目录和 BRIEF，不生成题意或完整题目。

## 制作流程

1. **填写构思**：出题人维护 BRIEF，说明题意、解法、约束、赛制与希望保留的设计。
2. **保密查重**：只用通用算法名、公开问题名和宽泛模型关键词检索；在报告中注明查询内容、来源及覆盖局限。
3. **审查解法**：证明正确性，分析复杂度、替代做法与可能反例。发现更好的可行算法时先向出题人说明，等待设计决定。
4. **制作产物**：编写题面、题解、标程、暴力、生成器、validator，以及适用的 checker；按实际题型组织文件。
5. **执行验证**：在授权范围内对拍、检查边界和错误做法，测量时间与内存，保留命令、种子和真实结果。
6. **复核交付**：检查各产物是否一致，形成交付包，列出尚未执行的人工独立审题和正式评测机校准。

每次实质工作更新题目目录中的 `STATUS.md`。BRIEF 保存出题人输入，AI 的建议与分析写入 `reports/`，不擅自改写构思。搜索没有命中不构成原创证明，未运行的检查不能标记为通过。

完整规则见 [出题工作流](docs/problem-workflow.md)，AI 入口见 [AGENTS.md](AGENTS.md)。

## 三种赛制

以下是本工具的工作约定，可由出题人根据目标比赛调整。

| 赛制 | 评分与文件约定 |
| --- | --- |
| CNOI-style 普通题 | 10、20 或 25 个独立等分数据点，不绑定 Subtask；通常读取 `[id].in`，输出 `[id].out` |
| CNOI-style 交互题 | 可以绑定测试包，得分取整；首包一般约束较弱且采用离散评分；不设置通信题 |
| IOI-style | 建议绑定 Subtask；离散评分须通过包内全部点；交互和通信题建议根据开销采用连续评分 |
| ICPC-style | 不设计部分分或 Subtask，题面不额外声明“没有部分分”；普通题默认标准输入输出 |

部分分方案由出题人指定，或由 AI 提出后交出题人决定。CNOI 的文件输入输出必须同时反映在题面、标程和评测运行方式中。

CNOI 除题意小样例外，还提供覆盖每档限制的下载样例，并尽量补一组适合手调的较强小样例。`down/` 即下发文件包，也就是题面中的选手目录，文件引用不重复写 `down/`。整套样例在 `down/` 中从 1 连续编号为 `[id]1.in` / `[id]1.ans` 等。小样例展示输入输出，大样例只写文件路径和实际满足的最紧测试点限制；样例不提示做法、不复用正式数据的特殊构造。细则见[样例与下载文件](docs/problem-workflow.md#cnoi-style-样例与下载文件)。

数据范围表和样例限制说明中的连续测试点编号，两个用逗号（`1, 2`），三个及以上用区间（`3 ~ 6`）；非连续段以逗号分隔。三种题面格式保持一致。

## Typst 题面

每题维护 `statement.md`、`statement.typ` 和 `statement.pdf`。所有 Typst 题面导入根目录 [problem-theme.typ](problem-theme.typ)，统一控制字体、行距、标题、引用、样例框与页码。

正文与标题采用 LXGW Bright，字体下载脚本固定上游提交并核验 SHA-256。字体按其 [OFL 许可证](fonts/lxgw-bright/OFL.txt)使用，来源与固定版本见 [SOURCE.md](fonts/lxgw-bright/SOURCE.md)。样例数据保留等宽字体。

编写题目内容后，从项目根目录执行：

```sh
python3 scripts/build_statement.py example
```

该脚本只编译已有的 `statement.typ`。最小入口、样例、评分表和文件输入输出组件见 [题面主题说明](docs/problem-theme.md)。编译后检查字体、公式、长行和分页；采用自然分页，无须将全部样例放在同一页。

## 题目交付 ZIP

```sh
python3 scripts/package_problem.py example
# 标程或题解文件名不同时可以指定：
python3 scripts/package_problem.py example --solution solution.py --editorial editorial.md
# 另打包仅含选手下载样例的 ZIP：
python3 scripts/package_problem.py example --samples-only
```

ZIP 只包含 `statement.md`、`statement.typ`、`statement.pdf`、题解、标程，以及 `down/`、`data/` 中的 `.in`、`.ans` 或 `.out` 文件。旧题仅有 `samples/` 时保持兼容；两个样例目录同时含文件会报错，避免交付两套来源。打包前检查每个输入恰有一个配套答案，拒绝孤立输入或答案。不会包含 BRIEF、STATUS、制作报告、评测工具、字体、项目文档或整个工作区。

`--samples-only` 生成 `<题目目录名>-down.zip`，仅含整套样例文件，解包后保留 `down/`（旧题则为 `samples/`）目录；不要求其他题目产物已生成。检查记录为 `reports/sample-delivery-validation.json`。

交付版 Typst 将共用主题和 limits 元信息内联到题面源码中，保留样例文件读取。工作目录中的题面仍导入共用主题；解包后的源码不依赖项目根目录，重新编译时需要本机具备相同字体。内联支持主题说明中的入口写法；使用其他本地资源时，应先调整题面使交付源码自包含。

打包工具核对 ZIP 清单并完整读取所有条目检查 CRC；若有 `data/manifest.json`，还核对数据 SHA-256。检查记录保留在工作目录的 `reports/delivery-validation.json`，不放入交付 ZIP。

## AI skills

项目约定使用两个 skills：

- `plain-oi-editorials`：正式题解的分析与表达。
- `typst`：Typst 文档编写、模板修改和中文排版。

skills 需要在所用 AI 环境中另行配置，本仓库不附带它们。缺少题解 skill 时，可以继续其他已授权工作，正式题解等待配置完成。创建目录和运行已有题面的编译脚本本身不依赖 AI。

## 目录

```text
README.md                     使用说明
AGENTS.md                     AI 项目约定
new_problem.py                创建指定标签的题目目录
problem-theme.typ             共用 Typst 主题
docs/
  BRIEF.template.md           构思模板
  problem-workflow.md         详细制作流程
  problem-theme.md            排版与编译说明
scripts/
  download_fonts.py           固定版本字体下载与校验
  build_statement.py          本地 PDF 编译
  package_problem.py          按白名单打包题目交付文件
fonts/lxgw-bright/             字体来源、许可证、下载清单
```

新题作为一级目录存放，题目产物默认留在该目录。

## 保密与版本管理

公开仓库只维护通用工具、模板和约定。发布版的 `.gitignore` 默认排除新建的题目目录、字体二进制、生成产物和本地配置。

未公开题目的 BRIEF、题面、算法、代码、数据、报告、PDF 和交付包应保存在本地或另一个私有仓库。向公共仓库提交改动前检查文件清单及 diff；不要用强制添加绕过题目目录的忽略规则，也不要推送已有私人题目仓库的历史。

联网查重须遵守 [工作流的外发边界](docs/problem-workflow.md#外发边界)。题面在本地编译，未公开内容不上传远程排版服务。平台发布与通用工具更新分别进行。
