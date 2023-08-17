# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/gerrit/Sites/lfb/qgis-gnavs-plugin/gnavs/gui/navigate/target.ui'
#
# Created by: PyQt5 UI code generator 5.15.6
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(1044, 843)
        self.gridLayout = QtWidgets.QGridLayout(Form)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setVerticalSpacing(15)
        self.gridLayout.setObjectName("gridLayout")
        self.lfbTargetGroup = QtWidgets.QGroupBox(Form)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lfbTargetGroup.sizePolicy().hasHeightForWidth())
        self.lfbTargetGroup.setSizePolicy(sizePolicy)
        self.lfbTargetGroup.setStyleSheet("border:none;\n"
"background-color:#ddd;")
        self.lfbTargetGroup.setTitle("")
        self.lfbTargetGroup.setCheckable(False)
        self.lfbTargetGroup.setChecked(False)
        self.lfbTargetGroup.setObjectName("lfbTargetGroup")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.lfbTargetGroup)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.verticalLayout_5 = QtWidgets.QVBoxLayout()
        self.verticalLayout_5.setContentsMargins(-1, 0, -1, -1)
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        self.lfbAttributeTableWidget = QtWidgets.QTableWidget(self.lfbTargetGroup)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lfbAttributeTableWidget.sizePolicy().hasHeightForWidth())
        self.lfbAttributeTableWidget.setSizePolicy(sizePolicy)
        self.lfbAttributeTableWidget.setMinimumSize(QtCore.QSize(0, 60))
        self.lfbAttributeTableWidget.setMaximumSize(QtCore.QSize(16777215, 50))
        self.lfbAttributeTableWidget.setStyleSheet("")
        self.lfbAttributeTableWidget.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.lfbAttributeTableWidget.setTabKeyNavigation(False)
        self.lfbAttributeTableWidget.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection)
        self.lfbAttributeTableWidget.setWordWrap(False)
        self.lfbAttributeTableWidget.setCornerButtonEnabled(False)
        self.lfbAttributeTableWidget.setRowCount(1)
        self.lfbAttributeTableWidget.setObjectName("lfbAttributeTableWidget")
        self.lfbAttributeTableWidget.setColumnCount(0)
        self.lfbAttributeTableWidget.verticalHeader().setVisible(False)
        self.verticalLayout_5.addWidget(self.lfbAttributeTableWidget)
        self.verticalLayout.addLayout(self.verticalLayout_5)
        self.lfbTargetDetailsWidget = QtWidgets.QWidget(self.lfbTargetGroup)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lfbTargetDetailsWidget.sizePolicy().hasHeightForWidth())
        self.lfbTargetDetailsWidget.setSizePolicy(sizePolicy)
        self.lfbTargetDetailsWidget.setObjectName("lfbTargetDetailsWidget")
        self.lfbTargetDetails = QtWidgets.QHBoxLayout(self.lfbTargetDetailsWidget)
        self.lfbTargetDetails.setContentsMargins(0, 10, 10, 10)
        self.lfbTargetDetails.setObjectName("lfbTargetDetails")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout()
        self.verticalLayout_2.setContentsMargins(0, 0, 0, -1)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.label_3 = QtWidgets.QLabel(self.lfbTargetDetailsWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_3.sizePolicy().hasHeightForWidth())
        self.label_3.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(8)
        self.label_3.setFont(font)
        self.label_3.setObjectName("label_3")
        self.verticalLayout_2.addWidget(self.label_3)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setContentsMargins(-1, 0, -1, -1)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.lfbDistanceEdit = QtWidgets.QLabel(self.lfbTargetDetailsWidget)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.lfbDistanceEdit.setFont(font)
        self.lfbDistanceEdit.setObjectName("lfbDistanceEdit")
        self.horizontalLayout_2.addWidget(self.lfbDistanceEdit)
        self.lfbDistanceUnit = QtWidgets.QLabel(self.lfbTargetDetailsWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lfbDistanceUnit.sizePolicy().hasHeightForWidth())
        self.lfbDistanceUnit.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.lfbDistanceUnit.setFont(font)
        self.lfbDistanceUnit.setObjectName("lfbDistanceUnit")
        self.horizontalLayout_2.addWidget(self.lfbDistanceUnit)
        spacerItem = QtWidgets.QSpacerItem(40, 10, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem)
        self.verticalLayout_2.addLayout(self.horizontalLayout_2)
        self.lfbTargetDetails.addLayout(self.verticalLayout_2)
        self.verticalLayout_4 = QtWidgets.QVBoxLayout()
        self.verticalLayout_4.setContentsMargins(0, -1, -1, -1)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.label_4 = QtWidgets.QLabel(self.lfbTargetDetailsWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_4.sizePolicy().hasHeightForWidth())
        self.label_4.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(8)
        self.label_4.setFont(font)
        self.label_4.setObjectName("label_4")
        self.verticalLayout_4.addWidget(self.label_4)
        self.lfbBearingLayout = QtWidgets.QWidget(self.lfbTargetDetailsWidget)
        self.lfbBearingLayout.setObjectName("lfbBearingLayout")
        self.lfbBearingeLayout = QtWidgets.QHBoxLayout(self.lfbBearingLayout)
        self.lfbBearingeLayout.setContentsMargins(5, -1, 5, 5)
        self.lfbBearingeLayout.setObjectName("lfbBearingeLayout")
        self.lfbBearingEdit = QtWidgets.QLabel(self.lfbBearingLayout)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.lfbBearingEdit.setFont(font)
        self.lfbBearingEdit.setText("")
        self.lfbBearingEdit.setObjectName("lfbBearingEdit")
        self.lfbBearingeLayout.addWidget(self.lfbBearingEdit)
        self.lfbBearingUnit = QtWidgets.QLabel(self.lfbBearingLayout)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lfbBearingUnit.sizePolicy().hasHeightForWidth())
        self.lfbBearingUnit.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.lfbBearingUnit.setFont(font)
        self.lfbBearingUnit.setObjectName("lfbBearingUnit")
        self.lfbBearingeLayout.addWidget(self.lfbBearingUnit)
        self.verticalLayout_4.addWidget(self.lfbBearingLayout)
        self.lfbTargetDetails.addLayout(self.verticalLayout_4)
        self.verticalLayout.addWidget(self.lfbTargetDetailsWidget)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setContentsMargins(5, 5, 5, 5)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.lfbTargetRemoveBtn = QtWidgets.QPushButton(self.lfbTargetGroup)
        font = QtGui.QFont()
        font.setPointSize(6)
        self.lfbTargetRemoveBtn.setFont(font)
        self.lfbTargetRemoveBtn.setStyleSheet("background-color: transparent;\n"
"color: red;\n"
"border: none;")
        self.lfbTargetRemoveBtn.setObjectName("lfbTargetRemoveBtn")
        self.horizontalLayout_3.addWidget(self.lfbTargetRemoveBtn)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem1)
        self.lfbTargetFokusBtn = QtWidgets.QPushButton(self.lfbTargetGroup)
        font = QtGui.QFont()
        font.setPointSize(6)
        font.setBold(True)
        font.setWeight(75)
        self.lfbTargetFokusBtn.setFont(font)
        self.lfbTargetFokusBtn.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.lfbTargetFokusBtn.setStyleSheet("QPushButton{\n"
"    border: 2px solid #333;\n"
"    color: #555;\n"
"    padding: 5px;\n"
"}\n"
"QPushButton:hover{\n"
"    background-color: yellow;\n"
"}\n"
"QPushButton:enabled{\n"
"    border:  2px solid green;\n"
"    background-color: green;\n"
"    color: #fff;\n"
"}")
        self.lfbTargetFokusBtn.setObjectName("lfbTargetFokusBtn")
        self.horizontalLayout_3.addWidget(self.lfbTargetFokusBtn)
        self.verticalLayout.addLayout(self.horizontalLayout_3)
        self.gridLayout.addWidget(self.lfbTargetGroup, 0, 0, 1, 1)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.label_3.setText(_translate("Form", "Entfernung"))
        self.lfbDistanceEdit.setText(_translate("Form", " "))
        self.lfbDistanceUnit.setText(_translate("Form", "m"))
        self.label_4.setText(_translate("Form", "Azimut"))
        self.lfbBearingUnit.setText(_translate("Form", "gon"))
        self.lfbTargetRemoveBtn.setText(_translate("Form", "ENTFERNEN"))
        self.lfbTargetFokusBtn.setText(_translate("Form", "FOKUS"))
