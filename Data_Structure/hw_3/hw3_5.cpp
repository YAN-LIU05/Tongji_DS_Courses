#include <iostream>
using namespace std;

#define MAX_NODES 1000 // 定义最大节点数

// 定义树节点结构体
struct TreeNode {
    int parent; // 节点的父节点
    TreeNode() {
        parent = 0; // 构造函数初始化父节点为 0
    }
};

// 查找最近公共祖先的函数
int get_grapa(TreeNode Tree[], int x, int y) {
    bool ancestors[MAX_NODES] = {false}; // 用于记录 x 的所有祖先

    // 如果两个节点相同，直接返回该节点
    if (x == y) return x; 

    // 存储 x 的所有祖先
    while (x != 0) {
        ancestors[x] = true; // 标记当前节点为祖先
        x = Tree[x].parent; // 移动到父节点
    }

    // 查找 y 是否在 x 的祖先中
    while (y != 0) {
        if (ancestors[y]) // 如果 y 是 x 的祖先
            return y; // 返回 y 作为最近公共祖先
        y = Tree[y].parent; // 移动到父节点
    }
    return -1; // 如果没有找到公共祖先，返回 -1
}

int main() {
    int T; // 测试用例的数量
    cin >> T; // 输入测试用例数量

    while (T--) { // 遍历每个测试用例
        int N, M; // N 是节点数量，M 是查询数量
        cin >> N >> M; // 输入节点数量和查询数量
        
        TreeNode Tree[MAX_NODES]; // 定义树节点数组

        // 输入树的结构
        for (int i = 1; i < N; i++) {
            int temp_parent, temp_children; // 临时变量存储父节点和子节点
            cin >> temp_parent >> temp_children; // 输入父子关系
            Tree[temp_children].parent = temp_parent; // 设置子节点的父节点
        }

        // 处理查询
        for (int i = 0; i < M; i++) {
            int x_node, y_node; // 存储查询的两个节点
            cin >> x_node >> y_node; // 输入要查询的节点
            cout << get_grapa(Tree, x_node, y_node) << endl; // 输出最近公共祖先
        }
    }

    return 0; // 程序结束
}
