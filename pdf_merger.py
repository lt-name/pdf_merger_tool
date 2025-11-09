#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import os
from pypdf import PdfWriter, PdfReader
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QFileDialog
from PySide6.QtGui import QDragEnterEvent, QDropEvent
from qfluentwidgets import (FluentIcon, PrimaryPushButton, PushButton,
                            ToolButton, ListWidget, InfoBar, InfoBarPosition,
                            MessageBox)


def merge_pdfs_cli(input_files, output_file):
    """
    命令行方式合并 PDF

    Args:
        input_files: PDF 文件路径列表
        output_file: 输出文件路径
    """
    try:
        print(f"开始合并 {len(input_files)} 个 PDF 文件...")

        writer = PdfWriter()

        for i, pdf_file in enumerate(input_files, 1):
            print(f"[{i}/{len(input_files)}] 正在处理: {pdf_file}")

            if not os.path.exists(pdf_file):
                print(f"警告: 文件不存在，跳过: {pdf_file}")
                continue

            try:
                reader = PdfReader(pdf_file)
                for page in reader.pages:
                    writer.add_page(page)
                print(f"  ✓ 已添加 {len(reader.pages)} 页")
            except Exception as e:
                print(f"  ✗ 处理失败: {e}")
                continue

        with open(output_file, "wb") as output:
            writer.write(output)

        print(f"\n✓ 合并完成！输出文件: {output_file}")
        return True

    except Exception as e:
        print(f"\n✗ 合并失败: {e}")
        return False


