/* 2352018 大数据 刘彦 */
#define _CRT_SECURE_NO_WARNINGS
#include "hw_check.h"
#include "../include/class_aat.h"
#include "../include/class_cft.h"
#include "../include_mariadb_x86/mysql/mysql.h"

/***************************************************************************
  函数名称：is_stu_valid
  功    能：检查cmd输入的参数stu是否合法
  输入参数：
  返 回 值：
  说    明：判断学号长度是否为7，且是否为全数字
 ***************************************************************************/
int is_stu_valid(const string& stu)
{
    if (stu.length() != 7)  // 学号必须是7位
        return 0;  // 长度不对，返回不合法
    for (size_t i = 0; i < stu.length(); i++)
        if (stu[i] < '0' || stu[i] > '9')  // 检查每个字符是否为数字
            return 0;  // 存在非数字字符，返回不合法
    return 1;  // 合法学号
}

/***************************************************************************
  函数名称：is_PDF_file
  功    能：检查文件是否是PDF格式
  输入参数：
  返 回 值：
  说    明：通过文件头检查是否是PDF文件
 ***************************************************************************/
int is_PDF_file(ifstream& fin)
{
    fin.clear();  // 清除文件流的任何错误状态
    fin.seekg(0, ios::beg);  // 将文件指针移动到文件开头
    char header[8];
    fin.read(header, 8);  // 读取文件头的前8个字节

    // 检查文件头是否以 "%PDF-1." 开头
    string pdf_file(header, 7);
    if (pdf_file == "%PDF-1.")
    {
        char version = header[7];  // 读取版本号字符
        if (version >= '0' && version <= '9')  // 判断版本号是否有效
            return 1;  // 是PDF文件
    }
    return 0;  // 不是PDF文件
}

/***************************************************************************
  函数名称：is_UTF8_file
  功    能：检查文件是否是UTF-8编码格式
  输入参数：
  返 回 值：
  说    明：逐字节检测文件是否符合UTF-8编码标准
 ***************************************************************************/
bool is_UTF8_file(ifstream& fin)
{
    unsigned char temp_ch;
    bool ascii = true;  // 默认认为是ASCII字符（UTF-8的子集）
    fin.clear();  // 清除文件流的任何错误状态
    fin.seekg(0, ios::beg);  // 将文件指针移到开头

    while (true)
    {
        temp_ch = fin.get();  // 获取文件中的下一个字符
        if (fin.eof())  // 到达文件末尾
            break;

        if ((temp_ch & 0x80) == 0)  // 1字节字符 (ASCII)
            continue;
        else if ((temp_ch & 0xe0) == 0xc0)  // 2字节字符
        {
            temp_ch = fin.get();
            if (fin.eof() || (temp_ch & 0xc0) != 0x80)
                return false;  // 不是合法的UTF-8字符
            ascii = false;
        }
        else if ((temp_ch & 0xf0) == 0xe0)  // 3字节字符
        {
            for (int i = 0; i < 2; ++i)
            {
                temp_ch = fin.get();
                if (fin.eof() || (temp_ch & 0xc0) != 0x80)
                    return false;  // 不是合法的UTF-8字符
            }
            ascii = false;
        }
        else if ((temp_ch & 0xf8) == 0xf0)  // 4字节字符
        {
            for (int i = 0; i < 3; ++i)
            {
                temp_ch = fin.get();
                if (fin.eof() || (temp_ch & 0xc0) != 0x80)
                    return false;  // 不是合法的UTF-8字符
            }
            ascii = false;
        }
        else
            return false;  // 无效的字节模式
    }
    return !ascii;  // 如果没有ASCII字符，则是UTF-8编码
}

/***************************************************************************
  函数名称：is_WIN_file
  功    能：检查文件是否使用Windows格式的换行符（CRLF）
  输入参数：
  返 回 值：
  说    明：检测文件是否包含回车符和换行符的组合（\r\n）
 ***************************************************************************/
bool is_WIN_file(ifstream& fin)
{
    char ch;
    bool hasCR = false;  // 是否发现回车符（\r）
    bool hasLF = false;  // 是否发现换行符（\n）

    while (fin.get(ch))  // 逐个字符读取文件
    {
        if (ch == '\r')  // 回车符
            hasCR = true;
        else if (ch == '\n')  // 换行符
            hasLF = true;
    }

    // 文件包含 \r 且没有 \n，说明是 Macintosh (CR) 格式
    if (hasCR && !hasLF)
        return false;
    return true;  // 文件是Windows格式
}

