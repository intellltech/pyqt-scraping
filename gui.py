# -*- coding: utf-8 -*-
"""
@name:XXX
@Date: 2019/11/9 14:58
@Version: v.0.0
"""

import sys
import icons
import re
import urllib.parse
from multiprocessing import Process, Manager, freeze_support
from datetime import datetime

from PyQt5.QtGui import QIcon, QStandardItemModel, QStandardItem
from PyQt5.QtCore import QThread, QDate
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, \
    QPushButton, QTextBrowser, QComboBox, QHBoxLayout, QVBoxLayout, QTableView, QCheckBox
from PyQt5 import QtWidgets, QtGui, QtCore

from scrapy.crawler import CrawlerProcess
from scraps.spiders.scraps import scrapspider
from scrapy.utils.project import get_project_settings

# import logging
# from twisted.internet import reactor
# from scrapy.crawler import CrawlerRunner
# from scrapy.utils.log import configure_logging

import urllib.robotparser

import scrapy.spiderloader
import scrapy.statscollectors
import scrapy.logformatter
import scrapy.dupefilters
import scrapy.squeues

import scrapy.extensions.spiderstate
import scrapy.extensions.corestats
import scrapy.extensions.telnet
import scrapy.extensions.logstats
import scrapy.extensions.memusage
import scrapy.extensions.memdebug
import scrapy.extensions.feedexport
import scrapy.extensions.closespider
import scrapy.extensions.debug
import scrapy.extensions.httpcache
import scrapy.extensions.statsmailer
import scrapy.extensions.throttle

import scrapy.core.scheduler
import scrapy.core.engine
import scrapy.core.scraper
import scrapy.core.spidermw
import scrapy.core.downloader

import scrapy.downloadermiddlewares.stats
import scrapy.downloadermiddlewares.httpcache
import scrapy.downloadermiddlewares.cookies
import scrapy.downloadermiddlewares.useragent
import scrapy.downloadermiddlewares.httpproxy
import scrapy.downloadermiddlewares.ajaxcrawl
# import scrapy.downloadermiddlewares.chunked
import scrapy.downloadermiddlewares.decompression
import scrapy.downloadermiddlewares.defaultheaders
import scrapy.downloadermiddlewares.downloadtimeout
import scrapy.downloadermiddlewares.httpauth
import scrapy.downloadermiddlewares.httpcompression
import scrapy.downloadermiddlewares.redirect
import scrapy.downloadermiddlewares.retry
import scrapy.downloadermiddlewares.robotstxt

import scrapy.spidermiddlewares.depth
import scrapy.spidermiddlewares.httperror
import scrapy.spidermiddlewares.offsite
import scrapy.spidermiddlewares.referer
import scrapy.spidermiddlewares.urllength

import scrapy.pipelines

import scrapy.core.downloader.handlers.http
import scrapy.core.downloader.handlers.datauri
import scrapy.core.downloader.handlers.file
import scrapy.core.downloader.handlers.s3
import scrapy.core.downloader.handlers.ftp
import scrapy.core.downloader.contextfactory

import gspread
from google.oauth2.service_account import Credentials

# credentials = Credentials.from_service_account_file('path of sheet.json',
#                                                     scopes=['https://www.googleapis.com/auth/spreadsheets',
#                                                             'https://www.googleapis.com/auth/drive'])
gc = gspread.authorize('credentials')

def isset(key, array, default = ""):
    if (key in array):
        return array[key]
    return default


