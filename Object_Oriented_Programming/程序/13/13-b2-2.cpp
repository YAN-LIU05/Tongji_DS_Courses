/* 2352018 大数据 刘彦 */
#include <iostream>
#include <fstream>
#include <cstring>

using namespace std;

// 学生结构体
struct Student {
    int no;          // 学号
    char name[9]; // 姓名
    int score;       // 成绩
    int rank;        // 名次
};

// 根据成绩排序的选择排序函数
void select_by_score(Student* students, int n)
{
    for (int i = 0; i < n - 1; i++)
    {
        int maxIndex = i;
        for (int j = i + 1; j < n; j++)
        {
            if (students[j].score > students[maxIndex].score)
                maxIndex = j;
        }
        // 交换
        Student temp = students[i];
        students[i] = students[maxIndex];
        students[maxIndex] = temp;
    }
}

// 计算名次
void my_rank(Student* students, int n)
{
    for (int i = 0; i < n; i++)
    {
        students[i].rank = i + 1; // 默认名次
        if (i > 0 && students[i].score == students[i - 1].score)
            students[i].rank = students[i - 1].rank; // 相同成绩共享名次
    }
}

// 根据学号排序的选择排序函数
void my_sort(Student* students, int n)
{
    for (int i = 0; i < n - 1; i++)
    {
        // 设定当前最小索引
        int minIndex = i;
        for (int j = i + 1; j < n; j++)
        {
            if (students[j].no < students[minIndex].no)
            {
                minIndex = j;
            }
        }
        // 如果找到更小的元素，进行交换
        if (minIndex != i)
        {
            Student temp = students[i];
            students[i] = students[minIndex];
            students[minIndex] = temp;
        }
    }
}

int main()
{
    ifstream fin;
    fin.open("student.txt", ios::in);
    if (!fin.is_open())
    {
        cerr << "打开文件student.txt失败." << endl;
        return -1;
    }

    int n = 0;

    // 读取学生人数
    fin >> n;

    // 动态分配学生数组
    Student* students = new Student[n];

    // 从文件中读取学生信息
    for (int i = 0; i < n; i++)
        fin >> students[i].no >> students[i].name >> students[i].score;

    fin.close();

    // 按成绩排序
    select_by_score(students, n);
    // 计算名次
    my_rank(students, n);
    // 根据名次和学号排序
    my_sort(students, n);
    // 输出结果
    for (int i = 0; i < n; i++)
        cout << students[i].no << " " << students[i].name << " " << students[i].score << " " << students[i].rank << endl;

    // 释放动态分配的内存
    delete[] students;

    return 0;
}
