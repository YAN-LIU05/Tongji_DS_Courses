import time
import random
from kafka import KafkaProducer
import json

    # 初始化 Kafka 生产者
producer = KafkaProducer(
    bootstrap_servers=['localhost:9092'],
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

    # 日志级别
log_levels = ['INFO', 'INFO', 'INFO', 'WARN', 'ERROR', 'DEBUG']

print("开始生成并发送日志...")
try:
    while True:
        log_message = {
            'timestamp': int(time.time() * 1000),
            'level': random.choice(log_levels),
            'message': f"This is a sample log message number {random.randint(1, 1000)}"
        }
            # 发送消息到 'log-stream' topic
        producer.send('log-stream', log_message)
        print(f"发送日志: {log_message}")
        time.sleep(random.uniform(0.5, 2)) # 随机间隔0.5到2秒
except KeyboardInterrupt:
    print("停止发送日志。")
finally:
    producer.close()