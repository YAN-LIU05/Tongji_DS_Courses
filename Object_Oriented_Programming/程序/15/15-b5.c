/* 2352018 大数据 刘彦 */
/* 2354040 杨安淇 2351753 黄保翔 2350488 邱恺煜 2351044 崔艺洋 2252036 苏惠 2152131 吴洪蕊 */
#define _CRT_SECURE_NO_WARNINGS
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

// 打印程序用法
void printUsage()
{
    printf("Usage : 15-b5 --infile hex格式文件 --outfile bin格式文件\n");
    printf("        15-b5 --infile a.hex --outfile a.bin\n");
}

// 判断一个字符串是否是有效的十六进制数（两个字符）
int valid_hex(const char* hexStr)
{
    if (hexStr == NULL || strlen(hexStr) != 2)
        return 0;  // 十六进制字节必须有两个字符

    // 检查每个字符是否是有效的十六进制字符
    for (int i = 0; i < 2; i++)
    {
        if (!((hexStr[i] >= '0' && hexStr[i] <= '9') ||
            (hexStr[i] >= 'a' && hexStr[i] <= 'f') ||
            (hexStr[i] >= 'A' && hexStr[i] <= 'F')))
        {
            return 0;  // 如果字符不是合法的十六进制字符，返回0
        }
    }
    return 1;  // 如果所有字符都是十六进制字符，则返回1
}

// 将十六进制文件转换为二进制文件
void hexToBinary(const char* infile, const char* outfile)
{
    FILE* inFile = fopen(infile, "r");
    if (!inFile)
    {
        fprintf(stderr, "输入文件 %s 打开失败!\n", infile);
        return;
    }

    FILE* outFile = fopen(outfile, "wb");
    if (!outFile)
    {
        fprintf(stderr, "输出文件 %s 打开失败!\n", outfile);
        fclose(inFile);
        return;
    }

    const int MAX_FILENAME_LENGTH = 1024;
    char* line = (char*)malloc(MAX_FILENAME_LENGTH * sizeof(char));  // 动态分配内存来读取每一行
    while (fgets(line, MAX_FILENAME_LENGTH, inFile))
    {
        char* hexByte = strtok(line, " \n");  // 读取每一行的第一个十六进制字节
        while (hexByte != NULL)
        {
            // 跳过 "-" 符号
            if (strcmp(hexByte, "-") == 0)
            {
                hexByte = strtok(NULL, " \n");
                continue;
            }

            // 只处理有效的十六进制字节
            if (valid_hex(hexByte))
            {
                unsigned char byte = (unsigned char)strtol(hexByte, NULL, 16);
                fputc(byte, outFile);
            }

            hexByte = strtok(NULL, " \n");  // 继续处理下一个十六进制字节
        }
    }

    free(line);  // 释放内存
    fclose(inFile);
    fclose(outFile);
}

// 处理命令行参数
int main(int argc, char* argv[])
{
    char* infile = NULL;
    char* outfile = NULL;
    int hasInfile = 0, hasOutfile = 0;

    for (int i = 1; i < argc; ++i)
    {
        if (strcmp(argv[i], "--infile") == 0 && i + 1 < argc)
        {
            infile = (char*)malloc(strlen(argv[++i]) + 1);
            strcpy(infile, argv[i]);
            hasInfile = 1;
        }
        else if (strcmp(argv[i], "--outfile") == 0 && i + 1 < argc)
        {
            outfile = (char*)malloc(strlen(argv[++i]) + 1);
            strcpy(outfile, argv[i]);
            hasOutfile = 1;
        }
        else
        {
            printUsage();
            return 1;
        }
    }

    if (!hasInfile)
    {
        printUsage();
        return 1;
    }

    if (!hasOutfile)
    {
        printUsage();
        return 1;
    }

    hexToBinary(infile, outfile);

    free(infile);
    free(outfile);

    return 0;
}
