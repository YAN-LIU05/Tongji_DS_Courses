/* 2352018 信06 刘彦 */
#define _CRT_SECURE_NO_WARNINGS
#include <stdio.h>
#include <string.h>

#define MAX_STUDENTS 10
#define MAX_ID_LENGTH 8
#define MAX_NAME_LENGTH 8

// 输入学生信息
void input(char id[][MAX_ID_LENGTH], char name[][MAX_NAME_LENGTH], int scores[]) 
{
    int i;
    for (i = 0; i < MAX_STUDENTS; ++i) 
    {
        printf("请输入第%d个人的学号、姓名、成绩\n", i + 1);
        scanf("%s %s %d", id[i], name[i], &scores[i]);
    }
}

// 冒泡排序，按学号降序排序
void sort(char id[][MAX_ID_LENGTH], char name[][MAX_NAME_LENGTH], int scores[], int n) 
{
    int i, j;
    char id0[MAX_ID_LENGTH];
    char name0[MAX_NAME_LENGTH];
    int temp;
    for (i = 0; i < n - 1; ++i) 
    {
        for (j = 0; j < n - i - 1; ++j) 
        {
            if (strcmp(id[j], id[j + 1]) < 0) 
            {
                // 交换姓名
                strcpy(name0, name[j]);
                strcpy(name[j], name[j + 1]);
                strcpy(name[j + 1], name0);
                // 交换学号
                strcpy(id0, id[j]);
                strcpy(id[j], id[j + 1]);
                strcpy(id[j + 1], id0);
                // 交换成绩
                temp = scores[j];
                scores[j] = scores[j + 1];
                scores[j + 1] = temp;
            }
        }
    }
}

// 打印及格学生名单
void print(char id[][MAX_ID_LENGTH], char name[][MAX_NAME_LENGTH], int scores[]) 
{
    int i;
    for (i = 0; i < MAX_STUDENTS; ++i) 
    {
        if (scores[i] >= 60)
        {
            printf("%s %s %d\n", name[i], id[i], scores[i]);
        }
    }
}

int main()
{
    char id[MAX_STUDENTS][MAX_ID_LENGTH];
    char name[MAX_STUDENTS][MAX_NAME_LENGTH];
    int scores[MAX_STUDENTS];

    // 输入学生信息
    input(id, name, scores);

    // 按学号降序排序
    sort(id, name, scores, MAX_STUDENTS);
    printf("\n");

    // 打印及格学生名单
    printf("及格名单(学号降序):\n");
    print(id, name, scores);

    return 0;
}