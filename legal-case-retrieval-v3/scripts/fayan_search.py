#!/usr/bin/env python3
"""
法研类案库检索脚本 v2.0
用于检索类似案例，获取案件信息、争议焦点、裁判理由等

检索流程：
1. 明确检索目标与核验口径（默认检索近五年的案例）
2. 预检索：理解用户意图，生成关键词组
3. 整理多组关键词
4. 执行数据库检索（智能分拣字段，精准匹配）
5. 输出结构化类案检索报告

输出字段：
- uniqid: 案例唯一标识
- title: 案例标题
- 案件名称/case_name
- 案号/case_id
- referencetype: 案例级别
- 相关内容/chunk
- 裁判年份/judgeyear
- 检索方式/search_type
"""

import argparse
import json
import sys
import re
from datetime import datetime
import requests


# 默认API地址
DEFAULT_SEARCH_API_URL = "http://192.168.10.111:9632/simliar/case/es"
DEFAULT_DETAIL_API_URL = "http://192.168.61.16/dbApi/wsSearch"


def get_default_judge_years():
    """获取默认近五年的判决年份"""
    current_year = datetime.now().year
    return list(range(current_year - 4, current_year + 1))


def analyze_question_intent(question: str, case_cause: str = ""):
    """
    预检索：分析用户检索意图，理解潜在法条结构，生成关键词组
    
    Args:
        question: 用户检索问题
        case_cause: 案由（可选）
    
    Returns:
        dict: 包含关键词组、检索目标、核验口径等
    """
    # 核心关键词（直接从问题提取）
    core_keywords = []
    
    # 补充关键词（相关法律概念）
    related_keywords = []
    
    # 提取问题中的关键法律术语
    question_lower = question.lower()
    
    # 法律概念映射
    legal_concepts = {
        "盗窃": ["入户盗窃", "多次盗窃", "扒窃", "携带凶器盗窃"],
        "抢劫": ["入户抢劫", "持刀抢劫", "冒充军警抢劫"],
        "故意伤害": ["轻微伤", "轻伤", "重伤", "正当防卫"],
        "诈骗": ["电信诈骗", "网络诈骗", "合同诈骗", "集资诈骗"],
        "毒品": ["贩卖毒品", "持有毒品", "运输毒品", "容留他人吸毒"],
    }
    
    # 从问题提取核心词
    for concept, related in legal_concepts.items():
        if concept in question_lower:
            core_keywords.append(concept)
            related_keywords.extend(related)
    
    # 如果没有匹配，使用原始问题作为关键词
    if not core_keywords:
        core_keywords = [question]
    
    # 生成关键词组
    keyword_groups = [
        # 组1：原始问题
        {"name": "原始问题", "keywords": [question], "weight": 1.0},
        # 组2：核心关键词
        {"name": "核心关键词", "keywords": core_keywords, "weight": 0.9},
    ]
    
    if related_keywords:
        keyword_groups.append({
            "name": "相关法律概念",
            "keywords": list(set(related_keywords)),
            "weight": 0.7
        })
    
    # 确定检索目标
    retrieval_goal = f"检索{case_cause if case_cause else '相关'}案例" if case_cause else "类案检索"
    
    # 确定核验口径
    verification_criteria = "命中条件：案例内容包含用户问题中的关键词"
    
    return {
        "retrieval_goal": retrieval_goal,
        "verification_criteria": verification_criteria,
        "keyword_groups": keyword_groups,
        "question": question,
        "case_cause": case_cause
    }


