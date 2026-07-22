#include <iostream>
#include <cstring>
#include <cstdlib> 

using namespace std;

int string_to_integer(const char *s); // 前向声明

class Tree {
public:
    // 节点结构体
    struct Node {
        char name; // 节点的名称（一个字符）
        int l, r, p; // 左子节点索引、右子节点索引、父节点索引
        
        // 默认构造函数，将左子节点、右子节点和父节点初始化为 -1，表示不存在
        Node() { 
            p = l = r = -1;
        }
    };

    // 默认构造函数：初始化树为空
    Tree();
    
    // 带参数的构造函数：初始化一个有 n 个节点的树
    Tree(int n);
    
    // 析构函数：释放树的资源
    ~Tree();
    
    // 清空树，释放所有节点内存
    void Clear();
    
    // 输入树的结构（节点名称和左右子节点的索引）
    int InputTree();
    
    // 获取树的根节点索引
    int Root() const;
    
    // 获取树的节点数量
    int Size() const;
    
    // 获取树的深度
    int Depth() const;
    
    // 静态方法：比较两棵树是否同构（结构是否相同）
    static bool tree_compare(const Tree &t1, const Tree &t2);
    
    // 打印树的结构：输出每个节点的信息（名称、左子节点、右子节点）
    void Print() const;

private:
    int size, root; // 树的节点数量和根节点的索引
    Node *list; // 指向树的节点数组
    
    // 查找树的根节点
    int FindRoot();
    
    // 使用递归计算树的深度
    int DepthDFS(int i) const;
    
    // 静态方法：递归比较两棵树的结构是否相同
    static bool tree_compareDFS(const Tree &t1, const Tree &t2, int i1, int i2);
};


// 默认构造函数
Tree::Tree() {
    size = 0;
    list = nullptr;
}

// 带参数的构造函数
Tree::Tree(int n) {
    size = n;
    list = (Node *)malloc(n * sizeof(Node)); // 分配内存给节点数组
    for (int i = 0; i < n; ++i) {
        new (&list[i]) Node(); // 使用 placement new 调用构造函数
    }
}

// 析构函数
Tree::~Tree() {
    Clear();
}

// 清空树
void Tree::Clear() {
    if (list) {
        for (int i = 0; i < size; ++i) {
            list[i].~Node(); // 手动调用析构函数
        }
        free(list); // 释放节点数组的内存
    }
    list = nullptr;
    size = 0;
}

// 输入树的结构
int Tree::InputTree() {
    for (int i = 0; i < size; i++) {
        char name;
        char s1[10], s2[10]; // 假设最大长度为 10
        cin >> name >> s1 >> s2; // 从输入读取节点信息
        list[i].name = name; // 设置节点名称
        list[i].l = string_to_integer(s1); // 转换左子节点索引
        list[i].r = string_to_integer(s2); // 转换右子节点索引
        // 更新子节点的父节点索引
        if (list[i].r >= 0) list[list[i].r].p = i;
        if (list[i].l >= 0) list[list[i].l].p = i;
    }
    return root = FindRoot(); // 查找根节点并设置根节点索引
}

// 获取根节点索引
int Tree::Root() const {
    return root;
}

// 获取树的节点数量
int Tree::Size() const {
    return size;
}

// 获取树的深度
int Tree::Depth() const {
    return DepthDFS(root);
}

// 比较两棵树是否同构
bool Tree::tree_compare(const Tree &t1, const Tree &t2) {
    if (t1.Size() != t2.Size()) // 如果节点数量不同，返回 false
        return false;
    return tree_compareDFS(t1, t2, t1.Root(), t2.Root()); // 深度优先搜索比较两棵树
}

// 打印树的节点信息
void Tree::Print() const {
    for (int i = 0; i < size; i++)
        cout << list[i].name << ' ' << list[i].l << ' ' << list[i].r << endl; // 输出节点信息
}

// 查找根节点
int Tree::FindRoot() {
    bool *bo = (bool *)malloc(size * sizeof(bool)); // 分配内存给布尔数组，用于标记访问过的节点
    memset(bo, 0, size * sizeof(bool)); // 初始化布尔数组
    int i = 0; // 从第一个节点开始
    while (list[i].p != -1 && !bo[list[i].p]) { // 迭代寻找父节点
        i = list[i].p; // 移动到父节点
        bo[i] = true; // 标记父节点已访问
    }
    free(bo); // 释放布尔数组的内存
    return list[i].p == -1 ? i : -1; // 如果找到了根节点，返回根节点索引；否则返回 -1
}

// 深度优先搜索计算深度
int Tree::DepthDFS(int i) const {
    if (i == -1) 
        return 0; // 如果索引为 -1，返回深度 0
    int dl = DepthDFS(list[i].l); // 递归计算左子树深度
    int dr = DepthDFS(list[i].r); // 递归计算右子树深度
    return max(dl, dr) + 1; // 返回最大深度加 1
}

// 深度优先搜索比较两棵树
bool Tree::tree_compareDFS(const Tree &t1, const Tree &t2, int i1, int i2) {
    if (i1 == -1 || i2 == -1) 
        return i1 == i2; // 如果其中一棵树遍历结束，检查索引是否相等
    if (t1.list[i1].name != t2.list[i2].name) 
        return false; // 如果节点名称不同，返回 false
    // 检查同构情况
    return ((tree_compareDFS(t1, t2, t1.list[i1].l, t2.list[i2].l) && tree_compareDFS(t1, t2, t1.list[i1].r, t2.list[i2].r)) ||
            (tree_compareDFS(t1, t2, t1.list[i1].l, t2.list[i2].r) && tree_compareDFS(t1, t2, t1.list[i1].r, t2.list[i2].l)));           
}

// 字符串转化为整数
int string_to_integer(const char *s) {
    int n = 0; // 初始化结果
    for (size_t i = 0; i < strlen(s); i++) { // 遍历字符串
        char c = s[i]; // 获取当前字符
        if (c == '-')
            return -1; // 如果是负号，返回 -1
        if (c >= '0' && c <= '9') // 如果是数字字符
            n = n * 10 + (c - '0'); // 将字符转化为整数
    }
    return n; // 返回转换结果
}

// 主函数
int main() {
    int n1, n2; // 两棵树的节点数量
    cin >> n1; // 输入第一棵树的节点数量
    
    // 使用 malloc 创建 Tree 对象并调用构造函数
    Tree *t1 = (Tree *)malloc(sizeof(Tree)); 
    new (t1) Tree(n1); // 调用构造函数

    t1->InputTree(); // 输入第一棵树的结构
    
    cin >> n2; // 输入第二棵树的节点数量
    
    // 使用 malloc 创建第二棵树对象并调用构造函数
    Tree *t2 = (Tree *)malloc(sizeof(Tree)); 
    new (t2) Tree(n2); // 调用构造函数

    t2->InputTree(); // 输入第二棵树的结构
    
    // 比较两棵树并输出结果
    cout << (Tree::tree_compare(*t1, *t2) ? "Yes" : "No") << endl; 
    cout << t1->Depth() << endl; // 输出第一棵树的深度
    cout << t2->Depth() << endl; // 输出第二棵树的深度
    
    // 手动调用析构函数和释放内存
    t1->~Tree(); // 调用析构函数
    free(t1); // 释放内存
    
    t2->~Tree(); // 调用析构函数
    free(t2); // 释放内存
    
    return 0; // 返回成功状态
}
