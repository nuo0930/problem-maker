// 共用题面主题。基于 Typst 0.14.2 的官方模板、page、table、raw 接口。
// 题目只写内容；所有排版规则集中在本文件。
#let resolve-io(style, kind, mode) = {
  assert(("auto", "files", "stdio", "interface").contains(mode))
  if mode != "auto" { mode }
  else if kind == "communication" { "interface" }
  else if style == "CNOI-style" and kind == "batch" { "files" }
  else { "stdio" }
}

#let problem(
  title: "",
  id: "",
  style: "ICPC-style",
  kind: "batch",
  contest: "",
  problem-id: none,
  time-limit: none,
  memory-limit: none,
  io-mode: "auto",
  test-count: none,
  total-score: 100,
  lang: "zh",
  body,
) = {
  assert(("CNOI-style", "IOI-style", "ICPC-style").contains(style), message: "未知赛制")
  assert(("batch", "interactive", "communication").contains(kind), message: "未知题型")
  if style == "CNOI-style" {
    assert(kind != "communication", message: "CNOI-style 不设通信题")
    if kind == "batch" {
      assert((10, 20, 25).contains(test-count), message: "CNOI 非交互题须有 10、20 或 25 个等分数据点")
      assert(calc.rem(total-score, test-count) == 0, message: "数据点分数须等分且为整数")
    }
  }
  if style == "ICPC-style" {
    assert(test-count == none, message: "ICPC 题面不配置评分数据点")
  }
  let mode = resolve-io(style, kind, io-mode)
  if mode == "files" { assert(id != "", message: "文件输入输出必须提供题目标签") }
  let input-name = if mode == "files" { id + ".in" } else if mode == "interface" { "通信接口" } else { "标准输入" }
  let output-name = if mode == "files" { id + ".out" } else if mode == "interface" { "通信接口" } else { "标准输出" }

  set document(title: title)
  set text(font: ("LXGW Bright", "New Computer Modern"), size: 10.5pt, lang: lang, region: if lang == "zh" { "cn" } else { "us" })
  set par(justify: true, leading: 1em, spacing: 0.8em,
    first-line-indent: if style == "CNOI-style" { (amount: 2em, all: true) } else { 0em })
  set page(paper: "a4", margin: (x: 19mm, top: 23mm, bottom: 20mm),
    header: if style == "ICPC-style" { none } else [
      #set text(size: 8.5pt, fill: luma(90))
      #set par(first-line-indent: 0pt)
      #grid(columns: (1fr, auto), [#contest], [#title])
      #v(3pt)
      #line(length: 100%, stroke: 0.4pt + luma(170))
    ],
    footer: [
      #set text(size: 8.5pt, fill: luma(90))
      #set par(first-line-indent: 0pt)
      #line(length: 100%, stroke: 0.4pt + luma(160))
      #v(4pt)
      #align(center, context counter(page).display("第 1 页，共 1 页", both: true))
    ],
  )
  set heading(numbering: none)
  show heading.where(level: 1): it => block(above: 1em, below: 0.55em, sticky: true)[
    #set par(first-line-indent: 0pt)
    #text(font: "LXGW Bright", size: 12pt, weight: "medium")[
      #if style == "CNOI-style" { [【#it.body】] } else { it.body }
    ]
  ]
  show raw: set text(font: "Noto Sans Mono CJK SC", size: 9pt)
  set table(stroke: 0.4pt + luma(150), inset: 6pt)
  show table.cell: set par(first-line-indent: 0pt)

  align(if style == "ICPC-style" { left } else { center })[
    #set par(first-line-indent: 0pt)
    #if problem-id != none { text(size: 10pt)[题目 #problem-id]; v(4pt) }
    #text(font: "LXGW Bright", size: 18pt, weight: "medium")[
      #title#if style == "CNOI-style" and id != "" { [（#id）] }
    ]
    #v(8pt)
  ]
  block(inset: (left: if style == "ICPC-style" { 1em } else { 0pt }))[
    #set text(size: 9pt)
    #set par(first-line-indent: 0pt)
    #grid(columns: (auto, auto), column-gutter: 1.8em, row-gutter: 4pt,
      [输入文件：], text(font: "Noto Sans Mono CJK SC", input-name),
      [输出文件：], text(font: "Noto Sans Mono CJK SC", output-name),
      [时间限制：], if time-limit == none { [—] } else { [#time-limit 秒] },
      [空间限制：], if memory-limit == none { [—] } else { [#memory-limit MiB] },
    )
  ]
  v(10pt)
  body
}

#let io-note(direction, id, style: "CNOI-style", kind: "batch", mode: "auto") = {
  assert(("input", "output").contains(direction))
  if resolve-io(style, kind, mode) == "files" {
    if direction == "input" { [从文件 #raw(id + ".in") 中读入数据。] }
    else { [输出到文件 #raw(id + ".out") 中。] }
  }
}

// 参考 CCPC Final 2024 的右侧歌词块：左对齐文字，底部细横线。
#let epigraph(body, width: 40%) = align(right, block(width: width, above: 12pt, below: 20pt)[
  #set align(left)
  #set par(first-line-indent: 0pt, justify: false, leading: 0.55em)
  #text(font: "LXGW Bright", size: 9.5pt, body)
  #v(5pt)
  #line(length: 100%, stroke: 0.45pt + luma(130))
])

#let sample-box(label, data) = block(width: 100%, breakable: false,
  inset: 7pt, stroke: 0.4pt + luma(160))[
  #set par(first-line-indent: 0pt, justify: false, leading: 0.6em, spacing: 4pt)
  #text(font: "LXGW Bright", size: 9pt, weight: "medium", label)
  #v(4pt)
  #text(font: "Noto Sans Mono CJK SC", size: 8.5pt, raw(data.trim(), block: true))
]

// 长十六进制行不能塞进半页宽；自动改为上下排列。
#let sample(input, output, number: 1, layout: "auto", explanation: none) = {
  assert(("auto", "side", "stack").contains(layout))
  let longest = (input + "\n" + output).split("\n").map(s => s.len()).fold(0, calc.max)
  let side = layout == "side" or (layout == "auto" and longest <= 42)
  block(breakable: true)[
    #heading(level: 1)[样例 #number]
    #grid(columns: if side { (1fr, 1fr) } else { (1fr,) }, gutter: 7pt,
      sample-box("输入", input), sample-box("输出", output))
  ]
  if explanation != none {
    v(5pt)
    explanation
  }
}

