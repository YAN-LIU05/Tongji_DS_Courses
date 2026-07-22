import csv
import time
import happybase
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
    # 固定宽度，方便 HBase 用字符串比较价格大小
    return f"{float(price):010.2f}"

def make_rowkey(row):
    # RowKey = city#yyyyMMdd#car_id
    return f'{row["city"].strip()}#{format_date(row["sale_date"])}#{row["car_id"].strip()}'

conn = happybase.Connection("localhost", 9090)
table = conn.table("car_sales")

start = time.time()
count = 0

with open("car_sales_data.csv", "r", encoding="utf-8-sig") as f:
    reader = csv.DictReader(f)

    with table.batch(batch_size=1000) as batch:
        for row in reader:
            rowkey = make_rowkey(row)

            batch.put(rowkey, {
                b"info:car_id": row["car_id"].strip().encode("utf-8"),
                b"info:brand": row["brand"].strip().encode("utf-8"),
                b"info:owner_name": row["owner_name"].strip().encode("utf-8"),
                b"info:status": row["status"].strip().encode("utf-8"),

                b"sale:city": row["city"].strip().encode("utf-8"),
                b"sale:price": format_price(row["price"]).encode("utf-8"),
                b"sale:sale_date": format_date(row["sale_date"]).encode("utf-8"),
            })

            count += 1

end = time.time()

print(f"普通 put 插入记录数：{count}")
print(f"普通 put 插入耗时：{end - start:.4f} 秒")

conn.close()
