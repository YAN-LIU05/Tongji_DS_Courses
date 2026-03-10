#include <iostream>
#include <fstream>
#include <cstdlib>
#include <ctime>
#include <cstring>

using namespace std;

const int MAX_NAME_LENGTH = 15; // 学生姓名的最大长度
const int MAX_SCHOOL_LENGTH = 10; // 学校名称的最大长度
const int MAX_ID_LENGTH = 15; // 报名号的最大长度

struct Student {
    char id[MAX_ID_LENGTH];
    char name[MAX_NAME_LENGTH];
    char school[MAX_SCHOOL_LENGTH];
};

bool my_select(int* have_selected, int count, int index) 
{
    for (int i = 0; i < count; ++i) 
    {
        if (have_selected[i] == index) 
            return true; // 索引已存在
    }
    return false; // 索引不存在
}

int main() 
{
    cout << "读取待抽签名单...";

    ifstream fin;
    fin.open("stulist.txt", ios::in);
    if (!fin.is_open()) 
    {
        cerr << "打开文件stulist.txt失败." << endl;
        return -1;
    }

    int N, M;
    fin >> N >> M; // 读取N和M
    fin.ignore();   // 忽略行末的换行符

    // 动态分配学生数组
    Student* students = new Student[M]; // 申请M个学生信息的内存

    // 读取学生信息
    for (int i = 0; i < M; ++i) 
    {
        fin >> students[i].id;
        fin >> students[i].name;
        fin.ignore(); // 忽略姓名后面的空格
        fin >> students[i].school;
    }

    fin.close();
    cout << "完成" << endl;
    // 设置随机数种子
    srand(static_cast<unsigned>(time(0)));

    cout << "正在抽签...";

    // 存储已选中的索引
    int* have_selected = new int[N]; // 申请N个索引的内存
    int count = 0;

    while (count < N) 
    {
        int randIndex = rand() % M; // 随机选择索引
        if (!my_select(have_selected, count, randIndex)) 
        {
            have_selected[count] = randIndex; // 添加新索引
            count++;
        }
    }

    // 选择结果并写入文件
    ofstream fout;
    fout.open("result.txt", ios::out);
    if (!fout.is_open()) 
    {
        cerr << "无法创建文件 result.txt" << endl;
        delete[] students; // 释放内存
        delete[] have_selected; // 释放内存
        return -1;
    }

    for (int i = 0; i < N; ++i) 
    {
        const Student& selected = students[have_selected[i]];
        fout << selected.id << " " << selected.name << " " << selected.school << endl;
    }

    fout.close();
    cout << "完成" << endl;

    // 释放动态分配的内存
    delete[] students; // 释放学生信息内存
    delete[] have_selected; // 释放索引内存

    return 0;
}
