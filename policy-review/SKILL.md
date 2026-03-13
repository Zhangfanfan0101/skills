---
name: policy-review
description: 系统化审查公司制度的合法性、合规性、完整性与可操作性；当用户需要制度审查、合规检查、制度完善或风险识别时使用
---

# 公司制度审查 Skill

## 任务目标
- 本 Skill 用于:系统化审查企业各类制度文件，识别潜在风险和改进空间
- 能力包含:多维度审查、合规性检查、问题识别、修改建议生成
- 触发条件:用户提及"制度审查"、"合规检查"、"制度完善"、"风险识别"等需求

## 前置准备
- 无需额外依赖或前置准备

## 操作步骤
- 标准流程:
  1. 制度文件获取与理解
     - 阅读用户提供的制度文件
     - 理解制度的目的、适用范围、核心内容
  2. 多维度审查
     - 根据 [references/review-dimensions.md](references/review-dimensions.md) 中的审查维度，逐项检查制度文件
     - 从合法性、合规性、完整性、可操作性、规范性等维度进行全面评估
  3. 合规性检查
     - 参考 [references/compliance-standards.md](references/compliance-standards.md) 中的合规标准
     - 检查制度是否符合相关法律法规要求
  4. 问题识别与建议生成
     - 汇总发现的问题，按严重程度分类
     - 针对每个问题提供具体的修改建议
  5. 输出审查报告
     - 根据 [references/report-template.md](references/report-template.md) 的结构生成报告
     - 使用 [assets/report-templates/](assets/report-templates/) 中的模板格式化输出

## 资源索引
- 领域参考:
  - [references/review-dimensions.md](references/review-dimensions.md) (何时读取:执行多维度审查时)
  - [references/compliance-standards.md](references/compliance-standards.md) (何时读取:进行合规性检查时)
  - [references/report-template.md](references/report-template.md) (何时读取:生成审查报告时)
- 输出资产:
  - [assets/report-templates/standard-report.md](assets/report-templates/standard-report.md) (用途:标准详细审查报告模板)
  - [assets/report-templates/summary-report.md](assets/report-templates/summary-report.md) (用途:简要审查报告模板)

## 注意事项
- 审查时需结合制度适用地的法律法规
- 对于模糊或不清晰的条款，应明确标注并建议修改
- 优先识别可能导致法律风险或重大管理问题的缺陷
- 建议应具体可执行，避免空泛表述

## 使用示例

### 示例1：完整制度审查
- 功能说明:对公司的考勤管理制度进行全面审查
- 执行方式:智能体主导，通过自然语言指导完成所有审查步骤
- 关键要点:覆盖所有审查维度，输出标准详细报告
- 操作流程:
  1. 用户上传考勤管理制度文档
  2. 智能体按5个维度逐项审查
  3. 引用合规标准检查劳动法相关要求
  4. 生成标准报告，列出问题和建议

### 示例2：合规性快速检查
- 功能说明:针对特定制度快速检查合规风险
- 执行方式:智能体主导，聚焦合规性维度
- 关键要点:重点检查法律法规符合性，输出简要报告
- 操作流程:
  1. 用户提供制度文档及关注点
  2. 智能体引用compliance-standards.md进行检查
  3. 生成简要报告，突出高风险项

### 示例3：制度完善建议
- 功能说明:基于现有制度提供完善建议
- 执行方式:智能体主导，识别缺陷并提供改进方案
- 关键要点:平衡合规性与可操作性，提供具体修改建议
- 操作流程:
  1. 用户说明制度背景和痛点
  2. 智能体分析制度的完整性和可操作性
  3. 提供分条列项的修改建议