// 连续两个编号保留逗号；三个及以上才缩写为区间。
#let test-point-label(tests) = {
  assert(tests.len() > 0, message: "数据点列表不能为空")
  let ids = tests.sorted()
  let parts = ()
  let start = ids.first()
  let last = start
  let append-run(start, last) = {
    if last - start >= 2 {
      (str(start) + " ~ " + str(last),)
    } else if last > start {
      (str(start), str(last))
    } else {
      (str(start),)
    }
  }
  for id in ids.slice(1) {
    if id == last + 1 {
      last = id
    } else {
      parts += append-run(start, last)
      start = id
      last = id
    }
  }
  parts += append-run(start, last)
  parts.join(", ")
}

// 文件样例只给路径和最紧约束标注，不读取大样例的内容。
#let sample-reference(number, id, tests, unit: "测试点") = {
  assert(("测试点", "测试包").contains(unit), message: "未知样例约束单位")
  heading(level: 1)[样例 #number]
  block(breakable: false)[
    #set par(first-line-indent: 0pt)
    见选手目录下的 #raw(id + "/" + id + str(number) + ".in") 与 #raw(id + "/" + id + str(number) + ".ans")。

    该样例满足#unit #(if type(tests) == array { test-point-label(tests) } else { tests }) 的约束条件。
  ]
}

// CNOI 非交互：允许归并相同约束的行，但每个数据点仍独立等分评分。
#let cnoi-data-table(count, rows, total-score: 100, range-columns: ()) = {
  assert((10, 20, 25).contains(count))
  assert(calc.rem(total-score, count) == 0)
  let seen = ()
  for row in rows {
    for id in row.tests {
      assert(id >= 1 and id <= count and not seen.contains(id), message: "数据点编号越界或重复")
      seen.push(id)
    }
  }
  assert(seen.len() == count, message: "评分表必须覆盖全部数据点")
  [共 #count 个独立数据点，每点 #(total-score / count) 分，按数据点分别计分。]
  table(columns: (auto, ..range-columns.map(_ => auto), 1fr),
    table.header([*数据点*], ..range-columns.map(column => strong(column.label)), [*特殊性质*]),
    ..rows.map(row => (
      test-point-label(row.tests),
      ..range-columns.map(column => row.ranges.at(column.key)),
      row.constraints,
    )).flatten(),
  )
}

// IOI 或 CNOI 交互：一个 Subtask 绑定一套约束。
#let subtask-table(rows, total-score: 100, integer-scores: false) = {
  assert(rows.map(row => row.score).sum() == total-score, message: "Subtask 总分不符")
  assert(rows.all(row => row.score > 0), message: "Subtask 分数须为正")
  if integer-scores { assert(rows.all(row => calc.floor(row.score) == row.score)) }
  table(columns: (auto, auto, 1fr),
    table.header([*Subtask*], [*分值*], [*附加约束*]),
    ..rows.enumerate().map(((i, row)) => (str(i + 1), str(row.score), row.constraints)).flatten(),
  )
}
