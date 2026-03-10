/* 2352018 大数据 刘彦 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define MAX_SIZE 4096

// 检查文件格式，返回相应的格式类型
const char* check_file_format(const char* file_path)
{
    FILE* file = fopen(file_path, "rb");
    if (!file)
        return "文件打开失败";

    char buffer[MAX_SIZE];
    int has_crlf = 0; // 是否包含 \r\n
    int has_lf = 0;   // 是否包含 \n

    // 遍历文件内容，检查换行符
    size_t bytesRead;
    while ((bytesRead = fread(buffer, 1, MAX_SIZE, file)) > 0)
    {
        for (size_t i = 0; i < bytesRead; ++i)
        {
            if (buffer[i] == '\r' && i + 1 < bytesRead && buffer[i + 1] == '\n')
            {
                has_crlf = 1;
                i++; // 跳过 '\n'
            }
            else if (buffer[i] == '\n')
                has_lf = 1;
        }
    }

    // 判断文件格式
    if (has_crlf && has_lf)
        return "文件格式无法识别";
    if (has_crlf)
        return "Windows格式";
    if (has_lf)
        return "Linux格式";

    return "文件格式无法识别"; // 如果文件内容为空或无法识别
}

// 将Windows格式文件转换为Linux格式
const char* convert_wtol(const char* file_in, const char* file_out)
{
    FILE* infile = fopen(file_in, "rb");
    if (!infile)
        return "文件打开失败";

    char buffer[MAX_SIZE];
    int is_windows = 0;
    int removed_cr_count = 0;  // 记录去除的0x0D数量

    // 检查是否是Windows格式
    size_t bytesRead;
    while ((bytesRead = fread(buffer, 1, MAX_SIZE, infile)) > 0)
    {
        for (size_t i = 0; i < bytesRead; ++i)
        {
            if (buffer[i] == '\r' && i + 1 < bytesRead && buffer[i + 1] == '\n')
            {
                is_windows = 1;
                break;
            }
        }
        if (is_windows)
            break;
    }

    if (!is_windows)
        return "文件格式无法识别";

    // 打开输出文件
    FILE* outfile = fopen(file_out, "wb");
    if (!outfile)
        return "文件写入失败";

    // 将 \r\n 转换为 \n 并写入目标文件
    fseek(infile, 0, SEEK_SET); // 重置文件指针
    while ((bytesRead = fread(buffer, 1, MAX_SIZE, infile)) > 0)
    {
        for (size_t i = 0; i < bytesRead; ++i)
        {
            if (buffer[i] == '\r' && i + 1 < bytesRead && buffer[i + 1] == '\n')
            {
                fputc('\n', outfile);
                i++; // 跳过 '\n'
                removed_cr_count++; // 记录去除的0x0D数量
            }
            else
                fputc(buffer[i], outfile);
        }
    }

    fclose(infile);
    fclose(outfile);

    // 输出转换信息
    printf("转换完成，去除%d个0x0D\n", removed_cr_count);

    return NULL; // 返回NULL时不做任何操作
}

// 将Linux格式文件转换为Windows格式
const char* convert_ltow(const char* file_in, const char* file_out)
{
    FILE* infile = fopen(file_in, "rb");
    if (!infile)
        return "文件打开失败";

    char buffer[MAX_SIZE];
    int is_linux = 0;
    int added_cr_count = 0;  // 记录添加的0x0D数量

    // 检查是否是Linux格式
    size_t bytesRead;
    while ((bytesRead = fread(buffer, 1, MAX_SIZE, infile)) > 0)
    {
        for (size_t i = 0; i < bytesRead; ++i)
        {
            if (buffer[i] == '\n')
            {
                if (i > 0 && buffer[i - 1] != '\r')
                {
                    is_linux = 1;
                    break;
                }
            }
        }
        if (is_linux)
            break;
    }

    if (!is_linux)
        return "文件格式无法识别";

    // 打开输出文件
    FILE* outfile = fopen(file_out, "wb");
    if (!outfile)
        return "文件写入失败";

    // 将 \n 转换为 \r\n 并写入目标文件
    fseek(infile, 0, SEEK_SET); // 重置文件指针
    while ((bytesRead = fread(buffer, 1, MAX_SIZE, infile)) > 0)
    {
        for (size_t i = 0; i < bytesRead; ++i)
        {
            if (buffer[i] == '\n')
            {
                fputc('\r', outfile);
                fputc('\n', outfile);
                added_cr_count++; // 记录添加的0x0D数量
            }
            else
                fputc(buffer[i], outfile);
        }
    }

    fclose(infile);
    fclose(outfile);

    // 输出转换信息
    printf("转换完成，加入%d个0x0D\n", added_cr_count);

    return NULL; // 返回NULL时不做任何操作
}

void printUsage()
{
    printf("Usage : 15-b6 --check 文件名 | --convert { wtol|ltow } 源文件名 目标文件名\n");
    printf("        15-b6 --check a.txt\n");
    printf("        15-b6 --convert wtol a.win.txt a.linux.txt\n");
    printf("        15-b6 --convert ltow a.linux.txt a.win.txt\n");
}

int main(int argc, char* argv[])
{
    if (argc < 3)
    {
        printUsage();
        return 1;
    }

    const char* command = argv[1];

    if (strcmp(command, "--check") == 0)
    {
        if (argc != 3)
        {
            printUsage();
            return 1;
        }
        const char* file_path = argv[2];
        printf("%s\n", check_file_format(file_path));
    }
    else if (strcmp(command, "--convert") == 0)
    {
        if (argc != 5)
        {
            printUsage();
            return 1;
        }
        const char* conversion_type = argv[2];
        const char* source_file = argv[3];
        const char* target_file = argv[4];

        if (strcmp(conversion_type, "wtol") == 0)
        {
            const char* result = convert_wtol(source_file, target_file);
            if (result != NULL)
                printf("%s\n", result);
        }
        else if (strcmp(conversion_type, "ltow") == 0)
        {
            const char* result = convert_ltow(source_file, target_file);
            if (result != NULL)
                printf("%s\n", result);
        }
        else
            printUsage();
    }
    else
    {
        printUsage();
    }

    return 0;
}
