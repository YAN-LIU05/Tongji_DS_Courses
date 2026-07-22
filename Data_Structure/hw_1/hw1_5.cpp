#include <iostream>
#include <cstring>

using namespace std;

#define MAX_NAME_LENGTH 100  // 学生姓名的最大长度
#define MAX_ID_LENGTH 100    // 学生ID的最大长度

// 定义学生结构体
typedef struct Student {
    char student_id[MAX_ID_LENGTH];  // 学生ID
    char name[MAX_NAME_LENGTH];       // 学生姓名
    Student* next;                    // 指向下一个学生的指针
} Student;

// 定义顺序链表结构体
typedef struct SequentialList {
    Student* head;  // 指向链表第一个学生的指针
    int size;       // 链表中学生的数量

    // 构造函数，初始化空链表
    SequentialList() {
        head = nullptr;  // 初始化时没有学生
        size = 0;       // 大小为0
    }

    // 在指定索引插入新学生
    int insert(int index, const char* student_id, const char* name) {
        // 检查索引是否有效
        if (index < 1 || index > size + 1) {
            return -1;  // 无效索引
        }

        Student* newStudent = new Student;  // 创建新学生
        strcpy(newStudent->student_id, student_id);  // 复制学生ID
        strcpy(newStudent->name, name);  // 复制学生姓名
        newStudent->next = nullptr;  // 初始化next指针

        // 在链表头部插入
        if (index == 1) {
            newStudent->next = head;  // 新学生指向当前头部
            head = newStudent;        // 更新头部为新学生
        } else {
            // 遍历到插入位置前一个学生
            Student* current = head;
            for (int i = 1; i < index - 1; i++) {
                current = current->next;  // 移动到下一个学生
            }
            newStudent->next = current->next;  // 将新学生连接到后一个学生
            current->next = newStudent;         // 将当前学生连接到新学生
        }
        size++;  // 增加链表大小
        return 0;  // 插入成功
    }

    // 在指定索引删除学生
    int remove(int index) {
        // 检查索引是否有效
        if (index < 1 || index > size) {
            return -1;  // 无效索引
        }

        Student* toDelete;  // 指向要删除的学生
        // 从链表头部删除
        if (index == 1) {
            toDelete = head;  // 获取头部学生
            head = head->next;  // 将头部移到下一个学生
        } else {
            // 遍历到删除位置前一个学生
            Student* current = head;
            for (int i = 1; i < index - 1; i++) {
                current = current->next;  // 移动到下一个学生
            }
            toDelete = current->next;  // 获取要删除的学生
            current->next = toDelete->next;  // 跳过要删除的学生
        }
        delete toDelete;  // 释放内存
        size--;  // 减少链表大小
        return 0;  // 删除成功
    }

    // 按姓名检查学生
    void checkByName(const char* name) {
        Student* current = head;  // 从头部开始
        for (int i = 1; current != nullptr; i++) {
            // 比较姓名
            if (strcmp(current->name, name) == 0) {
                cout << i << " " << current->student_id << " " << name << endl;  // 输出索引、ID和姓名
                return;  // 找到姓名
            }
            current = current->next;  // 移动到下一个学生
        }
        cout << -1 << endl;  // 未找到姓名
    }

    // 按ID检查学生
    void checkById(const char* student_id) {
        Student* current = head;  // 从头部开始
        for (int i = 1; current != nullptr; i++) {
            // 比较ID
            if (strcmp(current->student_id, student_id) == 0) {
                cout << i << " " << student_id << " " << current->name << endl;  // 输出索引、ID和姓名
                return;  // 找到ID
            }
            current = current->next;  // 移动到下一个学生
        }
        cout << -1 << endl;  // 未找到ID
    }

    // 统计学生数量
    int count() const {
        return size;  // 返回当前学生数量
    }

    // 析构函数，释放链表内存
    ~SequentialList() {
        while (head != nullptr) {
            Student* temp = head;  // 临时指针保存当前头部
            head = head->next;  // 移动头部到下一个学生
            delete temp;  // 释放当前学生内存
        }
    }
} SequentialList;

#include <iostream>
#include <cstring> // for strcpy
using namespace std;

#define MAX_ID_LENGTH 20
#define MAX_NAME_LENGTH 50

struct Student {
    char student_id[MAX_ID_LENGTH]; // 学生ID
    char name[MAX_NAME_LENGTH];       // 学生姓名
    Student* next;                    // 指向下一个学生的指针
};

struct SequentialList {
    Student* head;  // 指向链表第一个学生的指针
    int size;       // 链表中学生的数量

    // 构造函数，初始化空链表
    SequentialList() {
        head = nullptr;  // 初始化时没有学生
        size = 0;       // 大小为0
    }

    // 析构函数，释放链表内存
    ~SequentialList();

