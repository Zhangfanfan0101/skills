---
name: legal-case-retrieval-v3
description: 通用法律类案检索工具v3，支持两步调用获取完整案例信息；当用户需要检索类似案例、生成类案分析报告、检索案例参考使用
---

# 法律类案检索 Skill v2.0

## 任务目标
- 本 Skill 用于:检索类似案例并生成结构化分析报告
- 能力包含:类案检索、争议焦点识别、裁判理由分析、结构化报告生成
- 触发条件:用户提出类案检索需求、案例研究

## 检索流程（确保检索质量）

### 一、执行流程

**步骤1：明确检索目标与核验口径**
- 要找什么：用户问题涉及的法律问题类型
- 如何算命中：案例内容包含用户问题中的关键词

**步骤2：预检索**
- 根据用户检索意图
- 理解潜在法条结构
- 生成关键词组

**步骤3：整理多组关键词**
- 原始问题（权重1.0）
- 核心关键词（权重0.9）
- 相关法律概念（权重0.7）

**步骤4：执行数据库检索**
- 智能分拣字段
- 精准匹配
- 默认检索近五年的案例

**步骤5：输出结构化类案检索报告**
包含：
- 一、检索结论
- 二、案例列表，包括：
  - uniqid（案例唯一标识）
  - 案件名称/case_name
  - 案号/case_id
  - 相关内容/chunk
  - 裁判年份/judgeyear
  - 检索方式/search_type

---

## 前置准备
- 依赖说明:scripts脚本所需的依赖包及版本
  ```
  requests>=2.28.0  # 标准HTTP库，用于API调用
  ```
- 非标准文件/文件夹准备:如果Skill执行过程中需要使用除「Skill固定结构」外的文件或文件夹，需前置创建。当前路径视为相对于Skill目录的父目录
  ```bash
  # 示例:创建skill使用需要的文件/文件夹
  mkdir -p legal-case-retrieval-v3/output
  ```

## 操作步骤

### 1. 问题理解与要素提取
- 智能体分析用户需求，明确核心争议问题
- 提取案件基本信息：案由、当事人、关键事实、争议焦点
- 确定筛选条件：法院、判决年份、案件类型、审理程序、文书类型、省份、城市、法院层级
- **默认检索范围：近五年（当前年份-4 至 当前年份）的案例**

### 2. 类案检索执行
- 调用 `scripts/fayan_search.py` 处理检索请求
- 脚本采用两步调用：
  1. 第一步：调用类案检索API获取案例基本信息和uniqid
  2. 第二步：根据uniqid调用案例详情API获取完整字段
- 传入参数：
  - `--question`: 核心争议问题（**必填**）
  - `--case-cause`: 案由（可选）
  - `--top-k`: 返回案例数量（默认10）
  - `--api-url`: 类案检索API地址（可选，默认 `http://192.168.10.111:9632/simliar/case/es`）
  - `--detail-api-url`: 案例详情API地址（可选，默认 `http://192.168.61.16/dbApi/wsSearch`）
  - 筛选条件参数（可选）：
    - `--court`: 法院列表
    - `--judge-year`: 判决年份列表（**默认近五年**，如 `2022 2023 2024 2025 2026`）
    - `--case-type`: 案件类型列表
    - `--procedure`: 审理程序列表
    - `--doctype`: 文书类型列表
    - `--province`: 省份列表
    - `--city`: 城市列表
    - `--court-level`: 法院层级列表
  - `--no-default-years`: 不使用默认近五年年份
  - `--request-output`: 检索语句输出路径（JSON格式）
  - `--response-output`: API返回结果输出路径（JSON格式）
  - `--output`: 综合输出文件路径

### 3. 读取报告模板
- 读取 `assets/report-template.md` 文件
- 了解报告的结构和格式要求
- 确保生成的报告符合模板规范

### 4. 结果分析与回答生成
- 智能体分析检索到的案例
- 提取各案例的关键信息：
  - uniqid（案例唯一标识）
  - title（案例标题）
  - case_name（案件名称）
  - case_id（案号）
  - referencetype（案例级别）
  - chunk（相关内容）
  - judgeyear（裁判年份）
  - search_type（检索方式）
- 识别命中内容：用户问题与案例的匹配点
- 进行相关性分析：评估案例对当前问题的参考价值

### 5. 输出结构化报告（必须严格按模板格式）
- **必须严格遵循** `assets/report-template.md` 的模板格式生成报告
- 报告结构必须包含以下四部分（不得遗漏或变更顺序），**使用序号（一、二、三、四）而非Markdown标题**：

#### 一、检索说明
- 报告生成时间
- 检索问题
- 检索关键词

#### 二、检索目标
- 归纳用户问题的核心争议要点
- **应写成一段话形式，更加自然流畅，而不是要点式的**
- 明确检索的法律问题是什么

#### 三、问题回答
- **开头必须说明：共检索到X件相关案例**
- 基于检索到的案例分析生成对用户问题的回答
- 可以使用要点形式，清晰列出法律规则和裁判要点
- **必须在回答中引用检索到的案例**，例如："检索到的案例显示..."、"如案号（XXXX）XX刑终XX号显示..."
- 总结法律适用规则和裁判要点

