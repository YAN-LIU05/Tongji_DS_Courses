/* 2352018 大数据 刘彦 */
#include <iostream>
#include <fstream>
#include <cstring>

using namespace std;

struct student {
    int no;
    char name[9];
    int score;
    struct student* next;
};

int main() {
    ifstream fin("list.txt");
    if (!fin.is_open()) 
    {
        cerr << "打开文件list.txt失败." << endl;
        cerr << "链表建立失败." << endl;
        return -1;
    }

    student* head = nullptr;
    student* tail = nullptr;

    while (1) {
        student* new_student = new student;
        if (!new_student) 
        {
            cerr << "内存申请失败." << endl;
            return -1;  // 内存申请失败
        }
        fin >> new_student->no;
        if (new_student->no == 9999999) {
            delete new_student; // 释放内存
            break;
        }
        fin >> new_student->name >> new_student->score;

        new_student->next = nullptr;

        if (!head) {
            head = new_student;
            tail = new_student;
        }
        else {
            tail->next = new_student;
            tail = new_student;
        }
    }

    fin.close();

    // 遍历并打印链表
    student* current = head;
    while (current) {
        cout << current->no << " " << current->name << " " << current->score << endl;
        current = current->next;
    }

    // 释放链表
    current = head;
    while (current) {
        student* temp = current;
        current = current->next;
        delete temp;
    }

    return 0;
}