def search_similar_cases(
    question: str,
    case_cause: str = "",
    top_k: int = 10,
    court: list = None,
    judge_year: list = None,
    case_type: list = None,
    procedure: list = None,
    doctype: list = None,
    province: list = None,
    city: list = None,
    court_level: list = None,
    api_url: str = None,
    detail_api_url: str = None,
    use_default_years: bool = True
):
    """
    检索类似案例并获取完整信息
    
    检索流程：
    1. 明确检索目标与核验口径
    2. 预检索：分析用户意图，生成关键词组
    3. 整理多组关键词
    4. 执行数据库检索
    5. 输出结构化类案检索报告

    Args:
        question: 检索问题
        case_cause: 案由
        top_k: 返回结果数量
        court: 法院列表
        judge_year: 判决年份列表（默认近五年）
        case_type: 案件类型列表
        procedure: 审理程序列表
        doctype: 文书类型列表
        province: 省份列表
        city: 城市列表
        court_level: 法院层级列表
        api_url: 类案检索API地址
        detail_api_url: 案例详情API地址
        use_default_years: 是否使用默认近五年年份

    Returns:
        结构化类案检索报告
    """
    # ========== 步骤1：明确检索目标与核验口径 ==========
    api_url = api_url or DEFAULT_SEARCH_API_URL
    detail_api_url = detail_api_url or DEFAULT_DETAIL_API_URL
    
    # 使用默认近五年年份
    if judge_year is None and use_default_years:
        judge_year = get_default_judge_years()
    
    # ========== 步骤2：预检索 - 分析用户意图 ==========
    intent_analysis = analyze_question_intent(question, case_cause)
    
    # ========== 步骤3&4：整理关键词并执行检索 ==========
    data = {
        "question": question,
        "casecause": case_cause,
        "top_k": top_k,
        "court": court if court else [],
        "judgeyear": judge_year if judge_year else [],
        "casetype": case_type if case_type else [],
        "procedure": procedure if procedure else [],
        "doctype": doctype if doctype else [],
        "province": province if province else [],
        "city": city if city else [],
        "courtlevel": court_level if court_level else []
    }

    headers = {
        "Content-Type": "application/json"
    }

    try:
        # ========== 步骤4：执行数据库检索 ==========
        # 调用类案检索API
        response = requests.post(api_url, headers=headers, json=data, timeout=30)

        if response.status_code >= 400:
            raise Exception(f"类案检索HTTP请求失败: 状态码 {response.status_code}, 响应内容: {response.text}")

        result = response.json()
        
        # 从不同字段提取案例数据
        cases = []
        
        # 优先从 data 字段提取（包含 case_id）
        if isinstance(result, dict):
            if "data" in result and result["data"]:
                cases = result["data"]
            elif "cases" in result and result["cases"]:
                cases = result["cases"]
            else:
                # 从 _first, _second 等字段提取
                for key in ["_first", "_second", "_third", "_fifth"]:
                    if key in result and result[key]:
                        cases = result[key]
                        break

        if not cases:
            # 返回空结果
            return generate_empty_report(
                question=question,
                case_cause=case_cause,
                judge_year=judge_year,
                api_url=api_url,
                data=data,
                intent_analysis=intent_analysis
            )

        # ========== 步骤5：构建结构化案例列表 ==========
        structured_cases = []
        for case in cases:
            # 提取字段
            uniqid = case.get("uniqid", "")
            title = case.get("title", "")
            case_id = case.get("case_id") or case.get("caseid", "")
            case_name = case.get("case_name", "")
            referencetype = case.get("referencetype", "")
            chunk = case.get("chunk", "")
            search_type = case.get("search_type", "")
            
            # 提取裁判年份
            judgeyear = None
            # 从case_id中提取年份
            if case_id:
                year_match = re.findall(r'（(\d{4})）', str(case_id))
                if year_match:
                    judgeyear = int(year_match[0])
            # 从chunk中提取年份
            if not judgeyear:
                year_matches = re.findall(r'20[0-2]\d{1}年', chunk)
                if year_matches:
                    judgeyear = int(year_matches[0].replace('年', ''))
            
            structured_case = {
                "uniqid": uniqid,
                "title": title,
                "case_name": case_name,
                "case_id": case_id,
                "referencetype": referencetype,
                "chunk": clean_html_tags(chunk),
                "judgeyear": judgeyear,
                "search_type": search_type
            }
            
            # 过滤掉无效案例
            if uniqid or case_id or chunk:
                structured_cases.append(structured_case)

        # 生成检索结论
        conclusion = generate_conclusion(
            question=question,
            case_cause=case_cause,
            total_cases=len(structured_cases),
            year_range=judge_year,
            keyword_groups=intent_analysis["keyword_groups"]
        )

        # 构建最终报告
        report = {
            "report_header": {
                "title": "类案检索报告",
                "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "retrieval_goal": intent_analysis["retrieval_goal"],
                "verification_criteria": intent_analysis["verification_criteria"],
                "api_url": api_url,
                "request_params": data
            },
            "intent_analysis": intent_analysis,
            "retrieval_info": {
                "question": question,
                "case_cause": case_cause,
                "judge_year": judge_year,
                "top_k": top_k,
                "total_results": len(structured_cases)
            },
            "conclusion": conclusion,
            "cases": structured_cases
        }

        return report

    except requests.exceptions.RequestException as e:
        raise Exception(f"法研类案库检索失败: {str(e)}")


def clean_html_tags(text: str) -> str:
    """清理HTML标签"""
    if not text:
        return ""
    # 替换常见的HTML标签
    text = re.sub(r'<font[^>]*>', '', text)
    text = re.sub(r'</font>', '', text)
    return text.strip()


def generate_empty_report(question: str, case_cause: str, judge_year: list, api_url: str, data: dict, intent_analysis: dict) -> dict:
    """生成空结果报告"""
    return {
        "report_header": {
            "title": "类案检索报告",
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "retrieval_goal": intent_analysis["retrieval_goal"],
            "verification_criteria": intent_analysis["verification_criteria"],
            "api_url": api_url,
            "request_params": data
        },
        "intent_analysis": intent_analysis,
        "retrieval_info": {
            "question": question,
            "case_cause": case_cause,
            "judge_year": judge_year,
            "total_results": 0
        },
        "conclusion": {
            "summary": "未检索到符合条件的案例",
            "possible_reasons": [
                "检索条件过于严格",
                "数据库中暂无符合条件案例",
                "关键词表述方式可调整"
            ],
            "suggestions": [
                "尝试扩大检索年份范围",
                "调整或简化关键词",
                "去掉部分筛选条件"
            ]
        },
        "cases": []
    }