#### 四、案例列表（表格形式）
| 案例标题 | 案号 | 案例级别 | 相关性内容 | uniqid | 裁判年份 |
|----------|------|----------|------------|--------|----------|
| {title/案件名称/标题} | {案号} | {referencetype/案例级别} | {chunk内容} | {uniqid} | {年份} |
| ... | ... | ... | ... | ... | ... |

---

**⚠️ 重要约束：**
- 输出时必须使用 Markdown 表格展示案例列表
- 表格必须包含六列：案例标题（title）、案号、案例级别（referencetype）、相关性内容（chunk）、uniqid、裁判年份
- **案例标题（title）**：对应API返回的title字段，用于展示案例名称
- **案例级别（referencetype）**：对应API返回的referencetype字段，表示案例的参考级别（如指导性案例、典型案例、普通案例等）
- 报告结构必须为四部分：一检索说明、二检索目标、三问题回答、四案例列表
- 不得自行创建其他非模板格式的报告结构
- 如需补充分析，可在"问题回答"部分详述，不得单独另建章节
- **问题回答部分开头必须说明检索到的案例数量**
- **问题回答中必须引用检索到的案例作为法律规则分析的支撑**

---

## 资源索引

- 必要脚本:见 [scripts/fayan_search.py](scripts/fayan_search.py)
  - 用途与参数:法研类案库检索 v2.0，支持预检索分析、关键词组生成、近五年默认检索
  - 主要参数:
    - `--question`: 检索问题（必填）
    - `--case-cause`: 案由
    - `--top-k`: 返回数量
    - `--judge-year`: 判决年份（默认近五年）
    - `--no-default-years`: 禁用默认年份
    - `--output`: 输出文件路径

- 领域参考:见 [references/retrieval-process.md](references/retrieval-process.md) (何时读取:了解检索流程和方法)
- API参考:见 [references/api-guide.md](references/api-guide.md) (何时读取:了解法研类案库API的使用规范)
- 输出资产:见 [assets/report-template.md](assets/report-template.md) (直接用于生成结构化报告)

---

## 注意事项

- 检索语句和API返回结果必须保存为JSON文件，便于追溯和复现
- **默认检索近五年案例**：如需检索更早年份，使用 `--judge-year` 参数指定
- 相关性分析应基于案例的争议焦点、裁判理由与用户问题的匹配度
- 案例列表中的唯一标识应使用 uniqid，确保唯一性
- 仅在需要时读取参考文档，保持上下文简洁
- **⚠️ 输出格式强制要求**：使用本技能生成报告时，必须严格按照 `assets/report-template.md` 模板的四部分结构输出，使用序号（一、二、三、四）标记而非Markdown标题。检索目标应写成一段话形式，自然流畅；问题回答可使用要点形式；案例列表表格必须包含：案例标题、案号、相关性分析、裁判年份；生成说明需包含检索关键词。不得自行变更格式或省略任何部分。

---

## 使用示例

### 示例1：基础类案检索（默认近五年）
```bash
python scripts/fayan_search.py \
  --question "入户盗窃" \
  --case-cause "盗窃罪" \
  --top-k 10 \
  --response-output ./legal-case-retrieval-v3/output/response.json
```

### 示例2：指定年份范围检索
```bash
python scripts/fayan_search.py \
  --question "劳动合同经济补偿金计算基数" \
  --case-cause "劳动合同纠纷" \
  --top-k 5 \
  --judge-year 2023 2024 2025 \
  --response-output ./legal-case-retrieval-v3/output/response.json
```

### 示例3：带省份筛选的检索
```bash
python scripts/fayan_search.py \
  --question "正当防卫认定标准" \
  --case-cause "故意伤害罪" \
  --top-k 10 \
  --province "广东省" \
  --response-output ./legal-case-retrieval-v3/output/response.json
```

### 示例4：不使用默认近五年（检索全部年份）
```bash
python scripts/fayan_search.py \
  --question "诈骗罪构成要件" \
  --case-cause "诈骗罪" \
  --top-k 10 \
  --no-default-years \
  --response-output ./legal-case-retrieval-v3/output/response.json
```

### 示例5：完整工作流程
- 用户问题："搜索上海市法院近三年关于竞业限制纠纷的案例，分析违约金调整标准"
- 执行步骤：
  1. 提取关键信息：竞业限制纠纷、违约金调整、上海市、近三年
  2. 执行检索：
     ```bash
     python scripts/fayan_search.py \
       --question "竞业限制违约金调整标准" \
       --case-cause "竞业限制纠纷" \
       --province "上海市" \
       --judge-year 2023 2024 2025 \
       --top-k 10 \
       --response-output ./legal-case-retrieval-v3/output/response.json
     ```
  3. 分析检索结果，提取案例关键信息
  4. 生成结构化报告

---

## 输出字段说明

| 字段名 | 说明 | 示例 |
|--------|------|------|
| uniqid | 案例唯一标识 | 2dfd363c-12d5-4e0e-b541-ae980100c2f3 |
| title | 案例标题 | 陶某某盗窃罪一案 |
| case_name | 案件名称 | 陶某某盗窃罪一案 |
| case_id | 案号 | （2023）内0403刑初167号 |
| referencetype | 案例级别 | 指导性案例、典型案例、普通案例等 |
| chunk | 相关内容 | 被告人陶某某构成盗窃罪... |
| judgeyear | 裁判年份 | 2023 |
| search_type | 检索方式 | feature_summary_search |