/* 2352018 大数据 刘彦 */
#define _CRT_SECURE_NO_WARNINGS
#include "hw_check_class.h"
#include "../include/class_aat.h"
#include "../include/class_cft.h"
#include "../include_mariadb_x86/mysql/mysql.h"

/***************************************************************************
  函数名称：
  功    能：构造函数
  输入参数：
  返 回 值：
  说    明：
 ***************************************************************************/
Student::Student(const string& s1, const string& s2, const string& s3, const string& s4, const string& s5, const string& s6, const string& s7, const string& s8)
{
    term = s1;
    grade = s2;
    no = s3;
    name = s4;
    sex = s5;
    majorfull = s6;
    majorshort = s7;
    cno = s8;
}
Student::Student()
{
    term = "";
    grade = "";
    no = "";
    name = "";
    sex = "";
    majorfull = "";
    majorshort = "";
    cno = "";
}

Homework::Homework(const string& s1, const string& s2, const string& s3, const string& s4, const string& s5, const string& s6, const string& s7)
{
    kind = s1;
    cno = s2;
    number = s3;
    chapter = s4;
    week = s5;
    filename = s6;
    point = s7;
}

Config::Config()
{
    db_host = "";
    db_port = 0;
    db_name = "";
    db_username = "";
    db_passwd = "";
    db_currterm = "";
    src_rootdir = "";
}

hw_check::hw_check()
{
    action = "";
    cno = "";
    stu = "";
    file = "";
    chapter = -1;
    week = -1;
    cfgfile = "";
    display = "";
}

/***************************************************************************
  函数名称：read_db_config
  功    能：读取配置文件
  输入参数：
  返 回 值：
  说    明：读取配置文件中的数据库和文件目录信息
 ***************************************************************************/
int  Config::read_config(const string& cfgfile)
{
    string _cfgfile = cfgfile;
    config_file_tools cf(_cfgfile);  // 使用工具类读取配置文件
    if (!cf.is_read_succeeded())  // 检查是否成功读取配置文件
    {
        cerr << "无法打开配置文件[" << cfgfile << "]，结束运行." << endl;
        return 0;  // 读取配置文件失败，返回0
    }

    // 获取配置文件中的各项配置，若失败则输出错误信息并返回0
    if (cf.item_get_string("[文件目录]", "src_rootdir", Config::src_rootdir) < 0)
    {
        cerr << "取配置文件 [" << cfgfile << "] 的" << "[文件目录]" << "组的[" << "src_rootdir" << "]项的值出错." << endl;
        return 0;
    }
    if (cf.item_get_string("[数据库]", "db_host", Config::db_host) < 0)
    {
        cerr << "取配置文件 [" << cfgfile << "] 的" << "[数据库]" << "组的[" << "db_host" << "]项的值出错." << endl;
        return 0;
    }
    if (cf.item_get_int("[数据库]", "db_port", Config::db_port) < 0)
    {
        cerr << "取配置文件 [" << cfgfile << "] 的" << "[数据库]" << "组的[" << "db_port" << "]项的值出错." << endl;
        return 0;
    }
    if (cf.item_get_string("[数据库]", "db_name", Config::db_name) < 0)
    {
        cerr << "取配置文件 [" << cfgfile << "] 的" << "[数据库]" << "组的[" << "db_name" << "]项的值出错." << endl;
        return 0;
    }
    if (cf.item_get_string("[数据库]", "db_username", Config::db_username) < 0)
    {
        cerr << "取配置文件 [" << cfgfile << "] 的" << "[数据库]" << "组的[" << "db_username" << "]项的值出错." << endl;
        return 0;
    }
    if (cf.item_get_string("[数据库]", "db_passwd", Config::db_passwd) < 0)
    {
        cerr << "取配置文件 [" << cfgfile << "] 的" << "[数据库]" << "组的[" << "db_passwd" << "]项的值出错." << endl;
        return 0;
    }
    if (cf.item_get_string("[数据库]", "db_currterm", Config::db_currterm) < 0)
    {
        cerr << "取配置文件 [" << cfgfile << "] 的" << "[数据库]" << "组的[" << "db_currterm" << "]项的值出错." << endl;
        return 0;
    }
    return 1;  // 配置文件读取成功，返回1
}

