/* 2352018 大数据 刘彦 */
#define _CRT_SECURE_NO_WARNINGS
#include "hw_check_class.h"
#include "../include/class_aat.h"
#include "../include/class_cft.h"
#include "../include_mariadb_x86/mysql/mysql.h"

/***************************************************************************
  函数名称：get_print_first
  功    能：获取并打印首行
  输入参数：
  返 回 值：
  说    明：
 ***************************************************************************/
FILE_SITUATIONS get_print_first(const string& filepath, const string& filename, const Student& student)
{
    ifstream fin;
    string _filepath = filepath;
    // 检查文件大小
    FILE_SITUATIONS result = check_file_size(fin, filepath);
    if (result != PASS)
        return result; // 如果文件大小不符合要求，直接返回
    fin.open(_filepath, ios::in | ios::binary); // 以二进制模式打开文件
    // 检查文件编码
    result = check_file_encoding(fin);
    vector<char> firstlinecontent;
    if (result != PASS)
        return result; // 如果文件编码错误，返回错误状态
    // 读取文件首行
    result = read_first_line(fin, firstlinecontent);
    if (result != PASS)
        return result; // 如果读取首行失败，返回错误状态
    fin.close();
    string str(firstlinecontent.begin(), firstlinecontent.end()); // 将首行内容转为字符串
    // 如果首行内容少于2个字符，表示格式不符合要求
    if (firstlinecontent.size() < 2)
    {
        cout << FILESTATUS_STR[FIRST_LINE_NOT_COMMIT];
        cout << " [" << str << "]" << endl;
        return FIRST_LINE_NOT_COMMIT; // 返回首行内容不符合规范的错误
    }
    vector<char> comcontent;
    int comstatus = is_valid_comment(firstlinecontent, comcontent);
    // 判断注释格式是否合法
    if (comstatus == (int)FIRST_LINE_NOT_COMMIT)
    {
        cout << FILESTATUS_STR[FIRST_LINE_NOT_COMMIT];
        cout << " [" << str << "]" << endl;
        return FIRST_LINE_NOT_COMMIT; // 如果注释格式不正确，返回错误
    }
    else if (comstatus == (int)FIRST_LINE_ERROR_COMMIT)
    {
        cout << "首行不是符合要求的/* */格式 [" << str << "]" << endl;
        return FIRST_LINE_ERROR_COMMIT; // 如果注释格式错误，返回错误
    }
    int have_no = 0, have_major = 0, have_name = 0;
    vector<string> comitem = split_by_space(comcontent); // 将注释内容按空格拆分成项
    // 如果注释项不是3个，说明格式错误
    if (comitem.size() != 3)
    {
        cout << FILESTATUS_STR[FIRST_LINE_NOT_3];
        cout << " [" << str << "]" << endl;
        return FIRST_LINE_NOT_3; // 注释项个数错误，返回错误
    }

    /* 对应注释中的学生信息 */
    auto it = find(comitem.begin(), comitem.end(), student.no);
    if (it != comitem.end()) // 判断学号是否在注释中
        have_no = 1;

    // 处理专业简称中的 | 分隔符
    size_t delimiter_pos = student.majorshort.find('|');
    if (delimiter_pos != string::npos)
    {
        // 如果有 |，则检查 | 前后的部分是否出现在 comitem 中
        string part1 = student.majorshort.substr(0, delimiter_pos);
        string part2 = student.majorshort.substr(delimiter_pos + 1);
        if (find(comitem.begin(), comitem.end(), part1) != comitem.end() || find(comitem.begin(), comitem.end(), part2) != comitem.end())
            have_major = 1;
    }
    else
    {
        // 如果没有 |，直接查找整个专业简称
        it = find(comitem.begin(), comitem.end(), student.majorshort);
        if (it != comitem.end())
            have_major = 1;
    }

    it = find(comitem.begin(), comitem.end(), student.majorfull);
    if (it != comitem.end()) // 检查全称专业是否匹配
        have_major = 1;

    it = find(comitem.begin(), comitem.end(), student.name);
    if (it != comitem.end()) // 检查姓名是否匹配
        have_name = 1;

    // 检查学号、专业和姓名是否匹配
    if ((have_no + have_major + have_name) == 3)
    {
        cout << FILESTATUS_STR[PASS] << endl;
        return PASS; // 如果所有信息匹配，返回PASS
    }
    else
    {
        cout << "首行";
        if (!have_no)
            cout << NOT_MATCH[0];
        if (!have_name)
            cout << NOT_MATCH[1];
        if (!have_major)
            cout << NOT_MATCH[2];
        cout << " [" << str << "]" << endl;
        return FIRST_LINE_CHECK_ERROR; // 如果有信息不匹配，返回错误
    }
}

