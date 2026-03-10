/* 2352018 大数据 刘彦 */
#include <iostream>
#include <fstream>
#include <cstring>

using namespace std;

struct student {
    int no;
    char* name; // 动态分配的字符指针
    int* score; // 动态分配的整数指针
    struct student* next;
};

char* tj_strcpy(char* s1, const char* s2)
{
    if (s1 == NULL)
        return s1;

    char* s = s1;

    if (s2 == NULL)
        *s = '\0';
    else
    {
        for (; *s2 != '\0'; s++, s2++)
            *s = *s2;
        *s = '\0';
    }
    return s1;
}

int main() 
{
    ifstream fin;
    fin.open("list.txt", ios::in);
    if (!fin.is_open()) 
    {
        cerr << "打开文件list.txt失败." << endl;
        cerr << "链表建立失败." << endl;
        return -1;
    }

    student* head = nullptr;
    student* tail = nullptr;

    while (true) 
    {
        student* new_student = new student; // 申请学生节点
        if (!new_student)
        {
            cerr << "内存分配失败." << endl;
            return -1; // 内存分配失败
        }

        fin >> new_student->no;
        if (new_student->no == 9999999) 
        {
            delete new_student; // 释放内存
            break;
        }

        // 读取名字并根据实际长度分配内存
        char temp_name[9]; // 假设最大长度为8（加上'\0'）
        fin >> temp_name;
        temp_name[8] = '\0'; // 确保字符串终止符

        // 根据名字的实际长度分配内存
        new_student->name = new char[strlen(temp_name) + 1];
        if (!new_student->name) 
        {
            cerr << "内存分配失败." << endl;
            delete new_student;
            return -1; // 内存分配失败
        }
        tj_strcpy(new_student->name, temp_name); // 复制名字

        new_student->score = new int; // 申请成绩内存
        if (!new_student->score) 
        {
            cerr << "内存分配失败." << endl;
            delete[] new_student->name;
            delete new_student;
            return -1; // 内存分配失败
        }

        fin >> *(new_student->score); // 读取成绩
        new_student->next = nullptr;

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

    fin.close();

    // 遍历并打印链表
    student* current = head;
    while (current) 
    {
        cout << current->no << " " << current->name << " " << *(current->score) << endl;
        current = current->next;
    }

    // 释放链表（这里不考虑释放，按要求只处理申请错误）
    current = head;
    while (current) 
    {
        student* temp = current;
        current = current->next;
        delete[] temp->name;  // 释放name
        delete temp->score;    // 释放score
        delete temp;           // 释放student
    }

    return 0;
}
