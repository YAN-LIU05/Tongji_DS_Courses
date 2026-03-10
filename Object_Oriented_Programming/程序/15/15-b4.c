/* 2352018 大数据 刘彦 */
#define _CRT_SECURE_NO_WARNINGS
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

// 定义换行符
#ifdef _WIN32
#define NEWLINE "\r\n"
#else
#define NEWLINE "\n"
#endif

#define MAX_FILENAME_LENGTH 1024

void printHex(const char* buffer, int totalBytes, FILE* out)
{
    int lines = (totalBytes + 15) / 16;
    int loop = 0;
    for (int line = 0; line < lines; ++line) 
    {
        int offset = line * 16;
        fprintf(out, "%08x  ", offset);

        for (int i = 0; i < 16; ++i) 
        {
            if (offset + i < totalBytes) 
            {
                fprintf(out, "%02x", (unsigned char)buffer[offset + i]);
                if (i == 7) 
                {
                    fprintf(out, " -");
                    loop = 1;
                }
                fprintf(out, " ");
            }
            else 
                fprintf(out, "   ");
        }

        fprintf(out, "    ");
        if (loop == 0)
            fprintf(out, "  ");
        loop = 0;

        for (int i = 0; i < 16; ++i) 
        {
            if (offset + i < totalBytes) 
            {
                unsigned char ch = buffer[offset + i];
                if (ch >= 33 && ch <= 126)
                    fputc(ch, out);
                else
                    fputc('.', out);
            }
        }
        fprintf(out, NEWLINE);
    }
}

void printUsage() 
{
    printf("Usage : 15-b4 --infile 原始文件 [ --outfile hex格式文件 ]\n");
    printf("        15-b4 --infile a.docx\n");
    printf("        15-b4 --infile a.docx --outfile a.hex\n");
}

int main(int argc, char* argv[]) 
{
    char infile[MAX_FILENAME_LENGTH] = { 0 };
    char outfile[MAX_FILENAME_LENGTH] = { 0 };
    int hasInfile = 0, hasOutfile = 0;

    for (int i = 1; i < argc; ++i) {
        if (strcmp(argv[i], "--infile") == 0 && i + 1 < argc)
        {
            strncpy(infile, argv[++i], MAX_FILENAME_LENGTH - 1);
            hasInfile = 1;
        }
        else if (strcmp(argv[i], "--outfile") == 0 && i + 1 < argc) 
        {
            strncpy(outfile, argv[++i], MAX_FILENAME_LENGTH - 1);
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

    FILE* inFile = fopen(infile, "rb");
    if (!inFile) 
    {
        fprintf(stderr, "输入文件%s打开失败!\n", infile);
        return 1;
    }

    fseek(inFile, 0, SEEK_END);
    int totalBytes = (int)ftell(inFile);
    fseek(inFile, 0, SEEK_SET);

    char* buffer = (char*)malloc(totalBytes);
    if (!buffer)
    {
        fprintf(stderr, "内存分配失败!\n");
        fclose(inFile);
        return 1;
    }

    // 读取文件内容
    if (fread(buffer, 1, totalBytes, inFile) != totalBytes) 
    {
        fprintf(stderr, "读取文件内容失败!\n");
        free(buffer);
        fclose(inFile);
        return 1;
    }
    fclose(inFile);

    if (hasOutfile)
    {
        FILE* outFile = fopen(outfile, "wb");
        if (!outFile) 
        {
            fprintf(stderr, "输出文件%s打开失败!\n", outfile);
            free(buffer);
            return 1;
        }
        printHex(buffer, totalBytes, outFile);
        fclose(outFile);
    }
    else 
        printHex(buffer, totalBytes, stdout);

    free(buffer); // 释放内存
    return 0;
}
