#include <iostream>
using namespace std;

struct TreeNode {
    int val;
    int count;
    TreeNode* left;
    TreeNode* right;
    TreeNode(int x) 
    {
        val = x;
        count = 1;
        left = nullptr;
        right = nullptr;
    }
};

class BST {
private:
    TreeNode* root;

public:
    BST() 
    {
        root = nullptr;
    }

    // 插入操作
    void insert(int x);

    // 删除操作
    void remove(int x);

    // 查询某个数字的计数
    void count(int x);

    // 查询最小值
    void findMinValue();

    // 查询某个数字的前驱
    void findPredecessor(int x);

private:
    // 内部实现：插入值 x
    void insert(TreeNode*& node, int x);

    // 内部实现：删除值 x
    void remove(TreeNode*& node, int x);

    // 内部实现：查找节点 x
    TreeNode* find(TreeNode* node, int x);

    // 内部实现：查找树的最小值
    TreeNode* findMin(TreeNode* node);

    // 内部实现：查找树的最大值
    TreeNode* findMax(TreeNode* node);

    // 内部实现：查找 x 的前驱
    TreeNode* findPredecessor(TreeNode* node, int x);
};

/**
 * @brief           向二叉搜索树中插入值 x
 */
void BST::insert(int x) 
{
    insert(root, x);
}

/**
 * @brief           从二叉搜索树中删除值 x
 */
void BST::remove(int x) 
{
    if (!find(root, x))
        cout << "None" << endl;
    else
        remove(root, x);
}

/**
 * @brief           查询某个数字的计数
 */
void BST::count(int x) 
{
    TreeNode* node = find(root, x);
    if (node)
        cout << node->count << endl;
    else
        cout << "0" << endl;
}

/**
 * @brief           查询二叉搜索树中的最小值
 */
void BST::findMinValue() 
{
    TreeNode* minNode = findMin(root);
    cout << minNode->val << endl;
}

/**
 * @brief           查询某个数字的前驱
 */
void BST::findPredecessor(int x) 
{
    TreeNode* pred = findPredecessor(root, x);
    if (pred)
        cout << pred->val << endl;
    else
        cout << "None" << endl;
}

/**
 * @brief           内部实现：插入值 x
 */
void BST::insert(TreeNode*& node, int x) 
{
    if (node == nullptr) {
        node = new TreeNode(x);
        return;
    }
    if (x < node->val)
        insert(node->left, x);
    else if (x > node->val)
        insert(node->right, x);
    else
        node->count++;
}

/**
 * @brief           内部实现：删除值 x
 */
void BST::remove(TreeNode*& node, int x) 
{
    if (node == nullptr)
        return;
    if (x < node->val)
        remove(node->left, x);
    else if (x > node->val)
        remove(node->right, x);
    else {
        if (node->count > 1)
            node->count--;
        else {
            if (node->left == nullptr && node->right == nullptr) {
                delete node;
                node = nullptr;
            } 
            else if (node->left == nullptr) {
                TreeNode* temp = node;
                node = node->right;
                delete temp;
            } 
            else if (node->right == nullptr) {
                TreeNode* temp = node;
                node = node->left;
                delete temp;
            } 
            else {
                TreeNode* successor = findMin(node->right);
                node->val = successor->val;
                node->count = successor->count;
                remove(node->right, successor->val);
            }
        }
    }
}

/**
 * @brief           内部实现：查找节点 x
 */
TreeNode* BST::find(TreeNode* node, int x) 
{
    if (node == nullptr)
        return nullptr;
    if (x < node->val)
        return find(node->left, x);
    else if (x > node->val)
        return find(node->right, x);
    else
        return node;
}

/**
 * @brief           内部实现：查找树的最小值
 */
TreeNode* BST::findMin(TreeNode* node) 
{
    while (node && node->left)
        node = node->left;
    return node;
}

/**
 * @brief           内部实现：查找树的最大值
 */
TreeNode* BST::findMax(TreeNode* node) 
{
    while (node && node->right)
        node = node->right;
    return node;
}

/**
 * @brief           内部实现：查找 x 的前驱
 */
TreeNode* BST::findPredecessor(TreeNode* node, int x) 
{
    if (node == nullptr)
        return nullptr;
    if (x <= node->val)
        return findPredecessor(node->left, x);
    else {
        TreeNode* temp = findPredecessor(node->right, x);
        if (temp)
            return temp;
        return node;
    }
}

int main() 
{
    int n;
    cin >> n;
    BST bst;

    while (n--) {
        int op, x;
        cin >> op;

        if (op == 1) {
            cin >> x;
            bst.insert(x);
        } else if (op == 2) {
            cin >> x;
            bst.remove(x);
        } else if (op == 3) {
            cin >> x;
            bst.count(x);
        } else if (op == 4) {
            bst.findMinValue();
        } else if (op == 5) {
            cin >> x;
            bst.findPredecessor(x);
        }
    }

    return 0;
}
