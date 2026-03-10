#include <iostream>
#include <cstring>
#include <iomanip>

using namespace std;

const int MAXN = 2000; // 最大节点数
const int MAXM = 33 * MAXN; // 最大边数

struct Graph {
    int head[MAXN + 1]; // 每个节点的邻接链表起始位置
    int edges[MAXM * 2]; // 边数组
    int next[MAXM * 2];  // 下一条边的索引
    int edgeCount;       // 当前边数

    int n; // 节点数

    // 初始化图
    void init(int nodes) {
        n = nodes;
        edgeCount = 0;
        memset(head, -1, sizeof(head));
    }

    // 添加一条无向边
    void addEdge(int u, int v) {
        edges[edgeCount] = v;
        next[edgeCount] = head[u];
        head[u] = edgeCount++;
        edges[edgeCount] = u;
        next[edgeCount] = head[v];
        head[v] = edgeCount++;
    }
};

// 队列结构体
struct Queue {
    int data[MAXN + 1];
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

/**
 * @brief           计算六度空间范围内的节点数
 * @param graph     图的引用
 * @param start     起始节点
 * @return          返回覆盖的节点数
 */
int sixDegrees(Graph& graph, int start) {
    bool visited[MAXN + 1]; // 访问标记数组
    memset(visited, 0, sizeof(visited));
    Queue queue;
    queue.init();

    queue.enqueue(start);
    visited[start] = true;

    int level = 0;  // 当前层数
    int count = 1;  // 覆盖的节点数，包括自身

    while (!queue.isEmpty() && level < 6) {
        int size = queue.rear - queue.front; // 当前层节点数
        for (int i = 0; i < size; ++i) {
            int node = queue.dequeue();
            for (int j = graph.head[node]; j != -1; j = graph.next[j]) {
                int neighbor = graph.edges[j];
                if (!visited[neighbor]) {
                    queue.enqueue(neighbor);
                    visited[neighbor] = true;
                    count++;
                }
            }
        }
        level++;
    }

    return count;
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

    // 遍历每个节点，计算其六度空间覆盖率
    for (int i = 1; i <= n; ++i) {
        int reachable = sixDegrees(graph, i);
        float percentage = (float)reachable / n * 100.0;
        cout << i << ": " << fixed << setprecision(2) << percentage << "%" << endl;
    }

    return 0;
}
