# Form implementation generated from reading ui file 'ui/main_window.ui'
#
# Created by: PyQt6 UI code generator 6.6.0
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt6 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(781, 591)
        self.centralwidget = QtWidgets.QWidget(parent=MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setSizeConstraint(QtWidgets.QLayout.SizeConstraint.SetDefaultConstraint)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout()
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.toolTab = QtWidgets.QTabWidget(parent=self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.toolTab.sizePolicy().hasHeightForWidth())
        self.toolTab.setSizePolicy(sizePolicy)
        self.toolTab.setTabPosition(QtWidgets.QTabWidget.TabPosition.North)
        self.toolTab.setDocumentMode(False)
        self.toolTab.setObjectName("toolTab")
        self.tabSingle = QtWidgets.QWidget()
        self.tabSingle.setObjectName("tabSingle")
        self.horizontalLayoutWidget_2 = QtWidgets.QWidget(parent=self.tabSingle)
        self.horizontalLayoutWidget_2.setGeometry(QtCore.QRect(10, 10, 351, 31))
        self.horizontalLayoutWidget_2.setObjectName("horizontalLayoutWidget_2")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.horizontalLayoutWidget_2)
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.urlLabel = QtWidgets.QLabel(parent=self.horizontalLayoutWidget_2)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Preferred, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.urlLabel.sizePolicy().hasHeightForWidth())
        self.urlLabel.setSizePolicy(sizePolicy)
        self.urlLabel.setObjectName("urlLabel")
        self.horizontalLayout_2.addWidget(self.urlLabel)
        self.singleUrlInput = QtWidgets.QLineEdit(parent=self.horizontalLayoutWidget_2)
        self.singleUrlInput.setObjectName("singleUrlInput")
        self.horizontalLayout_2.addWidget(self.singleUrlInput)
        self.metaData = QtWidgets.QGroupBox(parent=self.tabSingle)
        self.metaData.setGeometry(QtCore.QRect(10, 50, 351, 101))
        self.metaData.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.metaData.setObjectName("metaData")
        self.gridLayoutWidget = QtWidgets.QWidget(parent=self.metaData)
        self.gridLayoutWidget.setGeometry(QtCore.QRect(10, 30, 331, 61))
        self.gridLayoutWidget.setObjectName("gridLayoutWidget")
        self.gridLayout = QtWidgets.QGridLayout(self.gridLayoutWidget)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setObjectName("gridLayout")
        self.singleArtistLabel = QtWidgets.QLabel(parent=self.gridLayoutWidget)
        self.singleArtistLabel.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight|QtCore.Qt.AlignmentFlag.AlignTrailing|QtCore.Qt.AlignmentFlag.AlignVCenter)
        self.singleArtistLabel.setObjectName("singleArtistLabel")
        self.gridLayout.addWidget(self.singleArtistLabel, 1, 0, 1, 1)
        self.singleSongNameLabel = QtWidgets.QLabel(parent=self.gridLayoutWidget)
        self.singleSongNameLabel.setObjectName("singleSongNameLabel")
        self.gridLayout.addWidget(self.singleSongNameLabel, 0, 0, 1, 1)
        self.singleArtistInput = QtWidgets.QLineEdit(parent=self.gridLayoutWidget)
        self.singleArtistInput.setObjectName("singleArtistInput")
        self.gridLayout.addWidget(self.singleArtistInput, 1, 1, 1, 1)
        self.singleSongNameInput = QtWidgets.QLineEdit(parent=self.gridLayoutWidget)
        self.singleSongNameInput.setObjectName("singleSongNameInput")
        self.gridLayout.addWidget(self.singleSongNameInput, 0, 1, 1, 1)
        self.toolTab.addTab(self.tabSingle, "")
        self.tabPlaylist = QtWidgets.QWidget()
        self.tabPlaylist.setAccessibleName("")
        self.tabPlaylist.setObjectName("tabPlaylist")
        self.toolTab.addTab(self.tabPlaylist, "")
        self.verticalLayout_2.addWidget(self.toolTab)
        spacerItem = QtWidgets.QSpacerItem(20, 10, QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Fixed)
        self.verticalLayout_2.addItem(spacerItem)
        self.downloadButton = QtWidgets.QPushButton(parent=self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.downloadButton.sizePolicy().hasHeightForWidth())
        self.downloadButton.setSizePolicy(sizePolicy)
        self.downloadButton.setMinimumSize(QtCore.QSize(100, 30))
        self.downloadButton.setObjectName("downloadButton")
        self.verticalLayout_2.addWidget(self.downloadButton, 0, QtCore.Qt.AlignmentFlag.AlignRight)
        self.horizontalLayout.addLayout(self.verticalLayout_2)
        spacerItem1 = QtWidgets.QSpacerItem(10, 20, QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Minimum)
        self.horizontalLayout.addItem(spacerItem1)
        self.debugConsole = QtWidgets.QTextBrowser(parent=self.centralwidget)
        self.debugConsole.setObjectName("debugConsole")
        self.horizontalLayout.addWidget(self.debugConsole)
        self.verticalLayout.addLayout(self.horizontalLayout)
        spacerItem2 = QtWidgets.QSpacerItem(20, 8, QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Fixed)
        self.verticalLayout.addItem(spacerItem2)
        self.progressBar = QtWidgets.QProgressBar(parent=self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.progressBar.sizePolicy().hasHeightForWidth())
        self.progressBar.setSizePolicy(sizePolicy)
        self.progressBar.setMaximumSize(QtCore.QSize(16777215, 1000000))
        self.progressBar.setBaseSize(QtCore.QSize(0, 0))
        self.progressBar.setProperty("value", 0)
        self.progressBar.setTextVisible(False)
        self.progressBar.setInvertedAppearance(False)
        self.progressBar.setObjectName("progressBar")
        self.verticalLayout.addWidget(self.progressBar)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(parent=MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 781, 21))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(parent=MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        self.toolTab.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
        MainWindow.setTabOrder(self.singleUrlInput, self.singleSongNameInput)
        MainWindow.setTabOrder(self.singleSongNameInput, self.singleArtistInput)
        MainWindow.setTabOrder(self.singleArtistInput, self.debugConsole)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.urlLabel.setText(_translate("MainWindow", "URL"))
        self.metaData.setTitle(_translate("MainWindow", "Metadata"))
        self.singleArtistLabel.setText(_translate("MainWindow", "Artist:"))
        self.singleSongNameLabel.setText(_translate("MainWindow", "Song Name:"))
        self.toolTab.setTabText(self.toolTab.indexOf(self.tabSingle), _translate("MainWindow", "Single"))
        self.toolTab.setTabText(self.toolTab.indexOf(self.tabPlaylist), _translate("MainWindow", "Playlist"))
        self.downloadButton.setText(_translate("MainWindow", "Download"))
