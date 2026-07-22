import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;

import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.fs.FSDataInputStream;
import org.apache.hadoop.fs.FileSystem;
import org.apache.hadoop.fs.Path;

public final class HdfsFileReader {
    private static final String DEFAULT_HDFS_PATH = "/my_doc/sample.txt";

    private HdfsFileReader() {
    }

    public static void main(String[] args) {
        String hdfsPath = args.length > 0 ? args[0] : DEFAULT_HDFS_PATH;

        try {
            printFile(hdfsPath);
        } catch (IOException exception) {
            System.err.printf("Failed to read HDFS file '%s': %s%n", hdfsPath, exception.getMessage());
            System.exit(1);
        }
    }

    private static void printFile(String hdfsPath) throws IOException {
        Configuration configuration = new Configuration();
        Path path = new Path(hdfsPath);

        try (FileSystem fileSystem = FileSystem.get(configuration)) {
            if (!fileSystem.exists(path)) {
                throw new IOException("file does not exist");
            }

            try (
                FSDataInputStream inputStream = fileSystem.open(path);
                BufferedReader reader = new BufferedReader(
                    new InputStreamReader(inputStream, StandardCharsets.UTF_8)
                )
            ) {
                String line;
                while ((line = reader.readLine()) != null) {
                    System.out.println(line);
                }
            }
        }
    }
}
