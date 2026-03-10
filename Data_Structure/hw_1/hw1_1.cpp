#include <iostream>
using namespace std;

struct ListNode {
    int val;            // 节点的值
    ListNode* next;    // 指向下一个节点的指针
    ListNode(int x) : val(x), next(nullptr) {} // 构造函数，初始化节点值和指针
};

//接收链表头指针的引用和旋转次数k
void rotate(ListNode*& head, int k) {
    if (!head || k == 0) return;

    // 计算链表的长度
    ListNode* tail = head;
    int length = 1;
    while (tail->next) {
        tail = tail->next;
        length++;
    }
    tail->next = head;  // 形成循环链表
    // 找到新的头节点位置
    k = k % length;
    int steps = length - k;
    ListNode* newTail = head;
    for (int i = 1; i < steps; i++) {
        newTail = newTail->next;
    }
    head = newTail->next;  // 新头节点
    newTail->next = nullptr; // 断开循环
}

//打印链表的所有节点值
//从头节点开始，逐个访问节点并打印其值，直到head为nullptr
void printList(ListNode* head) {
    while (head) {
        cout << head->val << " ";
        head = head->next;
    }
    cout << endl;
}

int main() {
    int n, k;
    cin >> n >> k;

    ListNode* head = nullptr;  //指向链表的头节点，初始为空
    ListNode* tail = nullptr;  //指向链表的尾节点，初始为空
    for (int i = 0; i < n; i++) {  //每次循环中，读取一个整数并用该值创建一个新的链表节点 newNode
        int value;
        cin >> value;
        ListNode* newNode = new ListNode(value);
        if (!head) {  //如果head为空（即链表还未创建），将newNode赋值给head和tail，表示链表的开始
            head = newNode;
            tail = head;
        } 
        else {  //如果链表已存在，将newNode添加到尾部：更新tail->next指向新节点,将tail更新为newNode，使其指向新的尾节点
            tail->next = newNode;
            tail = newNode;
        }
    }

    rotate(head, k);
    printList(head);



    // 清理内存
    while (head) {
        ListNode* temp = head;
        head = head->next;
        delete temp;
    }

    return 0;
}
