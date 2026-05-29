# 测试题 一 #

import csv
import time
from pathlib import Path
import requests


URL = "https://www.chinamoney.com.cn/ags/ms/cm-u-bond-md/BondMarketInfoListEN"
OUTPUT_FILE = Path("output/treasury_bonds_2023.csv")
PAGE_SIZE = 15

COLUMNS = ["ISIN", "Bond Code", "Issuer", "Bond Type", "Issue Date", "Latest Rating"]

# 调用网站api抓取一页数据 #
def fetch_page(page_no):
    payload = {
        "pageNo": str(page_no),
        "pageSize": str(PAGE_SIZE),
        "isin": "",
        "bondCode": "",
        "issueEnty": "",
        "bondType": "100001",
        "couponType": "",
        "issueYear": "2023",
        "rtngShrt": "",
        "bondSpclPrjctVrty": "",
    }
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Referer": "https://www.chinamoney.com.cn/english/bdInfo/",
        "X-Requested-With": "XMLHttpRequest",
    }
    resp = requests.post(URL, data=payload, headers=headers, timeout=20)
    resp.raise_for_status()
    data = resp.json()["data"]
    return data.get("resultList", []), int(data.get("total") or 0)

# 清洗单元格 #
def clean(value):
    value = "" if value is None else str(value).strip()
    return "" if value in {"---", "--", "null", "None"} else value

# 映射为csv输出列明 #
def convert(row):
    return {
        "ISIN": clean(row.get("isin")),
        "Bond Code": clean(row.get("bondCode")),
        "Issuer": clean(row.get("entyFullName")),
        "Bond Type": clean(row.get("bondType")),
        "Issue Date": clean(row.get("issueStartDate")),
        "Latest Rating": clean(row.get("debtRtng")),
    }

# 分页拉取所有数据 #
def fetch_all():
    rows = []
    total = 0
    page_no = 1

    while True:
        page_rows, total = fetch_page(page_no)
        rows.extend(convert(row) for row in page_rows)
        print(f"page {page_no}: {len(rows)} / {total}")

        if not page_rows or len(rows) >= total:
            break

        page_no += 1
        time.sleep(0.3)

    if total and len(rows) != total:
        raise RuntimeError(f"incomplete data: got {len(rows)}, expected {total}")

    return rows

# 保存到csv中 #
def save_csv(rows):
    OUTPUT_FILE.parent.mkdir(exist_ok=True)
    with OUTPUT_FILE.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=COLUMNS)
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    rows = fetch_all()
    save_csv(rows)
    print(f"saved {len(rows)} rows to {OUTPUT_FILE}")