/***************************************************************************
  函数名称：get_file_kind
  功    能：判断文件类型
  输入参数：
  返 回 值：
  说    明：根据文件扩展名判断文件类型
 ***************************************************************************/
int get_file_kind(const string& filename)
{
    size_t len = filename.length();
    size_t dotPos = string::npos;

    // 手动查找文件名中最后一个点的位置
    for (int i = len - 1; i >= 0; i--)
    {
        if (filename[i] == '.')
        {
            dotPos = i;
            break;
        }
    }

    // 如果找到了点，获取扩展名
    if (dotPos != string::npos)
    {
        string extension_name = filename.substr(dotPos + 1);
        for (char& c : extension_name)  // 将扩展名转换为小写
            c = my_tolower(c);

        // 根据扩展名返回文件类型
        if (extension_name == "h" || extension_name == "hpp" || extension_name == "c" || extension_name == "cpp")
            return SOURCE_FILE;  // 源代码文件
        else if (extension_name == "pdf")
            return PDF_FILE;  // PDF文件
        else
            return OTHER_FILE;  // 其他文件类型
    }
    return ERROR_FILE;  // 无效文件
}

/***************************************************************************
  函数名称：replaceDot
  功    能：替换姓名中的·为点
  输入参数：
  返 回 值：
  说    明：将“·”替换为“.”，常用于中文姓名处理
 ***************************************************************************/
string replaceDot(const string& input)
{
    string result = input;
    size_t pos = 0;
    while ((pos = result.find("·", pos)) != string::npos)
    {
        result.replace(pos, 2, ".");  // "·"占2个字节
        pos += 1;  // 继续搜索
    }
    return result;
}

/***************************************************************************
  函数名称：removeSpaces
  功    能：移除字符串中的所有空格
  输入参数：
  返 回 值：
  说    明：将字符串中的所有空格字符移除
 ***************************************************************************/
string removeSpaces(const string& str)
{
    string result;

    // 遍历原始字符串，逐个字符处理
    for (char ch : str) 
    {
        if (ch != ' ')  // 如果字符不是空格，则添加到结果字符串
            result += ch;
    }
    return result;
}

/***************************************************************************
  函数名称：replaceString
  功    能：替换字符串中的指定字符
  输入参数：
  返 回 值：
  说    明：遍历字符串，将指定字符替换为新的字符
 ***************************************************************************/
void replaceString(string& str, char old_value, char new_value)
{
    for (size_t i = 0; i < str.size(); ++i)
        if (str[i] == old_value)  // 找到目标字符
            str[i] = new_value;  // 替换字符
}

/***************************************************************************
  函数名称：is_valid_comment
  功    能：判断是否为合法注释格式
  输入参数：
  返 回 值：
  说    明：判断是否为单行注释或多行注释格式
 ***************************************************************************/
int is_valid_comment(const vector<char>& first_line, vector<char>& comcontent)
{
    // 检测单行注释
    if (first_line[0] == '/' && first_line[1] == '/')
    {
        size_t start = 2;
        comcontent.assign(first_line.begin() + start, first_line.end());
        return 1;
    }
    /* 检测多行注释 */
    size_t len = first_line.size();
    if (first_line[0] == '/' && first_line[1] == '*')
    {
        if (first_line[len - 1] == '/' && first_line[len - 2] == '*')
        {
            size_t start = 2;
            comcontent.assign(first_line.begin() + start, first_line.end() - 2);
            return 1;  // 合法的多行注释
        }
        else
            return (int)FIRST_LINE_ERROR_COMMIT;  // 多行注释格式不正确
    }
    return (int)FIRST_LINE_NOT_COMMIT;  // 不是注释行
}

/***************************************************************************
  函数名称：split_by_space
  功    能：按空格分割字符串
  输入参数：
  返 回 值：
  说    明：使用 stringstream 按空格分割字符串
 ***************************************************************************/
vector<string> split_by_space(const vector<char>& comcontent)
{
    string str(comcontent.begin(), comcontent.end());  // 将字符向量转为字符串
    stringstream ss(str);  // 使用 stringstream 进行分割
    istream_iterator<string> begin(ss), end;
    vector<string> result(begin, end);
    return result;
}

/***************************************************************************
  函数名称：get_base
  功    能：获取文件基本状态
  输入参数：
  返 回 值：文件状态
  说    明：判断文件类型、编码格式及换行符格式
 ***************************************************************************/
