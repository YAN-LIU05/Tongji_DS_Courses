/* 2352018 大数据 刘彦 */
#define _CRT_SECURE_NO_WARNINGS
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

// 学生结构体
struct Student {
    int no;      // 学号
    char name[9]; // 姓名
    int score;        // 成绩
    int rank;         // 名次
};

// 根据成绩排序的选择排序函数
void select_by_score(struct Student* students, int n)
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
        struct Student temp = students[i];
        students[i] = students[maxIndex];
        students[maxIndex] = temp;
    }
}

// 计算名次
void my_rank(struct Student* students, int n)
{
    for (int i = 0; i < n; i++)
    {
        students[i].rank = i + 1; // 默认名次
        if (i > 0 && students[i].score == students[i - 1].score)
        {
            students[i].rank = students[i - 1].rank; // 相同成绩共享名次
        }
    }
}

// 根据学号排序的选择排序函数
void my_sort(struct Student* students, int n)
{
    for (int i = 0; i < n - 1; i++)
    {
        for (int j = i + 1; j < n; j++)
        {
            if (students[j].rank == students[i].rank && students[j].no < students[i].no)
            {
                // 如果名次相同，按学号从小到大排序
                struct Student temp = students[i];
                students[i] = students[j];
                students[j] = temp;
            }
        }
    }
}

int main()
{
    FILE* file = fopen("student.txt", "r");
    if (file == NULL)
    {
        fprintf(stderr, "打开文件student.txt失败.\n");
        return -1;
    }

    int n = 0;

    // 读取学生人数
    fscanf(file, "%d", &n);

    // 动态分配学生数组
    struct Student* students = (struct Student*)malloc(n * sizeof(struct Student));

    // 从文件中读取学生信息
    for (int i = 0; i < n; i++)
        fscanf(file, "%d %s %d", &students[i].no, students[i].name, &students[i].score);
    fclose(file);

    // 按成绩排序
    select_by_score(students, n);
    // 计算名次
    my_rank(students, n);
    // 根据名次和学号排序
    my_sort(students, n);
    // 输出结果
    for (int i = 0; i < n; i++)
        printf("%d %s %d %d\n", students[i].no, students[i].name, students[i].score, students[i].rank);

    // 释放动态分配的内存
    free(students);

    return 0;
}