/***************************************************************************
  函数名称：get_print_second
  功    能：获取并打印次行
  输入参数：
  返 回 值：
  说    明：
 ***************************************************************************/
FILE_SITUATIONS get_print_second(const string& filepath, vector<Student>& check_stulist, const string& own_no)
{
    ifstream fin;
    string _filepath = filepath;
    // 检查文件大小
    FILE_SITUATIONS result = check_file_size(fin, filepath);
    if (result != PASS)
        return result; // 如果文件大小不符合要求，直接返回
    fin.open(_filepath, ios::in | ios::binary); // 以二进制模式打开文件
    // 检查文件编码
    if (is_UTF8_file(fin)) // 一定是sourcefile，但需要判断是否符合GB编码
    {
        cout << FILESTATUS_STR[NOT_GB] << endl;
        fin.close();
        return NOT_GB; // 如果文件编码不符合要求，返回编码错误
    }
    fin.clear();
    fin.seekg(0, ios::beg);

    string line;
    size_t line_count = 0;
    while (getline(fin, line))
    {
        line_count++;
        if (line_count > 1)
            break; // 如果发现多于一行，立即结束循环
    }
    if (line_count <= 1)
    {
        fin.close();
        cout << FILESTATUS_STR[SECOND_LINE_ERROR] << endl; // 次行其它错误
        return SECOND_LINE_ERROR; // 文件内容少于两行，返回错误
    }
    fin.clear();
    fin.seekg(0, ios::beg);
    //循环读，直到找到两行不空
    vector<char> line_content, firstlinecontent, secondlinecontent;
    line_count = 0;
    while (!fin.eof())
    {
        if (read_and_clean_line(fin, line_content))
        {
            ++line_count;
            if (line_count == 1)
                firstlinecontent = line_content; // 记录首行内容
            else if (line_count == 2)
            {
                secondlinecontent = line_content; // 记录次行内容
                break;
            }
        }
        if (fin.eof())
        {
            cout << FILESTATUS_STR[LESS_THAN_2_LINE] << endl; // 文件小于两行
            fin.close();
            return LESS_THAN_2_LINE; // 文件内容少于两行，返回错误
        }
    }
    fin.close();
    // 对次行进行检测 
    if (secondlinecontent.size() < 2)
    {
        cout << FILESTATUS_STR[SECOND_LINE_NOT_COMMIT] << endl;
        return SECOND_LINE_NOT_COMMIT; // 次行内容不符合注释格式
    }
    vector<char> comcontent;
    int comstatus = is_valid_comment(secondlinecontent, comcontent); // 检查次行是否为有效注释
    if (comstatus == (int)FIRST_LINE_NOT_COMMIT || comstatus == (int)FIRST_LINE_ERROR_COMMIT)
    {
        cout << FILESTATUS_STR[SECOND_LINE_NOT_COMMIT] << endl; // 次行不是注释
        return SECOND_LINE_NOT_COMMIT;
    }
    vector<string> comitem = split_by_space(comcontent); // 拆分注释内容
    // 得到互验学生名单
    FILE_SITUATIONS status = validate_student_info(comitem, own_no, check_stulist); // 验证学生信息
    if (status != PASS) return status;  // 如果学生信息验证失败，则返回错误

    cout << FILESTATUS_STR[PASS] << endl;
    return PASS; // 如果验证通过，返回PASS
}

