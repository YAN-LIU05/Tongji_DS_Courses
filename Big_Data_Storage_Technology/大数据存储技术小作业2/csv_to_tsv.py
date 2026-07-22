import csv
from datetime import datetime

def format_date(date_str):
    date_str = date_str.strip()
    for fmt in ("%Y/%m/%d", "%Y-%m-%d"):
        try:
            return datetime.strptime(date_str, fmt).strftime("%Y%m%d")
        except ValueError:
            pass
    raise ValueError(f"无法解析日期格式: {date_str}")

def format_price(price):
    return f"{float(price):010.2f}"

def make_rowkey(row):
    return f'{row["city"].strip()}#{format_date(row["sale_date"])}#{row["car_id"].strip()}'

count = 0

with open("car_sales_data.csv", "r", encoding="utf-8-sig") as fin, \
     open("car_sales_data.tsv", "w", encoding="utf-8") as fout:

    reader = csv.DictReader(fin)

    for row in reader:
        rowkey = make_rowkey(row)

        fields = [
            rowkey,
            row["car_id"].strip(),
            row["brand"].strip(),
            row["owner_name"].strip(),
            row["status"].strip(),
            row["city"].strip(),
            format_price(row["price"]),
            format_date(row["sale_date"])
        ]

        fout.write("\t".join(fields) + "\n")
        count += 1

print(f"car_sales.tsv 生成完成，共 {count} 条记录")