def generate_conclusion(question: str, case_cause: str, total_cases: int, year_range: list, keyword_groups: list) -> dict:
    """生成检索结论"""
    year_str = f"{min(year_range)}-{max(year_range)}" if year_range else "不限"
    
    summary = f"根据检索条件「{question}」{'，案由：' + case_cause if case_cause else ''}，在{year_str}年度裁判文书库中检索到{total_cases}件相关案例。"
    
    # 关键词组说明
    keywords_used = [g["name"] for g in keyword_groups]
    
    return {
        "summary": summary,
        "year_range": year_str,
        "keywords_used": keywords_used,
        "total_cases": total_cases,
        "case_cause": case_cause
    }


def main():
    parser = argparse.ArgumentParser(
        description='法研类案库检索工具 v2.0',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法：
  python fayan_search.py --question "入户盗窃" --case-cause "盗窃罪" --top-k 10
  python fayan_search.py --question "诈骗罪构成要件" --judge-year 2023 2024
  python fayan_search.py --question "正当防卫" --province "广东" "浙江"
        """
    )
    
    parser.add_argument('--question', required=True, help='检索问题')
    parser.add_argument('--case-cause', default='', help='案由')
    parser.add_argument('--top-k', type=int, default=10, help='返回结果数量（默认10）')
    parser.add_argument('--api-url', default=DEFAULT_SEARCH_API_URL, help='类案检索API地址')
    parser.add_argument('--detail-api-url', default=DEFAULT_DETAIL_API_URL, help='案例详情API地址')
    parser.add_argument('--court', nargs='*', help='法院列表')
    parser.add_argument('--judge-year', nargs='*', type=int, help=f'判决年份列表（默认近五年，当前为{get_default_judge_years()}）')
    parser.add_argument('--case-type', nargs='*', help='案件类型列表')
    parser.add_argument('--procedure', nargs='*', help='审理程序列表')
    parser.add_argument('--doctype', nargs='*', help='文书类型列表')
    parser.add_argument('--province', nargs='*', help='省份列表')
    parser.add_argument('--city', nargs='*', help='城市列表')
    parser.add_argument('--court-level', nargs='*', help='法院层级列表')
    parser.add_argument('--no-default-years', action='store_true', help='不使用默认近五年年份')
    parser.add_argument('--request-output', help='检索语句输出文件路径（JSON格式）')
    parser.add_argument('--response-output', help='API返回结果输出文件路径（JSON格式）')
    parser.add_argument('--output', help='综合输出文件路径（可选）')

    args = parser.parse_args()

    try:
        # 执行检索
        result = search_similar_cases(
            question=args.question,
            case_cause=args.case_cause,
            top_k=args.top_k,
            court=args.court,
            judge_year=args.judge_year,
            case_type=args.case_type,
            procedure=args.procedure,
            doctype=args.doctype,
            province=args.province,
            city=args.city,
            court_level=args.court_level,
            api_url=args.api_url,
            detail_api_url=args.detail_api_url,
            use_default_years=not args.no_default_years
        )

        # 保存检索语句
        if args.request_output:
            with open(args.request_output, 'w', encoding='utf-8') as f:
                json.dump(result["report_header"], f, ensure_ascii=False, indent=2)
            print(f"检索语句已保存到: {args.request_output}")

        # 保存API返回结果
        if args.response_output:
            with open(args.response_output, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            print(f"检索报告已保存到: {args.response_output}")

        # 输出综合结果
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            print(f"综合结果已保存到: {args.output}")
        else:
            # 输出格式化报告
            print("\n" + "="*80)
            print("类 案 检 索 报 告")
            print("="*80)
            print(f"\n【检索结论】{result['conclusion']['summary']}")
            print(f"\n【使用关键词组】{', '.join(result['conclusion']['keywords_used'])}")
            print(f"\n【案例列表】（共 {result['conclusion']['total_cases']} 件）")
            print("-"*80)
            
            for i, case in enumerate(result['cases'], 1):
                print(f"\n{i}. uniqid: {case['uniqid']}")
                print(f"   案例标题: {case['title']}")
                print(f"   案号: {case['case_id']}")
                print(f"   案例级别: {case['referencetype']}")
                print(f"   裁判年份: {case['judgeyear']}")
                print(f"   检索方式: {case['search_type']}")
                print(f"   相关内容: {case['chunk'][:150]}...")
            
            print("\n" + "="*80)

        return 0

    except Exception as e:
        print(f"错误: {str(e)}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())