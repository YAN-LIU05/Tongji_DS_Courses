#include <iostream>
#include <cstring>
using namespace std;

const int MAXN = 105;    // 最大村庄数
const int MAXE = MAXN * MAXN; // 最大边数

// 边的类
class Edge {
public:
    int u, v, weight;
    Edge() {
        u = 0;
        v = 0;
        weight = 0;
    }

    // 带参数构造函数
    Edge(int u, int v, int weight) {
        this->u = u;
        this->v = v;
        this->weight = weight;
    }
};

// 图的类
class Graph {
private:
    Edge edges[MAXE]; // 存储所有边
    int edgeCount;    // 边的总数
    int parent[MAXN]; // 并查集父节点
    int rank[MAXN];   // 并查集秩

public:
    Graph() {
        edgeCount = 0;
    }
    void addEdge(int u, int v, int weight);
    void initUnionFind(int n);
    int find(int x);
    bool unionSets(int x, int y);
    void sortEdges();
    int kruskal(int n);
};


// --- Graph 类外实现 ---
/**
 * @brief           向图中添加边
 * @param u         边的起点
 * @param v         边的终点
 * @param weight    边的权重
 */
void Graph::addEdge(int u, int v, int weight) {
    edges[edgeCount++] = Edge(u, v, weight); // 将边添加到边数组，并增加边计数
}

/**
 * @brief           初始化并查集
 * @param n         图中节点的数量
 */
void Graph::initUnionFind(int n) {
    for (int i = 0; i < n; ++i) {
        parent[i] = i; // 每个节点的父节点初始化为自身
        rank[i] = 0; // 每个节点的排序初始化为0
    }
}

/**
 * @brief           查找节点x的根节点，并进行路径压缩
 * @param x         要查找的节点
 * @return          返回根节点
 */
int Graph::find(int x) {
    if (parent[x] != x) {
        parent[x] = find(parent[x]); // 路径压缩
    }
    return parent[x];
}

/**
 * @brief           合并两个集合
 * @param x         第一个节点
 * @param y         第二个节点
 * @return          如果合并成功返回 true，否则返回 false
 */
bool Graph::unionSets(int x, int y) {
    int rootX = find(x);
    int rootY = find(y);
    if (rootX != rootY) {
        if (rank[rootX] > rank[rootY]) {
            parent[rootY] = rootX;
        } else if (rank[rootX] < rank[rootY]) {
            parent[rootX] = rootY;
        } else {
            parent[rootY] = rootX;
            rank[rootX]++;
        }
        return true;
    }
    return false;
}

/**
 * @brief           对图中的边进行排序
 */
void Graph::sortEdges() {
    for (int i = 0; i < edgeCount - 1; ++i) {
        for (int j = 0; j < edgeCount - i - 1; ++j) {
            if (edges[j].weight > edges[j + 1].weight) {
                Edge temp = edges[j];
                edges[j] = edges[j + 1];
                edges[j + 1] = temp;
            }
        }
    }
}

/**
 * @brief           使用克鲁斯卡尔算法找到最小生成树的总权重
 * @param n         图中节点的数量
 * @return          返回最小生成树的总权重
 */
int Graph::kruskal(int n) {
    sortEdges();          // 对边按权重排序
    int totalCost = 0;

   for (int i = 0; i < edgeCount; ++i) {
        int u = edges[i].u, v = edges[i].v;
        if (find(u) != find(v)) { // 如果两点属于不同连通分量
            unionSets(u, v);
            totalCost += edges[i].weight;
        }
    }

    return totalCost;
}

// --- 主函数 ---
int main() {
    int n;
    cin >> n;

    int distances[MAXN][MAXN];
    for (int i = 0; i < n; ++i) {
        for (int j = 0; j < n; ++j) {
            cin >> distances[i][j];
        }
    }

    int m;
    cin >> m;

    Graph graph;
    graph.initUnionFind(n); // 初始化并查集

    // 添加所有边到图
    for (int i = 0; i < n; ++i) {
        for (int j = i + 1; j < n; ++j) {
            graph.addEdge(i, j, distances[i][j]);
        }
    }

    // 处理已有的边
    for (int i = 0; i < m; ++i) {
        int a, b;
        cin >> a >> b;
        // 检查输入范围
    if (a < 1 || a > n || b < 1 || b > n) {
        return -1; // 停止程序或抛出错误
    }
        graph.addEdge(a - 1, b - 1, 0); // 添加边以供 Kruskal 排序和使用
        graph.unionSets(a - 1, b - 1); // 直接合并已有的路
    }

    // 输出最小生成树的总权值
    cout << graph.kruskal(n) << endl;

    return 0;
}