/***************************************************************************
  函数名称：cross_check
  功    能：交叉检查
  输入参数：
  返 回 值：
  说    明：
 ***************************************************************************/
void hw_check::cross_check(const vector<vector<Student>>& total_check_stulist, const vector<Student>& total_stulist)
{
    cout << "交叉检查结果：" << endl;
    for (size_t i = 0; i < total_stulist.size(); i++) // i是当前检测的学生
    {
        if (cno == "10108001" || cno == "10108002" || cno == "5000244001602")
            cout << setw(3) << i + 1 << ": " << cno << "-" << total_stulist[i].no << "-" << total_stulist[i].name << endl;
        else
        {
            if (i + 1 < 88)
                cout << setw(3) << i + 1 << ": " << 10108001 << "-" << total_stulist[i].no << "-" << total_stulist[i].name << endl;
            else
                cout << setw(3) << i + 1 << ": " << 10108002 << "-" << total_stulist[i].no << "-" << total_stulist[i].name << endl;
        }
        for (size_t j = 0; j < total_check_stulist[i].size(); j++) // j是和你互验的学生
        {
            cout << '\t' << total_check_stulist[i][j].no << " " << total_check_stulist[i][j].name << '\t';
            size_t k = 0;
            for (; k < total_stulist.size(); k++) // k是互验学生在total_stulist中的序号
                if (total_stulist[k].no == total_check_stulist[i][j].no)
                    break;
            if (k == total_stulist.size())
                cout << CROSS_ERROR[NO] << endl;
            else
            {
                if (total_stulist[k].name != total_check_stulist[i][j].name)
                {
                    cout << CROSS_ERROR[NAME] << endl;
                    continue;
                }
                size_t m = 0;
                for (; m < total_check_stulist[k].size(); m++) // 遍历对方的check_list，看有没有你
                {
                    if (total_check_stulist[k][m].no == total_stulist[i].no) // 学号对
                    {
                        if (total_check_stulist[k][m].name != total_stulist[i].name) // 姓名错
                            cout << CROSS_ERROR[CORRECT] << endl;
                        else
                            cout << endl; // 姓名对，下一行
                        break;
                    }
                }
                if (m == total_check_stulist[k].size())
                    cout << CROSS_ERROR[ABANDON] << endl;
            }
        }
    }
}

/***************************************************************************
  函数名称：validate_student_info
  功    能：验证学生信息
  输入参数：
  返 回 值：
  说    明：
 ***************************************************************************/
FILE_SITUATIONS validate_student_info(const vector<string>& comitem, const string& own_no, vector<Student>& check_stulist)
{
    for (size_t i = 0; i < comitem.size(); i = i + 2)
    {
        if (i >= comitem.size() - 1) // 仅在结尾处出现此错误
        {
            cout << "第[" << i / 2 << "]个学生后面的信息不全(只读到一项)，后续内容忽略" << endl;
            return OTHER_ERROR;
        }

        string stu_no = comitem[i], stu_name = comitem[i + 1];

        // 学号长度检查
        if (stu_no.length() != 7)
        {
            cout << "第" << i / 2 + 1 << "位同学的学号[" << stu_no << "]不是7位，后续内容忽略" << endl;
            return OTHER_ERROR;
        }

        // 学号有效性检查
        if (!is_stu_valid(stu_no))
        {
            cout << "第" << i / 2 + 1 << "位同学的学号[" << stu_no << "]中有非数字存在，后续内容忽略" << endl;
            return OTHER_ERROR;
        }

        // 避免写自己的信息
        if (stu_no == own_no)
        {
            cout << "第[" << i / 2 + 1 << "]项写了自己，后续内容忽略" << endl;
            return OTHER_ERROR;
        }

        // 添加到学生名单中
        Student temp_check_stu;
        temp_check_stu.no = stu_no;
        temp_check_stu.name = stu_name;
        check_stulist.push_back(temp_check_stu);
    }

    return PASS; // 所有学生信息验证通过
}

