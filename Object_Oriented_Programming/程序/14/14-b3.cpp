/* 2352018 大数据 刘彦 */
#include <iostream>
#include <cstring>

using namespace std;

/***************************************************************************
  函数名称：
  功    能：
  输入参数：
  返 回 值：
  说    明：
***************************************************************************/
int usage(const char* const procname)
{
	cout << "Usage: " << procname << " 要检查的学号/all 匹配学号/all 源程序名/all 相似度阀值(60-100) 输出(filename/screen)" << endl << endl;
	cout << "e.g. : " << procname << " 2159999 2159998 all       80 screen" << endl;
	cout << "       " << procname << " 2159999 all     14-b1.cpp 75 result.txt" << endl;
	cout << "       " << procname << " all     all     14-b2.cpp 80 check.dat" << endl;
	cout << "       " << procname << " all     all     all       85 screen" << endl;

	return 0;
}

// 学号检查函数
bool check_student_id_num(const char* id, const char* error_message) 
{
    if (strlen(id) != 7) 
    {
        cout << error_message << endl;
        return false;
    }
    for (int i = 0; i < 7; i++) 
    {
        if (id[i] < '0' || id[i] > '9') 
        {
            cout << error_message << endl;
            return false;
        }
    }
    return true;
}

// 处理学号的逻辑
bool check_student_id_all(int argc, char* argv[]) 
{
    // 检测检查学生的学号
    bool flag_of_id = (strcmp(argv[1], "all") == 0);

    if (!flag_of_id) 
    {
        if (!check_student_id_num(argv[1], "要检查的学号不是7位数字")) 
        {
            return false;
        }
    }

    // 检测匹配学生的学号
    bool match_id = (strcmp(argv[2], "all") == 0);

    if (!flag_of_id && strcmp(argv[1], argv[2]) == 0) 
    {
        cout << "匹配学号与要检查学号相同" << endl;
        return false;
    }

    if (!match_id) 
        if (!check_student_id_num(argv[2], "匹配学号不是7位数字")) 
            return false;


    if (flag_of_id && !match_id) 
    {
        cout << "检查学号是all，匹配学号必须是all" << endl;
        return false;
    }

    // 所有检查通过
    return true;
}

// 检测文件名的长度
bool check_filename_length(const char* filename, const char* error_message) 
{
    if (strlen(filename) > 32) 
    {
        cout << error_message << endl;
        return false;
    }
    return true;
}

// 输出检查结果的函数
void display_check_results(char* argv[])
{
    cout << "参数检查通过" << endl;
    cout << "检查学号：" << argv[1] << endl;
    cout << "匹配学号：" << argv[2] << endl;

    // 源文件名检查
    cout << "源文件名：" << (strcmp(argv[3], "all") == 0 ? "all" : argv[3]) << endl;
}


// 相似度检查函数
void check_similarity(const char* similarity_set) 
{
    int num = 80; // 默认阈值

    if (similarity_set[0] >= '6' && similarity_set[0] <= '9') 
    {
        if (similarity_set[1] >= '0' && similarity_set[1] <= '9')       
            num = (similarity_set[0] - '0') * 10 + (similarity_set[1] - '0');  // 将字符转换为整数
    }
    else if (similarity_set[0] == '1' && similarity_set[1] == '0' && similarity_set[2] == '0') 
        num = 100; // 直接设置为100

    cout << "匹配阈值：" << num << endl;
}

// 输出方式检查函数
void check_output_target(const char* outfile) 
{
    if (strcmp(outfile, "screen") == 0) 
        cout << "输出目标：screen" << endl;
    else
        cout << "输出目标：" << outfile << endl;
}

int main(int argc, char* argv[])
{
	if (argc < 6)
	{
		usage(argv[0]);
		return 0;
	}

    // 检测学号
    if (!check_student_id_all(argc, argv)) 
        return 0; // 参数检查失败


    // 检测源程序文件名的长度
    if (!check_filename_length(argv[3], "源程序文件名超过了32字节")) 
        return 0;

    // 检测输出结果文件名的长度
    if (!check_filename_length(argv[5], "输出结果文件名超过了32字节")) 
        return 0;

    // 输出检查结果
    display_check_results(argv);

    // 相似度检查
    check_similarity(argv[4]);

    // 输出方式检查
    check_output_target(argv[5]);

    return 0;
}