#include <iostream>
#include <string>
#include <map>
#include <vector>
#include <sstream>
using namespace std;
 
// 预处理祖先和后代
void preprocessFamilyTree(const string& person,
                          map<string, pair<vector<string>, vector<string>>>& family_tree,
                          map<string, map<string, bool>>& ancestors,
                          map<string, map<string, bool>>& descendants) {
    // 处理祖先
    vector<string> stack = { person };
    map<string, bool> visited;
    visited[person] = true;
 
    while (!stack.empty()) {
        string current = stack.back();
        stack.pop_back();
 
        for (const string& parent : family_tree[current].first) {
            if (!visited[parent]) {
                ancestors[person][parent] = true; // 标记为祖先
                visited[parent] = true;
                stack.push_back(parent);
            }
        }
    }
 
    // 处理后代
    stack.push_back(person);
    visited.clear();
    visited[person] = true;
 
    while (!stack.empty()) {
        string current = stack.back();
        stack.pop_back();
 
        for (const string& child : family_tree[current].second) {
            if (!visited[child]) {
                descendants[person][child] = true; // 标记为后代
                visited[child] = true;
                stack.push_back(child);
            }
        }
    }
}
 
// 判断是否是兄弟姐妹
bool isSiblingOf(const string& X, const string& Y, map<string, pair<vector<string>, vector<string>>>& familyTree) {
    return familyTree[X].first.size() == 1 && familyTree[Y].first.size() == 1 &&
           familyTree[X].first.back() == familyTree[Y].first.back(); // 比较父母是否相同
}
 
// 手动实现查找功能
bool isDescendantOf(const string& X, const string& Y, map<string, map<string, bool>>& ancestors, map<string, map<string, bool>>& descendants) {
    return descendants[Y].count(X); // 如果Y的后代中有X，则返回true
}
 
bool isAncestorOf(const string& X, const string& Y, map<string, map<string, bool>>& ancestors, map<string, map<string, bool>>& descendants) {
    return ancestors[Y].count(X); // 如果Y的祖先中有X，则返回true
}
 
int main() {
    while (true) {
        map<string, map<string, bool>> ancestors;  // 存储每个人的祖先
        map<string, map<string, bool>> descendants; // 存储每个人的后代
        int n, m;
        cin >> n >> m;
        cin.ignore();
        if (n == 0 && m == 0) break; // 结束条件
        string ancestor;
        cin.clear();
        getline(cin, ancestor); // 记录祖先
        cin.clear();
        vector<string> true_parent; // 建立一个栈，用于找到距离当前名字最近的上一代，即为其父母
        map<string, int> mp;
        mp[ancestor] = 0; // 初始化祖先的深度为0
        true_parent.push_back(ancestor); // 将祖先压入栈中
        map<string, pair<vector<string>, vector<string>>> family_tree; // 记录每人的父母和孩子
        family_tree[ancestor] = {{}, {}}; // 祖先的父母为空, 孩子未初始化
        for (int i = 1; i < n; i++) {
            string name;
            getline(cin, name);
            cin.clear();
            int index = name.find_first_not_of(' '); // 找到第一个不是空格的位置
            name = name.substr(index); // 截取不带空格的名字
            mp[name] = index; // 记录名字和深度
            family_tree[name] = {{}, {}}; // 初始化名字的父母和孩子为空
            while (!true_parent.empty() && mp[true_parent.back()] != index - 1) {
                true_parent.pop_back(); // 如果当前名字的深度比栈顶名字的深度小,则将栈顶名字弹出
            }
            string parent = true_parent.back();
            family_tree[parent].second.push_back(name); // 将当前名字加入父母的孩子中
            family_tree[name].first.push_back(parent); // 将父母加入当前名字的孩子中
            true_parent.push_back(name); // 将当前名字压入栈中
        }
 
        // 预处理祖先和后代
        for (auto& it : family_tree) {
            preprocessFamilyTree(it.first, family_tree, ancestors, descendants);
        }
 
        // 处理查询
        for (int i = 0; i < m; i++) {
            string order, name1, name2, relation, blank;
            getline(cin, order);
            cin.clear();
            istringstream iss(order);
            iss >> name1 >> relation >> relation >> relation >> blank >> name2;
            name2 = name2.erase(name2.length() - 1); // 去掉最后一个空格
            if (relation == "child") {
                if (family_tree[name2].second.empty()) {
                    cout << "False" << endl;
                } else {
                    bool found = false;
                    for (const string& child : family_tree[name2].second) {
                        if (child == name1) {
                            found = true;
                            break;
                        }
                    }
                    cout << (found ? "True" : "False") << endl;
                }
            } else if (relation == "parent") {
                if (family_tree[name2].first.empty()) {
                    cout << "False" << endl;
                } else {
                    bool found = false;
                    for (const string& parent : family_tree[name2].first) {
                        if (parent == name1) {
                            found = true;
                            break;
                        }
                    }
                    cout << (found ? "True" : "False") << endl;
                }
            } else if (relation == "sibling") {
                if (name1 == name2) {
                    cout << "True" << endl;
                } else if (isSiblingOf(name1, name2, family_tree)) {
                    cout << "True" << endl;
                } else {
                    cout << "False" << endl;
                }
            } else if (relation == "descendant") {
                if (name1 == name2 || isDescendantOf(name1, name2, ancestors, descendants)) {
                    cout << "True" << endl;
                } else {
                    cout << "False" << endl;
                }
            } else if (relation == "ancestor") {
                if (name1 == name2 || isAncestorOf(name1, name2, ancestors, descendants)) {
                    cout << "True" << endl;
                } else {
                    cout << "False" << endl;
                }
            }
        }
        cout << endl;
    }
}