import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.hbase.HBaseConfiguration;
import org.apache.hadoop.hbase.TableName;
import org.apache.hadoop.hbase.client.CheckAndMutate;
import org.apache.hadoop.hbase.client.CheckAndMutateResult;
import org.apache.hadoop.hbase.client.Connection;
import org.apache.hadoop.hbase.client.ConnectionFactory;
import org.apache.hadoop.hbase.client.Get;
import org.apache.hadoop.hbase.client.Put;
import org.apache.hadoop.hbase.client.Result;
import org.apache.hadoop.hbase.client.Table;
import org.apache.hadoop.hbase.util.Bytes;

public class CheckAndPutDemo {
    private static final byte[] FAMILY = Bytes.toBytes("info");
    private static final byte[] QUALIFIER = Bytes.toBytes("status");

    public static String getStatus(Table table, String rowkey) throws Exception {
        Get get = new Get(Bytes.toBytes(rowkey));
        get.addColumn(FAMILY, QUALIFIER);
        Result result = table.get(get);
        byte[] value = result.getValue(FAMILY, QUALIFIER);
        return value == null ? "NULL" : Bytes.toString(value);
    }

    public static boolean checkAndPutStatus(
            Table table,
            String rowkey,
            String expectedStatus,
            String newStatus
    ) throws Exception {
        Put put = new Put(Bytes.toBytes(rowkey));
        put.addColumn(FAMILY, QUALIFIER, Bytes.toBytes(newStatus));

        CheckAndMutate checkAndMutate = CheckAndMutate
                .newBuilder(Bytes.toBytes(rowkey))
                .ifEquals(FAMILY, QUALIFIER, Bytes.toBytes(expectedStatus))
                .build(put);

        CheckAndMutateResult result = table.checkAndMutate(checkAndMutate);
        return result.isSuccess();
    }

    public static void main(String[] args) throws Exception {
        String pendingRowKey = "上海#20240211#C1052";
        String soldRowKey = "上海#20240126#C1156";

        Configuration conf = HBaseConfiguration.create();

        try (Connection connection = ConnectionFactory.createConnection(conf);
             Table table = connection.getTable(TableName.valueOf("car_sales"))) {

            System.out.println("========== 成功场景 ==========");
            System.out.println("操作前状态：" + pendingRowKey + " " + getStatus(table, pendingRowKey));

            boolean success = checkAndPutStatus(table, pendingRowKey, "pending", "sold");

            System.out.println("checkAndPut 返回：" + success);
            System.out.println("操作后状态：" + pendingRowKey + " " + getStatus(table, pendingRowKey));

            System.out.println();
            System.out.println("========== 失败场景 ==========");
            System.out.println("操作前状态：" + soldRowKey + " " + getStatus(table, soldRowKey));

            boolean fail = checkAndPutStatus(table, soldRowKey, "pending", "sold");

            System.out.println("checkAndPut 返回：" + fail);
            System.out.println("操作后状态：" + soldRowKey + " " + getStatus(table, soldRowKey));
        }
    }
}
