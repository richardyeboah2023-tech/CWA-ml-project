import sys
import math
from typing import Optional, List

from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QColor, QFont, QPainter, QPen, QIntValidator, QDoubleValidator
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QFrame,
    QLabel,
    QHBoxLayout,
    QVBoxLayout,
    QGridLayout,
    QToolButton,
    QButtonGroup,
    QTableWidget,
    QTableWidgetItem,
    QAbstractItemView,
    QGraphicsDropShadowEffect,
    QPushButton,
    QSizePolicy,
    QStyle,
    QLineEdit,
    QStyledItemDelegate,
    QStackedWidget,
    QTabWidget,
    QCheckBox,
)

# QtCharts (PySide6-Addons)
try:
    from PySide6.QtCharts import QChart, QChartView, QLineSeries, QValueAxis, QCategoryAxis
    CHARTS_OK = True
except Exception:
    CHARTS_OK = False


# ---- Your engine bridge (exact) ----
# cwa_engine_bridge.py must be in the same folder as this file.
try:
    from cwa_engine_bridge import calculate_cwa as engine_calculate_cwa
    ENGINE_OK = True
    ENGINE_ERR = ""
except Exception as e:
    ENGINE_OK = False
    ENGINE_ERR = str(e)
    engine_calculate_cwa = None  # type: ignore


APP_QSS = """
QWidget#AppRoot {
    background: #eef2f7;
    font-family: Arial;
}

/* Unified rounded container */
QFrame#Shell {
    background: #ffffff;
    border: 1px solid #e5e7eb;
    border-radius: 18px;
}

/* Sidebar */
QFrame#Sidebar {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                               stop:0 #1f2b3e, stop:1 #2e3b52);
    border-top-left-radius: 17px;
    border-bottom-left-radius: 17px;
}
QLabel#SidebarSection {
    color: rgba(255,255,255,0.60);
    font-weight: 900;
    font-size: 13px;
    padding-left: 10px;
    padding-top: 6px;
    padding-bottom: 8px;
}
QToolButton[class="NavItem"] {
    color: rgba(255,255,255,0.90);
    font-weight: 900;
    font-size: 12px;
    text-align: left;
    padding: 10px 12px;
    border-radius: 10px;
    background: transparent;
}
QToolButton[class="NavItem"]:hover { background: rgba(255,255,255,0.08); }
QToolButton[class="NavItem"]:checked { background: #1d4ed8; color: #ffffff; }

/* Right content */
QFrame#RightPanel {
    background: #eef2f7;
    border-top-right-radius: 17px;
    border-bottom-right-radius: 17px;
}

/* Top bar */
QFrame#TopBar {
    background: #ffffff;
    border-bottom: 1px solid #e5e7eb;
    border-top-right-radius: 17px;
}
QLabel#TopTitle {
    color: #111827;
    font-weight: 900;
    font-size: 14px;
}
QLabel#TopRightLabel {
    color: #6b7280;
    font-weight: 900;
}
QLineEdit#TopCWAInput {
    border: 0px;
    background: transparent;
    color: #1d4ed8;
    font-weight: 900;
    font-size: 13px;
    padding: 0px;
}

/* Cards */
QFrame#Card {
    background: #ffffff;
    border: 1px solid #e5e7eb;
    border-radius: 12px;
}
QLabel#CardTitle {
    color: #111827;
    font-weight: 900;
    font-size: 12px;
}

/* Buttons */
QPushButton#AddCourseBtn {
    background: #1d4ed8;
    color: #ffffff;
    font-weight: 900;
    padding: 8px 12px;
    border-radius: 10px;
    border: 0px;
}
QPushButton#AddCourseBtn:hover { background: #1e40af; }

QPushButton#GhostBtn {
    background: transparent;
    color: #111827;
    font-weight: 900;
    padding: 8px 12px;
    border-radius: 10px;
    border: 1px solid #d1d5db;
}
QPushButton#GhostBtn:hover { background: #f3f4f6; }

/* Mini inputs */
QLineEdit[field="mini"] {
    border: 1px solid #cbd5e1;
    border-radius: 10px;
    padding: 6px 10px;
    background: #ffffff;
    color: #111827;
    font-weight: 900;
}

/* Table */
QTableWidget {
    background: #ffffff;
    border: 1px solid #e5e7eb;
    border-radius: 10px;
    gridline-color: #e5e7eb;
    color: #111827;
    font-weight: 800;
}
QHeaderView::section {
    background: #f3f4f6;
    color: #374151;
    font-weight: 900;
    border: 0px;
    border-bottom: 1px solid #e5e7eb;
    padding: 8px;
}
QTableWidget::item:selected {
    background: transparent;
    color: #111827;
}

/* Target tick box (VISIBLE ✓) */
QLabel[targetBox="true"] {
    min-width: 20px;
    max-width: 20px;
    min-height: 20px;
    max-height: 20px;
    border-radius: 4px;
    border: 1px solid #cbd5e1;
    background: #ffffff;
    color: transparent;
    font-weight: 900;
}
QLabel[targetBox="true"][checked="true"] {
    background: #1d4ed8;
    border: 1px solid #1d4ed8;
    color: #ffffff;
}

/* Tab look (semesters) */
QTabWidget::pane { border: 0px; }
QTabBar::tab {
    background: #f3f4f6;
    color: #374151;
    font-weight: 900;
    padding: 8px 14px;
    border-top-left-radius: 10px;
    border-top-right-radius: 10px;
    margin-right: 6px;
}
QTabBar::tab:selected {
    background: #ffffff;
    color: #111827;
}
"""