FILE_SITUATIONS get_base(const string& filepath, const string& filename)
{
    ifstream fin;
    string _filepath = filepath;
    fin.open(_filepath, ios::in | ios::binary);  // 以二进制模式打开文件
    if (!fin.is_open())
    {
        return NOT_SUBMIT;  // 文件无法打开，返回未提交状态
    }

    int file_kind = get_file_kind(filename);  // 获取文件类型
    if (file_kind == SOURCE_FILE)
    {
        if (is_UTF8_file(fin))  // 检查是否为UTF-8文件
        {
            fin.close();
            return NOT_GB;  // 不是GB编码文件
        }
        if (!is_WIN_file(fin))  // 检查是否为Windows换行符格式
        {
            fin.close();
            return NOT_WIN;  // 不是Windows格式
        }
    }

    if (file_kind == PDF_FILE)
    {
        if (!is_PDF_file(fin))  // 检查是否为PDF文件
        {
            fin.close();
            return NOT_PDF;  // 不是PDF文件
        }
    }

    fin.close();
    return PASS;  // 文件通过检查
}

/***************************************************************************
  函数名称：check_file_size
  功    能：检查文件大小及是否存在
  输入参数：
  返 回 值：
  说    明：
 ***************************************************************************/
FILE_SITUATIONS check_file_size(ifstream& fin, const string& filepath)
{
    fin.open(filepath, ios::in | ios::binary | ios::ate);
    if (!fin.is_open())
    {
        cout << FILESTATUS_STR[NOT_SUBMIT] << endl;
        return NOT_SUBMIT;
    }
    streamsize filesize = fin.tellg();
    if (filesize < 3)
    {
        cout << FILESTATUS_STR[LESS_THAN_3_BIT] << endl;
        fin.close();
        return LESS_THAN_3_BIT;
    }
    fin.close();
    return PASS;
}

/***************************************************************************
  函数名称：check_file_encoding
  功    能：检查文件编码
  输入参数：
  返 回 值：
  说    明：
 ***************************************************************************/
FILE_SITUATIONS check_file_encoding(ifstream& fin)
{
    if (is_UTF8_file(fin))
    {
        cout << FILESTATUS_STR[NOT_GB] << endl;
        fin.close();
        return NOT_GB;
    }
    if (!is_WIN_file(fin))
    {
        cout << FILESTATUS_STR[NOT_WIN] << endl;
        fin.close();
        return NOT_WIN;
    }
    return PASS;
}

/***************************************************************************
  函数名称：read_first_line
  功    能：检查首行
  输入参数：
  返 回 值：
  说    明：
 ***************************************************************************/
FILE_SITUATIONS read_first_line(ifstream& fin, vector<char>& firstlinecontent)
{
    fin.clear();
    fin.seekg(0, ios::beg);
    vector<char> line_content;
    char ch;
    while (!fin.eof())
    {
        while ((ch = fin.get()) != '\r' && ch != '\n' && (!fin.eof()))
            line_content.push_back(ch);
        if (ch == '\r')
            ch = fin.get();  // 如果读到'\r'，说明是Windows，需要再读一次
        // 去除首尾空格和Tab
        while (!line_content.empty() && (line_content.front() == ' ' || line_content.front() == '\t'))
            line_content.erase(line_content.begin());
        while (!line_content.empty() && (line_content.back() == ' ' || line_content.back() == '\t'))
            line_content.pop_back();
        if (!line_content.empty())
        {
            firstlinecontent = line_content;
            break;
        }
        if (fin.eof())
        {
            cout << FILESTATUS_STR[NO_FIRST_LINE] << endl;
            fin.close();
            return NO_FIRST_LINE;
        }
    }
    return PASS;
}

/***************************************************************************
  函数名称：read_and_clean_line
  功    能：读取文件中的有效行并去除前后空格与Tab
  输入参数：
  返 回 值：
  说    明：
 ***************************************************************************/
bool read_and_clean_line(ifstream& fin, vector<char>& line_content) 
{
    line_content.clear();
    char ch;

    // 逐个读取字符直到遇到换行或文件结束
    while ((ch = fin.get()) != '\r' && ch != '\n' && !fin.eof()) 
        line_content.push_back(ch);

    // 如果读取到 '\r'，则跳过 Windows 的换行符
    if (ch == '\r') 
        ch = fin.get();

    // 去除行前后的空格和 Tab
    while (!line_content.empty() && (line_content.front() == ' ' || line_content.front() == '\t')) 
        line_content.erase(line_content.begin());

    while (!line_content.empty() && (line_content.back() == ' ' || line_content.back() == '\t')) 
        line_content.pop_back();

    return !line_content.empty(); // 返回是否读取到有效内容
}