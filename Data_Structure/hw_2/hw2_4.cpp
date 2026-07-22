#include <iostream>
#include <cstring>
using namespace std;

// 链表的一个节点
struct QNode {
    int data[2]; // 使用数组存储坐标 {x, y}
    QNode* next; // 指向下一个节点的指针
};

class myQueue {
private:
    QNode* front; // 队列头指针
    QNode* rear;  // 队列尾指针
public:
    myQueue();                  // 构造一个空队列
    ~myQueue();                 // 销毁队列
    int in_queue(int x, int y);    // 在队尾插入元素
    int out_queue(int& x, int& y);  // 弹出队首的元素
    int get_head(int& x, int& y);  // 取队首的元素（不弹出）
    bool if_empty();             // 判断队列是否为空
};

// 构造函数，初始化空队列
myQueue::myQueue() {
    front = rear = new(nothrow) QNode; // 创建一个新节点作为头尾
    if (!front)
        exit(-2); // QOVERFLOW，内存分配失败
    front->next = NULL; // 初始化时，头节点指向 NULL
}

// 析构函数，释放队列中的所有节点
myQueue::~myQueue() {
    while (front) {
        rear = front->next; // 保存下一个节点
        delete front; // 删除当前节点
        front = rear; // 移动到下一个节点
    }
}

// 入队函数，将坐标 (x, y) 插入队列尾部
int myQueue::in_queue(int x, int y) {
    QNode* p = new(nothrow) QNode; // 创建新节点
    if (!p)
        exit(-2); // QOVERFLOW，内存分配失败
    p->data[0] = x; // 存储 x 坐标
    p->data[1] = y; // 存储 y 坐标
    p->next = NULL; // 新节点指向 NULL
    rear->next = p; // 将新节点链接到队尾
    rear = p; // 更新队尾指针
    return 0; // OK
}

// 出队函数，返回队首元素的坐标
int myQueue::out_queue(int& x, int& y) {
    if (front == rear)
        return -1; // ERROR，队列为空
    QNode* p = front->next; // 获取队首节点
    x = p->data[0]; // 获取 x 坐标
    y = p->data[1]; // 获取 y 坐标
    front->next = p->next; // 将头指针指向下一个节点
    if (rear == p) // 如果队列中只有一个节点
        rear = front; // 更新队尾指针
    delete p; // 删除队首节点
    return 0; // OK
}

// 获取队首元素的坐标，但不移除
int myQueue::get_head(int& x, int& y) {
    if (front == rear)
        return -1; // ERROR，队列为空
    QNode* p = front->next; // 获取队首节点
    x = p->data[0]; // 获取 x 坐标
    y = p->data[1]; // 获取 y 坐标
    return 0; // OK
}

// 判断队列是否为空
bool myQueue::if_empty() {
    return rear == front; // 如果队尾指针与队头指针相同，表示队列为空
}

// 处理邻居坐标的函数
void processNeighbor(int newx, int newy, bool map[1000][1000], bool vis[1000][1000], myQueue& Queue) {
    // 检查坐标是否在有效范围内，且该位置未被访问
    if (newx >= 0 && newx < 1000 && newy >= 0 && newy < 1000 && map[newx][newy] && !vis[newx][newy]) {
        vis[newx][newy] = true; // 标记为已访问
        Queue.in_queue(newx, newy); // 将新坐标入队
    }
}

// 广度优先搜索 (BFS) 函数
void bfs(int n, int m, bool map[1000][1000], bool vis[1000][1000], int x, int y) {
    myQueue Queue; // 创建队列
    Queue.in_queue(x, y); // 将起始坐标入队
    vis[x][y] = true; // 标记起始坐标为已访问
    const int dx[] = { 0, 0, -1, 1 }; // x 方向的移动
    const int dy[] = { -1, 1, 0, 0 }; // y 方向的移动
    while (!Queue.if_empty()) { // 当队列不为空时
        int curx, cury;
        Queue.out_queue(curx, cury); // 获取当前坐标
        for (int i = 0; i < 4; i++) { // 遍历四个方向
            int newx = curx + dx[i]; // 新的 x 坐标
            int newy = cury + dy[i]; // 新的 y 坐标
            processNeighbor(newx, newy, map, vis, Queue); // 处理邻居
        }
    }
}

bool map[1000][1000]; // 存储地图的二维数组
bool vis[1000][1000]; // 存储访问标记的二维数组

int main() {
    memset(vis, 0, sizeof(vis)); // 初始化访问标记为 false
    int n, m, count = 0; // n: 行数, m: 列数, count: 连通区域计数

    cin >> n >> m; // 输入地图的行数和列数

    // 输入地图数据
    for (int i = 0; i < n; i++)
        for (int j = 0; j < m; j++)
            cin >> map[i][j]; // 读取每个位置的值

    // 遍历地图，寻找未访问的连通区域
    for (int i = 1; i < n - 1; i++)
        for (int j = 1; j < m - 1; j++) {
            if (map[i][j] && !vis[i][j]) { // 如果当前位置为1且未访问
                count++; // 连通区域计数加一
                bfs(n, m, map, vis, i, j); // 进行 BFS 遍历
            }
        }

    cout << count << endl; // 输出连通区域的数量

    return 0; // 结束程序
}