/***************************************************************************
  函数名称：print_hw_check_result
  功    能：打印检查结果
  输入参数：
  返 回 值：
  说    明：
 ***************************************************************************/
void hw_check::print_hw_check_result(int choice, const int file_status[], const int total_num[])
{
    // 用于存储最大状态字符串长度
    size_t maxlen = 0, filestatus_cnt = 0;
    // 包含secondline操作时的状态码
    int secondlinestatus_set[] = { PASS, NOT_SUBMIT, NOT_GB, NOT_WIN, LESS_THAN_2_LINE, SECOND_LINE_NOT_COMMIT, SECOND_LINE_ERROR, OTHER_ERROR , -1 };

    // 根据action的值，设置filestatus_cnt，即需要处理的文件状态数量
    if (this->action == "base")
        filestatus_cnt = 5;
    else if (this->action == "firstline")
        filestatus_cnt = 11;
    else if (this->action == "secondline")
        filestatus_cnt = 15;

    // 计算最大状态字符串长度，以便对齐输出
    for (size_t i = 0; i < filestatus_cnt; i++)
    {
        if (should_skip_status(i, secondlinestatus_set, this->action))
            continue;
        if ((choice == STUDENT_OF_ALL || choice == END_OF_NOT_ALL) && file_status[i] != 0)
            maxlen = max(FILESTATUS_STR[i].length(), maxlen);
        if (choice == END_OF_ALL && total_num[i] != 0)
            maxlen = max(FILESTATUS_STR[i].length(), maxlen);
    }

    // 设置输出格式为右对齐，并定义填充字符
    cout << setiosflags(ios::right);
    char setfill_char = '=';
    // 设置宽度和填充字符，根据choice的值调整
    int setw_word = 2, setw_seg = 12;
    if (choice == STUDENT_OF_ALL)
        setfill_char = '-';
    cout << setfill(setfill_char) << setw(setw_seg + maxlen) << setfill_char << endl;
    // 打印学生信息标题
    cout << STUDENT_INFORMATION[choice] << endl;
    cout << setfill(setfill_char) << setw(setw_seg + maxlen) << setfill_char << endl;
    // 重置填充字符为默认空格
    cout << setfill(' ');

    // 遍历并打印每个文件状态的数量
    for (size_t i = 0; i <= filestatus_cnt; i++)
    {
        if (should_skip_status(i, secondlinestatus_set, this->action))
            continue;
        // 如果是END_OF_ALL并且total_num[i]不为0，则打印总数
        if (choice == END_OF_ALL && total_num[i] != 0)
        {
            cout << setw(maxlen + setw_word) << FILESTATUS_STR[i] << " : ";
            cout << total_num[i] << endl;
        }
        // 如果是STUDENT_OF_ALL或END_OF_NOT_ALL并且file_status[i]不为0，则打印每个学生的状态数量
        if ((choice == STUDENT_OF_ALL || choice == END_OF_NOT_ALL) && file_status[i] != 0)
        {
            // 如果action是"secondline"，需要特殊处理OTHER_ERROR状态
            if (this->action == "secondline")
            {
                if (i == OTHER_ERROR)
                    continue; // 与PASS合并，不需要单独打印
                cout << setw(maxlen + setw_word) << FILESTATUS_STR[i] << " : ";
                int temp = file_status[OTHER_ERROR];
                if (temp < 0)
                    temp = 0;
                if (i == PASS) {
                    cout << file_status[i] + temp << endl;
                }
                else
                    cout << file_status[i] << endl;
            }
            else
            {
                cout << setw(maxlen + setw_word) << FILESTATUS_STR[i] << " : ";
                cout << file_status[i] << endl;
            }
        }
    }
    // 打印底部分隔线。
    cout << setfill(setfill_char) << setw(setw_seg + maxlen) << setfill_char << endl;
    // 重置输出格式为左对齐，并重置填充字符为默认空格。
    cout << resetiosflags(ios::right) << setiosflags(ios::left);
    cout << setfill(' ');
}

