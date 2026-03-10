import sys
import math
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout,
                             QLineEdit, QPushButton, QTextEdit, QLabel, QGraphicsView,
                             QGraphicsScene, QFrame)
from PyQt6.QtGui import QPen, QBrush, QColor, QFont
from PyQt6.QtCore import Qt


# HeapVisualizer 类的逻辑保持不变
class HeapVisualizer:
    """
    一个用于堆排序并能逐步可视化的类。
    """

    def __init__(self):
        self.arr = []
        self.n = 0
        self.original_len = 0
        self.current_step = 0  # 0: a new sort, 1: built heap, 2: swapped, 3: heapified

    def set_array(self, arr):
        """设置待排序的数组。"""
        self.arr = arr.copy()
        self.n = len(self.arr)
        self.original_len = len(self.arr)
        self.current_step = 0

    def heapify(self, n, i):
        """调整以 i 为根节点的子树为大顶堆。"""
        largest = i
        left = 2 * i + 1
        right = 2 * i + 2

        if left < n and self.arr[left] > self.arr[largest]:
            largest = left
        if right < n and self.arr[right] > self.arr[largest]:
            largest = right

        if largest != i:
            self.arr[i], self.arr[largest] = self.arr[largest], self.arr[i]
            self.heapify(n, largest)

    def build_max_heap(self):
        """构建大顶堆。"""
        for i in range(self.n // 2 - 1, -1, -1):
            self.heapify(self.n, i)
        self.current_step = 1

    def swap_root_and_last(self):
        """交换堆顶和末尾元素。"""
        if self.n > 0:
            self.arr[0], self.arr[self.n - 1] = self.arr[self.n - 1], self.arr[0]
            self.n -= 1
            self.current_step = 2

    def heapify_step(self):
        """在交换后重新筛选堆。"""
        if self.n > 0:
            self.heapify(self.n, 0)
        self.current_step = 3


class HeapGraphicsView(QGraphicsView):
    """
    一个专门用于图形化显示堆的组件。
    """

    def __init__(self):
        super().__init__()
        self.scene = QGraphicsScene()
        self.setScene(self.scene)
        self.setRenderHint(self.renderHints().Antialiasing)

    def clear_scene(self):
        self.scene.clear()

    def update_heap(self, arr, heap_size):
        self.clear_scene()
        if not arr:
            return

        total_nodes = len(arr)

        node_radius = 20
        level_height = 80
        pen = QPen(Qt.GlobalColor.black, 2)
        heap_brush = QBrush(QColor("#aaddff"))
        sorted_brush = QBrush(QColor("#aaffc3"))
        font = QFont("Arial", 12, QFont.Weight.Bold)

        positions = {}
        view_width = self.width() - 2 * node_radius  # 留出边距
        for i in range(total_nodes):
            level = int(math.log2(i + 1))
            nodes_in_level = 2 ** level
            pos_in_level = i - (nodes_in_level - 1)

            h_spacing = view_width / (nodes_in_level + 1)
            x = h_spacing * (pos_in_level + 1) + node_radius
            y = level * level_height + node_radius
            positions[i] = (x, y)

        line_pen = QPen(QColor("#cccccc"), 1.5)
        for i in range(heap_size):
            if i not in positions: continue
            p_x, p_y = positions[i]
            left_child_idx = 2 * i + 1
            right_child_idx = 2 * i + 2
            if left_child_idx < heap_size and left_child_idx in positions:
                c_x, c_y = positions[left_child_idx]
                self.scene.addLine(p_x, p_y, c_x, c_y, line_pen)
            if right_child_idx < heap_size and right_child_idx in positions:
                c_x, c_y = positions[right_child_idx]
                self.scene.addLine(p_x, p_y, c_x, c_y, line_pen)

        for i in range(total_nodes):
            if i not in positions: continue
            x, y = positions[i]
            brush = heap_brush if i < heap_size else sorted_brush

            ellipse = self.scene.addEllipse(0, 0, 2 * node_radius, 2 * node_radius, pen, brush)
            ellipse.setPos(x - node_radius, y - node_radius)

            text = self.scene.addText(str(arr[i]), font)
            text_rect = text.boundingRect()
            text.setPos(x - text_rect.width() / 2, y - text_rect.height() / 2)


class App(QWidget):
    def __init__(self):
        super().__init__()
        self.title = '堆排序'
        self.heap_visualizer = HeapVisualizer()
        self.initUI()

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(100, 100, 800, 700)

        vbox = QVBoxLayout()

        # --- 输入和控制 ---
        input_control_box = QFrame()
        input_control_box.setFrameShape(QFrame.Shape.StyledPanel)

        grid = QVBoxLayout(input_control_box)

        input_layout = QHBoxLayout()
        input_layout.addWidget(QLabel("请输入一组以英文逗号分隔的数值:"))
        self.line_edit = QLineEdit()
        self.line_edit.setPlaceholderText("例如: 4, 1, 7, 3, 8, 5, 2, 6")
        input_layout.addWidget(self.line_edit)
        self.start_button = QPushButton("开始排序")
        self.start_button.clicked.connect(self.start_sort)
        input_layout.addWidget(self.start_button)
        grid.addLayout(input_layout)

        control_layout = QHBoxLayout()
        self.swap_button = QPushButton("1. 交换堆顶与末尾元素")
        self.swap_button.setEnabled(False)
        self.swap_button.clicked.connect(self.swap_elements)
        self.heapify_button = QPushButton("2. 重新筛选")
        self.heapify_button.setEnabled(False)
        self.heapify_button.clicked.connect(self.reheapify)
        control_layout.addWidget(self.swap_button)
        control_layout.addWidget(self.heapify_button)
        grid.addLayout(control_layout)

        vbox.addWidget(input_control_box)

        # --- 状态和结果显示 ---
        status_box = QFrame()
        status_box.setFrameShape(QFrame.Shape.StyledPanel)
        status_layout = QVBoxLayout(status_box)

        # 状态行
        info_layout = QHBoxLayout()
        self.status_label = QLabel("<b>状态:</b> 等待输入...")
        self.top_element_label = QLabel("<b>当前堆顶元素:</b> -")
        info_layout.addWidget(self.status_label, 2)
        info_layout.addWidget(self.top_element_label, 1)
        status_layout.addLayout(info_layout)

        # 数组和结果行
        array_font = QFont("Courier", 11)
        self.current_array_label = QLabel("<b>当前数组:</b> []")
        self.current_array_label.setFont(array_font)
        status_layout.addWidget(self.current_array_label)

        self.final_result_label = QLabel("<b>最终结果:</b> []")
        self.final_result_label.setFont(array_font)
        status_layout.addWidget(self.final_result_label)

        vbox.addWidget(status_box)

        # --- 图形化显示区域 ---
        self.heap_view = HeapGraphicsView()
        vbox.addWidget(self.heap_view, 1)

        # --- 日志输出区域 ---
        log_label = QLabel("操作日志:")
        self.log_area = QTextEdit()
        self.log_area.setReadOnly(True)
        self.log_area.setFixedHeight(120)
        vbox.addWidget(log_label)
        vbox.addWidget(self.log_area)

        self.setLayout(vbox)
        self.show()

    def update_displays(self):
        """一个集中的函数，用于更新所有可视化组件。"""
        arr = self.heap_visualizer.arr
        heap_size = self.heap_visualizer.n

        # 1. 更新图形视图
        self.heap_view.update_heap(arr, heap_size)

        # 2. 更新当前数组标签
        self.current_array_label.setText(f"<b>当前数组:</b> {arr}")

        # 3. 更新状态和堆顶元素标签
        self.update_status()

    def start_sort(self):
        input_text = self.line_edit.text()
        try:
            arr = [int(x.strip()) for x in input_text.split(',') if x.strip()]
            if not arr:
                self.log_area.setText("请输入有效的数值。")
                return
        except ValueError:
            self.log_area.setText("输入格式错误，请输入以英文逗号分隔的整数。")
            return

        self.heap_visualizer.set_array(arr)

        # 重置界面
        self.log_area.clear()
        self.final_result_label.setText("<b>最终结果:</b> []")
        self.log_area.append("原始数组: " + str(self.heap_visualizer.arr))

        self.heap_visualizer.build_max_heap()
        self.log_area.append("初始大顶堆构建完成")
        self.log_area.append("构建后数组: " + str(self.heap_visualizer.arr))

        self.update_displays()

        self.swap_button.setEnabled(True)
        self.heapify_button.setEnabled(False)
        self.start_button.setEnabled(False)

    def swap_elements(self):
        if self.heap_visualizer.n > 0:
            top_element = self.heap_visualizer.arr[0]
            last_element = self.heap_visualizer.arr[self.heap_visualizer.n - 1]

            self.log_area.append(f"\n步骤1: 交换堆顶 {top_element} 和末尾 {last_element}")
            self.heap_visualizer.swap_root_and_last()
            self.log_area.append("交换后数组: " + str(self.heap_visualizer.arr))

            self.update_displays()

            self.swap_button.setEnabled(False)
            self.heapify_button.setEnabled(True)
        else:  # Should not happen if buttons are disabled correctly, but as a safeguard
            self.finish_sort()

    def reheapify(self):
        if self.heap_visualizer.n > 0:
            self.log_area.append(f"步骤2: 对新堆顶 {self.heap_visualizer.arr[0]} 进行重新筛选**")
            self.heap_visualizer.heapify_step()
            self.log_area.append("筛选后数组: " + str(self.heap_visualizer.arr))

            self.update_displays()

            if self.heap_visualizer.n > 0:
                self.swap_button.setEnabled(True)
                self.heapify_button.setEnabled(False)
            else:  # This happens on the very last heapify when n becomes 0
                self.finish_sort()
        else:
            self.finish_sort()

    def update_status(self):
        if self.heap_visualizer.n > 0:
            self.top_element_label.setText(f"<b>当前堆顶元素:</b> {self.heap_visualizer.arr[0]}")
        else:
            self.top_element_label.setText("<b>当前堆顶元素:</b> -")

        sorted_part = self.heap_visualizer.arr[self.heap_visualizer.n:]

        status_text = "<b>状态:</b> "
        if self.heap_visualizer.current_step == 1:
            status_text += "已构建初始堆。请点击“交换”。"
        elif self.heap_visualizer.current_step == 2:
            status_text += "已交换元素。请点击“重新筛选”。"
        elif self.heap_visualizer.current_step == 3:
            status_text += "已重新筛选。请点击“交换”。"

        if sorted_part:
            status_text += f" (<b>已排序部分:</b> {sorted_part})"

        self.status_label.setText(status_text)

    def finish_sort(self):
        final_array = self.heap_visualizer.arr
        self.log_area.append("\n\n✅ --最终排序结果：-- \n" + str(final_array))
        self.final_result_label.setText(f"<b>最终结果:</b> {final_array}")
        self.status_label.setText("<b>状态:</b> 排序完成！")
        self.swap_button.setEnabled(False)
        self.heapify_button.setEnabled(False)
        self.start_button.setEnabled(True)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self.heap_visualizer and self.heap_visualizer.arr:
            self.heap_view.update_heap(self.heap_visualizer.arr, self.heap_visualizer.n)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec())