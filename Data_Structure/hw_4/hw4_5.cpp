#include <iostream>
#include <cstring>
using namespace std;

class Graph_course {
public:
    struct ArcNode {
        int adj_vex;             // 该弧的终点
        ArcNode* next_arc;       // 后继的弧

        ArcNode() {
            adj_vex = 0;
            next_arc = nullptr;
        }
    };

    struct VNode {
        int in_degree;          // 入度
        int val;                // 学时
        int max_preval;         // 前驱结点的最大学时
        int* pre;               // 前驱结点（用数组代替）
        int pre_size;           // 前驱结点数量
        ArcNode* first_arc;      // 邻接链表头指针

        VNode() {
            in_degree = 0;
            val = 0;
            max_preval = 0;
            pre_size = 0;
            first_arc = nullptr;
            pre = new int[100];  // 假设最多100个前驱结点
        }

        ~VNode() {
            delete[] pre;
        }
    };

    int vex_num;             // 图中课程数量
    int arc_num;             // 图中边的数量
    VNode* vertices;        // 图的邻接表

    Graph_course(int n) {
        vex_num = n;
        arc_num = 0;
        vertices = new VNode[n + 2];  // 多一个超级结点
    }

    ~Graph_course() {
        delete[] vertices;
    }

    // 添加边
    void add(int src, int dst);

    // 返回最大值
    int max(int a, int b);

    // 拓扑排序计算每门课程的最早完成时间
    bool topo_sort();

    // 深度优先搜索，检查课程是否影响总毕业时间
    bool dfs(int cur, int tgt);

};

// 函数体外实现

/**
 * @brief           向图中添加边
 * @param src        边的起点
 * @param dst        边的终点
 */
void Graph_course::add(int src, int dst) {
    ArcNode* p = vertices[src].first_arc;
    ArcNode* q = new ArcNode();
    q->adj_vex = dst;

    if (!q) exit(-1);

    if (p) {
        while (p->next_arc) p = p->next_arc;
        p->next_arc = q;
    } else {
        vertices[src].first_arc = q;
    }
    arc_num++;
}

/**
 * @brief           返回两个整数中的最大值
 * @param a         第一个整数
 * @param b         第二个整数
 * @return          返回 a 和 b 中的最大值
 */
int Graph_course::max(int a, int b) {
    return a > b ? a : b;
}

/**
 * @brief           拓扑排序计算每门课程的最早完成时间
 * @return          如果拓扑排序成功返回 true，否则返回 false
 */
bool Graph_course::topo_sort() {
    int cnt = 0;
    while (true) {
        int cur = -1;
        for (int i = 1; i <= vex_num; i++) {
            if (vertices[i].in_degree == 0) {
                cur = i;
                break;
            }
        }

        if (cur == -1) break;  // 没有入度为0的点，退出

        cnt++;
        vertices[cur].in_degree--;  // 处理该课程
        vertices[cur].val += vertices[cur].max_preval;  // 更新该课程的完成时间

        for (ArcNode* p = vertices[cur].first_arc; p; p = p->next_arc) {
            vertices[p->adj_vex].in_degree--;
            if (vertices[p->adj_vex].max_preval < vertices[cur].val) {
                vertices[p->adj_vex].max_preval = vertices[cur].val;
                vertices[p->adj_vex].pre_size = 1;
                vertices[p->adj_vex].pre[0] = cur;
            } else if (vertices[p->adj_vex].max_preval == vertices[cur].val) {
                vertices[p->adj_vex].pre[vertices[p->adj_vex].pre_size++] = cur;
            }
        }
    }

    return cnt == vex_num;
}

/**
 * @brief           深度优先搜索，检查课程是否影响总毕业时间
 * @param cur       当前课程
 * @param tgt       目标课程
 * @return          如果当前课程影响目标课程的毕业时间返回 true，否则返回 false
 */
bool Graph_course::dfs(int cur, int tgt) {
    if (cur == tgt) return true;
    if (vertices[cur].pre_size == 0) return false;

    for (int i = 0; i < vertices[cur].pre_size; i++) {
        if (dfs(vertices[cur].pre[i], tgt)) return true;
    }
    return false;
}



int main() {
    int n;
    cin >> n;

    Graph_course scheduler(n);

    for (int i = 1; i <= n; i++) {
        int num, pre;
        cin >> scheduler.vertices[i].val;
        cin >> num;
        for (int j = 0; j < num; j++) {
            cin >> pre;
            scheduler.vertices[i].in_degree++;
            scheduler.add(pre, i);
        }
    }

    for (int i = 1; i <= n; i++) {
        if (scheduler.vertices[i].first_arc == nullptr) {
            scheduler.add(i, n + 1);  // 无前驱的课程连接到超级结点
        }
    }

    if (!scheduler.topo_sort()) {
        return -1;
    }

    for (int i = 1; i <= n; i++) {
        cout << scheduler.vertices[i].val << " " << scheduler.dfs(n + 1, i) << endl;
    }


    return 0;
}