    int insert(int index, const char* student_id, const char* name);
    int remove(int index);
    void checkByName(const char* name);
    void checkById(const char* student_id);
    int count() const;
};

// 析构函数，释放链表内存
SequentialList::~SequentialList() {
    while (head != nullptr) {
        Student* temp = head;  // 临时指针保存当前头部
        head = head->next;      // 移动头部到下一个学生
        delete temp;            // 释放当前学生内存
    }
}

// 在指定索引插入新学生
int SequentialList::insert(int index, const char* student_id, const char* name) {
    if (index < 1 || index > size + 1) {
        return -1;  // 无效索引
    }

    Student* newStudent = new Student;  // 创建新学生
    strcpy(newStudent->student_id, student_id);  // 复制学生ID
    strcpy(newStudent->name, name);  // 复制学生姓名
    newStudent->next = nullptr;  // 初始化next指针

    // 在链表头部插入
    if (index == 1) {
        newStudent->next = head;  // 新学生指向当前头部
        head = newStudent;        // 更新头部为新学生
    } else {
        Student* current = head;  // 遍历到插入位置前一个学生
        for (int i = 1; i < index - 1; i++) {
            current = current->next;  // 移动到下一个学生
        }
        newStudent->next = current->next;  // 将新学生连接到后一个学生
        current->next = newStudent;         // 将当前学生连接到新学生
    }
    size++;  // 增加链表大小
    return 0;  // 插入成功
}

// 在指定索引删除学生
int SequentialList::remove(int index) {
    if (index < 1 || index > size) {
        return -1;  // 无效索引
    }

    Student* toDelete;  // 指向要删除的学生
    if (index == 1) {
        toDelete = head;  // 获取头部学生
        head = head->next;  // 将头部移到下一个学生
    } else {
        Student* current = head;  // 遍历到删除位置前一个学生
        for (int i = 1; i < index - 1; i++) {
            current = current->next;  // 移动到下一个学生
        }
        toDelete = current->next;  // 获取要删除的学生
        current->next = toDelete->next;  // 跳过要删除的学生
    }
    delete toDelete;  // 释放内存
    size--;  // 减少链表大小
    return 0;  // 删除成功
}

// 按姓名检查学生
void SequentialList::checkByName(const char* name) {
    Student* current = head;  // 从头部开始
    for (int i = 1; current != nullptr; i++) {
        if (strcmp(current->name, name) == 0) {
            cout << i << " " << current->student_id << " " << name << endl;  // 输出索引、ID和姓名
            return;  // 找到姓名
        }
        current = current->next;  // 移动到下一个学生
    }
    cout << -1 << endl;  // 未找到姓名
}

// 按ID检查学生
void SequentialList::checkById(const char* student_id) {
    Student* current = head;  // 从头部开始
    for (int i = 1; current != nullptr; i++) {
        if (strcmp(current->student_id, student_id) == 0) {
            cout << i << " " << student_id << " " << current->name << endl;  // 输出索引、ID和姓名
            return;  // 找到ID
        }
        current = current->next;  // 移动到下一个学生
    }
    cout << -1 << endl;  // 未找到ID
}

// 统计学生数量
int SequentialList::count() const {
    return size;  // 返回当前学生数量
}

int main() {
    int n;
    cin >> n;  // 输入学生数量
    SequentialList seqList;  // 创建顺序链表对象

    // 输入学生信息
    for (int i = 0; i < n; ++i) {
        char student_id[MAX_ID_LENGTH], name[MAX_NAME_LENGTH];
        cin >> student_id >> name;  // 输入学生ID和姓名
        seqList.insert(i + 1, student_id, name);  // 在链表中插入学生
    }

    // 处理操作
    char operation[10];
    while (cin >> operation) {
        if (strcmp(operation, "insert") == 0) {
            int index;
            char student_id[MAX_ID_LENGTH], name[MAX_NAME_LENGTH];
            cin >> index >> student_id >> name;  // 输入操作参数
            cout << seqList.insert(index, student_id, name) << endl;  // 执行插入操作

        } else if (strcmp(operation, "remove") == 0) {
            int index;
            cin >> index;  // 输入要删除的索引
            cout << seqList.remove(index) << endl;  // 执行删除操作

        } else if (strcmp(operation, "check") == 0) {
            char type[10], value[MAX_NAME_LENGTH];
            cin >> type >> value;  // 输入检查类型和对应值
            if (strcmp(type, "name") == 0) {
                seqList.checkByName(value);  // 按姓名检查
            } else if (strcmp(type, "no") == 0) {
                seqList.checkById(value);  // 按ID检查
            }
        } else if (strcmp(operation, "end") == 0) {
            cout << seqList.count() << endl;  // 输出链表中的学生数量
            break;  // 结束操作
        }
    }

    return 0;  // 程序结束
}
