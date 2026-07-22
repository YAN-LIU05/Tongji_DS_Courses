#include <iostream>
#include <cstring> 

using namespace std;

// 定义二叉树类
class BinaryTree {
public:
    // 构造函数，接受前序和中序遍历字符串
    BinaryTree(const char* preorder, const char* inorder) {
        strcpy(this->preorder, preorder); // 复制前序遍历字符串到成员变量
        strcpy(this->inorder, inorder);   // 复制中序遍历字符串到成员变量
        hasError = false;                 // 初始化错误标记
    }
    
    // 获取后序遍历结果
    void getPostorder(char* result);

private:
    char preorder[100];  // 存储前序遍历字符串，假设最大长度为100
    char inorder[100];   // 存储中序遍历字符串，假设最大长度为100
    bool hasError;       // 错误标记

    // 递归计算后序遍历
    void postorder(const char* preorder, const char* inorder, char* result, int& pos);
};

// 获取后序遍历的公共接口
void BinaryTree::getPostorder(char* result) {
    int pos = 0; // 定义位置索引
    postorder(preorder, inorder, result, pos);

    // 如果递归过程中出现错误，则设置结果为 "Error"
    if (hasError) {
        strcpy(result, "Error");
    } else {
        result[pos] = '\0'; // 添加字符串结尾符
    }
}

// 实现后序遍历的递归函数
void BinaryTree::postorder(const char* preorder, const char* inorder, char* result, int& pos) {
    // 基本情况：如果前序或中序字符串为空，返回
    if (preorder[0] == '\0' || inorder[0] == '\0') {
        return;
    }

    // 前序的第一个字符是根节点
    char root = preorder[0];
    // 在中序遍历中找到根节点的位置
    const char* root_pos = strchr(inorder, root);

    // 如果根节点不在中序字符串中，设置错误标记并返回
    if (root_pos == nullptr) {
        hasError = true;
        return;
    }

    // 递归分割中序和前序字符串，构造左右子树
    int left_size = root_pos - inorder; // 左子树的大小
    char left_inorder[100], right_inorder[100];
    char left_preorder[100], right_preorder[100];

    strncpy(left_inorder, inorder, left_size); // 左子树的中序
    left_inorder[left_size] = '\0';
    strcpy(right_inorder, root_pos + 1);       // 右子树的中序

    strncpy(left_preorder, preorder + 1, left_size); // 左子树的前序
    left_preorder[left_size] = '\0';
    strcpy(right_preorder, preorder + 1 + left_size); // 右子树的前序

    // 递归调用以获取左右子树的后序遍历
    postorder(left_preorder, left_inorder, result, pos);
    if (hasError) return;  // 如果递归调用出现错误，立即返回

    postorder(right_preorder, right_inorder, result, pos);
    if (hasError) return;  // 如果递归调用出现错误，立即返回

    // 将根节点添加到后序遍历的结果
    result[pos++] = root;
}

int main() {
    char line[200];
    char preorder[100], inorder[100];
    char result[100];

    // 持续读取输入，直到输入结束
    while (cin.getline(line, 200)) {
        // 查找空格位置，将前序和中序遍历分开
        char* space_pos = strchr(line, ' ');
        
        // 复制前序和中序遍历字符串
        strncpy(preorder, line, space_pos - line);
        preorder[space_pos - line] = '\0';
        strcpy(inorder, space_pos + 1);

        // 创建 BinaryTree 对象
        BinaryTree tree(preorder, inorder);

        // 获取后序遍历结果
        tree.getPostorder(result);

        // 输出后序遍历结果
        cout << result << endl;
    }

    return 0; // 返回 0 表示程序正常结束
}