/***************************************************************************
  函数名称：read_cmd
  功    能：读取并解析命令行参数
  输入参数：
  返 回 值：
  说    明：解析命令行参数并赋值给hw_check类中的相应成员
 ***************************************************************************/
int  hw_check::read_cmd(const args_analyse_tools* const args)
{
    // 判断学生文件是否有效，如果不为"all"则验证该文件
    if (args[ARGS_STU].get_string() != "all")
    {
        if (!is_stu_valid(args[ARGS_STU].get_string()))  // 检查文件是否有效
        {
            cout << "文件[" << args[ARGS_STU].get_string() << "]无法打开." << endl;
            cout << endl;
            cout << "[--严重错误--] 读取 [--stu] 指定的文件出错." << endl;
            return -2;  // 返回-2表示学生文件读取出错
        }
    }

    // 处理课号cno，检查其长度是否合法
    if (args[ARGS_CNO].get_string().length() >= 17)
    {

        this->action = args[ARGS_ACTION].get_string();
        this->cno = args[ARGS_CNO].get_string();
        this->stu = args[ARGS_STU].get_string();
        this->file = args[ARGS_FILE].get_string();
        this->chapter = args[ARGS_CHAPTER].existed() ? args[ARGS_CHAPTER].get_int() : -1;
        this->week = args[ARGS_WEEK].existed() ? args[ARGS_WEEK].get_int() : -1;
        this->cfgfile = args[ARGS_CFGFILE].get_string();
        this->display = args[ARGS_DISPLAY].get_string();
        return 1;  
    }

    // 如果课程号长度不是8位或13位，则返回错误
    if (args[ARGS_CNO].get_string().length() != 8 && args[ARGS_CNO].get_string().length() != 13)
    {
        cout << "课号不是8/13位" << endl;
        return -1;  // 返回-1表示课号格式错误
    }

    // 设置其他参数
    this->action = args[ARGS_ACTION].get_string();
    this->cno = args[ARGS_CNO].get_string();
    this->stu = args[ARGS_STU].get_string();
    this->file = args[ARGS_FILE].get_string();
    this->chapter = args[ARGS_CHAPTER].existed() ? args[ARGS_CHAPTER].get_int() : -1;
    this->week = args[ARGS_WEEK].existed() ? args[ARGS_WEEK].get_int() : -1;
    this->cfgfile = args[ARGS_CFGFILE].get_string();
    this->display = args[ARGS_DISPLAY].get_string();
    return 1;
}

/***************************************************************************
  函数名称：read_db_content
  功    能：读取数据库内容
  输入参数：无
  返 回 值：返回1表示成功，返回0表示失败
  说    明：连接数据库并执行SQL查询，获取数据库中的作业和学生信息
 ***************************************************************************/
