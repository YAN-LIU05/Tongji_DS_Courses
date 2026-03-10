#define _CRT_SECURE_NO_WARNINGS
#include <iostream>
#include <algorithm>
#include <cstring>
#include <string>
using namespace std;

typedef int Status; // 定义状态类型
#define LOVERFLOW -1 // 定义内存溢出状态
#define ERROR -2 // 定义错误状态
#define SUCCESS 0 // 定义成功状态

typedef struct Card {
    char suit[128]; // 扑克牌花色
    char rank[4];   // 扑克牌点数
    int getValue() const { // 获取牌的数值
        switch (rank[0]) {
            case 'A': return 1; // A的值为1
            case 'J': return 11; // J的值为11
            case 'Q': return 12; // Q的值为12
            case 'K': return 13; // K的值为13
            default: return (rank[1] == '0') ? 10 : rank[0] - '0'; // 处理其他牌
        }
    }
    bool operator<(const Card& other) const { // 重载小于运算符
        return this->getValue() > other.getValue(); // 比较牌的数值，按从大到小排序
    }
} CardType;

CardType extractedCards[256]; // 存放提取的扑克牌

typedef struct Node {
    CardType card;      // 节点存放的扑克牌信息
    Node* previous;     // 前驱指针
    Node* next;         // 后继指针
} *DoubleLinkedList;

Status InitializeList(DoubleLinkedList& list) { // 初始化双向链表
    list = (DoubleLinkedList)malloc(sizeof(Node)); // 申请内存
    if (!list)
        return LOVERFLOW; // 检查内存分配是否成功
    list->previous = list; // 初始化前驱指针
    list->next = list;     // 初始化后继指针
    return SUCCESS; // 返回成功状态
}

Status InsertCard(DoubleLinkedList& list, CardType card, bool atHead) { // 插入扑克牌
    DoubleLinkedList newNode = (DoubleLinkedList)malloc(sizeof(Node)); // 申请新节点内存
    if (!newNode)
        return LOVERFLOW; // 检查内存分配是否成功
    newNode->card = card; // 设置新节点的扑克牌
    if (atHead) { // 如果插入到头部
        list->next->previous = newNode; // 调整指针
        newNode->next = list->next;
        list->next = newNode;
        newNode->previous = list;
    } else { // 如果插入到尾部
        list->previous->next = newNode; // 调整指针
        newNode->previous = list->previous;
        list->previous = newNode;
        newNode->next = list;
    }
    return SUCCESS; // 返回成功状态
}

Status RemoveCard(DoubleLinkedList& list, CardType& card, bool fromHead) { // 移除扑克牌
    if (list->next == list) { // 检查链表是否为空
        strcpy(card.suit, "NULL"); // 设置返回值为"NULL"
        return SUCCESS;
    }
    if (fromHead) { // 从头部移除
        DoubleLinkedList nextNode = list->next; // 获取下一个节点
        card = nextNode->card; // 保存被移除的扑克牌
        list->next = list->next->next; // 调整指针
        list->next->previous = list;
        free(nextNode); // 释放内存
    } else { // 从尾部移除
        DoubleLinkedList prevNode = list->previous; // 获取前一个节点
        card = prevNode->card; // 保存被移除的扑克牌
        list->previous = list->previous->previous; // 调整指针
        list->previous->next = list;
        free(prevNode); // 释放内存
    }
    return SUCCESS; // 返回成功状态
}

Status DisplayList(DoubleLinkedList list, bool fromHead) { // 显示链表中的扑克牌
    DoubleLinkedList current = fromHead ? list->next : list->previous; // 确定开始显示的节点
    while (current != list) { // 遍历链表
        cout << current->card.suit << " " << current->card.rank << endl; // 输出扑克牌信息
        current = fromHead ? current->next : current->previous; // 移动到下一个节点
    }
    return SUCCESS; // 返回成功状态
}

Status ExtractCards(DoubleLinkedList& list, char* suit, bool fromHead) { // 提取特定花色的扑克牌
    DoubleLinkedList current = fromHead ? list->next : list->previous; // 确定开始遍历的节点
    DoubleLinkedList tempNode; // 临时节点用于释放内存
    int count = 0; // 记录提取的牌的数量

    while (current != list) { // 遍历链表
        if (strcmp(current->card.suit, suit) == 0) { // 如果花色匹配
            current->previous->next = current->next; // 调整指针
            current->next->previous = current->previous;
            extractedCards[count++] = current->card; // 保存提取的扑克牌
            tempNode = current; // 保存当前节点用于释放内存
            current = fromHead ? current->next : current->previous; // 移动到下一个节点
            free(tempNode); // 释放内存
        } else {
            current = fromHead ? current->next : current->previous; // 移动到下一个节点
        }
    }

    sort(extractedCards, extractedCards + count); // 对提取的牌进行排序
    for (int i = 0; i < count; i++) 
        InsertCard(list, extractedCards[i], fromHead); // 将提取的牌插入链表
    return SUCCESS; // 返回成功状态
}

int main() {
    DoubleLinkedList list; // 声明链表
    InitializeList(list); // 初始化链表
    bool fromHead = true; // 标记当前操作方向
    string command; // 存储命令
    int n; // 存储命令数量

    cin >> n; // 输入命令数量
    for (int i = 0; i < n; i++) {
        cin >> command; // 输入命令
        if (command == "Append") {
            CardType currentCard; // 声明当前扑克牌
            cin >> currentCard.suit >> currentCard.rank; // 输入扑克牌信息
            InsertCard(list, currentCard, !fromHead); // 放到牌堆底部
        } else if (command == "Revert") {
            fromHead = !fromHead; // 切换操作方向
        } else if (command == "Pop") {
            CardType currentCard; // 声明当前扑克牌
            RemoveCard(list, currentCard, fromHead); // 移除扑克牌
            if (strcmp(currentCard.suit, "NULL") == 0)
                cout << currentCard.suit << endl; // 输出"NULL"
            else
                cout << currentCard.suit << " " << currentCard.rank << endl; // 输出扑克牌信息
        } else if (command == "Extract") {
            char suit[128]; // 声明花色字符串
            cin >> suit; // 输入花色
            ExtractCards(list, suit, fromHead); // 提取特定花色的扑克牌
        }
    }

    DisplayList(list, fromHead); // 显示链表中的扑克牌
    return 0; // 结束程序
}
