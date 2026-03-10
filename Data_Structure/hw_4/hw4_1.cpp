#include <iostream>
#include <cstring>

using namespace std;

const int MAXN = 1000; // 最大顶点数

// 图的结构体
struct Graph {
    int adj[MAXN][MAXN]; // 邻接矩阵
    int n;               // 顶点数
    bool visited[MAXN];  // 访问标记数组

    // 初始化图
    void init(int vertices) {
        n = vertices;
        memset(adj, 0, sizeof(adj));
        memset(visited, 0, sizeof(visited));
    }

    // 添加一条边
    void addEdge(int u, int v) {
        adj[u][v] = 1;
        adj[v][u] = 1;
    }
};

// 队列结构体
struct Queue {
    int data[MAXN];
    int front, rear;

    // 初始化队列
    void init() {
        front = rear = 0;
    }

    // 入队
    void enqueue(int value) {
        data[rear++] = value;
    }

    // 出队
    int dequeue() {
        return data[front++];
    }

    // 判断队列是否为空
    bool isEmpty() {
        return front == rear;
    }
};

// 存储连通分量的结构体
struct Component {
    int nodes[MAXN]; // 节点列表
    int size;        // 节点数量

    // 初始化
    void init() {
        size = 0;
    }

    // 添加节点
    void addNode(int node) {
        for (int i = 0; i < size; ++i) {
            if (nodes[i] == node) 
                return;
        }
        nodes[size++] = node;
    }

    // 输出连通分量
    void print();
};

void Component::print() {
     cout << "{";
    for (int i = 0; i < size; ++i) {
         if (i > 0) cout << " ";
        cout << nodes[i];
    }
    cout << "}";
}

/**
 * @brief           深度优先搜索（DFS）算法
 * @param graph     图的引用
 * @param v         当前节点
 * @param component 连通分量的引用
 */

void dfs(Graph& graph, int v, Component& component) {
    graph.visited[v] = true;
    component.addNode(v);

    for (int i = 0; i < graph.n; ++i) {
        if (graph.adj[v][i] && !graph.visited[i]) {
            dfs(graph, i, component);
        }
    }
}

/**
 * @brief           广度优先搜索（BFS）算法
 * @param graph     图的引用
 * @param start     起始节点
 * @param component 连通分量的引用
 */
void bfs(Graph& graph, int start, Component& component) {
    Queue queue;
    queue.init();
    queue.enqueue(start);
    graph.visited[start] = true;

    while (!queue.isEmpty()) {
        int v = queue.dequeue();
        component.addNode(v);

        for (int i = 0; i < graph.n; ++i) {
            if (graph.adj[v][i] && !graph.visited[i]) {
                queue.enqueue(i);
                graph.visited[i] = true;
            }
        }
    }
}

int main() {
    int n, m;
    cin >> n >> m;

    Graph graph;
    graph.init(n);

    for (int i = 0; i < m; ++i) {
        int u, v;
        cin >> u >> v;
        graph.addEdge(u, v);
    }

    Component componentsDFS[MAXN], componentsBFS[MAXN];
    int dfsCount = 0, bfsCount = 0;

    // DFS
    memset(graph.visited, 0, sizeof(graph.visited));
    for (int i = 0; i < n; ++i) {
        if (!graph.visited[i]) {
            componentsDFS[dfsCount].init();
            dfs(graph, i, componentsDFS[dfsCount]);
            ++dfsCount;
        }
    }

    // BFS
    memset(graph.visited, 0, sizeof(graph.visited));
    for (int i = 0; i < n; ++i) {
        if (!graph.visited[i]) {
            componentsBFS[bfsCount].init();
            bfs(graph, i, componentsBFS[bfsCount]);
            ++bfsCount;
        }
    }

    // 输出DFS结果
    for (int i = 0; i < dfsCount; ++i) {
        componentsDFS[i].print();
    }
    cout << endl;

    // 输出BFS结果
    for (int i = 0; i < bfsCount; ++i) {
        componentsBFS[i].print();
    }
    cout << endl;

    return 0;
}

