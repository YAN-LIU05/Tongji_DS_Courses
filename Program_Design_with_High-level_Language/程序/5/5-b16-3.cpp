/* 2352018 信06 刘彦 */
#include <iostream>
#include <string>

using namespace std;

#define MAX_STUDENTS 10
#define MAX_ID_LENGTH 8
#define MAX_NAME_LENGTH 8

// 输入学生信息
void input(string id[], string name[], int scores[]) 
{
    for (int i = 0; i < MAX_STUDENTS; ++i) 
    {
        cout << "请输入第" << (i + 1) << "个人的学号、姓名、成绩" << endl;
        cin >> id[i];
        cin >> name[i];
        cin >> scores[i];
        cin.ignore(65536, '\n'); 
    }
}

// 冒泡排序，按学号升序排序
void sort(int scores[], string id[], string name[]) 
{
    for (int i = 0; i < MAX_STUDENTS - 1; ++i) 
    {
        for (int j = 0; j < MAX_STUDENTS - i - 1; ++j) 
        {
            if (id[j] > id[j + 1]) 
            {
                // 交换成绩
                int tempScore = scores[j];
                scores[j] = scores[j + 1];
                scores[j + 1] = tempScore;

                // 交换学号
                string tempId = id[j];
                id[j] = id[j + 1];
                id[j + 1] = tempId;

                // 交换姓名
                string tempName = name[j];
                name[j] = name[j + 1];
                name[j + 1] = tempName;
            }
        }
    }
}

// 打印所有学生信息
void print(string id[], string name[], int scores[]) 
{
    for (int i = 0; i < MAX_STUDENTS; ++i) {
        cout << name[i] << " " << id[i] << " " << scores[i] << endl;
    }
}

int main() 
{
    string id[MAX_STUDENTS];
    string name[MAX_STUDENTS];
    int scores[MAX_STUDENTS];

    // 输入学生信息
    input(id, name, scores);

    // 按学号升序排序
    sort(scores, id, name);
    cout << endl;

    // 打印所有学生信息
    cout << "全部学生(学号升序):" << endl;
    print(id, name, scores);

    return 0;
}