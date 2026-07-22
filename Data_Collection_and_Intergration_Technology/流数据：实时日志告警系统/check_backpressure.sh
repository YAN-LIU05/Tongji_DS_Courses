# --- 检查反压的脚本 check_backpressure.sh ---
#!/bin/bash
JOB_ID=5198815b9a8153a9d9027d96f8d17fd5
if [ -z "$JOB_ID" ]; then
    echo "No running job found."
    exit 1
fi
echo "Checking backpressure for Job ID: $JOB_ID"

# 获取所有 vertex ID
VERTEX_IDS=$(curl -s http://localhost:8081/jobs/$JOB_ID | jq -r '.vertices[].id')

while true; do
    echo "--- $(date) ---"
    for id in $VERTEX_IDS; do
        # 获取算子名称
        name=$(curl -s http://localhost:8081/jobs/$JOB_ID | jq -r --arg id "$id" '.vertices[] | select(.id==$id) | .name')
        # 查询反压状态
        status=$(curl -s http://localhost:8081/jobs/$JOB_ID/vertices/$id/backpressure | jq -r '.status')
        echo "Vertex: $name | Status: $status"
    done
    sleep 5 # 每5秒检查一次
done