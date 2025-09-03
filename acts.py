# pylint: disable=E0611, C0103, R0902, W1514, E1101, W0201, R1732, W0613, R0904
"""
UtilityAI 애플리케이션

이 스크립트는 Tennis Ball Data Annotation을 위해 제작됐습니다. 
PyQt5를 사용하여 GUI 애플리케이션을 생성합니다. 
주요 클래스는 MainWindow와 FormWidget으로, 메인 윈도우와 폼 위젯을 각각 정의합니다.

Classes:
    MainWindow: 애플리케이션의 메인 윈도우를 정의하고 UI를 초기화합니다.
    FormWidget: 폼 위젯을 정의하고 UI를 초기화합니다.
"""

import os.path
import sys
import urllib.request
import re
from ast import literal_eval

import resources_rc

# import cv2
import numpy as np
from PyQt5.QtCore import QPoint, QRectF, QSize, Qt
from PyQt5.QtGui import (
    QColor,
    QIcon,
    QKeyEvent,
    QMouseEvent,
    QPainter,
    QPaintEvent,
    QPen,
    QPixmap,
    QResizeEvent,
    QKeySequence
)
from PyQt5.QtWidgets import (
    QAction,
    QApplication,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QListWidgetItem,
    QMainWindow,
    QToolBar,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

__appname__ = "UtilityAI"

class MainWindow(QMainWindow):
    """메인 윈도우 클래스.

    이 클래스는 애플리케이션의 메인 윈도우를 초기화하고 UI를 설정합니다.
    """

    def __init__(self):
        """초기화 메서드.

        메인 윈도우를 초기화하고 UI를 설정합니다.
        """
        super().__init__()
        self.initUI()

    def initUI(self):
        """UI 초기화 메서드.

        윈도우 타이틀, 아이콘, 상태바, 툴바 및 중앙 위젯을 설정합니다.
        """
        self.setWindowTitle(__appname__)
        self.setWindowIcon(QIcon(":logo"))

        self.statusBar()
        self.statusBar().showMessage("Ready")

        self.form_widget = FormWidget(self)
        self.setCentralWidget(self.form_widget)

        self.setGeometry(100, 100, 500, 400)

        # --- left toolbar ---
        self.leftToolbar = QToolBar("Main Toolbar", self)
        self.leftToolbar.setIconSize(QSize(100, 60))

        openClipDirAction = self.initAction(":open", "Open Image Directory", "Ctrl+O")
        openStrokeAction = self.initAction(":open", "Open KeyPoint Directory", "Ctrl+K")
        prevAction = self.initAction(":prev", "Prev Image", QKeySequence(Qt.Key_Left))
        nextAction = self.initAction(":next", "Next Image", QKeySequence(Qt.Key_Right))
        saveAction = self.initAction(":save", "Save Image", QKeySequence(Qt.Key_Down))
        exceptAction = self.initAction(":except", "Except Image", "X")
        initStrokeAction = self.initAction(":except", "Init Point", "I")
        setPrevStrokeAction = self.initAction(":except", "Set previous stroke", "V")

        self.leftToolbar.addAction(openClipDirAction)
        self.leftToolbar.addAction(openStrokeAction)
        self.leftToolbar.addAction(prevAction)
        self.leftToolbar.addAction(nextAction)
        self.leftToolbar.addAction(saveAction)
        self.leftToolbar.addAction(exceptAction)
        self.leftToolbar.addAction(initStrokeAction)
        self.leftToolbar.addAction(setPrevStrokeAction)

        self.addToolBar(Qt.LeftToolBarArea, self.leftToolbar)

        # --- right toolbar ---
        self.rightToolbar = QToolBar("Stroke Toolbar", self)
        self.rightToolbar.setIconSize(QSize(100, 60))
        
        self.rightButtons = {}
        for index, _ in enumerate(self.form_widget.StrokeType):
            toolButton = QToolButton(self)
            toolButton.setCheckable(True)
            toolButton.setObjectName(self.form_widget.StrokeType[index])
            toolButton.setText(f"{self.form_widget.StrokeType[index]}") 
            self.rightToolbar.addWidget(toolButton)
            self.rightButtons[index] = toolButton
        
        self.addToolBar(Qt.RightToolBarArea, self.rightToolbar)

        # --- event connect ---
        openClipDirAction.triggered.connect(self.form_widget.openDirClipClicked)
        openStrokeAction.triggered.connect(self.form_widget.openDirStrokeClicked)
        prevAction.triggered.connect(self.filePrevEvent)
        nextAction.triggered.connect(self.fileNextEvent)
        saveAction.triggered.connect(self.StrokeSaveEvent)
        exceptAction.triggered.connect(self.exceptClipEvent)
        initStrokeAction.triggered.connect(self.initStrokeEvent)
        # setPrevStrokeAction.triggered.connect(self.form_widget.setPreviousStrokeEvent)

    def initAction(self, icon: str, toolTip: str, shortcut: str) -> QAction:
        action = QAction(QIcon(icon), toolTip, self)
        action.setShortcut(shortcut)
        action.setStatusTip(toolTip)
        return action

    # --- event list ---
    def keyPressEvent(self, event: QKeyEvent) -> None:
        self.form_widget.keyPressEvent(event)

        stroke_type = self.form_widget.stroke
        for btn in self.rightButtons.values():
            btn.setChecked(False)
        self.rightButtons[stroke_type].setChecked(True)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        self.form_widget.mousePressEvent(event)

    def fileNextEvent(self):
        self.form_widget.fileNextEvent()
        
        stroke_type = self.form_widget.stroke
        for btn in self.rightButtons.values():
            btn.setChecked(False)
        self.rightButtons[stroke_type].setChecked(True)

    def filePrevEvent(self):
        for btn in self.rightButtons.values():
            btn.setChecked(False)
        self.form_widget.filePrevEvent()
    
    def StrokeSaveEvent(self):
        for btn in self.rightButtons.values():
            btn.setChecked(False)
        self.form_widget.StrokeSaveEvent()
    
    def exceptClipEvent(self):
        self.form_widget.exceptClipEvent()
    
    def initStrokeEvent(self):
        self.form_widget.initStrokeEvent()
    
    def setPreviousStrokeEvent(self):
        self.form_widget.setPreviousStrokeEvent()



class FormWidget(QWidget):

    storkeDirpath: str
    txtFile: str

    def __init__(self, parent: QWidget):
        super().__init__()
        self.mainWindow = parent
        self.imageViewerWidget = QLabel()
        self.imageViewerWidget.mousePressEvent = self.mousePressEvent

        imageViewer = QHBoxLayout()
        imageViewer.addWidget(self.imageViewerWidget)

        mainBox = QVBoxLayout()
        mainBox.addLayout(imageViewer)

        self.setLayout(mainBox)

        self.stroke = 0
        self.currIndex = 0
        self.resize(1280, 720)      # w, h

        self.initStatic()
        self.openDirClipClicked()
        self.openDirStrokeClicked()
        self.checkExceptFile()

    def openDirClipClicked(self) -> None:
        self.clipDirpath = QFileDialog.getExistingDirectory(
            self, self.tr("Open Data files"), os.getcwd(), QFileDialog.ShowDirsOnly
        )  #'./data/clips'

        self.allClipList = self.scanAllItems(self.clipDirpath)

        self.mClipList = {
            i: item for i, item in enumerate(list(self.allClipList.keys()))
        }
        self.len_ClipList = len(self.mClipList)


    def openDirStrokeClicked(self) -> None:
        self.storkeDirpath = QFileDialog.getExistingDirectory(
            self, self.tr("Open Data files"), os.getcwd(), QFileDialog.ShowDirsOnly
        )  #'./data/labels'

        self.resume = False
        allTxtList = self.scanAllItems(self.storkeDirpath)
        if self.resume and len(allTxtList) != 0:
            latestItem = os.path.basename(allTxtList[-2]).replace("txt", "jpg")
            resumeImg = os.path.join(self.imageDirpath, latestItem)
            resumeImg = str(os.path.abspath(resumeImg))

            resumeIndex = self.mImgList.index(resumeImg)
            print(f"Resume.. Index : {resumeIndex} Image : {latestItem}")
        else:
            resumeIndex = 0
            print(f"No resume.. Index : {resumeIndex} Image : {resumeIndex}")

        self.imagesOpenEvent(resumeIndex)


    def scanAllItems(self, folderPath: str) -> dict:

        def natural_key(s):
            return [int(text) if text.isdigit() else text.lower()
                    for text in re.split(r'(\d+)', s)]

        item = {}
        for root, dirs, files in sorted(os.walk(folderPath), key=lambda x: natural_key(x[0])):
            for file in sorted(files, key=natural_key):
                if ".txt" in file or ".jpg" in file:
                    relativePath = os.path.join(root, file)
                    path = str(os.path.abspath(relativePath))
                    
                    if root not in list(item.keys()):
                        item[root] = [file]
                    else:
                        item[root].append(file)
        return item

    def filePrevEvent(self) -> None:
        self.StrokeSaveEvent()
        self.imagesOpenEvent(-1)

    def fileNextEvent(self) -> None:
        self.StrokeSaveEvent()
        self.imagesOpenEvent(1)

    def StrokeSaveEvent(self) -> None:

        with open(os.path.join(self.storkeDirpath, self.txtFile), "w") as f:
            exportData = f'{self.stroke} \n'
            f.write(exportData)

        print(f'{self.txtFile}: keypad({self.keypad}) class {self.stroke}, {self.StrokeType[int(self.stroke)]} ({self.currIndex}/{self.len_ClipList})')


    def exceptClipEvent(self) -> None:
        self.checkExceptFile()

        with open(self.exceptFile, "r") as f:
            items = f.read()

        if self.txtFile in items:
            print(f"Duplic... {self.txtFile}")
        else:
            with open(self.exceptFile, "a") as f:
                f.write(f"{self.txtFile}\n")
            print(f"Except... {self.txtFile}")

    def initStrokeEvent(self) -> None:
        self.initStroke()
        self.refreshPaint()

    def setCurrIndex(self, index: int) -> None:
        if self.currIndex + index >= len(self.mClipList) or self.currIndex + index <= 0:
            print(f"Check the index {self.currIndex + index}")
        else:
            self.currIndex = self.currIndex + index

    def imagesOpenEvent(self, index: int) -> None:
        self.initStroke()
        self.setCurrIndex(index)
        self.ClipPath = self.mClipList[self.currIndex]

        oriFPS = 30
        setFPS = 5
        self.sampledImagePathes = [os.path.join(self.ClipPath, imgName) 
                                   for i, imgName
                                   in enumerate(self.allClipList[self.ClipPath])
                                   if i % (oriFPS // setFPS) == 0]
        self.setImage()
        self.txtOpenEvent()
        self.refreshPaint()

        self.mainWindow.setWindowTitle(__appname__ + " / " + self.ClipPath)

    def setImage(self) -> QPixmap:
        max_per_row = 10
        img_max_w, img_max_h = 30, 50
        padding = 2

        pixmaps = []
        for imgPath in self.sampledImagePathes:
            pm = QPixmap(imgPath)
            pm = pm.scaled(img_max_w, img_max_h, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            pixmaps.append(pm)

        num_images = len(pixmaps)
        rows = (num_images + max_per_row - 1) // max_per_row
        cols = min(max_per_row, num_images)

        canvas_width = cols * img_max_w + (cols - 1) * padding
        canvas_height = rows * img_max_h + (rows - 1) * padding

        canvas = QPixmap(canvas_width, canvas_height)
        canvas.fill(QColor(200, 200, 255))

        painter = QPainter(canvas)
        for idx, p in enumerate(pixmaps):
            row = idx // max_per_row
            col = idx % max_per_row
            x = col * (img_max_w + padding)
            y = row * (img_max_h + padding)
            painter.drawPixmap(x, y, p)
        painter.end()

        self.pixmap = canvas

        resizeWidth, resizeHeight = self.scaledImageSize()
        self.pixmap = self.pixmap.scaled(resizeWidth, resizeHeight, Qt.KeepAspectRatio, Qt.SmoothTransformation)

        self.oriWidth, self.oriHeight = canvas.width(), canvas.height()
        self.resizeWidth, self.resizeHeight = self.pixmap.width(), self.pixmap.height()
        self.sizeRatio = self.resizeWidth / self.oriWidth
        self.reverseRatio = self.oriWidth / self.resizeWidth

        return self.pixmap


    def txtOpenEvent(self) -> None:

        if self.storkeDirpath is None:
            return

        clipFile = os.path.basename(self.ClipPath)
        txtFile = f'{clipFile}.txt'
        
        if txtFile in os.listdir(self.storkeDirpath):
            txtPath = os.path.join(self.storkeDirpath, txtFile)
            with open(txtPath, 'r') as f:
                lines = f.readlines()
                for index, line in enumerate(lines):
                    if index != 0:
                        continue
                    line_ = list(map(float, line.strip().split(" ")))
                    self.stroke = int(line_[0])
        else:
            txtPath = os.path.join(self.storkeDirpath, txtFile)
            with open(txtPath, "w") as f:
                pass

            self.initStroke()

        self.txtFile = txtFile

    def checkExceptFile(self) -> None:
        self.exceptFile = os.path.join(self.storkeDirpath, "except.txt")
        if not os.path.exists(self.exceptFile):
            with open(self.exceptFile, "w") as f:
                f.write("")

    def initStroke(self) -> None:
        self.stroke = 0
        self.keypad = '1'

    def initStatic(self) -> None:

        self.StrokeType = [
            "natural (1)",              # keypad: 1, label: 0
            "far-serve (Q)",            # keypad: Q, label: 1
            "far-forehands (W)",        # keypad: W, label: 2
            "far-backhands (E)",        # keypad: E, label: 3
            "closely-serve (A)",        # keypad: A, label: 4
            "closely-forehands (S)",    # keypad: S, label: 5
            "closely-backhands (D)",    # keypad: D, label: 6
        ]
        
        self.storkeDirpath = ""
        self.txtFile = ""

    def paintEvent(self, event: QPaintEvent) -> None:

        if not self._paintFlag:
            return

        pixmap = self.setImage()
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing, True)

        x_offset = 0
        for idx, width in enumerate(getattr(self, 'image_widths', [])):

            for point in self.points:
                if point_belongs_to_image(point, idx):
                    qp = QPoint(point[1] + x_offset, point[2])
                    painter.setPen(QPen(Qt.red, 3))
                    painter.drawEllipse(qp, 10, 10)

            x_offset += int(img_width * self.sizeRatio + 10 * self.sizeRatio)

        painter.end()

        self.imageViewerWidget.setPixmap(pixmap)
        self.imageViewerWidget.update()

    def refreshPaint(self) -> None:
        """페인트 새로 고침.

        페인트 플래그를 설정하고 페인트 이벤트를 호출합니다.
        """
        self._paintFlag = True
        self.paintEvent(None)
        self._paintFlag = False

    def scaledImageSize(self) -> tuple[int, int]:
        w = self.frameGeometry().width() - 44
        h = self.frameGeometry().height() - 200
        return w, h

    def keyPressEvent(self, event: QKeyEvent) -> None:
        if event.key() == Qt.Key_1:
            self.stroke = 0
            self.keypad = '1'
        if event.key() == Qt.Key_Q:
            self.stroke = 1
            self.keypad = 'Q'
        if event.key() == Qt.Key_W:
            self.stroke = 2
            self.keypad = 'W'
        if event.key() == Qt.Key_E:
            self.stroke = 3
            self.keypad = 'E'
        if event.key() == Qt.Key_A:
            self.stroke = 4
            self.keypad = 'A'
        if event.key() == Qt.Key_S:
            self.stroke = 5
            self.keypad = 'S'
        if event.key() == Qt.Key_D:
            self.stroke = 6
            self.keypad = 'D'

    def resizeEvent(self, event: QResizeEvent) -> None:
        self.refreshPaint()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    windowExample = MainWindow()
    windowExample.show()
    sys.exit(app.exec_())
