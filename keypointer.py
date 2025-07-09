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

        self.toolbarBox = QToolBar(self)
        self.form_widget = FormWidget(self)
        self.setCentralWidget(self.form_widget)

        self.setGeometry(100, 100, 500, 400)

        openImageAction = self.initAction(":open", "Open Image Directory", "Ctrl+O")
        openKeypointAction = self.initAction(
            ":open", "Open KeyPoint Directory", "Ctrl+K"
        )
        prevAction = self.initAction(":prev", "Prev Image", "A")
        nextAction = self.initAction(":next", "Next Image", "D")
        saveAction = self.initAction(":save", "Save Image", "S")
        exceptAction = self.initAction(":except", "Except Image", "E")
        initpointAction = self.initAction(":except", "Init Point", "X")

        setPrevPointAction = self.initAction(":except", "Set previous point", "V")

        # 왼쪽 메뉴 바부터 시작
        self.toolbarBox.addAction(openImageAction)
        self.toolbarBox.addAction(openKeypointAction)
        self.toolbarBox.addAction(prevAction)
        self.toolbarBox.addAction(nextAction)
        self.toolbarBox.addAction(saveAction)
        self.toolbarBox.addAction(exceptAction)
        self.toolbarBox.addAction(initpointAction)
        self.toolbarBox.addAction(setPrevPointAction)

        for index, _ in enumerate(self.form_widget.ballType):
            toolButton = QToolButton(self)
            toolButton.setCheckable(True)
            toolButton.setObjectName(self.form_widget.ballType[index])
            toolButton.setText(f"{self.form_widget.ballType[index]}({index + 1})")
            self.toolbarBox.addWidget(toolButton)

        self.toolbarBox.setIconSize(QSize(100, 60))
        self.addToolBar(Qt.LeftToolBarArea, self.toolbarBox)

        openImageAction.triggered.connect(self.form_widget.openDirClicked)
        openKeypointAction.triggered.connect(self.form_widget.openDirKeyPointClicked)
        prevAction.triggered.connect(self.form_widget.filePrevEvent)
        nextAction.triggered.connect(self.form_widget.fileNextEvent)
        saveAction.triggered.connect(self.form_widget.imageSaveEvent)
        exceptAction.triggered.connect(self.form_widget.exceptImageEvent)
        initpointAction.triggered.connect(self.form_widget.initPointEvent)
        setPrevPointAction.triggered.connect(self.form_widget.setPreviousPointEvent)

    def initAction(self, icon: str, toolTip: str, shortcut: str) -> QAction:
        """액션 초기화 메서드.

        주어진 아이콘, 이름, 단축키를 사용하여 액션을 초기화합니다.

        Args:
            icon_path (str): 액션 아이콘 경로.
            action_name (str): 액션 이름.
            shortcut (str): 액션 단축키.

        Returns:
            QAction: 초기화된 QAction 객체.
        """
        action = QAction(QIcon(icon), toolTip, self)
        action.setShortcut(shortcut)
        action.setStatusTip(toolTip)
        return action

    def keyPressEvent(self, event: QKeyEvent) -> None:
        """키보드 키를 눌렀을 때 발생하는 Event Handler.

        키보드 키를 눌렀을 때 발생하는 이벤트를 폼 위젯으로 전달합니다.

        Args:
            event (QKeyEvent): 키보드 키 이벤트.
        """
        self.form_widget.keyPressEvent(event)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        """마우스를 클릭했을 때 발생하는 Event Handler.

        마우스를 클릭했을 때 발생하는 이벤트를 폼 위젯으로 전달합니다.

        Args:
            event (QMouseEvent): 마우스 클릭 이벤트.
        """
        self.form_widget.mousePressEvent(event)