int  hw_check::read_db_content()
{
    MYSQL* mysql;
    MYSQL_RES* result;
    MYSQL_ROW row;

    // 初始化MySQL连接
    if ((mysql = mysql_init(nullptr)) == nullptr)
    {
        cerr << "mysql_init failed" << endl;
        return 0;  // 初始化失败，返回0
    }

    // 连接到MySQL数据库
    if (mysql_real_connect(mysql, db_host.c_str(), db_username.c_str(), db_passwd.c_str(), db_name.c_str(), db_port, NULL, 0) == NULL)
    {
        cerr << "mysql_real_connect failed(" << mysql_error(mysql) << ")" << endl;
        return 0;  // 连接失败，返回0
    }

    mysql_set_character_set(mysql, "gbk");  // 设置字符集为GBK

    // 构建查询命令：获取作业信息
    string sql_hwquery_command = "select * from view_hwcheck_hwlist";
    if (cno.length() == 8 || cno.length() == 13)
        sql_hwquery_command = sql_hwquery_command + " where hw_cno = " + cno;
    else if (cno == "10108001,10108002")
        sql_hwquery_command = sql_hwquery_command + " where hw_cno in " + "('10108001', '10108002')";

    result = execute_query(mysql, sql_hwquery_command);  // 执行查询
    if (result == nullptr) 
    {
        mysql_close(mysql);
        return 0; 
    }

    if ((int)mysql_num_rows(result) <= 0)  // 如果查询结果为空
    {
        cerr << "查询到符合要求的记录为0." << endl;
        mysql_free_result(result);
        mysql_close(mysql);
        return 0;  // 查询结果为空，返回0
    }

    mysql_free_result(result);  // 释放结果集

    // 添加章节和周次的筛选条件
    if (chapter != -1)
        sql_hwquery_command = sql_hwquery_command + " and hw_chapter = " + to_string(chapter);
    if (week != -1)
        sql_hwquery_command = sql_hwquery_command + " and hw_week = " + to_string(week);

    // 执行查询命令，获取作业详情
    result = execute_query(mysql, sql_hwquery_command);
    if (result == nullptr) 
    {
        mysql_close(mysql);
        return 0;  
    }

    // 将查询结果存入作业列表
    while ((row = mysql_fetch_row(result)) != nullptr)
    {
        Homework hw(row[0], row[1], row[2], row[3], row[4], row[5], row[6]);
        hwlist.push_back(hw);
    }
    mysql_free_result(result);  // 释放结果集

    // 获取学生信息
    string sql_stuquery_command = "select * from view_hwcheck_stulist";
    if (cno.length() == 8 || cno.length() == 13)
        sql_stuquery_command = sql_stuquery_command + " where stu_cno = " + cno;
    else if (removeSpaces(cno) == "10108001,10108002")
        sql_stuquery_command = sql_stuquery_command + " where stu_cno in " + "('10108001', '10108002')";
    if (stu != "all")
        sql_stuquery_command = sql_stuquery_command + " and stu_no = " + stu;

    // 执行查询，获取学生信息
    result = execute_query(mysql, sql_stuquery_command);
    if (result == nullptr) 
    {
        mysql_close(mysql);
        return 0;  
    }

    // 将查询结果存入学生列表
    while ((row = mysql_fetch_row(result)) != nullptr)
    {
        Student stu(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7]);
        stulist.push_back(stu);
    }
    mysql_free_result(result);  // 释放结果集

    mysql_close(mysql);  // 关闭MySQL连接

    if (!check_file_validity())
        return 0;  

    return 1;  
}

/***************************************************************************
  函数名称：execute_query
  功    能：执行MySQL查询并返回结果
  输入参数：
  返 回 值：
  说    明：执行MySQL查询并检查错误，返回结果集
 ***************************************************************************/
MYSQL_RES* hw_check::execute_query(MYSQL* mysql, const string& query)
{
    if (mysql_query(mysql, query.c_str()))  // 执行SQL查询
    {
        cerr << "mysql_query failed(" << mysql_error(mysql) << ")" << endl;
        return nullptr;  // 查询失败，返回nullptr
    }

    MYSQL_RES* result = mysql_store_result(mysql);  // 存储查询结果
    if (result == nullptr)
    {
        cout << "mysql_store_result failed" << endl;
        return nullptr;  // 存储结果失败，返回nullptr
    }

    return result;  // 返回查询结果集
}

/***************************************************************************
  函数名称：check_file_validity
  功    能：检查文件格式的有效性
  输入参数：
  返 回 值：
  说    明：根据不同的检查动作，检查文件格式是否合法
 ***************************************************************************/
bool hw_check::check_file_validity()
{
    if (this->action == "firstline")
    {
        if (this->file == "all")  // 检查所有文件
        {
            for (auto it = hwlist.begin(); it != hwlist.end();)
            {
                if (get_file_kind(it->filename) != SOURCE_FILE)  // 如果文件不是源程序文件，则删除
                    it = hwlist.erase(it);
                else
                    ++it;
            }
        }
        else
        {
            if (get_file_kind(this->file) != SOURCE_FILE)  // 检查单个文件
            {
                cerr << "首行检查的文件[" << this->file << "]必须是源程序文件." << endl;
                return false;  // 文件格式无效，返回false
            }
        }
    }
    else if (this->action == "secondline")
    {
        if (get_file_kind(this->file) != SOURCE_FILE)  // 检查次行文件
        {
            cerr << "次行检查的文件[" << this->file << "]必须是源程序文件." << endl;
            return false;  
        }
    }
    return true; 
}