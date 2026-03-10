/* 2352018 大数据 刘彦 */
/* 2350995 王喜临 2354040 杨安淇 2351044 崔艺洋 2353581 季节 2351753 黄保翔 2353572 汪君哲 */
#define _CRT_SECURE_NO_WARNINGS
#include <iostream>
#include <fstream>
#include <iomanip>
#include <cstring>
#include <sstream>

using namespace std;

void printUsage()
{
    cout << "Usage : 15-b2 --infile hex格式文件 --outfile bin格式文件" << endl;
    cout << "        15-b2 --infile a.hex --outfile a.bin" << endl;
}

// 判断一个字符串是否是有效的十六进制数（两个字符）
bool valid_hex(const char* hexStr)
{
    if (hexStr == nullptr || strlen(hexStr) != 2)
        return false;  // 十六进制字节必须有两个字符

    // 检查每个字符是否是有效的十六进制字符
    for (int i = 0; i < 2; i++)
    {
        if (!((hexStr[i] >= '0' && hexStr[i] <= '9') ||
            (hexStr[i] >= 'a' && hexStr[i] <= 'f') ||
            (hexStr[i] >= 'A' && hexStr[i] <= 'F')))
        {
            return false;  // 如果字符不是合法的十六进制字符，返回false
        }
    }
    return true;  // 如果所有字符都是十六进制字符，则返回true
}

// 将十六进制文件转换为二进制文件
void hexToBinary(const char* infile, const char* outfile)
{
    ifstream inFile(infile);
    if (!inFile)
    {
        cerr << "输入文件" << infile << "打开失败!" << endl;
        return;
    }

    ofstream outFile(outfile, ios::binary);
    if (!outFile)
    {
        cerr << "输出文件" << outfile << "打开失败!" << endl;
        return;
    }
    const int MAX_FILENAME_LENGTH = 1024;
    char* line = new char[MAX_FILENAME_LENGTH];  // 动态分配内存来读取每一行
    while (inFile.getline(line, MAX_FILENAME_LENGTH))
    {
#ifdef _WIN32
        char* address = strtok(line, " ");
#else
        strtok(line, " ");
#endif
         

        char* hexByte = strtok(nullptr, " ");  // 读取第一个十六进制字节
        while (hexByte != nullptr)
        {
            // 跳过 "-" 符号
            if (strcmp(hexByte, "-") == 0)
            {
                hexByte = strtok(nullptr, " ");
                continue;
            }

            // 只处理有效的十六进制字节
            if (valid_hex(hexByte))
            {
                unsigned char byte = static_cast<unsigned char>(strtol(hexByte, nullptr, 16));
                outFile.put(byte);
            }

            hexByte = strtok(nullptr, " ");  // 继续处理下一个十六进制字节
        }
    }

    delete[] line;  
    inFile.close();
    outFile.close();
}

// 处理命令行参数
int main(int argc, char* argv[])
{
    char* infile = nullptr;
    char* outfile = nullptr;
    bool hasInfile = false, hasOutfile = false;

    for (int i = 1; i < argc; ++i)
    {
        if (strcmp(argv[i], "--infile") == 0 && i + 1 < argc)
        {
            infile = new char[strlen(argv[++i]) + 1];
            strcpy(infile, argv[i]);
            hasInfile = true;
        }
        else if (strcmp(argv[i], "--outfile") == 0 && i + 1 < argc)
        {
            outfile = new char[strlen(argv[++i]) + 1];
            strcpy(outfile, argv[i]);
            hasOutfile = true;
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

    delete[] infile;
    delete[] outfile;

    return 0;
}
