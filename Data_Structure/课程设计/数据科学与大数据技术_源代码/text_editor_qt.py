import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QTextEdit, QVBoxLayout, QWidget,
    QStatusBar, QLabel, QInputDialog, QMessageBox, QFileDialog)
from PyQt6.QtGui import QAction, QIcon


class TextEditor(QMainWindow):
    """
    一个基于 PyQt6 的功能全面的文本编辑器。

    功能:
    - 限制200字符输入。
    - 实时、分别统计中文、英文字母、数字、英文单词和空格数。
    - 统计指定子串的出现次数。
    - 提供三种删除子串模式：删除全部、删除第一个、删除第N个。
    - 支持与主流编辑器（如Word）逻辑一致的撤销和恢复。
    - 支持保存文件。
    - 支持在原窗口进行文本与16进制编码的相互转换，并允许在16进制模式下修改。
    """
    MAX_CHARS = 200

    def __init__(self):
        super().__init__()
        self.setWindowTitle("简单文本编辑器")
        self.setGeometry(100, 100, 950, 500)

        # 状态变量，用于跟踪当前是否为16进制显示模式
        self.is_hex_mode = False

        # 设置中心组件
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        # 布局
        layout = QVBoxLayout(self.central_widget)

        # 文本编辑区域
        self.text_edit = QTextEdit()
        self.text_edit.setPlaceholderText("在此输入文本，最多 {} 个字符...".format(self.MAX_CHARS))
        layout.addWidget(self.text_edit)

        # 信号连接
        self.text_edit.textChanged.connect(self.on_text_changed)

        # 创建UI组件
        self.create_actions()
        self.create_menu_bar()
        self.create_tool_bar()
        self.create_status_bar()

        # 初始化状态栏
        self.update_status()

    def create_actions(self):
        """创建所有动作 (Actions)"""
        # 文件操作
        self.save_action = QAction(QIcon.fromTheme("document-save"), "保存(&S)", self)
        self.save_action.setShortcut("Ctrl+S")
        self.save_action.triggered.connect(self.save_file)

        # 编辑操作
        self.undo_action = QAction(QIcon.fromTheme("edit-undo"), "撤销(&U)", self)
        self.undo_action.setShortcut("Ctrl+Z")
        self.undo_action.triggered.connect(self.text_edit.undo)

        self.redo_action = QAction(QIcon.fromTheme("edit-redo"), "恢复(&R)", self)
        self.redo_action.setShortcut("Ctrl+Shift+Z")
        self.redo_action.triggered.connect(self.text_edit.redo)

        self.count_str_action = QAction("统计子串出现次数(&F)", self)
        self.count_str_action.setShortcut("Ctrl+F")
        self.count_str_action.triggered.connect(self.count_substring)

        # 转换操作
        self.toggle_hex_action = QAction(QIcon.fromTheme("utilities-terminal"), "转换为16进制(&H)", self)
        self.toggle_hex_action.setShortcut("Ctrl+H")
        self.toggle_hex_action.setStatusTip("将当前文本转换为UTF-8的16进制编码")
        self.toggle_hex_action.triggered.connect(self.toggle_hex_conversion)

        # 创建三种删除动作
        self.delete_all_action = QAction("删除全部匹配子串", self)
        self.delete_all_action.triggered.connect(self.delete_all_substrings)

        self.delete_first_action = QAction("删除第一个匹配子串", self)
        self.delete_first_action.triggered.connect(self.delete_first_substring)

        self.delete_nth_action = QAction("删除第 N 个匹配子串...", self)
        self.delete_nth_action.triggered.connect(self.delete_nth_substring)

    def create_menu_bar(self):
        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu("文件(&F)")
        file_menu.addAction(self.save_action)
        file_menu.addSeparator()
        file_menu.addAction("退出(&X)", self.close)

        edit_menu = menu_bar.addMenu("编辑(&E)")
        edit_menu.addAction(self.undo_action)
        edit_menu.addAction(self.redo_action)
        edit_menu.addSeparator()
        edit_menu.addAction(self.count_str_action)
        edit_menu.addAction(self.toggle_hex_action)
        edit_menu.addSeparator()
        delete_menu = edit_menu.addMenu("删除子串(&D)")
        delete_menu.addAction(self.delete_all_action)
        delete_menu.addAction(self.delete_first_action)
        delete_menu.addAction(self.delete_nth_action)

    def create_tool_bar(self):
        tool_bar = self.addToolBar("常用操作")
        tool_bar.addAction(self.save_action)
        tool_bar.addSeparator()
        tool_bar.addAction(self.undo_action)
        tool_bar.addAction(self.redo_action)
        tool_bar.addSeparator()
        tool_bar.addAction(self.toggle_hex_action)

    def create_status_bar(self):
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_label = QLabel("准备就绪")
        self.status_bar.addWidget(self.status_label)

    def on_text_changed(self):
        """当文本框内容改变时调用的槽函数"""
        # 如果是16进制模式，则不执行任何操作，允许用户自由编辑。
        if self.is_hex_mode:
            return

        # --- 以下代码仅在普通文本模式下执行 ---
        current_text = self.text_edit.toPlainText()
        if len(current_text) > self.MAX_CHARS:
            self.text_edit.blockSignals(True)
            self.text_edit.setPlainText(current_text[:self.MAX_CHARS])
            cursor = self.text_edit.textCursor()
            cursor.setPosition(self.MAX_CHARS)
            self.text_edit.setTextCursor(cursor)
            self.text_edit.blockSignals(False)

        self.update_status()

    def update_status(self):
        text = self.text_edit.toPlainText()
        chinese_char_count = sum(1 for char in text if '\u4e00' <= char <= '\u9fff')
        english_letter_count = sum(1 for char in text if 'a' <= char.lower() <= 'z')
        digit_count = sum(1 for char in text if char.isdigit())
        potential_words = text.split()
        english_word_count = sum(1 for word in potential_words if any('a' <= char.lower() <= 'z' for char in word))
        space_count = text.count(" ")
        newline_count = text.count("\n")
        tab_count = text.count("\t")

        status_text = (f"中文: {chinese_char_count} | 英文: {english_letter_count} | "
                       f"数字: {digit_count} | 英文单词: {english_word_count} | 空格: {space_count} | 换行符: {newline_count} | 制表符: {tab_count}  "
                       f"总字符: {len(text)}/{self.MAX_CHARS}")
        self.status_label.setText(status_text)

    def count_substring(self):
        if self.is_hex_mode:
            QMessageBox.warning(self, "模式错误", "请先从16进制恢复为文本再进行统计。")
            return
        text = self.text_edit.toPlainText()
        if not text:
            QMessageBox.information(self, "提示", "编辑器内容为空。")
            return
        substring, ok = QInputDialog.getText(self, "统计子串", "请输入要统计的字符串:")
        if ok and substring:
            count = text.count(substring)
            QMessageBox.information(self, "统计结果", f"字符串 '{substring}' 在文中出现了 {count} 次。")

    def toggle_hex_conversion(self):
        """根据当前模式，在文本和16进制编码之间进行切换"""
        self.text_edit.blockSignals(True)

        try:
            if not self.is_hex_mode:
                # --- 模式：文本 -> 16进制 ---
                text = self.text_edit.toPlainText()
                if not text:
                    QMessageBox.information(self, "提示", "编辑器内容为空，无法转换。")
                    return

                hex_representation = ' '.join(f'{b:02x}' for b in text.encode('utf-8'))
                self.text_edit.setPlainText(hex_representation)
                self.is_hex_mode = True
                self.status_bar.showMessage("已成功转换为16进制编码。", 3000)

            else:
                # --- 模式：16进制 -> 文本 ---
                hex_text = self.text_edit.toPlainText()
                if not hex_text:
                    QMessageBox.information(self, "提示", "编辑器内容为空，无法恢复。")
                    return

                # 清理输入，移除空格和换行符，以支持更自由的格式
                cleaned_hex = ''.join(hex_text.split())

                # 如果清理后是空字符串，则直接设置为空文本
                if not cleaned_hex:
                    self.text_edit.setPlainText("")
                else:
                    byte_data = bytes.fromhex(cleaned_hex)
                    original_text = byte_data.decode('utf-8')
                    self.text_edit.setPlainText(original_text)

                self.is_hex_mode = False
                self.status_bar.showMessage("已从16进制成功恢复文本。", 3000)

        except (ValueError, UnicodeDecodeError) as e:
            QMessageBox.critical(self, "转换错误", f"无法从16进制恢复，格式可能不正确或不是有效的UTF-8序列。\n错误: {e}")
        finally:
            self.update_hex_action_state()
            self.text_edit.blockSignals(False)

            # 只有在成功切换回文本模式后，才手动触发一次状态更新
            if not self.is_hex_mode:
                self.on_text_changed()

    def update_hex_action_state(self):
        """根据is_hex_mode状态更新按钮的文本、图标和提示"""
        if self.is_hex_mode:
            self.toggle_hex_action.setText("从16进制恢复(&H)")
            self.toggle_hex_action.setIcon(QIcon.fromTheme("document-revert"))
            self.toggle_hex_action.setStatusTip("将16进制编码恢复为原始文本")
            self.status_label.setText("当前为16进制模式，字符统计和限制已禁用。可自由编辑后恢复。")
        else:
            self.toggle_hex_action.setText("转换为16进制(&H)")
            self.toggle_hex_action.setIcon(QIcon.fromTheme("utilities-terminal"))
            self.toggle_hex_action.setStatusTip("将当前文本转换为UTF-8的16进制编码")

    # --- 其他功能在执行前增加模式检查 ---
    def delete_all_substrings(self):
        """(3a) 删除所有匹配的子串"""
        text = self.text_edit.toPlainText()
        substring, ok = QInputDialog.getText(self, "删除全部子串", "请输入要删除的子串:")
        if ok and substring:
            if substring not in text:
                QMessageBox.warning(self, "未找到", f"文中未找到字符串 '{substring}'。")
                return
            new_text = text.replace(substring, '')
            self.text_edit.setPlainText(new_text)
            QMessageBox.information(self, "操作成功", f"已删除所有出现的 '{substring}'。")

    def delete_first_substring(self):
        """(3b) 删除第一个匹配的子串"""
        text = self.text_edit.toPlainText()
        substring, ok = QInputDialog.getText(self, "删除第一个子串", "请输入要删除的子串:")
        if ok and substring:
            if substring not in text:
                QMessageBox.warning(self, "未找到", f"文中未找到字符串 '{substring}'。")
                return
            new_text = text.replace(substring, '', 1)
            self.text_edit.setPlainText(new_text)
            QMessageBox.information(self, "操作成功", f"已删除第一个出现的 '{substring}'。")

    def delete_nth_substring(self):
        """(3c) 删除第 N 个匹配的子串"""
        text = self.text_edit.toPlainText()
        substring, ok1 = QInputDialog.getText(self, "删除第 N 个子串 - 步骤 1/2", "请输入要删除的子串:")
        if not (ok1 and substring): return

        total_count = text.count(substring)
        if total_count == 0:
            QMessageBox.warning(self, "未找到", f"文中未找到字符串 '{substring}'。")
            return

        n, ok2 = QInputDialog.getInt(self, "删除第 N 个子串 - 步骤 2/2",
                                     f"'{substring}' 共出现 {total_count} 次。\n请输入要删除第几个 (1-{total_count}):",
                                     1, 1, total_count)
        if not ok2: return

        start_index = -1
        for i in range(n):
            start_index = text.find(substring, start_index + 1)
            if start_index == -1:
                QMessageBox.critical(self, "逻辑错误", "查找第 N 个子串时发生错误。")
                return

        new_text = text[:start_index] + text[start_index + len(substring):]
        self.text_edit.setPlainText(new_text)
        QMessageBox.information(self, "操作成功", f"已删除第 {n} 个出现的 '{substring}'。")

    def save_file(self):
        """(4) 保存文本内容到文件"""
        if self.is_hex_mode:
            reply = QMessageBox.question(self, "保存确认",
                                         "当前内容为16进制编码，是否要将其恢复为文本后再保存？\n"
                                         "选择 'Yes' 以文本形式保存，'No' 以当前16进制形式保存。",
                                         QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel)
            if reply == QMessageBox.StandardButton.Cancel:
                return
            if reply == QMessageBox.StandardButton.Yes:
                # 尝试转换回文本，但不阻塞保存
                try:
                    hex_text = self.text_edit.toPlainText()
                    cleaned_hex = ''.join(hex_text.split())
                    if cleaned_hex:
                        byte_data = bytes.fromhex(cleaned_hex)
                        original_text = byte_data.decode('utf-8')
                        self.text_edit.setPlainText(original_text)
                        self.is_hex_mode = False  # 手动更新状态
                        self.update_hex_action_state()
                except Exception as e:
                    QMessageBox.critical(self, "转换失败", f"无法从16进制恢复为文本，保存操作已取消。\n错误: {e}")
                    return

        file_path, _ = QFileDialog.getSaveFileName(self, "保存文件", "", "Text Files (*.txt);;All Files (*)")
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(self.text_edit.toPlainText())
                self.status_bar.showMessage(f"文件已保存至: {file_path}", 3000)
            except Exception as e:
                QMessageBox.critical(self, "错误", f"无法保存文件:\n{e}")


# 程序入口
if __name__ == "__main__":
    app = QApplication(sys.argv)
    editor = TextEditor()
    editor.show()
    sys.exit(app.exec())