class PDFMergerGUI(QWidget):
    """PDF 合并工具的图形界面"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("PDF 合并工具")
        self.resize(800, 600)

        # PDF 文件列表
        self.pdf_files = []

        # 启用拖放功能
        self.setAcceptDrops(True)

        self.setup_ui()

    def setup_ui(self):
        """设置用户界面"""
        # 创建主布局
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        # 按钮区域
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)

        # 添加文件按钮
        self.add_btn = PrimaryPushButton(FluentIcon.ADD, "添加 PDF 文件")
        self.add_btn.clicked.connect(self.add_files)
        button_layout.addWidget(self.add_btn)

        # 移除选中按钮
        self.remove_btn = PushButton(FluentIcon.REMOVE, "移除选中")
        self.remove_btn.clicked.connect(self.remove_selected)
        button_layout.addWidget(self.remove_btn)

        # 清空列表按钮
        self.clear_btn = PushButton(FluentIcon.DELETE, "清空列表")
        self.clear_btn.clicked.connect(self.clear_list)
        button_layout.addWidget(self.clear_btn)

        button_layout.addStretch()
        main_layout.addLayout(button_layout)

        # 文件列表
        self.list_widget = ListWidget()
        self.list_widget.setSelectionMode(ListWidget.ExtendedSelection)
        main_layout.addWidget(self.list_widget)

        # 移动按钮区域
        move_layout = QHBoxLayout()
        move_layout.setSpacing(10)

        self.up_btn = ToolButton(FluentIcon.UP)
        self.up_btn.setToolTip("上移")
        self.up_btn.clicked.connect(self.move_up)
        move_layout.addWidget(self.up_btn)

        self.down_btn = ToolButton(FluentIcon.DOWN)
        self.down_btn.setToolTip("下移")
        self.down_btn.clicked.connect(self.move_down)
        move_layout.addWidget(self.down_btn)

        move_layout.addStretch()
        main_layout.addLayout(move_layout)

        # 合并按钮
        self.merge_btn = PrimaryPushButton(FluentIcon.DOCUMENT, "合并 PDF")
        self.merge_btn.clicked.connect(self.merge_pdfs)
        self.merge_btn.setFixedHeight(45)
        main_layout.addWidget(self.merge_btn)

    def _add_pdf_files(self, file_paths):
        """
        添加 PDF 文件到列表（内部方法）

        Args:
            file_paths: 文件路径列表

        Returns:
            添加成功的文件数量
        """
        added_count = 0
        for file_path in file_paths:
            if not os.path.exists(file_path):
                continue

            if not file_path.lower().endswith('.pdf'):
                continue

            if file_path not in self.pdf_files:
                self.pdf_files.append(file_path)
                self.list_widget.addItem(os.path.basename(file_path))
                added_count += 1

        return added_count

    def add_files(self):
        """通过文件对话框添加 PDF 文件"""
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "选择 PDF 文件",
            "",
            "PDF 文件 (*.pdf);;所有文件 (*.*)"
        )

        if files:
            added_count = self._add_pdf_files(files)

            if added_count > 0:
                InfoBar.success(
                    title="添加成功",
                    content=f"已添加 {added_count} 个文件，共 {len(self.pdf_files)} 个文件",
                    orient=Qt.Horizontal,
                    isClosable=True,
                    position=InfoBarPosition.TOP,
                    duration=2000,
                    parent=self
                )

    def remove_selected(self):
        """移除选中的文件"""
        selected_items = self.list_widget.selectedItems()
        if not selected_items:
            InfoBar.warning(
                title="警告",
                content="请先选择要移除的文件",
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=2000,
                parent=self
            )
            return

        # 从后往前删除，避免索引错位
        selected_rows = [self.list_widget.row(item) for item in selected_items]
        selected_rows.sort(reverse=True)

        for row in selected_rows:
            self.list_widget.takeItem(row)
            del self.pdf_files[row]

        InfoBar.success(
            title="移除成功",
            content=f"已移除 {len(selected_rows)} 个文件",
            orient=Qt.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP,
            duration=2000,
            parent=self
        )

    def clear_list(self):
        """清空文件列表"""
        if not self.pdf_files:
            return

        w = MessageBox("确认", "确定要清空所有文件吗？", self)
        if w.exec():
            self.list_widget.clear()
            self.pdf_files.clear()
            InfoBar.success(
                title="清空成功",
                content="列表已清空",
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=2000,
                parent=self
            )

    def move_up(self):
        """上移选中的文件"""
        selected_items = self.list_widget.selectedItems()
        if not selected_items:
            return

        rows = [self.list_widget.row(item) for item in selected_items]
        rows.sort()

        for row in rows:
            if row > 0:
                # 交换文件
                self.pdf_files[row], self.pdf_files[row - 1] = \
                    self.pdf_files[row - 1], self.pdf_files[row]

                # 交换列表项
                item = self.list_widget.takeItem(row)
                self.list_widget.insertItem(row - 1, item)
                self.list_widget.setCurrentRow(row - 1)

    def move_down(self):
        """下移选中的文件"""
        selected_items = self.list_widget.selectedItems()
        if not selected_items:
            return

        rows = [self.list_widget.row(item) for item in selected_items]
        rows.sort(reverse=True)

        for row in rows:
            if row < len(self.pdf_files) - 1:
                self.pdf_files[row], self.pdf_files[row + 1] = \
                    self.pdf_files[row + 1], self.pdf_files[row]

                item = self.list_widget.takeItem(row)
                self.list_widget.insertItem(row + 1, item)
                self.list_widget.setCurrentRow(row + 1)

    def merge_pdfs(self):
        """合并 PDF 文件"""
        if not self.pdf_files:
            InfoBar.warning(
                title="警告",
                content="请先添加 PDF 文件",
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=2000,
                parent=self
            )
            return

        # 选择输出文件
        output_file, _ = QFileDialog.getSaveFileName(
            self,
            "保存合并后的 PDF",
            "",
            "PDF 文件 (*.pdf)"
        )

        if not output_file:
            return

        try:
            InfoBar.info(
                title="处理中",
                content="正在合并 PDF...",
                orient=Qt.Horizontal,
                isClosable=False,
                position=InfoBarPosition.TOP,
                duration=1000,
                parent=self
            )

            writer = PdfWriter()

            # 逐个读取并添加 PDF
            for i, pdf_file in enumerate(self.pdf_files):
                reader = PdfReader(pdf_file)

                for page in reader.pages:
                    writer.add_page(page)

            with open(output_file, "wb") as output:
                writer.write(output)

            InfoBar.success(
                title="合并完成",
                content=f"共合并 {len(self.pdf_files)} 个文件",
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=3000,
                parent=self
            )

            w = MessageBox(
                "成功",
                f"PDF 合并完成！\n\n共合并 {len(self.pdf_files)} 个文件\n保存至: {output_file}",
                self
            )
            w.exec()

        except Exception as e:
            InfoBar.error(
                title="合并失败",
                content=str(e),
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=5000,
                parent=self
            )

    def dragEnterEvent(self, event: QDragEnterEvent):
        """处理拖入事件"""
        # 检查是否包含文件
        if event.mimeData().hasUrls():
            # 检查是否至少有一个 PDF 文件
            urls = event.mimeData().urls()
            has_pdf = any(url.toLocalFile().lower().endswith('.pdf') for url in urls)

            if has_pdf:
                event.acceptProposedAction()
            else:
                event.ignore()
        else:
            event.ignore()

    def dropEvent(self, event: QDropEvent):
        """处理放下事件"""
        # 获取所有文件路径
        file_paths = []
        for url in event.mimeData().urls():
            file_path = url.toLocalFile()
            if file_path:
                file_paths.append(file_path)

        # 添加文件
        if file_paths:
            added_count = self._add_pdf_files(file_paths)

            if added_count > 0:
                InfoBar.success(
                    title="拖放成功",
                    content=f"已添加 {added_count} 个文件，共 {len(self.pdf_files)} 个文件",
                    orient=Qt.Horizontal,
                    isClosable=True,
                    position=InfoBarPosition.TOP,
                    duration=2000,
                    parent=self
                )
            else:
                InfoBar.warning(
                    title="提示",
                    content="未找到有效的 PDF 文件或文件已存在",
                    orient=Qt.Horizontal,
                    isClosable=True,
                    position=InfoBarPosition.TOP,
                    duration=2000,
                    parent=self
                )

        event.acceptProposedAction()


def print_usage():
    """打印使用说明"""
    print("""
