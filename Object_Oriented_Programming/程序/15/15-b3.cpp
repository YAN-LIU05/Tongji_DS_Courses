/* 2352018 大数据 刘彦 */
#include <iostream>
#include <fstream>
#include <cstdio>
#include <cstring>

using namespace std;

const int MAX_SIZE = 4096;

// 检查文件格式，返回相应的格式类型
const char* check_file_format(const char* file_path) 
{
    ifstream file(file_path, ios::binary);
    if (!file.is_open()) 
        return "文件打开失败";

    char buffer[MAX_SIZE];
    bool has_crlf = false; // 是否包含 \r\n
    bool has_lf = false;   // 是否包含 \n

    // 遍历文件内容，检查换行符
    while (file.read(buffer, MAX_SIZE)) 
    {
        for (int i = 0; i < file.gcount(); ++i) 
        {
            if (buffer[i] == '\r' && i + 1 < file.gcount() && buffer[i + 1] == '\n') 
            {
                has_crlf = true;
                i++; // 跳过 '\n'
            }
            else if (buffer[i] == '\n') 
                has_lf = true;
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
    ifstream infile(file_in, ios::binary);
    if (!infile.is_open()) 
        return "文件打开失败";

    char buffer[MAX_SIZE];
    bool is_windows = false;

    // 检查是否是Windows格式
    while (infile.read(buffer, MAX_SIZE)) 
    {
        for (int i = 0; i < infile.gcount(); ++i)
        {
            if (buffer[i] == '\r' && i + 1 < infile.gcount() && buffer[i + 1] == '\n') 
            {
                is_windows = true;
                break;
            }
        }
        if (is_windows) 
            break;
    }

    if (!is_windows) 
        return "文件格式无法识别";

    // 打开输出文件
    ofstream outfile(file_out, ios::binary);
    if (!outfile.is_open()) 
        return "文件写入失败";

    infile.clear();
    infile.seekg(0, ios::beg);

    // 将 \r\n 转换为 \n 并写入目标文件
    while (infile.read(buffer, MAX_SIZE)) 
    {
        for (int i = 0; i < infile.gcount(); ++i) 
        {
            if (buffer[i] == '\r' && i + 1 < infile.gcount() && buffer[i + 1] == '\n') 
            {
                outfile.put('\n');
                i++; // 跳过 '\n'
            }
            else 
                outfile.put(buffer[i]);
        }
    }

    return NULL;
}

// 将Linux格式文件转换为Windows格式
const char* convert_ltow(const char* file_in, const char* file_out) 
{
    ifstream infile(file_in, ios::binary);
    if (!infile.is_open()) 
        return "文件打开失败";

    char buffer[MAX_SIZE];
    bool is_linux = false;

    // 检查是否是Linux格式
    while (infile.read(buffer, MAX_SIZE))
    {
        for (int i = 0; i < infile.gcount(); ++i) 
        {
            if (buffer[i] == '\n') 
            {
                if (i > 0 && buffer[i - 1] != '\r')
                {
                    is_linux = true;
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
    ofstream outfile(file_out, ios::binary);
    if (!outfile.is_open()) 
        return "文件写入失败";

    infile.clear();
    infile.seekg(0, ios::beg);

    // 将 \n 转换为 \r\n 并写入目标文件
    while (infile.read(buffer, MAX_SIZE)) 
    {
        for (int i = 0; i < infile.gcount(); ++i) 
        {
            if (buffer[i] == '\n') 
            {
                outfile.put('\r');
                outfile.put('\n');
            }
            else 
                outfile.put(buffer[i]);
        }
    }

    return NULL;
}

void printUsage()
{
    cout << "Usage : 15-b3 --check 文件名 | --convert { wtol|ltow } 源文件名 目标文件名" << endl;
    cout << "        15-b3 --check a.txt" << endl;
    cout << "        15-b3 --convert wtol a.win.txt a.linux.txt" << endl;
    cout << "        15-b3 --convert ltow a.linux.txt a.win.txt" << endl;
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
        cout << check_file_format(file_path) << endl;

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
            cout << convert_wtol(source_file, target_file) << endl;
        else if (strcmp(conversion_type, "ltow") == 0) 
            cout << convert_ltow(source_file, target_file) << endl;
        else 
            printUsage();

    }
    else 
        printUsage();

    return 0;
}
