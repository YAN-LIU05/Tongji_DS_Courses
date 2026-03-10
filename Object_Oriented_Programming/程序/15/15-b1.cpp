/* 2352018 大数据 刘彦 */
#define _CRT_SECURE_NO_WARNINGS
#include <iostream>
#include <fstream>
#include <iomanip>
#include <cstring>

using namespace std;

// 定义换行符
#ifdef _WIN32
#define NEWLINE "\r\n"
#else
#define NEWLINE "\n"
#endif

void printHex(char* buffer, int totalBytes, ostream & out)
{
    int lines = (totalBytes + 15) / 16;
    int loop = 0;
    for (int line = 0; line < lines; ++line)
    {
        int offset = line * 16;
        out << setw(8) << setfill('0') << hex << offset << "  ";

        for (int i = 0; i < 16; ++i)
        {
            if (offset + i < totalBytes)
            {
                out << setw(2) << setfill('0') << static_cast<int>(static_cast<unsigned char>(buffer[offset + i]));
                if (i == 7)
                {
                    out << " -";
                    loop = 1;
                }
                out << " ";
            }
            else {
                out << "   ";
            }
        }

        out << "    ";
        if (loop == 0)
            out << "  ";
        loop = 0;
        for (int i = 0; i < 16; ++i)
        {
            if (offset + i < totalBytes)
            {
                unsigned char ch = buffer[offset + i];
                if (ch >= 33 && ch <= 126)
                    out << ch;
                else
                    out << '.';
            }
        }
        out << NEWLINE;  // 使用条件编译的换行符
    }
}

void printUsage() 
{
    cout << "Usage : 15-b1 --infile 原始文件 [ --outfile hex格式文件 ]" << endl;
    cout << "        15-b1 --infile a.docx" << endl;
    cout << "        15-b1 --infile a.docx --outfile a.hex" << endl;
}

int main(int argc, char* argv[])
{
    const int MAX_FILENAME_LENGTH = 1024;
    char infile[MAX_FILENAME_LENGTH] = { 0 };
    char outfile[MAX_FILENAME_LENGTH] = { 0 };
    bool hasInfile = false, hasOutfile = false;

    for (int i = 1; i < argc; ++i) 
    {
        if (strcmp(argv[i], "--infile") == 0 && i + 1 < argc) 
        {
            strncpy(infile, argv[++i], MAX_FILENAME_LENGTH - 1);
            hasInfile = true;
        }
        else if (strcmp(argv[i], "--outfile") == 0 && i + 1 < argc) 
        {
            strncpy(outfile, argv[++i], MAX_FILENAME_LENGTH - 1);
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

    ifstream inFile(infile, ios::binary);
    if (!inFile) 
    {
        cerr << "输入文件" << infile << "打开失败!" << endl;
        return 1;
    }

    inFile.seekg(0, ios::end);
    int totalBytes = static_cast<int>(inFile.tellg());
    inFile.seekg(0, ios::beg);

    char* buffer = new char[totalBytes];

    // 读取文件内容
    inFile.read(buffer, totalBytes);
    if (!inFile) 
    {
        cerr << "读取文件内容失败!" << endl;
        delete[] buffer; // 释放内存
        return 1;
    }
    inFile.close();

    if (hasOutfile)
    {
        ofstream outFile(outfile, ios::binary);
        if (!outFile) 
        {
            cerr << "输出文件" << outfile << "打开失败!" << endl;
            delete[] buffer; // 释放内存
            return 1;
        }
        printHex(buffer, totalBytes, outFile);
        outFile.close();
    }
    else 
        printHex(buffer, totalBytes, cout);

    delete[] buffer; // 释放内存
    return 0;
}