PDF 合并工具
=============

使用方法:

1. 图形界面模式（默认）:
   python pdf_merger.py

2. 命令行模式:
   python pdf_merger.py -o output.pdf file1.pdf file2.pdf file3.pdf

   参数:
   -o, --output  输出文件路径（必需）
   -h, --help    显示帮助信息

示例:
   python pdf_merger.py -o merged.pdf doc1.pdf doc2.pdf doc3.pdf
   python pdf_merger.py --output result.pdf *.pdf
""")


def main():
    """主函数"""
    # 检查是否为命令行模式
    if len(sys.argv) > 1:
        if "-h" in sys.argv or "--help" in sys.argv:
            print_usage()
            return

        # 解析命令行参数
        if "-o" in sys.argv:
            output_index = sys.argv.index("-o") + 1
        elif "--output" in sys.argv:
            output_index = sys.argv.index("--output") + 1
        else:
            print("错误: 缺少输出文件参数 (-o 或 --output)")
            print_usage()
            return

        if output_index >= len(sys.argv):
            print("错误: 未指定输出文件名")
            print_usage()
            return

        output_file = sys.argv[output_index]

        # 获取输入文件列表
        input_files = [arg for i, arg in enumerate(sys.argv[1:], 1)
                       if i not in [output_index - 1, output_index] and not arg.startswith('-')]

        if not input_files:
            print("错误: 未指定输入文件")
            print_usage()
            return

        # 执行命令行合并
        merge_pdfs_cli(input_files, output_file)

    else:
        app = QApplication(sys.argv)

        window = PDFMergerGUI()
        window.show()

        sys.exit(app.exec())


if __name__ == "__main__":
    main()