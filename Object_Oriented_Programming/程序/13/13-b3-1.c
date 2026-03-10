/* 2352018 大数据 刘彦 */
#define _CRT_SECURE_NO_WARNINGS
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

struct student {
    int no;
    char name[9];
    int score;
    struct student* next;
};

int main() 
{
    FILE* file = fopen("list.txt", "r");
    if (file == NULL) 
    {
        fprintf(stderr, "打开文件list.txt失败.\n");
        fprintf(stderr, "链表建立失败.\n");
        return -1;
    }

    struct student* head = NULL;
    struct student* tail = NULL;

    while (1) 
    {
        struct student* new_student = (struct student*)malloc(sizeof(struct student));
        if (!new_student) 
        {
            fprintf(stderr, "内存申请失败.\n");
            return -1;  // 内存申请失败
        }

        fscanf(file, "%d", &new_student->no);
        if (new_student->no == 9999999) 
        {
            free(new_student);  // 释放未使用的内存
            break;  // 结束读取
        }

        fscanf(file, "%s", new_student->name);
        fscanf(file, "%d", &new_student->score);
        new_student->next = NULL;

        // 将新学生添加到链表的尾部
        if (head == NULL) 
        {
            head = new_student;
            tail = new_student;
        }
        else 
        {
            tail->next = new_student;
            tail = new_student;
        }
    }

    fclose(file);

    // 遍历链表并打印信息
    struct student* current = head;
    while (current != NULL) 
    {
        printf("%d %s %d\n", current->no, current->name, current->score);
        current = current->next;
    }

    // 释放链表
    current = head;
    while (current != NULL)
    {
        struct student* temp = current;
        current = current->next;
        free(temp);
    }

    return 0;
}
