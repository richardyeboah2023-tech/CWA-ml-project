"""
CWA Estimator — PySide6 layout (fixed CoursesTable using QAbstractItemView enums).

Save this as main.py and keep styles.qss in the same folder (if you have it).
Requires: pip install PySide6 matplotlib
Run: python main.py
"""
import sys
from PySide6.QtCore import Qt, QSize
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QLabel,
    QPushButton, QListWidget, QListWidgetItem, QFrame, QTableWidgetItem,
    QCheckBox, QHeaderView, QSpacerItem, QSizePolicy, QGridLayout, QHBoxLayout as QHBox
)
from PySide6.QtWidgets import QTableWidget, QWidget as QtWidget, QAbstractItemView
# Matplotlib embedding
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

# Sample data (matches screenshot)
COURSES = [
    ("Mathematics", "3", "47", True, "55"),
    ("Physics", "5", "45", True, "52"),
    ("History", "4", "32", True, "68"),
    ("Biology", "5", "36", True, "66"),
    ("Chemistry", "3", "49", True, "75"),
]


class Card(QFrame):
    """Simple card/container with rounded corners — styling is provided in QSS."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("card")
        self.setFrameShape(QFrame.NoFrame)
        self.setContentsMargins(12, 12, 12, 12)


class Sidebar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("sidebar")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        # Top menu icon area
        menu_button = QPushButton("\u2630")  # simple hamburger glyph
        menu_button.setObjectName("menuButton")
        menu_button.setMaximumWidth(36)
        layout.addWidget(menu_button, alignment=Qt.AlignLeft)

        # App title
        title = QLabel("Academic Tools")
        title.setObjectName("sidebarTitle")
        layout.addWidget(title)

        # Navigation (use QListWidget for selectable items)
        nav = QListWidget()
        nav.setObjectName("navList")
        nav.setSpacing(6)
        items = [
            ("CWA Estimator", True),
            ("GPA Calculator", False),
            ("CGPA Calculator", False),
            ("", None),  # spacer group separator
            ("Settings", False),
            ("About", False),
        ]
        for text, active in items:
            if text == "":
                # separator
                sep = QListWidgetItem()
                sep.setFlags(Qt.NoItemFlags)
                nav.addItem(sep)
                continue
            it = QListWidgetItem(text)
            it.setText(text)
            it.setSizeHint(QSize(160, 40))
            if active:
                it.setData(Qt.UserRole, "active")
            nav.addItem(it)
        # Select the first item visually
        nav.setCurrentRow(0)
        layout.addWidget(nav)

        layout.addStretch()


class CoursesTable(QTableWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setColumnCount(5)
        self.setHorizontalHeaderLabels(["Course", "Credits", "Current Score", "Target", "Allocated Score"])
        self.verticalHeader().setVisible(False)
        self.setShowGrid(False)
        self.setAlternatingRowColors(True)
        # Use QAbstractItemView enum values (not self.SelectRows)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        # Use QAbstractItemView for edit trigger enum
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.setFocusPolicy(Qt.NoFocus)

        header = self.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)

        self.populate()

    def populate(self):
        self.setRowCount(len(COURSES))
        for row, (course, credits, score, target, alloc) in enumerate(COURSES):
            self.setItem(row, 0, QTableWidgetItem(course))
            self.setItem(row, 1, QTableWidgetItem(credits))
            self.setItem(row, 2, QTableWidgetItem(score))

            # Checkbox widget for "Target"
            cb = QCheckBox()
            cb.setChecked(bool(target))
            cb_cell = QWidget()
            cb_layout = QHBoxLayout(cb_cell)
            cb_layout.setContentsMargins(0, 0, 0, 0)
            cb_layout.addWidget(cb, alignment=Qt.AlignCenter)
            self.setCellWidget(row, 3, cb_cell)

            self.setItem(row, 4, QTableWidgetItem(alloc))


class ChartCanvas(FigureCanvas):
    """Simple line chart similar to screenshot."""
    def __init__(self, parent=None, width=5, height=3, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super().__init__(fig)
        fig.tight_layout()
        self.plot_sample()

    def plot_sample(self):
        ax = self.axes
        ax.clear()
        # Sample points that vaguely match the screenshot trend
        x = [0, 1, 2, 3]
        current = [70, 76, 74, 77]
        adjusted = [72, 74, 72, 76]
        ax.plot(x, current, marker='o', color="#2a67d9", linewidth=2, label="Current CWA")
        ax.plot(x, adjusted, marker='o', color="#9bb7f8", linestyle='--', linewidth=2, label="Adjusted CWA")
        ax.set_ylim(64, 82)
        ax.set_xticks([0, 1, 2, 3])
        ax.set_xticklabels(["Initial", "Selected", "Adjusted", "Final"])
        ax.grid(axis='y', color="#f0f0f0")
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.legend(loc='lower left', frameon=False, fontsize=9)
        self.draw()


class SummaryCard(Card):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QGridLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setVerticalSpacing(10)

        labels = [
            ("Total Credits:", "21"),
            ("Selected Credits:", "9"),
            ("Remaining Credits:", "12"),
            ("Target CWA:", "72.5"),
            ("Required Avg:", "68.3"),
        ]
        for i, (k, v) in enumerate(labels):
            key = QLabel(k)
            key.setObjectName("summaryKey")
            val = QLabel(v)
            val.setObjectName("summaryValue")
            if i in (3, 4):  # emphasize the last two values
                val.setProperty("emphasized", True)
            layout.addWidget(key, i, 0, alignment=Qt.AlignLeft)
            layout.addWidget(val, i, 1, alignment=Qt.AlignRight)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CWA Estimator — PySide6")
        self.resize(1100, 700)

        central = QWidget()
        self.setCentralWidget(central)
        root = QHBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)

        # Sidebar
        self.sidebar = Sidebar()
        self.sidebar.setFixedWidth(220)
        root.addWidget(self.sidebar)

        # Main content area (with padding and background)
        content_wrap = QWidget()
        content_layout = QVBoxLayout(content_wrap)
        content_layout.setContentsMargins(24, 24, 24, 24)
        content_layout.setSpacing(16)

        # Header: title and current CWA
        header = QWidget()
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(8, 8, 8, 8)
        title = QLabel("CWA Estimator")
        title.setObjectName("pageTitle")
        header_layout.addWidget(title, alignment=Qt.AlignLeft)

        header_layout.addStretch()
        current_label = QLabel("Current CWA:")
        current_label.setObjectName("currentLabel")
        current_value = QLabel("72.4")
        current_value.setObjectName("currentValue")
        header_layout.addWidget(current_label, alignment=Qt.AlignVCenter)
        header_layout.addWidget(current_value, alignment=Qt.AlignVCenter)

        content_layout.addWidget(header)

        # Top card: courses table
        courses_card = Card()
        courses_layout = QVBoxLayout(courses_card)
        courses_layout.setContentsMargins(8, 8, 8, 8)
        courses_title = QLabel("Courses (Semester 1)")
        courses_title.setObjectName("cardTitle")
        courses_layout.addWidget(courses_title)
        self.table = CoursesTable()
        courses_layout.addWidget(self.table)
        content_layout.addWidget(courses_card, stretch=2)

        # Bottom row: chart and summary
        bottom_row = QWidget()
        br_layout = QHBoxLayout(bottom_row)
        br_layout.setSpacing(16)

        chart_card = Card()
        chart_layout = QVBoxLayout(chart_card)
        chart_title = QLabel("CWA Distribution Graph")
        chart_title.setObjectName("cardTitle")
        chart_layout.addWidget(chart_title)
        chart = ChartCanvas(width=6, height=3)
        chart.setMinimumHeight(220)
        chart_layout.addWidget(chart)
        br_layout.addWidget(chart_card, stretch=3)

        summary_card = Card()
        summary_title = QLabel("Distribution Summary")
        summary_title.setObjectName("cardTitle")
        summary_layout = QVBoxLayout(summary_card)
        summary_layout.addWidget(summary_title)
        summary_layout.addWidget(SummaryCard())
        br_layout.addWidget(summary_card, stretch=1)

        content_layout.addWidget(bottom_row, stretch=1)

        root.addWidget(content_wrap, stretch=1)

        # Load stylesheet
        try:
            with open("styles.qss", "r", encoding="utf-8") as f:
                self.setStyleSheet(f.read())
        except Exception:
            pass


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec())