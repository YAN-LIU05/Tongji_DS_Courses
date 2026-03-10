/* 2352018 大数据 刘彦 */
#pragma once
#include <iostream>
#include <fstream>
#include <iomanip>
#include <cstdio>
#include <cstdlib>
#include <vector>
#include <string>
#include <sstream>

#include "../include/class_aat.h"
#include "../include_mariadb_x86/mysql/mysql.h"
using namespace std;

class hw_check;
class Student;
class Homework;

enum ARGS {
	ARGS_HELP = 0, ARGS_DEBUG, ARGS_ACTION, ARGS_CNO, ARGS_STU,
	ARGS_FILE, ARGS_CHAPTER, ARGS_WEEK, ARGS_DISPLAY, ARGS_CFGFILE
};
enum FILES_KIND {
	ERROR_FILE = 0, SOURCE_FILE, PDF_FILE, OTHER_FILE
};
enum PRINT_SITUATIONS {
	END_OF_NOT_ALL = 0, STUDENT_OF_ALL, END_OF_ALL
};
enum FILE_SITUATIONS {
	PASS = 0,                  // 通过
	NOT_SUBMIT,                // 未提交
	NOT_PDF,                   // 错误的PDF文件，只有base会使用
	NOT_WIN,                   // VS无法解析
	NOT_GB,                    // 不符合GB编码

	LESS_THAN_3_BIT,           // 文件小于3字节
	NO_FIRST_LINE,             // 无有效首行
	FIRST_LINE_ERROR_COMMIT,   // 首行多行注释格式不正确
	FIRST_LINE_NOT_COMMIT,     // 首行不是注释行
	FIRST_LINE_NOT_3,          // 首行不是三项
	FIRST_LINE_CHECK_ERROR,    // 首行检查出错

	LESS_THAN_2_LINE,          // 文件小于两行
	SECOND_LINE_NOT_COMMIT,    // 次行不是注释
	SECOND_LINE_ERROR,         // 次行其它错误
	OTHER_ERROR                // 检测出错，但仍正常继续
};
enum CROSS_SITUATIONS {
	NO = 0, NAME, CORRECT, ABANDON
};

int is_stu_valid(const string& stuno);
int get_file_kind(const string& filename);
bool is_UTF8_file(ifstream& fin);
bool is_WIN_file(ifstream& fin);
int is_PDF_file(ifstream& fin);
string replaceDot(const string& input);
string removeSpaces(const string& str);
int  is_valid_comment(const vector<char>& firstlinecontent, vector<char>& comcontent);
vector<string> split_by_space(const vector<char>& comcontent);
FILE_SITUATIONS get_base(const string& filepath, const string& filename);
FILE_SITUATIONS get_print_first(const string& filepath, const string& filename, const Student& student);
FILE_SITUATIONS get_print_second(const string& filepath, vector<Student>& check_stulist, const string& own_no);
FILE_SITUATIONS check_file_size(ifstream& fin, const string& filepath);
FILE_SITUATIONS check_file_encoding(ifstream& fin);
FILE_SITUATIONS read_first_line(ifstream& fin, vector<char>& firstlinecontent);
bool read_and_clean_line(ifstream& fin, vector<char>& line_content);

const string FILESTATUS_STR[] = { "正确" ,"未提交" , "PDF文件格式不正确" , "源文件格式不正确(VS无法识别)",
								  "源文件格式不正确(非GB编码)",  "文件小于3字节","无有效首行",
								  "首行多行注释格式不正确", "首行不是注释行","首行不是三项","首行检查出错",
								  "文件小于两行", "次行不是注释","次行其它错误","" };
const string STUDENT_INFORMATION[] = { "详细信息", "学生详细信息", "整体详细信息", "" };
const string NOT_MATCH[] = { "学号不匹配", "姓名不匹配", "班级不匹配", "" };
const string CROSS_ERROR[] = { "对方学号不存在", "对方姓名不正确", "没写对你名字", "抛弃了你", "" };
const int FILE_STATUS_NUM = 14;