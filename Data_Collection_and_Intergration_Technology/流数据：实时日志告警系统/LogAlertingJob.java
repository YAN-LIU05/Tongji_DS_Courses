import org.apache.flink.api.common.eventtime.WatermarkStrategy;
import org.apache.flink.api.common.serialization.SimpleStringSchema;
import org.apache.flink.connector.kafka.source.KafkaSource;
import org.apache.flink.connector.kafka.source.enumerator.initializer.OffsetsInitializer;
import org.apache.flink.streaming.api.datastream.DataStream;
import org.apache.flink.streaming.api.environment.StreamExecutionEnvironment;

public class LogAlertingJob {
    public static void main(String[] args) throws Exception {
        // 1. 获取流执行环境
        final StreamExecutionEnvironment env = StreamExecutionEnvironment.getExecutionEnvironment();

        // 2. 配置 Kafka Source
        KafkaSource<String> source = KafkaSource.<String>builder()
            .setBootstrapServers("localhost:9092") // Kafka 服务器地址
            .setTopics("log-stream")               // 消费的 Topic
            .setGroupId("flink-log-consumer-group") // 消费者组ID
            .setStartingOffsets(OffsetsInitializer.latest()) // 从最新的消息开始消费
            .setValueOnlyDeserializer(new SimpleStringSchema()) // 反序列化器
            .build();

        // 3. 从 Kafka Source 创建数据流
        DataStream<String> kafkaStream = env.fromSource(source, WatermarkStrategy.noWatermarks(), "Kafka Source");

        // 4. 定义处理逻辑：【临时修改】不过滤，直接打印所有日志
        DataStream<String> errorStream = kafkaStream
            .filter(log -> log.contains("\"level\": \"ERROR\""))
            .map(log -> "ALERT! High-priority issue detected: " + log);

        // 添加一个新的 map 算子来计算延迟并格式化输出
        DataStream<String> alertStream = errorStream.map(log -> {
            // 简陋的 JSON 解析：通过字符串操作找到时间戳
            try {
                String timestampStr = log.split("\"timestamp\": ")[1].split(",")[0].trim();
                long producerTimestamp = Long.parseLong(timestampStr);
                long flinkTimestamp = System.currentTimeMillis();
                long latency = flinkTimestamp - producerTimestamp;
                return "ALERT! High-priority issue detected: " + log + " | Latency: " + latency + " ms";
            } catch (Exception e) {
                return "ALERT! Could not parse log: " + log;
            }
        });

        // 5. 输出结果到控制台【直接打印原始流】
        // errorStream.print();
        alertStream.print(); 

        // 6. 执行作业
        env.execute("Real-time Log Alerting System");
    }
}