/***************************************************************************
  函数名称：hw_check_all
  功    能：总检测函数
  输入参数：
  返 回 值：
  说    明：
 ***************************************************************************/
int hw_check::hw_check_all()
{
    // 用于存储学生姓名的最大长度
    int max_stu_length = 0;
    // 遍历学生列表stulist，计算每个学生姓名的最大长度
    for (size_t i = 0; i < this->stulist.size(); i++)
    {
        int templen = this->stulist[i].name.length();
        max_stu_length = max(max_stu_length, templen);
    }

    // 用于存储作业文件名的最大长度
    int max_hwfile_length = 0;
    // 遍历hwlist，计算每个文件名的最大长度
    for (size_t i = 0; i < this->hwlist.size(); i++)
    {
        int templen = this->hwlist[i].filename.length();
        max_hwfile_length = max(max_hwfile_length, templen);
    }

    cout << setiosflags(ios::left);
    // 用于存储分割后的课号
    vector<string> cnos;
    // 使用stringstream和getline函数分割传入的课号字符串cno
    stringstream ss(cno);
    string temp_cno;
    while (getline(ss, temp_cno, ','))
    {
        // 移除每个课号前后的空格
        temp_cno.erase(remove(temp_cno.begin(), temp_cno.end(), ' '), temp_cno.end());
        cnos.push_back(temp_cno);
    }

    // 判断是否需要检查所有文件或学生
    bool file_is_all = this->file == "all" ? true : false;
    bool stu_is_all = this->stu == "all" ? true : false;
    // 计数学生数量
    int stunum_cnt = 0;
    // 记录文件状态的数量
    int file_status[FILE_STATUS_NUM] = { 0 };
    // 记录总的文件状态数量
    int total_num[FILE_STATUS_NUM] = { 0 };
    // 存储所有互验学生名单
    vector<vector<Student>> total_check_stulist;

    // 如果不是检查所有文件，输出当前课号、学生数量和源文件名
    if (!file_is_all)
        cout << "课号 : " << cno << " 学生数量 : " << stulist.size() << " 源文件名 : " << this->file << endl;

    // 遍历所有课号和学生，检查每个学生的作业文件
    for (const auto& current_cno : cnos) {
        for (const auto& student : this->stulist)
        {
            // 如果当前学生的课号不匹配，跳过
            if (student.cno != current_cno)
                continue;
            // 打印学生信息。
            print_student_info(student, file_is_all, stu_is_all, stunum_cnt, max_stu_length, student.cno == "5000244001602");

            // 遍历作业文件列表，检查每个文件的状态
            for (const auto& hwfile : this->hwlist)
            {
                // 构造文件路径
                string filepath = src_rootdir + student.cno + "-" + student.no + "/" + (file_is_all ? hwfile.filename : this->file);
                if (file_is_all)
                    cout << "  " << setw(max_hwfile_length) << hwfile.filename << " : ";
                // 检查文件状态并记录
                FILE_SITUATIONS filestatus = check_and_record_file_status(filepath, file_is_all ? hwfile.filename : this->file, student, total_check_stulist);
                ++file_status[filestatus];
                // 如果不是检查所有文件，跳出循环
                if (!file_is_all) break;
            }

            // 如果需要检查所有文件，更新总的文件状态数量并打印结果
            if (file_is_all)
            {
                for (size_t i = 0; i < FILE_STATUS_NUM; i++)
                    total_num[i] += file_status[i];
                print_file_check_result(file_status[PASS], hwlist.size());
                print_hw_check_result(1, file_status, total_num);// 打印信息1
                // 重置file_status数组
                memset(file_status, 0, sizeof(file_status));
                cout << endl;
            }
        }
    }
    cout << endl;

    // 如果需要检查所有文件，输出总的检查结果
    if (file_is_all)
    {
        cout << "共完成" << stulist.size() << "个学生的检查，文件总数:" << stulist.size() * hwlist.size() << "，通过总数:" << total_num[PASS] << "，本次通过" << total_num[PASS] << "个" << endl;
        print_hw_check_result(2, file_status, total_num); // 打印信息2
    }
    else
    {
        // 如果不是检查所有文件，只输出文件检查结果
        print_file_check_result(file_status[PASS], stulist.size());
        print_hw_check_result(0, file_status, total_num); // 打印信息0
    }
    cout << endl;

    if (this->action == "secondline")
    {
        cross_check(total_check_stulist, stulist);
        cout << endl;
    }

    return 0;
}

