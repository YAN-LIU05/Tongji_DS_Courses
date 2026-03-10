#include <iostream>
#include <cstdlib> 
using namespace std;

struct TreeNode {
    int val; // 节点值
    TreeNode *left; // 左子节点
    TreeNode *right; // 右子节点
    TreeNode(int x) {
        val = x;
        left = NULL;
        right = NULL;
    }
};

class Solution {
private:
    int start; // 开始感染的节点值
    int res = 0; // 记录最大时间

public:
    int cal_time(TreeNode* root, int start);  // 计算从指定节点开始感染整棵树所需的时间
    int dfs(TreeNode* cur); // 深度优先搜索
};

// 计算从指定节点开始感染整棵树所需的时间
int Solution::cal_time(TreeNode* root, int start) {
    this->start = start;
    dfs(root);
    return res;
}

// 深度优先搜索
int Solution::dfs(TreeNode* cur) {
    if (cur == nullptr) return 0; // 递归终止条件

    int rl = dfs(cur->left);  // 左子树返回值
    int rr = dfs(cur->right); // 右子树返回值

    // 找到感染起点
    if (cur->val == start) {
        res = max(res, max(rl, rr)); // 更新结果
        return -1; // 返回-1表示找到感染起点
    }

    // 处理从左子树传播的情况
    if (rl < 0) {
        res = max(res, -rl + rr); // 更新结果
        return rl - 1; // 返回传播路径
    }
    // 处理从右子树传播的情况
    else if (rr < 0) {
        res = max(res, -rr + rl); // 更新结果
        return rr - 1; // 返回传播路径
    }
    // 返回左右子树的最大深度
    return max(rl, rr) + 1;
}

int main() {
    int n, start;
    cin >> n >> start; // 输入节点数和起始节点

    // 动态分配节点数组
    TreeNode** nodes = (TreeNode**)malloc(n * sizeof(TreeNode*));
    for (int i = 0; i < n; ++i) {
        nodes[i] = (TreeNode*)malloc(sizeof(TreeNode)); // 创建节点
        nodes[i]->val = i; // 初始化节点值
        nodes[i]->left = nullptr; // 初始化子节点
        nodes[i]->right = nullptr;
    }

    // 输入每个节点的左右子节点
    for (int i = 0; i < n; ++i) {
        int left, right;
        cin >> left >> right; // 左右子节点编号
        if (left != -1) {
            nodes[i]->left = nodes[left]; // 连接左子节点
        }
        if (right != -1) {
            nodes[i]->right = nodes[right]; // 连接右子节点
        }
    }

    Solution solution;
    int result = solution.cal_time(nodes[0], start); // 从根节点开始计算
    cout << result << endl; // 输出结果

    // 释放内存
    for (int i = 0; i < n; ++i) {
        free(nodes[i]); // 释放每个节点
    }
    free(nodes); // 释放节点数组

    return 0;
}
