#include <iostream>
 
using namespace std;
 
struct Node {
    char data;          // 节点值
    Node* left_p;      // 左子树指针
    Node* right_p;     // 右子树指针
 
    Node(char d) {
        data = d;
        left_p = nullptr;
        right_p = nullptr;
    }
};
 
// 链表节点结构体
struct StackNode {
    Node* data;         // 存储的树节点
    StackNode* next;    // 指向下一个节点
 
    StackNode(Node* d) {
        data = d;
        next = nullptr;
    } 
};
 
// 栈结构体
struct Stack {
    StackNode* top; // 栈顶指针
 
    Stack() {
        top = nullptr; // 初始化栈为空
    }
 
    // 入栈操作
    void push(Node* node) {
        StackNode* newNode = new StackNode(node); // 创建新栈节点
        newNode->next = top; // 将新节点指向当前栈顶
        top = newNode; // 更新栈顶
    }
 
    // 出栈操作
    Node* pop() {
        if (top == nullptr) return nullptr; // 如果栈为空，返回 nullptr
        StackNode* temp = top; // 临时保存栈顶节点
        Node* result = temp->data; // 获取栈顶节点数据
        top = top->next; // 更新栈顶
        delete temp; // 释放旧栈顶节点内存
        return result; // 返回栈顶节点数据
    }
 
    // 判断栈是否为空
    bool isEmpty() {
        return top == nullptr; // 如果 top 为 nullptr，表示栈为空
    }
};
 
// 构建树的逻辑
void buildTree(int n, Node* root) {
    Stack stack; // 创建栈实例
    Node* pointer = root;
    bool left = true;
 
    while (n) {
        char opt[5]; // 字符数组来存储操作
        cin >> opt; // 读取操作
 
        if (opt[0] == 'p' && opt[1] == 'o' && opt[2] == 'p') { // 判断是否为 "pop"
            if (left) left = false; // 仅在左子树未遍历时pop
            else {
                if (stack.isEmpty()) continue;
                pointer = stack.pop(); // 回到上一个未遍历的节点
            }
        } else { // 处理 push 操作
            char dt;
            cin >> dt; // 读取节点值
            stack.push(pointer); // 保存当前节点到栈
 
            if (left) {
                pointer->left_p = new Node(dt); // 插入左子节点
                pointer = pointer->left_p; // 移动到左子节点
            } else {
                pointer->right_p = new Node(dt); // 插入右子节点
                pointer = pointer->right_p; // 移动到右子节点
                stack.pop(); // 当前节点已满，回退
            }
            left = true; // 允许插入下一个节点
            n--;
        }
    }
}
 
// 后序遍历函数
void back_traverse(Node* root) {
    if (root) {
        back_traverse(root->left_p); // 递归访问左子树
        back_traverse(root->right_p); // 递归访问右子树
        cout << root->data; // 输出当前节点的值
    }
}
 
int main() {
    int n;
    cin >> n; // 读取节点数
 
    char dt;
    char opt[5]; // 字符数组来存储操作
    cin >> opt >> dt; // 初始化根节点
    Node* root = new Node(dt);
 
    buildTree(n - 1, root); // 构建树
    back_traverse(root); // 输出后序遍历
    cout << endl; // 输出换行
 
    return 0;
}