class CrawlWindows(QWidget):

    def __init__(self):
        super(CrawlWindows, self).__init__()

        self.domain = 'www.realcommercial.com.au'
        self.targetUrl = f'https://{self.domain}'
        self.channelTexts = ["Buy", "Lease", "Sold", "Leased"]
        self.channelParams = ["for-sale", "for-lease", "sold", "leased"]
        self.propertyTexts = ["All types", "Shop && Retail", "Develpment Sites && Land",
                              "Hotel, Motel && Leisure", "Commmercial Farming && Rural",
                              "Warehouse, Factory && Industrial", "Offices", "Show Rooms && Large Format Retail",
                              "Medical && Consulting", "Other"]
        self.propertyParams = ["", "retail", "land-development", "hotel-motel-leisure", "commercial-farming", "industrial-warehouse", "offices",
                               "showrooms-bulky-goods", "medical-consulting", "other"]
        self.tenureTexts = [
            "Any", "Vacant possenssion", "Tenanted Investment"]
        self.tenureParams = ["", "vacant", "tenanted"]
        self.sliderValues = [['', 100000, 150000, 200000, 250000, 300000, 350000, 400000, 450000, 500000, 600000, 700000, 800000, 900000, 1000000,
                              1250000, 1500000, 2000000, 2500000, 3000000, 4000000, 5000000, 10000000, 25000000, 50000000, 100000000, ''],
                             ['', 5000, 10000, 15000, 20000, 25000, 30000, 35000, 40000, 45000, 50000, 60000, 70000, 80000, 90000, 100000,
                              150000, 200000, 250000, 500000, 1000000, 2000000, ''],
                             ['', 50, 100, 150, 200, 250, 300, 350, 400, 500, 750,
                              1000, 1500, 2000, 3000, 5000, 10000, 20000, ''],
                             ['', 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1500, 2000, 3000, 4000, 5000, 10000, 20000, 50000, 100000, 500000, '']]
        self.carSpaceTexts = ["Any", "1+", "2+", "3+", "4+", "5+", "6+", "7+",
                              "8+", "9+", "10+", "25+", "50+", "100+", "250+", "500+", "1,000+"]
        self.carSpaceValues = [0, 1, 2, 3, 4, 5, 6,
                               7, 8, 9, 10, 25, 50, 100, 250, 500, 1000]
        self.energyRatingTexts = ["Any", "1+", "2+", "3+", "4+", "5+", "6"]
        self.energyRatingValues = [0, 1, 2, 3, 4, 5, 6]
        self.channel = 0
        self.priceType = self.channel % 2
        self.database = {}
        self.datefrom = ""
        self.dateto = ""
        self.today = datetime.now().date()

        self.resize(600, 300)
        self.setWindowIcon(QIcon(':icons/favicon.ico'))
        self.setWindowTitle('scraps to scrape (http://scraps.toscrape.com)')

        self.p = None
        self.Q = Manager().Queue()
        self.log_thread = LogThread(self)
        self.setupUi()
        # self.ua_line = QLineEdit(self)
        # self.obey_combo = QComboBox(self)
        # self.obey_combo.addItems(['Yes', 'No'])
        # # self.save_location = QLineEdit(self)
        # self.log_browser = QTextBrowser(self)
        # self.tableview = QTableView(self)
        # self.tableview.setModel(QStandardItemModel())
        # self.crawl_button = QPushButton('Start crawl', self)
        # self.crawl_button.clicked.connect(lambda: self.crawl_slot(self.crawl_button))

        # self.h_layout = QHBoxLayout()
        # self.v_layout = QVBoxLayout()
        # self.h_layout.addWidget(QLabel('Input User-Agent:'))
        # self.h_layout.addWidget(self.ua_line)
        # # self.h_layout.addWidget(QLabel('Save path'))
        # # self.h_layout.addWidget(self.save_location)
        # self.h_layout.addWidget(QLabel('Robot protocol:'))
        # self.h_layout.addWidget(self.obey_combo)
        # self.v_layout.addLayout(self.h_layout)
        # self.v_layout.addWidget(QLabel('Output log box:'))
        # self.v_layout.addWidget(self.log_browser)
        # self.v_layout.addWidget(self.tableview)
        # self.v_layout.addWidget(self.crawl_button)
        # self.setLayout(self.v_layout)

    def crawl_slot(self, button):
        if button.text() == 'Start Search':
            # self.log_browser.clear()
            model = self.tableViewResult.model()
            model.removeRows(0, model.rowCount())
            self.database.clear()

            # for key, value in self.database.items():
            #     value['rowNum'] = -1

            self.btnSearch.setText('Stop Search')
            # ua = self.ua_line.text().strip()
            # is_obey = True if self.obey_combo.currentText() == 'Yes' else False
            # save_location = self.save_location.text().strip()
            self.datefrom = self.dateSelectFrom.date().toString("yyyy-MM-dd")
            self.dateto = self.dateSelectTo.date().toString("yyyy-MM-dd")

            # self.tableViewResult.model().setFilterKeyColumn(1)  # 1 corresponds to the second column
            # self.tableViewResult.model().setFilterMinimumDate(self.datefrom)

            self.p = Process(target=crawl_run, args=(
                self.Q, self.setupURL(), self.database, self.priceType))
            # self.log_browser.setText('The collection process is starting...')
            self.p.start()

            self.log_thread.start()
        else:
            self.btnSearch.setText('Start Search')
            self.p.terminate()

            self.log_thread.terminate()

    def setupUi(self):
        self.verticalLayout_30 = QtWidgets.QVBoxLayout(self)
        self.verticalLayout_30.setObjectName("verticalLayout_30")
        self.verticalLayout_28 = QtWidgets.QVBoxLayout()
        self.verticalLayout_28.setObjectName("verticalLayout_28")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        spacerItem = QtWidgets.QSpacerItem(
            40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem)
        self.label_6 = QtWidgets.QLabel(self)
        font = QtGui.QFont()
        font.setPointSize(18)
        font.setBold(True)
        font.setWeight(75)
        self.label_6.setFont(font)
        self.label_6.setAlignment(QtCore.Qt.AlignCenter)
        self.label_6.setObjectName("label_6")
        self.horizontalLayout_3.addWidget(self.label_6)
        spacerItem1 = QtWidgets.QSpacerItem(
            40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem1)
        self.btnShowFilter = QtWidgets.QPushButton(self)
        self.btnShowFilter.setObjectName("btnShowFilter")
        self.horizontalLayout_3.addWidget(self.btnShowFilter)
        self.verticalLayout_28.addLayout(self.horizontalLayout_3)
        self.scrollArea = QtWidgets.QScrollArea(self)
        self.scrollArea.setMinimumSize(QtCore.QSize(738, 443))
        self.scrollArea.setMaximumSize(QtCore.QSize(16777215, 443))
        font = QtGui.QFont()
        font.setPointSize(9)
        self.scrollArea.setFont(font)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName("scrollArea")
        self.scrollAreaWidgetContents = QtWidgets.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 959, 441))
        self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")
        self.verticalLayout_29 = QtWidgets.QVBoxLayout(
            self.scrollAreaWidgetContents)
        self.verticalLayout_29.setObjectName("verticalLayout_29")
        self.groupBox_5 = QtWidgets.QGroupBox(self.scrollAreaWidgetContents)
        font = QtGui.QFont()
        font.setPointSize(9)
        self.groupBox_5.setFont(font)
        self.groupBox_5.setTitle("")
        self.groupBox_5.setObjectName("groupBox_5")
        self.horizontalLayout_37 = QtWidgets.QHBoxLayout(self.groupBox_5)
        self.horizontalLayout_37.setObjectName("horizontalLayout_37")
        self.channels = []
        font = QtGui.QFont()
        font.setPointSize(13)
        font.setBold(True)
        font.setWeight(75)
        for x in range(4):
            self.channels.append(QtWidgets.QRadioButton(self.groupBox_5))
            self.channels[x].setFont(font)
            self.horizontalLayout_37.addWidget(self.channels[x])
        self.channels[0].setChecked(True)
        self.verticalLayout_29.addWidget(self.groupBox_5)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout()
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.label_7 = QtWidgets.QLabel(self.scrollAreaWidgetContents)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.label_7.setFont(font)
        self.label_7.setObjectName("label_7")
        self.verticalLayout_2.addWidget(self.label_7)
        self.surroundingCheckBox = QtWidgets.QCheckBox(
            self.scrollAreaWidgetContents)
        self.surroundingCheckBox.setObjectName("surroundingCheckBox")
        self.surroundingCheckBox.setChecked(True)
        self.verticalLayout_2.addWidget(self.surroundingCheckBox)

        self.lineEditAreaSearch = QtWidgets.QLineEdit(
            self.scrollAreaWidgetContents)
        font = QtGui.QFont()
        font.setPointSize(9)
        self.lineEditAreaSearch.setFont(font)
        self.lineEditAreaSearch.setObjectName("lineEditAreaSearch")
        self.verticalLayout_2.addWidget(self.lineEditAreaSearch)
        self.listViewAreaList = QtWidgets.QListView(
            self.scrollAreaWidgetContents)
        font = QtGui.QFont()
        font.setPointSize(9)
        self.listViewAreaList.setFont(font)
        self.listViewAreaList.setObjectName("listViewAreaList")
        self.verticalLayout_2.addWidget(self.listViewAreaList)
        spacerItem2 = QtWidgets.QSpacerItem(
            20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_2.addItem(spacerItem2)
        self.horizontalLayout.addLayout(self.verticalLayout_2)
        self.groupBox_6 = QtWidgets.QGroupBox(self.scrollAreaWidgetContents)
        font = QtGui.QFont()
        font.setPointSize(9)
        font.setBold(True)
        font.setWeight(75)
        self.groupBox_6.setFont(font)
        self.groupBox_6.setObjectName("groupBox_6")
        self.horizontalLayout_6 = QtWidgets.QHBoxLayout(self.groupBox_6)
        self.horizontalLayout_6.setObjectName("horizontalLayout_6")
        self.verticalLayout_5 = QtWidgets.QVBoxLayout()
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        self.verticalLayout_6 = QtWidgets.QVBoxLayout()
        self.verticalLayout_6.setObjectName("verticalLayout_5")
        self.checkProperties = []
        for x in range(10):
            self.checkProperties.append(QtWidgets.QCheckBox(self.groupBox_6))
            font = QtGui.QFont()
            font.setPointSize(9)
            font.setBold(False)
            font.setWeight(50)
            self.checkProperties[x].setFont(font)
            if x < 5:
                self.verticalLayout_5.addWidget(self.checkProperties[x])
            else:
                self.verticalLayout_6.addWidget(self.checkProperties[x])
        self.checkProperties[0].setChecked(True)
        self.horizontalLayout_6.addLayout(self.verticalLayout_5)
        self.horizontalLayout_6.addLayout(self.verticalLayout_6)
        self.horizontalLayout.addWidget(self.groupBox_6)
        self.verticalLayout_27 = QtWidgets.QVBoxLayout()
        self.verticalLayout_27.setObjectName("verticalLayout_27")
        self.groupBox_7 = QtWidgets.QGroupBox(self.scrollAreaWidgetContents)
        font = QtGui.QFont()
        font.setPointSize(9)
        font.setBold(True)
        font.setWeight(75)
        self.groupBox_7.setFont(font)
        self.groupBox_7.setObjectName("groupBox_7")
        self.verticalLayout_7 = QtWidgets.QVBoxLayout(self.groupBox_7)
        self.verticalLayout_7.setObjectName("verticalLayout_7")
        self.horizontalLayout_7 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_7.setObjectName("horizontalLayout_7")
        self.horizontalLayout_8 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_8.setObjectName("horizontalLayout_7")
        self.optionTenures = []
        for x in range(3):
            self.optionTenures.append(QtWidgets.QRadioButton(self.groupBox_7))
            font = QtGui.QFont()
            font.setPointSize(9)
            font.setBold(False)
            font.setWeight(50)
            self.optionTenures[x].setFont(font)
            if x < 2:
                self.horizontalLayout_7.addWidget(self.optionTenures[x])
            else:
                self.horizontalLayout_8.addWidget(self.optionTenures[x])
        self.optionTenures[0].setChecked(True)
        spacerItem3 = QtWidgets.QSpacerItem(
            40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_8.addItem(spacerItem3)
        self.verticalLayout_7.addLayout(self.horizontalLayout_7)
        self.verticalLayout_7.addLayout(self.horizontalLayout_8)
        self.verticalLayout_27.addWidget(self.groupBox_7)
        self.groupBox_8 = QtWidgets.QGroupBox(self.scrollAreaWidgetContents)
        font = QtGui.QFont()
        font.setPointSize(9)
        font.setBold(True)
        font.setWeight(75)
        self.groupBox_8.setFont(font)
        self.groupBox_8.setObjectName("groupBox_8")
        self.verticalLayout_8 = QtWidgets.QVBoxLayout(self.groupBox_8)
        self.verticalLayout_8.setObjectName("verticalLayout_8")
        self.horizontalLayout_9 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_9.setObjectName("horizontalLayout_9")
        self.sliderPriceMin = QtWidgets.QSlider(self.groupBox_8)
        font = QtGui.QFont()
        font.setPointSize(9)
        self.sliderPriceMin.setFont(font)
        self.sliderPriceMin.setOrientation(QtCore.Qt.Horizontal)
        self.sliderPriceMin.setObjectName("sliderPriceMin")
        self.horizontalLayout_9.addWidget(self.sliderPriceMin)
        self.lineEditPriceMin = QtWidgets.QLineEdit(self.groupBox_8)
        self.lineEditPriceMin.setMaximumSize(QtCore.QSize(80, 16777215))
        font = QtGui.QFont()
        font.setPointSize(9)
        self.lineEditPriceMin.setFont(font)
        self.lineEditPriceMin.setText("")
        self.lineEditPriceMin.setAlignment(
            QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter)
        self.lineEditPriceMin.setObjectName("lineEditPriceMin")
        self.horizontalLayout_9.addWidget(self.lineEditPriceMin)
        self.verticalLayout_8.addLayout(self.horizontalLayout_9)
        self.horizontalLayout_10 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_10.setObjectName("horizontalLayout_10")
        self.sliderPriceMax = QtWidgets.QSlider(self.groupBox_8)
        font = QtGui.QFont()
        font.setPointSize(9)
        self.sliderPriceMax.setFont(font)
        self.sliderPriceMax.setProperty("value", 99)
        self.sliderPriceMax.setOrientation(QtCore.Qt.Horizontal)
        self.sliderPriceMax.setObjectName("sliderPriceMax")
        self.horizontalLayout_10.addWidget(self.sliderPriceMax)
        self.lineEditPriceMax = QtWidgets.QLineEdit(self.groupBox_8)
        self.lineEditPriceMax.setMaximumSize(QtCore.QSize(80, 16777215))
        font = QtGui.QFont()
        font.setPointSize(9)
        self.lineEditPriceMax.setFont(font)
        self.lineEditPriceMax.setAlignment(
            QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter)
        self.lineEditPriceMax.setObjectName("lineEditPriceMax")
        self.horizontalLayout_10.addWidget(self.lineEditPriceMax)
        self.verticalLayout_8.addLayout(self.horizontalLayout_10)
        self.verticalLayout_27.addWidget(self.groupBox_8)
        self.horizontalLayout.addLayout(self.verticalLayout_27)
        self.verticalLayout_29.addLayout(self.horizontalLayout)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.label_5 = QtWidgets.QLabel(self.scrollAreaWidgetContents)
        font = QtGui.QFont()
        font.setPointSize(9)
        font.setBold(True)
        font.setWeight(75)
        self.label_5.setFont(font)
        self.label_5.setObjectName("label_5")
        self.verticalLayout.addWidget(self.label_5)
        self.plainKeywords = QtWidgets.QPlainTextEdit(
            self.scrollAreaWidgetContents)
        font = QtGui.QFont()
        font.setPointSize(9)
        self.plainKeywords.setFont(font)
        self.plainKeywords.setObjectName("plainKeywords")
        self.verticalLayout.addWidget(self.plainKeywords)
        self.horizontalLayout_2.addLayout(self.verticalLayout)
        self.verticalLayout_4 = QtWidgets.QVBoxLayout()
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.groupBox_10 = QtWidgets.QGroupBox(self.scrollAreaWidgetContents)
        font = QtGui.QFont()
        font.setPointSize(9)
        font.setBold(True)
        font.setWeight(75)
        self.groupBox_10.setFont(font)
        self.groupBox_10.setObjectName("groupBox_10")
        self.verticalLayout_10 = QtWidgets.QVBoxLayout(self.groupBox_10)
        self.verticalLayout_10.setObjectName("verticalLayout_10")
        self.horizontalLayout_13 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_13.setObjectName("horizontalLayout_13")
        self.sliderLandAreaMin = QtWidgets.QSlider(self.groupBox_10)
        font = QtGui.QFont()
        font.setPointSize(9)
        self.sliderLandAreaMin.setFont(font)
        self.sliderLandAreaMin.setOrientation(QtCore.Qt.Horizontal)
        self.sliderLandAreaMin.setObjectName("sliderLandAreaMin")
        self.horizontalLayout_13.addWidget(self.sliderLandAreaMin)
        self.lineEditLandAreaMin = QtWidgets.QLineEdit(self.groupBox_10)
        self.lineEditLandAreaMin.setMaximumSize(QtCore.QSize(80, 16777215))
        font = QtGui.QFont()
        font.setPointSize(9)
        self.lineEditLandAreaMin.setFont(font)
        self.lineEditLandAreaMin.setText("")
        self.lineEditLandAreaMin.setAlignment(
            QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter)
        self.lineEditLandAreaMin.setObjectName("lineEditLandAreaMin")
        self.horizontalLayout_13.addWidget(self.lineEditLandAreaMin)
        self.verticalLayout_10.addLayout(self.horizontalLayout_13)
        self.horizontalLayout_14 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_14.setObjectName("horizontalLayout_14")
        self.sliderLandAreaMax = QtWidgets.QSlider(self.groupBox_10)
        font = QtGui.QFont()
        font.setPointSize(9)
        self.sliderLandAreaMax.setFont(font)
        self.sliderLandAreaMax.setProperty("value", 99)
        self.sliderLandAreaMax.setOrientation(QtCore.Qt.Horizontal)
        self.sliderLandAreaMax.setObjectName("sliderLandAreaMax")
        self.horizontalLayout_14.addWidget(self.sliderLandAreaMax)
        self.lineEditLandAreaMax = QtWidgets.QLineEdit(self.groupBox_10)
        self.lineEditLandAreaMax.setMaximumSize(QtCore.QSize(80, 16777215))
        font = QtGui.QFont()
        font.setPointSize(9)
        self.lineEditLandAreaMax.setFont(font)
        self.lineEditLandAreaMax.setAlignment(
            QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter)
        self.lineEditLandAreaMax.setObjectName("lineEditLandAreaMax")
        self.horizontalLayout_14.addWidget(self.lineEditLandAreaMax)
        self.verticalLayout_10.addLayout(self.horizontalLayout_14)
        self.groupBox_9 = QtWidgets.QGroupBox(self.scrollAreaWidgetContents)
        font = QtGui.QFont()
        font.setPointSize(9)
        font.setBold(True)
        font.setWeight(75)
        self.groupBox_9.setFont(font)
        self.groupBox_9.setObjectName("groupBox_9")
        self.verticalLayout_9 = QtWidgets.QVBoxLayout(self.groupBox_9)
        self.verticalLayout_9.setObjectName("verticalLayout_9")
        self.horizontalLayout_11 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_11.setObjectName("horizontalLayout_11")
        self.sliderFloorAreaMin = QtWidgets.QSlider(self.groupBox_9)
        font = QtGui.QFont()
        font.setPointSize(9)
        self.sliderFloorAreaMin.setFont(font)
        self.sliderFloorAreaMin.setOrientation(QtCore.Qt.Horizontal)
        self.sliderFloorAreaMin.setObjectName("sliderFloorAreaMin")
        self.horizontalLayout_11.addWidget(self.sliderFloorAreaMin)
        self.lineEditFloorAreaMin = QtWidgets.QLineEdit(self.groupBox_9)
        self.lineEditFloorAreaMin.setMaximumSize(QtCore.QSize(80, 16777215))
        font = QtGui.QFont()
        font.setPointSize(9)
        self.lineEditFloorAreaMin.setFont(font)
        self.lineEditFloorAreaMin.setText("")
        self.lineEditFloorAreaMin.setAlignment(
            QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter)
        self.lineEditFloorAreaMin.setObjectName("lineEditFloorAreaMin")
        self.horizontalLayout_11.addWidget(self.lineEditFloorAreaMin)
        self.verticalLayout_9.addLayout(self.horizontalLayout_11)
        self.horizontalLayout_12 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_12.setObjectName("horizontalLayout_12")
        self.sliderFloorAreaMax = QtWidgets.QSlider(self.groupBox_9)
        font = QtGui.QFont()
        font.setPointSize(9)
        self.sliderFloorAreaMax.setFont(font)
        self.sliderFloorAreaMax.setProperty("value", 99)
        self.sliderFloorAreaMax.setOrientation(QtCore.Qt.Horizontal)
        self.sliderFloorAreaMax.setObjectName("sliderFloorAreaMax")
        self.horizontalLayout_12.addWidget(self.sliderFloorAreaMax)
        self.lineEditFloorAreaMax = QtWidgets.QLineEdit(self.groupBox_9)
        self.lineEditFloorAreaMax.setMaximumSize(QtCore.QSize(80, 16777215))
        font = QtGui.QFont()
        font.setPointSize(9)
        self.lineEditFloorAreaMax.setFont(font)
        self.lineEditFloorAreaMax.setAlignment(
            QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter)
        self.lineEditFloorAreaMax.setObjectName("lineEditFloorAreaMax")
        self.horizontalLayout_12.addWidget(self.lineEditFloorAreaMax)
        self.verticalLayout_9.addLayout(self.horizontalLayout_12)
        self.verticalLayout_4.addWidget(self.groupBox_9)
        self.verticalLayout_4.addWidget(self.groupBox_10)
        self.horizontalLayout_2.addLayout(self.verticalLayout_4)
        self.verticalLayout_3 = QtWidgets.QVBoxLayout()
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.verticalLayout_26 = QtWidgets.QVBoxLayout()
        self.verticalLayout_26.setObjectName("verticalLayout_26")
        self.label = QtWidgets.QLabel(self.scrollAreaWidgetContents)
        font = QtGui.QFont()
        font.setPointSize(9)
        font.setBold(True)
        font.setWeight(75)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.verticalLayout_26.addWidget(self.label)
        self.comboCarSpaces = QtWidgets.QComboBox(
            self.scrollAreaWidgetContents)
        self.comboCarSpaces.setMinimumSize(QtCore.QSize(150, 0))
        font = QtGui.QFont()
        font.setPointSize(9)
        self.comboCarSpaces.setFont(font)
        self.comboCarSpaces.setObjectName("comboCarSpaces")
        for x in range(len(self.carSpaceTexts)):
            self.comboCarSpaces.addItem(self.carSpaceTexts[x])
        self.verticalLayout_26.addWidget(self.comboCarSpaces)
        self.verticalLayout_3.addLayout(self.verticalLayout_26)
        self.verticalLayout_25 = QtWidgets.QVBoxLayout()
        self.verticalLayout_25.setObjectName("verticalLayout_25")
        self.label_4 = QtWidgets.QLabel(self.scrollAreaWidgetContents)
        font = QtGui.QFont()
        font.setPointSize(9)
        font.setBold(True)
        font.setWeight(75)
        self.label_4.setFont(font)
        self.label_4.setObjectName("label_4")
        self.verticalLayout_25.addWidget(self.label_4)
        self.comboNABERS = QtWidgets.QComboBox(self.scrollAreaWidgetContents)
        self.comboNABERS.setMinimumSize(QtCore.QSize(150, 0))
        font = QtGui.QFont()
        font.setPointSize(9)
        self.comboNABERS.setFont(font)
        self.comboNABERS.setObjectName("comboNABERS")
        for x in range(len(self.energyRatingTexts)):
            self.comboNABERS.addItem(self.energyRatingTexts[x])
        self.verticalLayout_25.addWidget(self.comboNABERS)
        self.label_8 = QtWidgets.QLabel(self.scrollAreaWidgetContents)
        font = QtGui.QFont()
        font.setPointSize(9)
        font.setBold(True)
        font.setWeight(75)
        self.label_8.setFont(font)
        self.label_8.setObjectName("label_8")
        self.label_9 = QtWidgets.QLabel(self.scrollAreaWidgetContents)
        self.label_9.setFont(font)
        self.label_9.setObjectName("label_9")
        self.verticalLayout_25.addWidget(self.label_8)
        font = QtGui.QFont()
        font.setPointSize(9)
        self.dateSelectFrom = QtWidgets.QDateEdit()
        self.dateSelectFrom.setFont(font)
        self.dateSelectFrom.setDisplayFormat("yyyy-MM-dd")
        self.dateSelectFrom.setObjectName("dateSelectFrom")
        self.verticalLayout_25.addWidget(self.dateSelectFrom)
        self.verticalLayout_25.addWidget(self.label_9)
        self.dateSelectTo = QtWidgets.QDateEdit()
        self.dateSelectTo.setFont(font)
        self.dateSelectTo.setDisplayFormat("yyyy-MM-dd")
        self.dateSelectTo.setObjectName("dateSelectTo")
        self.dateSelectTo.setDate(QDate(self.today))
        self.verticalLayout_25.addWidget(self.dateSelectTo)
        spacerItem4 = QtWidgets.QSpacerItem(
            20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_25.addItem(spacerItem4)
        self.horizontalLayout_36 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_36.setObjectName("horizontalLayout_36")
        self.btnSave = QtWidgets.QPushButton(
            self.scrollAreaWidgetContents)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.btnSave.setFont(font)
        self.btnSave.setObjectName("btnSave")
        self.horizontalLayout_36.addWidget(self.btnSave)
        spacerItem5 = QtWidgets.QSpacerItem(
            40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_36.addItem(spacerItem5)
        self.btnSearch = QtWidgets.QPushButton(self.scrollAreaWidgetContents)
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.btnSearch.setFont(font)
        self.btnSearch.setObjectName("btnSearch")
        self.horizontalLayout_36.addWidget(self.btnSearch)
        self.verticalLayout_25.addLayout(self.horizontalLayout_36)
        self.verticalLayout_3.addLayout(self.verticalLayout_25)
        self.horizontalLayout_2.addLayout(self.verticalLayout_3)
        self.verticalLayout_29.addLayout(self.horizontalLayout_2)
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        self.verticalLayout_28.addWidget(self.scrollArea)
        self.verticalLayout_30.addLayout(self.verticalLayout_28)
        self.tableViewResult = QtWidgets.QTableView(self)
        font = QtGui.QFont()
        font.setPointSize(9)
        self.tableViewResult.setFont(font)
        self.tableViewResult.setObjectName("tableViewResult")
        self.tableViewResult.setModel(QStandardItemModel())
        self.verticalLayout_30.addWidget(self.tableViewResult)

        self.hideSTH()
        self.retranslateUi()
        self.connectSignal()
        self.setupSliders()
        QtCore.QMetaObject.connectSlotsByName(self)

    def hideSTH(self):
        # self.label_7.hide()
        # self.lineEditAreaSearch.hide()
        self.listViewAreaList.hide()

    def retranslateUi(self):
        _translate = QtCore.QCoreApplication.translate
        self.label_6.setText(_translate("Dialog", "Filters"))
        self.btnShowFilter.setText(_translate("Dialog", "Hide"))
        for x in range(4):
            self.channels[x].setText(_translate(
                "Dialog", self.channelTexts[x]))
        self.label_7.setText(_translate("Dialog", "Area"))
        self.surroundingCheckBox.setText(
            _translate("Dialog", "Include surrounding suburbs"))
        self.groupBox_6.setTitle(_translate("Dialog", "Property types"))
        for x in range(10):
            self.checkProperties[x].setText(
                _translate("Dialog", self.propertyTexts[x]))
        self.groupBox_7.setTitle(_translate("Dialog", "Tenure type"))
        for x in range(3):
            self.optionTenures[x].setText(
                _translate("Dialog", self.tenureTexts[x]))
        self.groupBox_8.setTitle(_translate("Dialog", "Price"))
        self.lineEditPriceMin.setPlaceholderText(_translate("Dialog", "Any"))
        self.lineEditPriceMax.setPlaceholderText(_translate("Dialog", "Any"))
        self.label_5.setText(_translate("Dialog", "Keywords"))
        self.groupBox_10.setTitle(_translate("Dialog", "Land area"))
        self.lineEditLandAreaMin.setPlaceholderText(
            _translate("Dialog", "Any"))
        self.lineEditLandAreaMax.setPlaceholderText(
            _translate("Dialog", "Any"))
        self.groupBox_9.setTitle(_translate("Dialog", "Floor area"))
        self.lineEditFloorAreaMin.setPlaceholderText(
            _translate("Dialog", "Any"))
        self.lineEditFloorAreaMax.setPlaceholderText(
            _translate("Dialog", "Any"))
        self.label.setText(_translate("Dialog", "Car spaces"))
        self.label_4.setText(_translate("Dialog", "NABERS Energy Rating"))
        self.label_8.setText(_translate("Dialog", "Date Updated From"))
        self.label_9.setText(_translate("Dialog", "Date Updated To"))
        self.btnSave.setText(_translate("Dialog", "Save to GS"))
        self.btnSearch.setText(_translate("Dialog", "Start Search"))
        header_labels = ["ID", "Title", "Date Updated", "Street", "Suburb", "State", "Postcode", "Price",
                         "Price Range", "Agency Company", "Agency Contact", "Property", "Land Area", "Floor Area", "Car Spaces", "Highlights", "Description", "Link"]
        self.tableViewResult.model().setHorizontalHeaderLabels(header_labels)

    def connectSignal(self):
        self.btnShowFilter.clicked.connect(self.onShowFilter)
        self.btnSearch.clicked.connect(lambda: self.crawl_slot(self.btnSearch))
        self.btnSave.clicked.connect(lambda: self.saveSheet(self.btnSave))

        for x in range(10):
            self.checkProperties[x].stateChanged.connect(
                lambda state, x=x: self.onChangePropertyType(state, x))

        for x in range(4):
            self.channels[x].toggled.connect(
                lambda checked, x=x: self.onSelectChannel(checked, x))

    def setupSliders(self):
        self.sliderPriceMin.setMinimum(0)
        self.sliderPriceMin.setMaximum(
            len(self.sliderValues[self.priceType]) - 1)
        self.sliderPriceMax.setMinimum(0)
        self.sliderPriceMax.setMaximum(
            len(self.sliderValues[self.priceType]) - 1)

        self.sliderFloorAreaMin.setMinimum(0)
        self.sliderFloorAreaMin.setMaximum(len(self.sliderValues[2]) - 1)
        self.sliderFloorAreaMax.setMinimum(0)
        self.sliderFloorAreaMax.setMaximum(len(self.sliderValues[2]) - 1)

        self.sliderLandAreaMin.setMinimum(0)
        self.sliderLandAreaMin.setMaximum(len(self.sliderValues[3]) - 1)
        self.sliderLandAreaMax.setMinimum(0)
        self.sliderLandAreaMax.setMaximum(len(self.sliderValues[3]) - 1)

        self.sliderPriceMin.sliderMoved[int].connect(
            lambda value: self.onSliderRelease(value, 0, self.sliderPriceMin, self.sliderPriceMax, self.lineEditPriceMin, self.lineEditPriceMax, self.priceType))
        self.sliderPriceMax.sliderMoved[int].connect(
            lambda value: self.onSliderRelease(value, 1, self.sliderPriceMin, self.sliderPriceMax, self.lineEditPriceMin, self.lineEditPriceMax, self.priceType))
        self.lineEditPriceMin.editingFinished.connect(
            lambda: self.onRangeInputChange(0, self.sliderPriceMin, self.sliderPriceMax, self.lineEditPriceMin, self.lineEditPriceMax, self.priceType))
        self.lineEditPriceMax.editingFinished.connect(
            lambda: self.onRangeInputChange(1, self.sliderPriceMin, self.sliderPriceMax, self.lineEditPriceMin, self.lineEditPriceMax, self.priceType))

        self.sliderFloorAreaMin.sliderMoved[int].connect(
            lambda value: self.onSliderRelease(value, 0, self.sliderFloorAreaMin, self.sliderFloorAreaMax, self.lineEditFloorAreaMin, self.lineEditFloorAreaMax, 2))
        self.sliderFloorAreaMax.sliderMoved[int].connect(
            lambda value: self.onSliderRelease(value, 1, self.sliderFloorAreaMin, self.sliderFloorAreaMax, self.lineEditFloorAreaMin, self.lineEditFloorAreaMax, 2))
        self.lineEditFloorAreaMin.editingFinished.connect(
            lambda: self.onRangeInputChange(0, self.sliderFloorAreaMin, self.sliderFloorAreaMax, self.lineEditFloorAreaMin, self.lineEditFloorAreaMax, 2))
        self.lineEditFloorAreaMax.editingFinished.connect(
            lambda: self.onRangeInputChange(1, self.sliderFloorAreaMin, self.sliderFloorAreaMax, self.lineEditFloorAreaMin, self.lineEditFloorAreaMax, 2))

        self.sliderLandAreaMin.sliderMoved[int].connect(
            lambda value: self.onSliderRelease(value, 0, self.sliderLandAreaMin, self.sliderLandAreaMax, self.lineEditLandAreaMin, self.lineEditLandAreaMax, 3))
        self.sliderLandAreaMax.sliderMoved[int].connect(
            lambda value: self.onSliderRelease(value, 1, self.sliderLandAreaMin, self.sliderLandAreaMax, self.lineEditLandAreaMin, self.lineEditLandAreaMax, 3))
        self.lineEditLandAreaMin.editingFinished.connect(
            lambda: self.onRangeInputChange(0, self.sliderLandAreaMin, self.sliderLandAreaMax, self.lineEditLandAreaMin, self.lineEditLandAreaMax, 3))
        self.lineEditLandAreaMax.editingFinished.connect(
            lambda: self.onRangeInputChange(1, self.sliderLandAreaMin, self.sliderLandAreaMax, self.lineEditLandAreaMin, self.lineEditLandAreaMax, 3))

    def onShowFilter(self):
        if (self.scrollArea.isHidden()):
            self.scrollArea.show()
        else:
            self.scrollArea.hide()

    def onChangePropertyType(self, state, x):
        if state == 2:
            if x == 0:
                for i in range(1, 10):
                    self.checkProperties[i].setChecked(False)
            else:
                self.checkProperties[0].setChecked(False)
        else:
            for i in range(0, 11):
                if i == 10:
                    break
                if i != x and self.checkProperties[i].isChecked():
                    break
            if i == 10:
                self.checkProperties[0].setChecked(True)

    def onSliderRelease(self, value, type, sliderMin, sliderMax, editMin, editMax, rangeIndex):
        minValue = sliderMin.value()
        maxValue = sliderMax.value()
        valueRange = len(self.sliderValues[rangeIndex]) - 1

        if type == 0:
            # if value == valueRange:
            #     minValue = 0
            #     sliderMin.setValue(minValue)
            #     text = ""
            # elif value > maxValue:
            if value > maxValue:
                minValue = maxValue
                sliderMin.setValue(minValue)
                text = editMax.text()
            else:
                minValue = value
                text = str(self.sliderValues[rangeIndex][minValue])
            editMin.setText(text)
        else:
            # if value == 0:
            #     maxValue = valueRange
            #     sliderMax.setValue(maxValue)
            #     text = ""
            # elif minValue > value:
            if minValue > value:
                maxValue = minValue
                sliderMax.setValue(maxValue)
                text = editMin.text()
            else:
                maxValue = value
                text = str(self.sliderValues[rangeIndex][maxValue])
            editMax.setText(text)

    def onRangeInputChange(self, type, sliderMin, sliderMax, editMin, editMax, rangeIndex):
        minText = editMin.text()
        maxText = editMax.text()
        valueRange = len(self.sliderValues[rangeIndex]) - 1

        if minText == "":
            minPrice = 0
        else:
            minPrice = int(minText)

        if maxText == "":
            maxPrice = 0
        else:
            maxPrice = int(maxText)

        if maxPrice < minPrice and maxPrice > 0:
            if type == 0:
                minPrice = maxPrice
                editMin.setText(str(minPrice))
            else:
                maxPrice = minPrice
                editMax.setText(str(maxPrice))

        if type == 0:
            value = minPrice
        else:
            value = maxPrice

        for x in range(1, valueRange):
            if self.sliderValues[0][x] >= value:
                break

        if type == 0:
            sliderMin.setValue(x)
        else:
            if value <= 0:
                x = valueRange
            sliderMax.setValue(x)

    def onSelectChannel(self, checked, x):
        if checked == True:
            self.channel = x
            self.priceType = x % 2
            self.sliderPriceMin.setMaximum(
                len(self.sliderValues[self.priceType]) - 1)
            self.sliderPriceMax.setMaximum(
                len(self.sliderValues[self.priceType]) - 1)

    def setupURL(self):
        # Define the base URL
        base_url = self.targetUrl + '/'

        base_url += self.channelParams[self.channel] + '/'

        # Define the GET parameters as a dictionary
        query_params = {}

        if self.surroundingCheckBox.isChecked():
            query_params["includePropertiesWithin"] = 'includesurrounding'
        else:
            query_params["includePropertiesWithin"] = 'excludesurrounding'

        location_string = self.lineEditAreaSearch.text()

        # Replace spaces, commas, and hyphens with hyphens
        cleaned_string = re.sub(r'[\s,/-]+', '-', location_string)

        # Convert to lowercase
        locations = cleaned_string.lower()

        if locations != "":
            query_params["locations"] = locations

        # Set Property Param
        if not self.checkProperties[0].isChecked():
            properties = ""
            for x in range(1, len(self.checkProperties)):
                if (self.checkProperties[x].isChecked()):
                    properties += self.propertyParams[x] + ","
            query_params["propertyTypes"] = properties[:-1]

        # Set Tenure param
        if not self.optionTenures[0].isChecked():
            properties = ""
            for x in range(1, len(self.optionTenures)):
                if (self.optionTenures[x].isChecked()):
                    query_params["tenure"] = self.tenureParams[x]

        # Set Max & Min Price
        if self.lineEditPriceMax.text() != "":
            query_params["maxPrice"] = int(self.lineEditPriceMax.text())
        if self.lineEditPriceMin.text() != "":
            query_params["minPrice"] = int(self.lineEditPriceMin.text())

        # Set Floor & Land Area
        if self.lineEditFloorAreaMax.text() != "":
            query_params["maxFloorArea"] = int(
                self.lineEditFloorAreaMax.text())
        if self.lineEditFloorAreaMin.text() != "":
            query_params["minFloorArea"] = int(
                self.lineEditFloorAreaMin.text())
        if self.lineEditLandAreaMax.text() != "":
            query_params["maxSiteArea"] = int(self.lineEditLandAreaMax.text())
        if self.lineEditLandAreaMin.text() != "":
            query_params["minSiteArea"] = int(self.lineEditLandAreaMin.text())

        # Set Car Space
        if self.comboCarSpaces.currentIndex() != 0:
            query_params["numParkingSpaces"] = self.carSpaceValues[self.comboCarSpaces.currentIndex()]

        # Set NABERS Energy Rating
        if self.comboNABERS.currentIndex() != 0:
            query_params["energyEfficiency"] = self.energyRatingValues[self.comboNABERS.currentIndex()]

        # Build keywords array
        # Define a regular expression pattern to match words and special characters
        text = self.plainKeywords.toPlainText()

        # Filter out empty strings from the result
        words = re.findall(r'\S+', text)

        if len(words):
            query_params["keywords"] = "+".join(words)

        # Function to build the URL
        def build_url(base_url, query_params):
            # Encode the query parameters and join them with the base URL
            query_string = urllib.parse.urlencode(query_params)
            return f"{base_url}?{query_string}"

        # Call the function to build the URL
        final_url = build_url(base_url, query_params)
        print(final_url)
        return final_url

    def saveSheet(self, button):

        now = datetime.now().strftime("%y%m%d%H%M%S%f")
        spreadsheet = gc.create(f'realcommercial-{now}')
        spreadsheet.share('softprom0109@gmail.com', perm_type='user', role='writer')

        # Replace with your Google Sheet title
        # spreadsheet = gc.open('PythonSheet')

        # Select the worksheet where you want to upload data (e.g., the first worksheet)
        worksheet = spreadsheet.get_worksheet(
            0)  # 0 represents the first worksheet

        # Data to be uploaded
        data_to_upload = [
            ["ID", "Title", "Date Updated", "Street", "Suburb", "State", "Postcode", "Price",
                         "Price Range", "Agency Company", "Agency Contact", "Property", "Land Area", "Floor Area", "Car Spaces", "Highlights", "Description", "Link"],
            # Add more rows as needed
        ]

        for value in self.database.values():
            data = value
            detail = isset('detail', data, [])

            updatedAt = isset('lastUpdatedAt', detail)
            address = data['address']
            street = address["streetAddress"]
            suburb = address["suburb"]
            state = address["state"]
            postcode = address["postcode"]

            if data["minPrice"] == 0:
                minPrice = 'Any'
            else:
                minPrice = data["minPrice"]

            if data["maxPrice"] == 0:
                maxPrice = 'Any'
            else:
                maxPrice = data["maxPrice"]

            if updatedAt != "" and updatedAt <= self.datefrom or updatedAt >= self.dateto + "T23:59:59Z":
                continue

            item = []
            item.append(data['id'])
            item.append(isset('title', data))
            item.append(updatedAt)
            item.append(street)
            item.append(suburb)
            item.append(state)
            item.append(postcode)
            item.append(isset('price', data['details']))
            item.append(f'{minPrice} - {maxPrice}')
            item.append(data['agencies'][0]['name'])

            contacts = ""
            floor = ""
            land = ""
            carspace = ""
            highlight = ""
            description = ""
            if ('detail' in data):
                
                if len(detail["agencies"]) and "salespeople" in detail["agencies"][0] and len(detail["agencies"][0]["salespeople"]):
                    salespeople = detail['agencies'][0]["salespeople"]
                    for contact in salespeople:
                        contacts += f'{contact["name"]} : {contact["phone"]["display"]}' + " "
                for attr in detail['attributes']:
                    if attr['id'] == "floor-area":
                        floor = attr["value"]
                    elif attr['id'] == "land-area":
                        land = attr["value"]
                    elif attr['id'] == "car-spaces":
                        carspace = attr["value"]
                highlight = "\n".join(detail['highlights'])
                description = detail['description'].replace("<br/>", "\n")
                        
            item.append(contacts)
            item.append(", ".join(data['attributes']['propertyTypes']))
            item.append(land)
            item.append(floor)
            item.append(carspace)
            item.append(highlight)
            item.append(description)
            item.append(data['pdpUrl'])

            data_to_upload.append(item)

        # print (data_to_upload)
        # Upload data to the Google Sheet
        worksheet.insert_rows(data_to_upload, 2)  # Change the row number as needed

class LogThread(QThread):
    def __init__(self, gui):
        super(LogThread, self).__init__()
        self.gui = gui

    def run(self) -> None:
        while True:
            if not self.gui.Q.empty():
                record = self.gui.Q.get()

                if record['type'] == 4:
                    self.gui.btnSearch.setText('Start Search')
                    break

                data = record['data']
                id = data['id']
                if record['type'] == 1:
                    row = self.gui.tableViewResult.model().rowCount()
                    data['rowNum'] = row
                    self.gui.database[id] = data

                    if self.gui.targetUrl not in data['pdpUrl']:
                        data['pdpUrl'] = self.gui.targetUrl + data['pdpUrl']

                        if data["minPrice"] == 0:
                            minPrice = 'Any'
                        else:
                            minPrice = data["minPrice"]

                        if data["maxPrice"] == 0:
                            maxPrice = 'Any'
                        else:
                            maxPrice = data["maxPrice"]

        #header_labels = ["ID", "Title", "Date Updated", "Street", "Suburb", "State", "Postcode", "Price", "Price Range", "Agency Company", "Agency Contact", "Property", "Land Area", "Floor Area", "Carspaces"]
                    self.gui.tableViewResult.model().insertRow(
                        row,
                        [
                            # ID
                            QStandardItem(data['id']),
                            # Title
                            QStandardItem(isset('title', data)),
                            # Date Updated
                            QStandardItem(""),
                            # Street
                            QStandardItem(
                                isset('streetAddress', data['address'])),
                            # Suburb
                            QStandardItem(""),
                            # State
                            QStandardItem(""),
                            # Postcode
                            QStandardItem(""),
                            # Price Posted
                            QStandardItem(isset('price', data['details'])),
                            # Approx. Price Range
                            QStandardItem(
                                f'{minPrice} - {maxPrice}'),
                            # Agency Comp.
                            QStandardItem(
                                data['agencies'][0]['name']),
                            # Agency Contact
                            QStandardItem(""),
                            # Property Type
                            QStandardItem(
                                ", ".join(data['attributes']['propertyTypes'])),
                            # Land Area
                            QStandardItem(""),
                            # Floor Area
                            QStandardItem(data['attributes']['area']),
                            # Car spaces
                            QStandardItem(""),
                            # Highlights
                            QStandardItem(""),
                            # Description
                            QStandardItem(""),
                            # Link
                            QStandardItem(data['pdpUrl']),
                        ]
                    )
                elif record['type'] == 2:
                    data = record['data']
                    rowNum = self.gui.database[id]['rowNum']

                    updatedAt = data['lastUpdatedAt']
                    address = data['address']
                    street = address["streetAddress"]
                    suburb = address["suburb"]
                    state = address["state"]
                    postcode = address["postcode"]
                    uid = re.sub(r'[^a-zA-Z0-9]', '',
                                 street)[:4] + suburb[:2] + state[:2]

                    if updatedAt <= self.gui.datefrom or updatedAt >= self.gui.dateto + "T23:59:59Z":
                        self.gui.tableViewResult.setRowHidden(rowNum, True)

                    self.gui.database[id]['detail'] = data
                    self.gui.database[id]['uid'] = uid

                    self.gui.tableViewResult.model().item(
                        rowNum, 2).setText(updatedAt)
                    self.gui.tableViewResult.model().item(
                        rowNum, 4).setText(suburb)
                    self.gui.tableViewResult.model().item(
                        rowNum, 5).setText(state)
                    self.gui.tableViewResult.model().item(
                        rowNum, 6).setText(postcode)

                    for attr in data['attributes']:
                        if attr['id'] == "floor-area":
                            self.gui.tableViewResult.model().item(
                                rowNum, 13).setText(attr["value"])
                        elif attr['id'] == "land-area":
                            self.gui.tableViewResult.model().item(
                                rowNum, 12).setText(attr["value"])
                        elif attr['id'] == "car-spaces":
                            self.gui.tableViewResult.model().item(
                                rowNum, 14).setText(attr["value"])

                    if len(data["agencies"]) and "salespeople" in data["agencies"][0] and len(data["agencies"][0]["salespeople"]):
                        salespeople = data['agencies'][0]["salespeople"]
                        contacts = ""
                        for contact in salespeople:
                            contacts += f'{contact["name"]} : {contact["phone"]["display"]}' + " "
                        self.gui.tableViewResult.model().item(
                            rowNum, 10).setText(contacts)

                    self.gui.tableViewResult.model().item(
                        rowNum, 15).setText("\n".join(data['highlights']))
                    self.gui.tableViewResult.model().item(
                        rowNum, 16).setText(data['description'].replace("<br/>", "\n"))

                elif record['type'] == 3:
                    try:
                        data = record['data']
                        rowNum = self.gui.database[id]['rowNum']
                        self.gui.database[id]['minPrice'] = data['minPrice']
                        self.gui.database[id]['maxPrice'] = data['maxPrice']

                        if data["minPrice"] == 0:
                            minPrice = 'Any'
                        else:
                            minPrice = data["minPrice"]

                        if data["maxPrice"] == 0:
                            maxPrice = 'Any'
                        else:
                            maxPrice = data["maxPrice"]

                        self.gui.tableViewResult.model().item(
                            rowNum, 8).setText(f'{minPrice} - {maxPrice}')
                    except Exception as e:
                        # Handle other exceptions (generic Exception class)
                        print("An error occurred")
                        print(f"Error details: {e}")

                self.msleep(20)


def crawl_run(Q, url, dataset, isLease):
    # CrawlerProcess
    settings = get_project_settings()

    process = CrawlerProcess(settings=settings)
    process.crawl(scrapspider, Q=Q, base_url=url,
                  dataset=dataset, isLease=isLease)
    process.start()

    """
    # CrawlerRunner
    configure_logging(install_root_handler=False)
    logging.basicConfig(filename='output.log', format='%(asctime)s - %(levelname)s: %(message)s', level=logging.INFO)
    runner = CrawlerRunner(settings={
        'USER_AGENT': ua,
        'ROBOTSTXT_OBEY': is_obey,
        'SAVE_CONTENT': 'scraps.jl',
        'ITEM_PIPELINES': {
            'scraps.pipelines.ChanelPipeline': 300,
        },
    })
    d = runner.crawl(scrapspider, Q=Q)
    d.addBoth(lambda _: reactor.stop())
    reactor.run()
    """


if __name__ == '__main__':
    freeze_support()
    app = QApplication(sys.argv)
    scraps = CrawlWindows()
    scraps.show()
    sys.exit(app.exec_())
