# 正则匹配核心代码 #

import re
from datetime import date

CUSTOM = "*自定义*"

# 年月日转换 #
def _date(match):
    y, m, d = map(int, match.groups())
    return date(y, m, d).isoformat()

# 提取标的证卷相关内容 #
def _extract_stock_code(text):
    compact = re.sub(r"\s+", "", text)
    pos = compact.find("标的证券")
    part = compact[pos : pos + 200] if pos >= 0 else compact
    match = re.search(r"(?:股票代码|证券代码)[:：]?(\d{6}\.(?:SH|SZ|BJ))", part, re.I)
    if not match and pos >= 0:
        match = re.search(r"(\d{6}\.(?:SH|SZ|BJ))", part, re.I)
    return match.group(1).upper() if match else ""

# 提取日期 #
def _extract_period(text):
    compact = re.sub(r"\s+", "", text)
    pos = compact.find("换股期限")
    part = compact[pos : pos + 220] if pos >= 0 else compact
    pattern = r"(\d{4})\s*(?:年|-|/|\.)\s*(\d{1,2})\s*(?:月|-|/|\.)\s*(\d{1,2})\s*日?"
    return [_date(m) for m in re.finditer(pattern, part)][:2]

# 正则搜索函数 #
def _run_regex(text, pattern):
    matches = list(re.finditer(pattern, text, re.S))
    if not matches:
        return ""

    result = []
    for match in matches:
        if match.lastindex is None:
            value = match.group(0).strip()
        elif match.lastindex == 1:
            value = match.group(1).strip()
        else:
            value = [v.strip() if v else "" for v in match.groups()]
        result.append(value)

    return result[0] if len(result) == 1 else result

# 提取结构化字段 #
def reg_search(text, regex_list):
    result = []
    extractors = {
        "标的证券": _extract_stock_code,
        "换股期限": _extract_period,
    }

    for rules in regex_list:
        item = {}
        for name, pattern in rules.items():
            if pattern == CUSTOM:
                item[name] = extractors.get(name, lambda _: "")(text)
            else:
                item[name] = _run_regex(text, pattern)
        result.append(item)

    return result