class FormWidget(QWidget):
    """폼 위젯 클래스.

    이 클래스는 애플리케이션의 주요 폼 위젯을 초기화하고 설정합니다.
    """

    keypointDirpath: str
    txtFile: str

    def __init__(self, parent: QWidget):
        """초기화 메서드.

        폼 위젯을 초기화하고 설정합니다.

        Args:
            parent (QWidget): 부모 위젯.
        """
        super().__init__()
        self.mainWindow = parent
        self.imageViewerWidget = QLabel()
        self.imageViewerWidget.mousePressEvent = self.mousePressEvent

        imageViewer = QHBoxLayout()
        imageViewer.addWidget(self.imageViewerWidget)

        mainBox = QVBoxLayout()
        mainBox.addLayout(imageViewer)

        self.setLayout(mainBox)

        self.currIndex = 0
        self.offsetX = 5
        self.offsetY = 10
        self.offsetPos = 1

        self.resume = False

        self.filtering_mul = 1

        self.prev_point = [0, -1, -1, -1, -1, -1, -1, 0]    # [class, cx, cy, obj_w, obj_h, px1, py1, vis]

        self.obj_h = 90
        self.obj_w = 120

        self.resize(1280, 720)      # w, h
        self.initStatic()

        self.openDirClicked()
        self.openDirKeyPointClicked()

        self.checkExceptFile()

    def openDirClicked(self) -> None:
        """디렉토리 열기 이벤트 핸들러.

        프레임 별 영상 이미지가 있는 디렉토리를 선택합니다.
        선택한 디렉토리의 최신 항목을 기준으로 작업을 재개합니다.
        """
        self.imageDirpath = QFileDialog.getExistingDirectory(
            self, self.tr("Open Data files"), os.getcwd(), QFileDialog.ShowDirsOnly
        )  #'./donghae_a/part1/images'

        self.allImgList = self.scanAllItems(self.imageDirpath)
        self.mImgList = [
            item for i, item in enumerate(self.allImgList) if i % self.filtering_mul == 0
        ]  # filtering
        self.len_ImgList = len(self.mImgList)


    def openDirKeyPointClicked(self) -> None:
        """키포인트 디렉토리 열기 이벤트 핸들러.

        키포인트 데이터 파일이 있는 디렉토리를 선택합니다.
        선택한 디렉토리의 최신 항목을 기준으로 작업을 재개합니다.
        """
        self.keypointDirpath = QFileDialog.getExistingDirectory(
            self, self.tr("Open Data files"), os.getcwd(), QFileDialog.ShowDirsOnly
        )  #'./donghae_a/part1/labels'

        # resume
        allTxtList = self.scanAllItems(self.keypointDirpath)
        if self.resume and len(allTxtList) != 0:
            latestItem = os.path.basename(allTxtList[-2]).replace("txt", "jpg")
            resumeImg = os.path.join(self.imageDirpath, latestItem)
            resumeImg = str(os.path.abspath(resumeImg))

            resumeIndex = self.mImgList.index(resumeImg)
            print(f"Resume.. Index : {resumeIndex} Image : {latestItem}")
        else:
            resumeIndex = 0
            print(f"No resume.. Index : {resumeIndex} Image : {resumeIndex}")

        self.imageOpenEvent(resumeIndex)


    def scanAllItems(self, folderPath: str) -> list:
        """지정된 폴더의 모든 항목을 스캔합니다.

        폴더 내의 모든 .txt 및 .jpg 파일 경로를 반환합니다.

        Args:
            folderPath (str): 폴더 경로.

        Returns:
            list: 폴더 내의 모든 .txt 및 .jpg 파일 경로 목록.
        """
        item = []
        for root, _, files in os.walk(folderPath):
            for file in sorted(files):
                if ".txt" in file or ".jpg" in file:
                    relativePath = os.path.join(root, file)
                    path = str(os.path.abspath(relativePath))
                    item.append(path)
        return item

    def filePrevEvent(self) -> None:
        """이전 파일 이벤트 핸들러.

        현재 이미지를 저장하고 이전 이미지를 엽니다.
        """
        self.imageSaveEvent()
        self.imageOpenEvent(-1)

    def fileNextEvent(self) -> None:
        """다음 파일 이벤트 핸들러.

        현재 이미지를 저장하고 다음 이미지를 엽니다.
        """
        self.imageSaveEvent()
        self.imageOpenEvent(1)

    def setPreviousPointEvent(self) -> None:
        self.points = self.prev_point
        self.refreshPaint()


    def imageSaveEvent(self) -> None:
        """이미지 저장 이벤트 핸들러.

        현재 키포인트 데이터를 파일에 저장합니다.
        """
        exportData = ""
        tempData = ""

        self.prev_point = self.points

        f = open(os.path.join(self.keypointDirpath, self.txtFile), "w")
        for line in self.points:
            # [class, cx, cy, obj_w, obj_h, px1, py1, vis]
            
            if line[1] == -1 or line[2] == -1:  # 공이 없는 경우 빈 파일 저장
                continue

            tempData = ""
            for index, item in enumerate(line):
                if index == 1:
                    item = round(item * self.reverseRatio / self.oriWidth, 4)   # cx
                if index == 2:
                    item = round(item * self.reverseRatio / self.oriHeight, 4)   # cy
                if index == 3:
                    item = round(item * self.reverseRatio / self.oriWidth, 4)   # objs_w
                if index == 4:
                    item = round(item * self.reverseRatio / self.oriHeight, 4)   # objs_h
                if index == 5:
                    item = round(item * self.reverseRatio / self.oriWidth, 4)   # px1
                if index == 6:
                    item = round(item * self.reverseRatio / self.oriHeight, 4)   # py1

                tempData = tempData + str(item) + " "
            exportData = exportData + tempData[0 : len(tempData) - 1] + "\n"
        f.write(exportData[0 : len(exportData) - 1])
        f.close()
        len_Done = len(os.listdir(self.keypointDirpath)) - 1

        print(
            f"Save... {self.txtFile} : \n"
            f"{self.points} -> {exportData} | {round(len_Done/self.len_ImgList*100, 2)}% | {len_Done} / {self.len_ImgList})"
        )

    def exceptImageEvent(self) -> None:
        """예외 이미지 이벤트 핸들러.

        현재 이미지 파일을 예외 파일 목록에 추가합니다.
        """
        self.checkExceptFile()

        with open(self.exceptFile, "r") as f:
            items = f.read()

        if self.txtFile in items:
            print(f"Duplic... {self.txtFile}")
        else:
            with open(self.exceptFile, "a") as f:
                f.write(f"{self.txtFile}\n")
            print(f"Except... {self.txtFile}")

    def initPointEvent(self) -> None:
        """키포인트 초기화 이벤트 핸들러.

        키포인트 데이터를 초기화하고 다시 그립니다.
        """
        self.initPoints()
        self.refreshPaint()

    def setCurrIndex(self, index: int) -> None:
        """현재 인덱스를 설정합니다.

        현재 인덱스를 주어진 값으로 설정합니다.

        Args:
            index (int): 새로운 인덱스 값.
        """
        if self.currIndex + index >= len(self.mImgList) or self.currIndex + index <= 0:
            print(f"Check the index {self.currIndex + index}")
        else:
            self.currIndex = self.currIndex + index

    def imageOpenEvent(self, index: int) -> None:
        """이미지 열기 이벤트 핸들러.

        주어진 인덱스에 따라 이미지를 엽니다.

        Args:
            index (int): 이미지 목록에서 이동할 인덱스.
        """
        self.initPoints()
        self.setCurrIndex(index)
        self.imgPath = self.mImgList[self.currIndex]
        self.oriPixmap = QPixmap(self.imgPath)
        self.setImage()
        self.txtOpenEvent()
        self.refreshPaint()

        self.mainWindow.setWindowTitle(__appname__ + " / " + self.imgPath)

    def setImage(self) -> QPixmap:
        """이미지를 설정합니다.

        이미지를 리사이즈하고 설정합니다.

        Returns:
            QPixmap: 설정된 QPixmap 객체.
        """
        self.pixmap = self.oriPixmap
        oriWidth, oriHeight = self.pixmap.width(), self.pixmap.height()
        resizeWidth, resizeHeight = self.scaledImageSize()

        if oriWidth >= oriHeight:
            self.sizeRatio = resizeWidth / oriWidth
            self.reverseRatio = oriWidth / resizeWidth
            self.pixmap = self.pixmap.scaledToWidth(resizeWidth)
        else:
            self.sizeRatio = resizeWidth / oriWidth
            self.reverseRatio = oriHeight / resizeHeight
            self.pixmap = self.pixmap.scaledToHeight(int(oriHeight * self.sizeRatio))

        self.oriWidth, self.oriHeight = oriWidth, oriHeight
        self.resizeWidth, self.resizeHeight = resizeWidth, resizeHeight

        return self.pixmap

    def txtOpenEvent(self) -> None:
        """텍스트 파일 열기 이벤트 핸들러.

        현재 이미지에 해당하는 텍스트 파일을 엽니다.
        """

        if self.keypointDirpath is None:
            return

        imageFile = os.path.basename(self.imgPath)
        txtFile = imageFile.replace(".jpg", ".txt")

        values = []
        if txtFile in os.listdir(self.keypointDirpath):
            txtPath = os.path.join(self.keypointDirpath, txtFile)

            f = open(txtPath)
            lines = f.readlines()
            for index, line in enumerate(lines):
                line_ = list(map(float, line.strip().split(" ")))
                line_new = [0, 0, 0, 0, 0, 0, 0, 0]    # [class, cx, cy, obj_w, obj_h, px1, py1, vis]
                line_new[0] = int(line_[0])
                line_new[1] = int(line_[1] * self.oriWidth * self.sizeRatio)
                line_new[2] = int(line_[2] * self.oriHeight * self.sizeRatio)
                line_new[3] = int(line_[3] * self.oriWidth * self.sizeRatio)
                line_new[4] = int(line_[4] * self.oriHeight * self.sizeRatio)
                line_new[5] = int(line_[5] * self.oriWidth * self.sizeRatio)
                line_new[6] = int(line_[6] * self.oriHeight * self.sizeRatio)
                line_new[7] = int(line_[7])
                values.append(line_new)
            f.close()
        else:
            txtPath = os.path.join(self.keypointDirpath, txtFile)
            with open(txtPath, "w") as f:
                pass

        if len(values) > 0:
            self.points = values
        else:
            self.initPoints()

        self.txtFile = txtFile

    def checkExceptFile(self) -> None:
        """예외 파일 확인.

        예외 파일이 존재하는지 확인하고, 존재하지 않으면 새로 생성합니다.
        """
        self.exceptFile = os.path.join(self.keypointDirpath, "except.txt")
        if not os.path.exists(self.exceptFile):
            with open(self.exceptFile, "w") as f:
                f.write("")

    def initPoints(self) -> None:
        """키포인트 초기화.

        키포인트 데이터를 초기화합니다.
        """
        self.points = []
        self.points.append([0, -1, -1, -1, -1, -1, -1, 0])  # [class, cx, cy, obj_w, obj_h, px1, py1, vis]
        self.keyPoint = 0

    def initStatic(self) -> None:
        """정적 데이터 초기화

        정적 데이터를 초기화합니다.
        """
        self.ballType = [
            "ball",  # 1
        ]

        self.personType = [
            "nose",  # 0
            "left-eye",  # 1
            "right-eye",  # 2
            "left-ear",  # 3
            "right-ear",  # 4
            "left-shoulder",  # 5
            "right-shoulder",  # 6
            "left-elbow",  # 7
            "right-elbow",  # 8
            "left-wrist",  # 9
            "right-wrist",  # 10
            "left-hip",  # 11
            "right-hip",  # 12
            "left-knee",  # 13
            "right-knee",  # 14
            "left-ankle",  # 15
            "right-ankle",  # 16
        ]

        self.keypointDirpath = ""
        self.txtFile = ""

    def paintEvent(self, event: QPaintEvent) -> None:
        """페인트 이벤트 핸들러.

        화면에 이미지를 그리고 키포인트를 표시합니다.

        Args:
            event (QPaintEvent): 페인트 이벤트.
        """
        if self._paintFlag:
            pixmap = self.setImage()
            self.painter = QPainter(pixmap)

            for _, value in enumerate(self.points):
                point = QPoint(value[1], value[2])

                if point != QPoint(0, 0):
                    self.painter.setPen(QPen(self.paintColor(value[7]), 3))
                    self.painter.setRenderHint(QPainter.Antialiasing, True)
                    self.painter.drawPoint(point)
                    pSize = 20
                    pt = QRectF(
                        point.x() - pSize / 2, point.y() - pSize / 2, pSize, pSize
                    )
                    self.painter.drawEllipse(pt)

            self.painter.end()
            self.imageViewerWidget.setPixmap(self.pixmap)
            self.imageViewerWidget.update()

    def paintColor(self, value: int) -> QColor:
        """페인트 색상 설정.

        키포인트의 가시성에 따라 페인트 색상을 설정합니다.

        Args:
            value (int): 키포인트의 가시성 값.

        Returns:
            QColor: 설정된 색상.
        """
        if value == 1:
            return Qt.blue
        return Qt.red

    def refreshPaint(self) -> None:
        """페인트 새로 고침.

        페인트 플래그를 설정하고 페인트 이벤트를 호출합니다.
        """
        self._paintFlag = True
        self.paintEvent(None)
        self._paintFlag = False

    def scaledImageSize(self) -> tuple[int, int]:
        """이미지 크기 조정.

        창 크기에 맞게 이미지를 조정합니다.

        Returns:
            tuple: 조정된 이미지의 너비와 높이.
        """
        w = self.frameGeometry().width() - 44
        h = self.frameGeometry().height() - 200
        return w, h

    def keyPressEvent(self, event: QKeyEvent) -> None:
        """키보드 키를 눌렀을 때 발생하는 이벤트 처리기.

        이 메서드는 키보드 키를 눌렀을 때 발생하는 이벤트를 폼 위젯으로 전달합니다.

        Args:
            event (QKeyEvent): 키보드 키 이벤트.
        """
        if event.key() == Qt.Key_1:
            self.keyPoint = 0

        elif event.key() == Qt.Key_I:
            self.points[self.keyPoint][2] -= self.offsetPos
        elif event.key() == Qt.Key_J:
            self.points[self.keyPoint][1] -= self.offsetPos
        elif event.key() == Qt.Key_K:
            self.points[self.keyPoint][2] += self.offsetPos
        elif event.key() == Qt.Key_L:
            self.points[self.keyPoint][1] += self.offsetPos

        self.refreshPaint()

    def mousePressEvent(self, event: QMouseEvent) -> None:
        """마우스를 클릭했을 때 발생하는 이벤트 처리기.

        이 메서드는 마우스를 클릭했을 때 발생하는 이벤트를 폼 위젯으로 전달합니다.

        Args:
            event (QMouseEvent): 마우스 클릭 이벤트.
        """

        # cx, cy
        self.points[self.keyPoint][1] = event.x() - int(
            self.offsetX * max(self.sizeRatio, self.reverseRatio)
        )
        self.points[self.keyPoint][2] = event.y() - int(
            self.offsetY * max(self.sizeRatio, self.reverseRatio)
        )

        # obj_w, obj_h
        self.points[self.keyPoint][3] = self.obj_w - int(
            self.offsetX * max(self.sizeRatio, self.reverseRatio)
        )
        self.points[self.keyPoint][4] = self.obj_h - int(
            self.offsetY * max(self.sizeRatio, self.reverseRatio)
        )

        # px1, py1
        self.points[self.keyPoint][5] = event.x() - int(
            self.offsetX * max(self.sizeRatio, self.reverseRatio)
        )
        self.points[self.keyPoint][6] = event.y() - int(
            self.offsetY * max(self.sizeRatio, self.reverseRatio)
        )

        # vis
        if event.button() == Qt.LeftButton:
            self.points[self.keyPoint][7] = 1
        elif event.button() == Qt.RightButton:
            self.points[self.keyPoint][7] = 0

        self.refreshPaint()

    def resizeEvent(self, event: QResizeEvent) -> None:
        """윈도우 크기 조정 이벤트 핸들러.

        윈도우 크기가 변경될 때 발생하는 이벤트를 처리합니다.

        Args:
            event (QResizeEvent): 리사이즈 이벤트.
        """
        self.refreshPaint()
        self.txtOpenEvent()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    windowExample = MainWindow()
    windowExample.show()
    sys.exit(app.exec_())
