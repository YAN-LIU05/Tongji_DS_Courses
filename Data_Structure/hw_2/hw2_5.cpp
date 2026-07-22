#include <iostream>
#include <cstring> // 用于处理字符数组
using namespace std;

class MaxQueue {
private:
    int* mainQueue; // 主队列
    int* maxQueue;  // 辅助队列
    int front;      // 主队列头索引
    int rear;       // 主队列尾索引
    int maxFront;   // 辅助队列头索引
    int maxRear;    // 辅助队列尾索引
    int capacity;   // 队列容量
    int size;       // 当前元素数量

public:
    MaxQueue(int n);   // 构造函数
    ~MaxQueue();       // 析构函数
    void enqueue(int value); // 入队
    void dequeue();     // 出队
    void getMax();      // 获取最大值
    void printQueue();  // 打印队列
};

// 构造函数
MaxQueue::MaxQueue(int n) {
    capacity = n; // 设置队列的容量
    mainQueue = new int[capacity]; // 创建主队列
    maxQueue = new int[capacity]; // 创建辅助队列，用于存储当前最大值
    front = rear = 0; // 初始化队列的前后指针
    maxFront = maxRear = 0; // 初始化最大值队列的前后指针
    size = 0; // 初始化队列大小
}

// 析构函数
MaxQueue::~MaxQueue() {
    delete[] mainQueue; // 释放主队列的内存
    delete[] maxQueue; // 释放辅助队列的内存
}

// 入队操作
void MaxQueue::enqueue(int value) {
    // 检查队列是否已满
    if (size >= capacity) {
        cout << "Queue is Full" << endl; // 输出队列已满
        return; // 退出函数
    }

    // 将新元素添加到主队列
    mainQueue[rear] = value; 
    rear = (rear + 1) % capacity; // 更新后指针，循环使用
    size++; // 增加队列大小

    // 更新辅助队列，保持其递减顺序
    while (maxRear > maxFront && maxQueue[maxRear - 1] < value) {
        maxRear--; // 移除小于新值的元素
    }
    maxQueue[maxRear++] = value; // 添加新元素到辅助队列
}

// 出队操作
void MaxQueue::dequeue() {
    // 检查队列是否为空
    if (size == 0) {
        cout << "Queue is Empty" << endl; // 输出队列为空
        return; // 退出函数
    }
    
    // 记录出队的元素
    int value = mainQueue[front];
    front = (front + 1) % capacity; // 更新前指针，循环使用
    size--; // 减小队列大小

    // 如果出队的元素是当前最大值，移除它
    if (value == maxQueue[maxFront]) {
        maxFront++; // 更新最大值队列的前指针
        // 检查是否需要移除相同的最大值
        while (maxFront < maxRear && maxQueue[maxFront] == value) {
        maxFront++; // 移除所有相同的最大值
    }
    }
    cout << value << endl; // 输出出队的元素
}

// 获取最大值
void MaxQueue::getMax() {
    // 检查辅助队列是否为空
    if (maxFront == maxRear) {
        cout << "Queue is Empty" << endl; // 输出队列为空
        return; // 退出函数
    }
    cout << maxQueue[maxFront] << endl; // 输出当前最大值
}

// 打印队列
void MaxQueue::printQueue() {
    // 检查队列是否为空
    if (size == 0) {
        cout << "Queue is Empty" << endl; // 输出队列为空
        return; // 退出函数
    }
    // 遍历并打印主队列中的所有元素
    for (int i = 0, idx = front; i < size; i++, idx = (idx + 1) % capacity) {
        cout << mainQueue[idx] << " "; // 打印每个元素
    }
    cout << endl; // 换行
}


// 主函数
int main() {
    int n;
    cin >> n; // 队列的最大容量
    MaxQueue mq(n); // 创建 MaxQueue 实例

    char command[10]; // 用字符数组存储命令
    while (cin >> command) {
        if (strcmp(command, "enqueue") == 0) {
            int value;
            cin >> value;
            mq.enqueue(value);
        } else if (strcmp(command, "dequeue") == 0) {
            mq.dequeue();
        } else if (strcmp(command, "max") == 0) {
            mq.getMax();
        } else if (strcmp(command, "quit") == 0) {
            mq.printQueue(); // 输出队列中的所有元素
            break;
        }
    }

    return 0;
}


