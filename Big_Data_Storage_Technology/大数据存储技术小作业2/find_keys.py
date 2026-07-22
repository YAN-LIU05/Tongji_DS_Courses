import happybase

conn = happybase.Connection("localhost", 9090)
table = conn.table("car_sales")

c1001_key = None
pending_key = None
sold_key = None

for key, data in table.scan(columns=[b"info:car_id", b"info:status"]):
    rowkey = key.decode("utf-8")
    car_id = data.get(b"info:car_id", b"").decode("utf-8")
    status = data.get(b"info:status", b"").decode("utf-8")

    if car_id == "C1001":
        c1001_key = rowkey

    if status == "pending" and pending_key is None:
        pending_key = rowkey

    if status == "sold" and sold_key is None:
        sold_key = rowkey

    if c1001_key and pending_key and sold_key:
        break

print("C1001_ROWKEY =", c1001_key)
print("PENDING_ROWKEY =", pending_key)
print("SOLD_ROWKEY =", sold_key)

conn.close()
