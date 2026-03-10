/* 2352018 大数据 刘彦 */
#define _CRT_SECURE_NO_WARNINGS
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

struct student {
    int no;
    char* name; // 动态分配的字符指针
    int* score; // 动态分配的整数指针
    struct student* next;
};

int main() 
{
    FILE* infile = fopen("list.txt", "r");
    if (infile == NULL) 
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
            fprintf(stderr, "内存分配失败.\n");
            return -1; // 内存分配失败
        }

        fscanf(infile, "%d", &new_student->no);
        if (new_student->no == 9999999) 
        {
            free(new_student); // 释放内存
            break;
        }

        // 读取名字并根据实际长度分配内存
        char temp_name[9]; 
        fscanf(infile, "%8s", temp_name);
        temp_name[8] = '\0'; // 确保字符串终止符

        // 根据名字的实际长度分配内存
        new_student->name = (char*)malloc((strlen(temp_name) + 1) * sizeof(char)); 
        if (!new_student->name)
        {
            fprintf(stderr, "内存分配失败.\n");
            free(new_student);
            return -1; // 内存分配失败
        }
        strcpy(new_student->name, temp_name); // 复制名字

        new_student->score = (int*)malloc(sizeof(int));
        if (!new_student->score) 
        {
            fprintf(stderr, "内存分配失败.\n");
            free(new_student->name);
            free(new_student);
            return -1; // 内存分配失败
        }

        fscanf(infile, "%d", new_student->score);
        new_student->next = NULL;

        if (!head)
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

    fclose(infile);

    // 遍历并打印链表
    struct student* current = head;
    while (current)
    {
        printf("%d %s %d\n", current->no, current->name, *(current->score));
        current = current->next;
    }

    // 释放链表
    current = head;
    while (current) 
    {
        struct student* temp = current;
        current = current->next;
        free(temp->name);  // 释放name
        free(temp->score); // 释放score
        free(temp);        // 释放student
    }

    return 0;
}