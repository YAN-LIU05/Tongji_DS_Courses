#include <iostream>
#include <queue>
#include <climits>
using namespace std;

#define MAX_NODE_NUM 1005

struct ArcNode {
    int adjvex;    // 该弧的终点
    int val;       // 边权
    ArcNode* next_arc;
    ArcNode(int v, int w) {
        adjvex = v;   // 设置邻接点
        val = w;      // 设置边的权重
        next_arc = nullptr;  // 初始化指向下一个边的指针
    }
};

struct VNode {
    ArcNode* first_arc;
    VNode() {
        first_arc = nullptr;
    }
};

struct Node {
    int dis, vex;
    bool operator<(const Node& a) const {
        return dis > a.dis;  // 小根堆
    }
};

class Graph {
public:
    VNode vertices[MAX_NODE_NUM];
    int vex_num, arc_num;

    Graph(int n, int m) {
        vex_num = n;  // 设置图的顶点数量
        arc_num = m;  // 设置图的边的数量
    }


    void addArc(int src, int dst, int val) {
        ArcNode* arc = new ArcNode(dst, val);
        arc->next_arc = vertices[src].first_arc;
        vertices[src].first_arc = arc;
    }
};

/**
 * @brief           使用dijkstra算法计算从起点到所有其他点的最短路径
 * @param graph     图的引用
 * @param dis       距离数组，存储从起点到各点的距离
 * @param start     起点
 */
void dijkstra(Graph& graph, int* dis, int start) {
    priority_queue<Node> pq;
    bool vis[MAX_NODE_NUM] = {false};

    for (int i = 1; i <= graph.vex_num; ++i)
        dis[i] = INT_MAX;
    dis[start] = 0;
    pq.push({0, start});

    while (!pq.empty()) {
        Node curr = pq.top();
        pq.pop();

        int u = curr.vex;
        if (vis[u]) continue;
        vis[u] = true;

        for (ArcNode* p = graph.vertices[u].first_arc; p; p = p->next_arc) {
            int v = p->adjvex, w = p->val;
            if (dis[v] > dis[u] + w) {
                dis[v] = dis[u] + w;
                pq.push({dis[v], v});
            }
        }
    }
}

int main() {
    int n, m;
    cin >> n >> m;
    Graph graph(n, m);

    for (int i = 0; i < m; ++i) {
        int src, dst, val;
        cin >> src >> dst >> val;
        graph.addArc(src, dst, val);
        graph.addArc(dst, src, val);
    }

    int grass_num, horse_num;
    cin >> grass_num >> horse_num;

    int grass[MAX_NODE_NUM];
    for (int i = 0; i < grass_num; ++i) {
        cin >> grass[i];
    }

    int dis[MAX_NODE_NUM][MAX_NODE_NUM];  // 牧草点到所有点的距离
    for (int i = 0; i < grass_num; ++i) {
        dijkstra(graph, dis[grass[i]], grass[i]);
    }

    for (int i = 0; i < horse_num; ++i) {
        int src, dst;
        cin >> src >> dst;

        int min_path = INT_MAX;
        for (int j = 0; j < grass_num; ++j) {
            int g = grass[j];
            if (dis[g][src] != INT_MAX && dis[g][dst] != INT_MAX) {
                min_path = min(min_path, dis[g][src] + dis[g][dst]);
            }
        }
        cout << min_path << endl;
    }

    return 0;
}