class ShadowCard(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("Card")
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(22)
        shadow.setOffset(0, 8)
        shadow.setColor(QColor(0, 0, 0, 30))
        self.setGraphicsEffect(shadow)


class IntDelegate(QStyledItemDelegate):
    def __init__(self, lo: int, hi: int, parent=None):
        super().__init__(parent)
        self._v = QIntValidator(lo, hi)

    def createEditor(self, parent, option, index):
        ed = QLineEdit(parent)
        ed.setValidator(self._v)
        ed.setProperty("field", "mini")
        return ed


class DoubleDelegate(QStyledItemDelegate):
    def __init__(self, lo: float, hi: float, decimals: int = 2, parent=None):
        super().__init__(parent)
        v = QDoubleValidator(lo, hi, decimals)
        v.setNotation(QDoubleValidator.StandardNotation)
        self._v = v

    def createEditor(self, parent, option, index):
        ed = QLineEdit(parent)
        ed.setValidator(self._v)
        ed.setProperty("field", "mini")
        return ed


class CWAEstimatorPage(QWidget):
    """
    - Add course scrolls to new row.
    - No placeholders/defaults.
    - No 'Target score' input.
    - Distribution Summary: Total Credits, Selected Credits, Remaining Credits, Target CWA, Required Avg.
    - Selected = sum of credits from table inputs (active rows).
    - Remaining = Total - Selected.
    - Target tick: credits > 0 and Current Score >= Allocated Score.
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        self.target_cwa_edit: QLineEdit | None = None

        self.sum_total_credits: QLabel | None = None
        self.sum_selected_credits: QLabel | None = None
        self.sum_remaining_credits: QLabel | None = None
        self.sum_required_avg: QLabel | None = None
        self.sum_engine_status: QLabel | None = None

        self.semester_tabs: QTabWidget | None = None
        self.tables: List[QTableWidget] = []

        self.series_current = None
        self.series_adjusted = None

        self._current_cwa_getter = lambda: "0"
        self._building = False

        self._build_ui()

    # ---- hook from MainWindow ----
    def set_current_cwa_getter(self, getter):
        self._current_cwa_getter = getter

    # ---- helpers ----
    @staticmethod
    def _safe_int(text: str) -> int:
        try:
            return int(float((text or "0").strip()))
        except Exception:
            return 0

    @staticmethod
    def _safe_float(text: str) -> float:
        try:
            return float((text or "0").strip())
        except Exception:
            return 0.0

    @staticmethod
    def _text(item: Optional[QTableWidgetItem]) -> str:
        return item.text().strip() if item else ""

    def _get_current_cwa(self) -> float:
        try:
            return float((self._current_cwa_getter() or "0").strip())
        except Exception:
            return 0.0

    def _target_cwa_value(self) -> Optional[float]:
        if not self.target_cwa_edit:
            return None
        txt = self.target_cwa_edit.text().strip()
        if txt == "":
            return None
        return self._safe_float(txt)

    def _row_bg(self, r: int) -> QColor:
        return QColor("#eaf7e5") if (r % 2 == 0) else QColor("#dbf0d4")

    # ---- table / semesters ----
    def _make_table(self) -> QTableWidget:
        t = QTableWidget(0, 5)
        t.setHorizontalHeaderLabels(["Course", "Credits", "Current Score", "Target", "Allocated Score"])
        t.verticalHeader().setVisible(False)
        t.setShowGrid(True)
        t.setSelectionMode(QAbstractItemView.NoSelection)
        t.setEditTriggers(
            QAbstractItemView.DoubleClicked
            | QAbstractItemView.SelectedClicked
            | QAbstractItemView.EditKeyPressed
        )
        t.setFocusPolicy(Qt.StrongFocus)
        t.horizontalHeader().setStretchLastSection(True)
        t.horizontalHeader().setDefaultAlignment(Qt.AlignCenter)

        t.setColumnWidth(0, 280)
        t.setColumnWidth(1, 90)
        t.setColumnWidth(2, 150)
        t.setColumnWidth(3, 110)
        t.setColumnWidth(4, 170)

        t.setItemDelegateForColumn(1, IntDelegate(0, 60, t))
        t.setItemDelegateForColumn(2, DoubleDelegate(0.0, 100.0, 2, t))
        t.setItemDelegateForColumn(4, DoubleDelegate(0.0, 100.0, 2, t))

        t.itemChanged.connect(self.recompute)
        return t

    def add_semester(self) -> None:
        if not self.semester_tabs:
            return
        idx = self.semester_tabs.count() + 1
        table = self._make_table()
        self.tables.append(table)
        self.semester_tabs.addTab(table, f"Semester {idx}")
        self.semester_tabs.setCurrentWidget(table)
        self.add_course_row()
        self.recompute()

    def current_table(self) -> Optional[QTableWidget]:
        if not self.semester_tabs:
            return None
        w = self.semester_tabs.currentWidget()
        return w if isinstance(w, QTableWidget) else None

    def _set_item(self, t: QTableWidget, r: int, c: int, text: str, align: Qt.AlignmentFlag, editable: bool) -> None:
        it = QTableWidgetItem(text)
        it.setTextAlignment(align)
        it.setBackground(self._row_bg(r))
        flags = Qt.ItemIsSelectable | Qt.ItemIsEnabled
        if editable:
            flags |= Qt.ItemIsEditable
        it.setFlags(flags)
        t.setItem(r, c, it)

    def add_course_row(self) -> None:
        t = self.current_table()
        if not t:
            return

        r = t.rowCount()

        t.blockSignals(True)
        t.insertRow(r)

        self._set_item(t, r, 0, "", Qt.AlignVCenter | Qt.AlignLeft, True)
        self._set_item(t, r, 1, "", Qt.AlignCenter, True)
        self._set_item(t, r, 2, "", Qt.AlignCenter, True)
        self._set_item(t, r, 4, "", Qt.AlignCenter, True)

        self._set_target_box(t, r, checked=False, bg=self._row_bg(r))
        t.setRowHeight(r, 40)
        t.blockSignals(False)

        self._restyle_table(t)
        self.recompute()

        t.setCurrentCell(r, 0)
        t.scrollToItem(t.item(r, 0), QAbstractItemView.PositionAtBottom)

    # ---- target tick box ----
    def _set_target_box(self, table: QTableWidget, r: int, checked: bool, bg: QColor) -> None:
        holder = table.cellWidget(r, 3)
        if holder is None:
            holder = QWidget()
            lay = QHBoxLayout(holder)
            lay.setContentsMargins(0, 0, 0, 0)
            lay.setAlignment(Qt.AlignCenter)

            box = QLabel("")
            box.setAlignment(Qt.AlignCenter)
            box.setProperty("targetBox", True)
            lay.addWidget(box)

            table.setCellWidget(r, 3, holder)

        box = holder.findChild(QLabel)
        if box is not None:
            box.setText("✓" if checked else "")
            box.setProperty("checked", "true" if checked else "false")
            box.style().unpolish(box)
            box.style().polish(box)

        holder.setAutoFillBackground(True)
        pal = holder.palette()
        pal.setColor(holder.backgroundRole(), bg)
        holder.setPalette(pal)

    def _restyle_table(self, t: QTableWidget) -> None:
        t.blockSignals(True)
        for r in range(t.rowCount()):
            bg = self._row_bg(r)

            for col, align in [
                (0, Qt.AlignVCenter | Qt.AlignLeft),
                (1, Qt.AlignCenter),
                (2, Qt.AlignCenter),
                (4, Qt.AlignCenter),
            ]:
                it = t.item(r, col)
                if it:
                    it.setBackground(bg)
                    it.setTextAlignment(align)

            cr_txt = self._text(t.item(r, 1))
            cur_txt = self._text(t.item(r, 2))
            alloc_txt = self._text(t.item(r, 4))
            cr = self._safe_int(cr_txt) if cr_txt else 0
            cur = self._safe_float(cur_txt) if cur_txt else 0.0
            alloc = self._safe_float(alloc_txt) if alloc_txt else 0.0

            # ✅ FIX: tick when Current Score >= Allocated Score, and credits > 0
            reached = (cr > 0) and (alloc_txt != "") and (cur >= alloc)
            self._set_target_box(t, r, checked=reached, bg=bg)

        t.blockSignals(False)

    # ---- credits summary ----
    def _credits_from_tables(self) -> int:
        selected = 0
        for t in self.tables:
            for r in range(t.rowCount()):
                name_txt = self._text(t.item(r, 0))
                cr_txt = self._text(t.item(r, 1))
                cur_txt = self._text(t.item(r, 2))
                alloc_txt = self._text(t.item(r, 4))

                active = (name_txt != "") or (cr_txt != "") or (cur_txt != "") or (alloc_txt != "")
                cr = self._safe_int(cr_txt) if cr_txt else 0
                if active and cr > 0:
                    selected += cr
        return selected

    def _set_chart_reset(self) -> None:
        if CHARTS_OK and self.series_current and self.series_adjusted:
            self.series_current.clear()
            self.series_adjusted.clear()

    def _fallback_required_avg(self, completed: int, remaining: int, current_cwa: float, target_cwa: float) -> float:
        if remaining <= 0:
            return 0.0
        return (target_cwa * (completed + remaining) - current_cwa * completed) / remaining

    def recompute(self) -> None:
        if self._building:
            return

        for t in self.tables:
            self._restyle_table(t)

        selected = self._credits_from_tables()
        total = selected
        remaining = total - selected

        if self.sum_total_credits:
            self.sum_total_credits.setText(str(total))
        if self.sum_selected_credits:
            self.sum_selected_credits.setText(str(selected))
        if self.sum_remaining_credits:
            self.sum_remaining_credits.setText(str(remaining))

        target_cwa = self._target_cwa_value()
        if self.sum_required_avg:
            self.sum_required_avg.setText("-")

        if self.sum_engine_status:
            if ENGINE_OK:
                self.sum_engine_status.setText("Engine: connected (cwa_engine_bridge.py)")
            else:
                self.sum_engine_status.setText(f"Engine: not connected ({ENGINE_ERR})")

        if target_cwa is None or total <= 0:
            self._set_chart_reset()
            return

        if remaining <= 0:
            self._set_chart_reset()
            return

        current_cwa = self._get_current_cwa()
        name = "Student"
        completed = selected
        required = None

        if ENGINE_OK and engine_calculate_cwa is not None:
            try:
                required = float(
                    engine_calculate_cwa(
                        name, int(completed), int(remaining), float(current_cwa), float(target_cwa)
                    )
                )
                if not math.isfinite(required):
                    raise RuntimeError(f"Engine returned non-finite: {required}")
            except Exception:
                required = None

        if required is None:
            required = self._fallback_required_avg(completed, remaining, current_cwa, float(target_cwa))

        if self.sum_required_avg:
            self.sum_required_avg.setText(f"{required:.1f}")

        if CHARTS_OK and self.series_current and self.series_adjusted:
            self.series_current.clear()
            self.series_adjusted.clear()
            self.series_current.append(0, current_cwa)
            self.series_current.append(1, current_cwa)
            self.series_current.append(2, current_cwa)
            self.series_adjusted.append(0, current_cwa)
            self.series_adjusted.append(1, max(0.0, min(100.0, required)))
            self.series_adjusted.append(2, float(target_cwa))

    # ---- build UI ----
    def _build_ui(self):
        self._building = True

        root = QVBoxLayout(self)
        root.setContentsMargins(18, 0, 18, 18)
        root.setSpacing(14)

        # Courses card
        courses_card = ShadowCard()
        courses_layout = QVBoxLayout(courses_card)
        courses_layout.setContentsMargins(14, 14, 14, 14)
        courses_layout.setSpacing(10)

        header = QHBoxLayout()
        title = QLabel("Courses")
        title.setObjectName("CardTitle")

        add_sem_btn = QPushButton("+ Add semester")
        add_sem_btn.setObjectName("GhostBtn")
        add_sem_btn.setCursor(Qt.PointingHandCursor)
        add_sem_btn.clicked.connect(self.add_semester)

        add_course_btn = QPushButton("+ Add course")
        add_course_btn.setObjectName("AddCourseBtn")
        add_course_btn.setCursor(Qt.PointingHandCursor)
        add_course_btn.clicked.connect(self.add_course_row)

        header.addWidget(title)
        header.addStretch(1)
        header.addWidget(add_sem_btn)
        header.addSpacing(8)
        header.addWidget(add_course_btn)

        courses_layout.addLayout(header)

        self.semester_tabs = QTabWidget()
        self.semester_tabs.setDocumentMode(True)
        self.semester_tabs.currentChanged.connect(lambda _: self.recompute())
        courses_layout.addWidget(self.semester_tabs, 1)

        root.addWidget(courses_card, 2)

        # Bottom row
        bottom_row = QHBoxLayout()
        bottom_row.setSpacing(14)

        # Graph card
        graph_card = ShadowCard()
        graph_card.setMinimumWidth(650)
        gl = QVBoxLayout(graph_card)
        gl.setContentsMargins(14, 14, 14, 14)
        gl.setSpacing(10)

        gtitle = QLabel("CWA Distribution Graph")
        gtitle.setObjectName("CardTitle")
        gl.addWidget(gtitle)

        if CHARTS_OK:
            gl.addWidget(self._build_chart(), 1)
        else:
            lab = QLabel("QtCharts not available. Install: pip install PySide6-Addons")
            lab.setStyleSheet("color:#6b7280; font-weight:900;")
            lab.setAlignment(Qt.AlignCenter)
            gl.addWidget(lab, 1)

        # Summary card
        summary_card = ShadowCard()
        summary_card.setMinimumWidth(360)
        sl = QVBoxLayout(summary_card)
        sl.setContentsMargins(14, 14, 14, 14)
        sl.setSpacing(10)

        stitle = QLabel("Distribution Summary")
        stitle.setObjectName("CardTitle")
        sl.addWidget(stitle)

        grid = QGridLayout()
        grid.setHorizontalSpacing(10)
        grid.setVerticalSpacing(14)

        def lbl(text: str) -> QLabel:
            l = QLabel(text)
            l.setStyleSheet("color:#374151; font-weight:900;")
            return l

        def blue_value(text="") -> QLabel:
            r = QLabel(text)
            r.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            r.setStyleSheet("color:#1d4ed8; font-weight:900;")
            return r

        grid.addWidget(lbl("Total Credits:"), 0, 0)
        self.sum_total_credits = blue_value("0")
        grid.addWidget(self.sum_total_credits, 0, 1)

        grid.addWidget(lbl("Selected Credits:"), 1, 0)
        self.sum_selected_credits = blue_value("0")
        grid.addWidget(self.sum_selected_credits, 1, 1)

        grid.addWidget(lbl("Remaining Credits:"), 2, 0)
        self.sum_remaining_credits = blue_value("0")
        grid.addWidget(self.sum_remaining_credits, 2, 1)

        grid.addWidget(lbl("Target CWA:"), 3, 0)
        self.target_cwa_edit = QLineEdit("")  # no placeholder, no default
        self.target_cwa_edit.setProperty("field", "mini")
        self.target_cwa_edit.setValidator(QDoubleValidator(0.0, 100.0, 2, self))
        self.target_cwa_edit.textChanged.connect(self.recompute)
        grid.addWidget(self.target_cwa_edit, 3, 1, alignment=Qt.AlignRight)

        grid.addWidget(lbl("Required Avg:"), 4, 0)
        self.sum_required_avg = blue_value("-")
        grid.addWidget(self.sum_required_avg, 4, 1)

        sl.addLayout(grid)

        self.sum_engine_status = QLabel("")
        self.sum_engine_status.setStyleSheet("color:#6b7280; font-weight:900;")
        sl.addSpacing(10)
        sl.addWidget(self.sum_engine_status)
        sl.addStretch(1)

        bottom_row.addWidget(graph_card, 3)
        bottom_row.addWidget(summary_card, 2)

        bottom_wrap = QWidget()
        bottom_wrap.setLayout(bottom_row)
        root.addWidget(bottom_wrap, 2)

        # Semester 1 by default
        self.add_semester()

        self._building = False
        self.recompute()

    def _build_chart(self) -> QChartView:
        self.series_current = QLineSeries()
        self.series_adjusted = QLineSeries()

        pen_current = QPen(QColor("#1d4ed8"))
        pen_current.setWidth(3)
        self.series_current.setPen(pen_current)
        self.series_current.setPointsVisible(True)
        self.series_current.setName("Current CWA")

        pen_adjusted = QPen(QColor("#93c5fd"))
        pen_adjusted.setWidth(2)
        pen_adjusted.setStyle(Qt.DashLine)
        self.series_adjusted.setPen(pen_adjusted)
        self.series_adjusted.setPointsVisible(True)
        self.series_adjusted.setName("Adjusted CWA")

        chart = QChart()
        chart.addSeries(self.series_current)
        chart.addSeries(self.series_adjusted)
        chart.setBackgroundVisible(False)
        chart.setPlotAreaBackgroundVisible(False)
        chart.legend().setVisible(True)
        chart.legend().setAlignment(Qt.AlignBottom)
        chart.legend().setLabelColor(QColor("#374151"))

        axis_x = QCategoryAxis()
        axis_x.setRange(0, 2)
        axis_x.append("Initial", 0)
        axis_x.append("Selected", 1)
        axis_x.append("Adjusted", 2)
        axis_x.setLabelsPosition(QCategoryAxis.AxisLabelsPositionOnValue)
        axis_x.setLabelsColor(QColor("#6b7280"))
        axis_x.setGridLineVisible(False)

        axis_y = QValueAxis()
        axis_y.setRange(0, 100)
        axis_y.setTickCount(6)
        axis_y.setLabelsColor(QColor("#6b7280"))
        axis_y.setGridLineColor(QColor("#e5e7eb"))

        chart.addAxis(axis_x, Qt.AlignBottom)
        chart.addAxis(axis_y, Qt.AlignLeft)
        self.series_current.attachAxis(axis_x)
        self.series_current.attachAxis(axis_y)
        self.series_adjusted.attachAxis(axis_x)
        self.series_adjusted.attachAxis(axis_y)

        view = QChartView(chart)
        view.setRenderHint(QPainter.Antialiasing, True)
        view.setStyleSheet("background: transparent;")
        view.setMinimumHeight(270)
        return view


# ----------------- OTHER PAGES -----------------

class CGPACalculatorPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(14)

        card = ShadowCard()
        cl = QVBoxLayout(card)
        cl.setContentsMargins(14, 14, 14, 14)
        cl.setSpacing(10)

        title = QLabel("CGPA Calculator")
        title.setObjectName("CardTitle")
        cl.addWidget(title)

        grid = QGridLayout()
        grid.setHorizontalSpacing(10)
        grid.setVerticalSpacing(10)

        def lbl(text: str) -> QLabel:
            l = QLabel(text)
            l.setStyleSheet("color:#374151; font-weight:900;")
            return l

        self.prev_cgpa = QLineEdit("")
        self.prev_cgpa.setProperty("field", "mini")
        self.prev_cgpa.setValidator(QDoubleValidator(0.0, 5.0, 3, self))
        self.prev_cgpa.textChanged.connect(self.recompute)

        self.prev_credits = QLineEdit("")
        self.prev_credits.setProperty("field", "mini")
        self.prev_credits.setValidator(QIntValidator(0, 999999, self))
        self.prev_credits.textChanged.connect(self.recompute)

        self.sem_gpa = QLineEdit("")
        self.sem_gpa.setProperty("field", "mini")
        self.sem_gpa.setValidator(QDoubleValidator(0.0, 5.0, 3, self))
        self.sem_gpa.textChanged.connect(self.recompute)

        self.sem_credits = QLineEdit("")
        self.sem_credits.setProperty("field", "mini")
        self.sem_credits.setValidator(QIntValidator(0, 999999, self))
        self.sem_credits.textChanged.connect(self.recompute)

        self.new_cgpa = QLabel("-")
        self.new_cgpa.setStyleSheet("color:#1d4ed8; font-weight:900; font-size:14px;")
        self.new_total = QLabel("-")
        self.new_total.setStyleSheet("color:#1d4ed8; font-weight:900;")

        grid.addWidget(lbl("Previous CGPA:"), 0, 0)
        grid.addWidget(self.prev_cgpa, 0, 1)
        grid.addWidget(lbl("Previous Credits:"), 1, 0)
        grid.addWidget(self.prev_credits, 1, 1)
        grid.addWidget(lbl("This Semester GPA:"), 2, 0)
        grid.addWidget(self.sem_gpa, 2, 1)
        grid.addWidget(lbl("This Semester Credits:"), 3, 0)
        grid.addWidget(self.sem_credits, 3, 1)

        grid.addWidget(lbl("New Total Credits:"), 4, 0)
        grid.addWidget(self.new_total, 4, 1, alignment=Qt.AlignRight)
        grid.addWidget(lbl("New CGPA:"), 5, 0)
        grid.addWidget(self.new_cgpa, 5, 1, alignment=Qt.AlignRight)

        cl.addLayout(grid)
        cl.addStretch(1)
        layout.addWidget(card, 1)

    def recompute(self):
        def f(ed: QLineEdit) -> Optional[float]:
            t = ed.text().strip()
            if t == "":
                return None
            try:
                return float(t)
            except Exception:
                return None

        def i(ed: QLineEdit) -> Optional[int]:
            t = ed.text().strip()
            if t == "":
                return None
            try:
                return int(float(t))
            except Exception:
                return None

        pcgpa = f(self.prev_cgpa)
        pcr = i(self.prev_credits)
        sgpa = f(self.sem_gpa)
        scr = i(self.sem_credits)

        if pcgpa is None or pcr is None or sgpa is None or scr is None or (pcr + scr) <= 0:
            self.new_cgpa.setText("-")
            self.new_total.setText("-")
            return

        total_credits = pcr + scr
        new_cgpa = (pcgpa * pcr + sgpa * scr) / total_credits

        self.new_total.setText(str(total_credits))
        self.new_cgpa.setText(f"{new_cgpa:.3f}")


class SettingsPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(14)

        card = ShadowCard()
        cl = QVBoxLayout(card)
        cl.setContentsMargins(14, 14, 14, 14)
        cl.setSpacing(10)

        title = QLabel("Settings")
        title.setObjectName("CardTitle")
        cl.addWidget(title)

        self.auto_recalc = QCheckBox("Auto recalculate")
        self.auto_recalc.setChecked(True)
        self.confirm_reset = QCheckBox("Confirm before reset")
        self.confirm_reset.setChecked(False)

        cl.addWidget(self.auto_recalc)
        cl.addWidget(self.confirm_reset)

        engine = QLabel(
            ("Engine status: connected (cwa_engine_bridge.py)" if ENGINE_OK else f"Engine status: not connected ({ENGINE_ERR})")
        )
        engine.setStyleSheet("color:#6b7280; font-weight:900;")
        cl.addSpacing(8)
        cl.addWidget(engine)

        cl.addStretch(1)
        layout.addWidget(card, 1)


class AboutPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(14)

        card = ShadowCard()
        cl = QVBoxLayout(card)
        cl.setContentsMargins(14, 14, 14, 14)
        cl.setSpacing(10)

        title = QLabel("About")
        title.setObjectName("CardTitle")
        cl.addWidget(title)

        text = QLabel(
            "Academic Tools\n\n"
            "CWA Estimator + CGPA utilities.\n"
            "This UI is connected to the CWA engine via cwa_engine_bridge.py.\n"
        )
        text.setWordWrap(True)
        text.setStyleSheet("color:#374151; font-weight:900;")
        cl.addWidget(text)
        cl.addStretch(1)

        layout.addWidget(card, 1)


class MainWindow(QMainWindow):
    """
    Navigation:
      - CWA Estimator
      - CGPA Calculator
      - Settings
      - About
    """

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Academic Tools")
        self.resize(1200, 740)

        self.page_title: QLabel | None = None
        self.current_cwa_input: QLineEdit | None = None
        self.current_cwa_container: QWidget | None = None

        self.stack: QStackedWidget | None = None
        self.cwa_page: CWAEstimatorPage | None = None

        self._build()
        self._apply_nav(0)

    def _build(self):
        root = QWidget()
        root.setObjectName("AppRoot")
        self.setCentralWidget(root)

        root_layout = QVBoxLayout(root)
        root_layout.setContentsMargins(26, 26, 26, 26)

        shell = QFrame()
        shell.setObjectName("Shell")
        shadow = QGraphicsDropShadowEffect(shell)
        shadow.setBlurRadius(34)
        shadow.setOffset(0, 10)
        shadow.setColor(QColor(0, 0, 0, 40))
        shell.setGraphicsEffect(shadow)

        shell_layout = QHBoxLayout(shell)
        shell_layout.setContentsMargins(1, 1, 1, 1)
        shell_layout.setSpacing(0)

        # Sidebar
        sidebar = QFrame()
        sidebar.setObjectName("Sidebar")
        sidebar.setFixedWidth(240)
        sb = QVBoxLayout(sidebar)
        sb.setContentsMargins(16, 18, 16, 18)
        sb.setSpacing(10)

        section = QLabel("Academic Tools")
        section.setObjectName("SidebarSection")
        sb.addWidget(section)

        group = QButtonGroup(self)
        group.setExclusive(True)
        icon_size = QSize(22, 22)

        def nav(text: str, std_icon: QStyle.StandardPixmap, idx: int, checked=False) -> QToolButton:
            b = QToolButton()
            b.setCheckable(True)
            b.setChecked(checked)
            b.setCursor(Qt.PointingHandCursor)
            b.setProperty("class", "NavItem")
            b.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
            b.setIcon(self.style().standardIcon(std_icon))
            b.setIconSize(icon_size)
            b.setText(text)
            b.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            b.clicked.connect(lambda: self._apply_nav(idx))
            group.addButton(b)
            return b

        sb.addWidget(nav("CWA Estimator", QStyle.SP_ComputerIcon, 0, checked=True))
        sb.addWidget(nav("CGPA Calculator", QStyle.SP_DriveHDIcon, 1))
        sb.addSpacing(14)
        sb.addWidget(nav("Settings", QStyle.SP_FileDialogDetailedView, 2))
        sb.addWidget(nav("About", QStyle.SP_MessageBoxInformation, 3))
        sb.addStretch(1)

        # Right panel
        right = QFrame()
        right.setObjectName("RightPanel")
        rl = QVBoxLayout(right)
        rl.setContentsMargins(0, 0, 0, 0)
        rl.setSpacing(14)

        # Top bar
        topbar = QFrame()
        topbar.setObjectName("TopBar")
        topbar.setFixedHeight(58)
        tl = QHBoxLayout(topbar)
        tl.setContentsMargins(18, 12, 18, 12)

        hamburger = QLabel("☰")
        hamburger.setStyleSheet("color:#111827; font-weight:900; font-size:16px;")

        self.page_title = QLabel("CWA Estimator")
        self.page_title.setObjectName("TopTitle")

        tl.addWidget(hamburger)
        tl.addSpacing(10)
        tl.addWidget(self.page_title)
        tl.addStretch(1)

        # Current CWA (only visible on CWA page)
        self.current_cwa_container = QWidget()
        cwal = QHBoxLayout(self.current_cwa_container)
        cwal.setContentsMargins(0, 0, 0, 0)
        cwal.setSpacing(6)

        right_lbl = QLabel("Current CWA:")
        right_lbl.setObjectName("TopRightLabel")

        self.current_cwa_input = QLineEdit("")
        self.current_cwa_input.setObjectName("TopCWAInput")
        self.current_cwa_input.setFixedWidth(70)
        self.current_cwa_input.setValidator(QDoubleValidator(0.0, 100.0, 2, self))

        cwal.addWidget(right_lbl)
        cwal.addWidget(self.current_cwa_input)

        tl.addWidget(self.current_cwa_container)
        rl.addWidget(topbar)

        # Pages stack
        self.stack = QStackedWidget()
        rl.addWidget(self.stack, 1)

        # Pages
        self.cwa_page = CWAEstimatorPage()
        self.cwa_page.set_current_cwa_getter(
            lambda: (self.current_cwa_input.text().strip() if self.current_cwa_input else "0") or "0"
        )
        self.current_cwa_input.textChanged.connect(self.cwa_page.recompute)

        self.stack.addWidget(self.cwa_page)          # 0
        self.stack.addWidget(CGPACalculatorPage())   # 1
        self.stack.addWidget(SettingsPage())         # 2
        self.stack.addWidget(AboutPage())            # 3

        shell_layout.addWidget(sidebar)
        shell_layout.addWidget(right, 1)

        root_layout.addWidget(shell, 1)
        self.setStyleSheet(APP_QSS)

    def _apply_nav(self, idx: int):
        assert self.stack is not None
        self.stack.setCurrentIndex(idx)

        titles = ["CWA Estimator", "CGPA Calculator", "Settings", "About"]
        if self.page_title:
            self.page_title.setText(titles[idx])

        if self.current_cwa_container:
            self.current_cwa_container.setVisible(idx == 0)

        if idx == 0 and self.cwa_page:
            self.cwa_page.recompute()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setFont(QFont("Arial", 10))
    w = MainWindow()
    w.show()
    sys.exit(app.exec())