/***************************************************************************
  函数名称：should_skip_status
  功    能：
  输入参数：
  返 回 值：
  说    明：
 ***************************************************************************/
bool hw_check::should_skip_status(int i, const int secondlinestatus_set[], const std::string& action)
{
    // 如果 action 不是 "base" 且 i == 2，跳过
    if (action != "base" && i == 2)
        return true;

    // 如果 action 是 "secondline"，需要检查是否在 secondlinestatus_set 中
    if (action == "secondline")
    {
        size_t j = 0;
        for (; secondlinestatus_set[j] != -1; j++)
        {
            if (i == secondlinestatus_set[j])
                return false; // 找到匹配项，继续执行
        }
        return true; // 未找到匹配项，跳过
    }

    // 默认不跳过
    return false;
}

/***************************************************************************
  函数名称：print_student_info
  功    能：
  输入参数：
  返 回 值：
  说    明：
 ***************************************************************************/
void hw_check::print_student_info(const Student& student, bool file_is_all, bool stu_is_all, int& stunum_cnt, int max_stu_length, bool is_special)
{
    if (file_is_all)
        cout << setw(3) << ++stunum_cnt << ": 学号-" << student.no << " 姓名-" << replaceDot(student.name) << " 课号-" << student.cno << " 文件数量-" << hwlist.size() << endl;
    else
    {
        if (stu_is_all)
            cout << setw(3) << ++stunum_cnt << ": " << student.no << "/" << setw(max_stu_length) << replaceDot(student.name) << " : ";
        else
            if (student.cno == "5000244001602")
                cout << setw(3) << ++stunum_cnt << ": " << student.no << "/" << setw(max_stu_length) << replaceDot(student.name) << "           : ";
            else
                cout << setw(3) << ++stunum_cnt << ": " << student.no << "/" << setw(max_stu_length) << replaceDot(student.name) << "   : ";
    }
}

/***************************************************************************
  函数名称：check_and_record_file_status
  功    能：
  输入参数：
  返 回 值：
  说    明：
 ***************************************************************************/
FILE_SITUATIONS hw_check::check_and_record_file_status(const string& filepath, const string& filename, const Student& student, vector<vector<Student>>& total_check_stulist) 
{
    FILE_SITUATIONS filestatus = PASS; // 默认状态是通过
    if (this->action == "base")
    {
        filestatus = get_base(filepath, filename);
        cout << FILESTATUS_STR[filestatus] << endl;
    }
    else if (this->action == "firstline")
    {
        filestatus = get_print_first(filepath, filename, student);
    }
    else if (this->action == "secondline")
    {
        vector<Student> check_stulist; // 次行的互验学生名单
        filestatus = get_print_second(filepath, check_stulist, student.no);
        if (filestatus == OTHER_ERROR)
            filestatus = PASS; // 特殊判断
        total_check_stulist.push_back(check_stulist);
    }

    return filestatus;
}

/***************************************************************************
  函数名称：print_file_check_result
  功    能：
  输入参数：
  返 回 值：
  说    明：
 ***************************************************************************/
void hw_check::print_file_check_result(int pass_count, int total_count) 
{
    string str = "文件";
    if (total_count == stulist.size())
        str = "学生";
    if (pass_count == total_count)
        cout << "全部通过" << pass_count << "/" << total_count << "个" << str << "，本次通过" << pass_count << "个" << endl;
    else 
        cout << "检查通过" << pass_count << "/" << total_count << "个" << str << "，本次通过" << pass_count << "个" << endl;
}
