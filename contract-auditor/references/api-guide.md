# 法研类案库 API 指南

## 目录
- [API概述](#api概述)
- [接口一：类案检索API](#接口一类案检索api)
- [接口二：案例详情API](#接口二案例详情api)
- [错误处理](#错误处理)
- [使用示例](#使用示例)

## API概述
法研类案库提供两个API接口：
1. **类案检索API**: 检索类似案例，返回案例基本信息和uniqid
2. **案例详情API**: 根据uniqid获取案例的完整字段信息

**基础信息**
- 认证方式: 无需认证（同服务器环境内部调用）
- 数据格式: JSON

## 接口一：类案检索API
用于检索类似案例，获取案例基本信息和唯一标识符。

**接口地址**: `http://192.168.10.111:9632/simliar/case/es`
**请求方式**: POST

### 请求头
```
Content-Type: application/json
```

### 请求体
```json
{
  "question": "检索问题",
  "casecause": "案由",
  "top_k": 10,
  "court": ["法院名称"],
  "judgeyear": [2022, 2023],
  "casetype": ["民事案件"],
  "procedure": ["一审"],
  "doctype": ["判决书"],
  "province": ["省份"],
  "city": ["城市"],
  "courtlevel": ["基层法院"]
}
```

### 响应格式
```json
{
  "cases": [
    {
      "uniqid": "案例唯一标识",
      "case_number": "案号",
      "court": "审理法院",
      "judge_date": "判决日期",
      "case_cause": "案由",
      "procedure": "审理程序",
      "doctype": "文书类型",
      "parties": "当事人信息",
      "fact": "案件事实",
      "dispute_focus": "争议焦点",
      "judgment_reason": "裁判理由",
      "judgment_result": "裁判结果",
      "relevance_score": 0.95
    }
  ],
  "total": 100
}
```

### 参数说明

| 参数名 | 类型 | 说明 | 示例 |
|--------|------|------|------|
| question | string | 检索问题，描述核心争议点 | "违约金计算标准" |
| casecause | string | 案由 | "房屋租赁合同纠纷" |
| top_k | integer | 返回结果数量，默认10 | 10 |
| court | array | 法院列表 | ["北京市朝阳区人民法院"] |
| judgeyear | array | 判决年份列表 | [2022, 2023] |
| casetype | array | 案件类型列表 | ["民事案件"] |
| procedure | array | 审理程序列表 | ["一审", "二审"] |
| doctype | array | 文书类型列表 | ["判决书", "裁定书"] |
| province | array | 省份列表 | ["北京市", "上海市"] |
| city | array | 城市列表 | ["朝阳区", "浦东新区"] |
| courtlevel | array | 法院层级列表 | ["基层法院", "中级人民法院"] |

## 接口二：案例详情API
根据uniqid获取案例的完整字段信息。

**接口地址**: `http://192.168.61.16/dbApi/wsSearch`
**请求方式**: POST

### 请求头
```
Content-Type: application/json
```

### 请求体
```json
{
  "query": {
    "query": {
      "bool": {
        "must": [
          {
            "terms": {
              "uniqid": ["a65947a7-e691-4b4b-993c-b1040032df41"]
            }
          }
        ]
      }
    }
  }
}
```

### 响应格式
```json
{
  "hits": {
    "hits": [
      {
        "_source": {
          "uniqid": "案例唯一标识",
          "case_number": "案号",
          "court": "审理法院",
          "judge_date": "判决日期",
          "case_cause": "案由",
          "procedure": "审理程序",
          "doctype": "文书类型",
          "parties": "当事人信息",
          "fact": "案件事实",
          "dispute_focus": "争议焦点",
          "judgment_reason": "裁判理由",
          "judgment_result": "裁判结果",
          "full_text": "完整文书内容",
          "other_fields": "其他完整字段"
        }
      }
    ],
    "total": 1
  }
}
```

**注意**: 脚本会自动提取 `_source` 字段作为案例完整信息。

### 参数说明

| 参数名 | 类型 | 说明 | 示例 |
|--------|------|------|------|
| uniqid | array | 案例唯一标识列表 | ["a65947a7-e691-4b4b-993c-b1040032df41"] |

## 错误处理

### HTTP状态码
- 200: 请求成功
- 400: 请求参数错误
- 500: 服务器内部错误

### 常见错误
- 缺少必填参数
- 参数格式错误
- 筛选条件不匹配任何案例
- 服务器连接失败
- uniqid无效或不存在

## 使用示例

### Python示例
```python
import requests

# 第一步：检索类似案例
search_url = "http://192.168.10.111:9632/simliar/case/es"
search_data = {
    "question": "违约金计算标准",
    "casecause": "房屋租赁合同纠纷",
    "top_k": 10,
    "court": ["北京市朝阳区人民法院"],
    "judgeyear": [2022, 2023]
}
search_response = requests.post(search_url, json=search_data)
search_result = search_response.json()

# 第二步：获取完整案例信息
detail_url = "http://192.168.61.16/dbApi/wsSearch"
unique_ids = [case.get("uniqid") for case in search_result.get("cases", [])]
detail_data = {
    "query": {
        "query": {
            "bool": {
                "must": [
                    {
                        "terms": {
                            "uniqid": unique_ids
                        }
                    }
                ]
            }
        }
    }
}
detail_response = requests.post(detail_url, json=detail_data)
detail_result = detail_response.json()
cases = [hit.get("_source") for hit in detail_result.get("hits", {}).get("hits", [])]
```

### 命令行示例
```bash
python scripts/fayan_search.py \
  --question "违约金计算标准" \
  --case-cause "房屋租赁合同纠纷" \
  --top-k 10 \
  --request-output ./legal-case-retrieval-v3/output/request.json \
  --response-output ./legal-case-retrieval-v3/output/response.json
```

### 使用自定义API地址
```bash
python scripts/fayan_search.py \
  --question "违约金计算标准" \
  --case-cause "房屋租赁合同纠纷" \
  --api-url "http://your-api/search" \
  --detail-api-url "http://your-api/detail" \
  --top-k 10
```

## 注意事项
- 筛选参数均为可选，可根据需要组合使用
- 类案检索API返回结果按相关性分数排序
- 案例详情API会返回案例的所有字段，包括完整文书内容
- 建议合理设置top_k值，避免返回过多结果影响性能
- API部署在同服务器环境，无需额外认证
- 如果详情API调用失败，脚本会使用检索API返回的部分字段
