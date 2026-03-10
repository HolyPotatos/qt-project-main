from PyQt5.QtWidgets import QMainWindow, QListWidgetItem, QTableWidgetItem
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QHeaderView, QAbstractItemView
from ui.OrderWindow import Ui_OrderWindow 
from models.order import Order, OrderProduct


class OrderDialog(QMainWindow, Ui_OrderWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.setWindowTitle("История заказов")
        self.setWindowModality(Qt.ApplicationModal)
        self.orderTableWidget.setColumnCount(3)
        self.orderTableWidget.setHorizontalHeaderLabels(["№ заказа", "Дата", "Сумма, руб."])
        header = self.orderTableWidget.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents) 
        header.setSectionResizeMode(1, QHeaderView.Stretch)          
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents) 
        self.orderTableWidget.setSelectionMode(QAbstractItemView.SingleSelection)
        self.orderTableWidget.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.orderTableWidget.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.orderTableWidget.itemClicked.connect(self.show_order_details)
        self.load_orders()

    def load_orders(self):
        self.orderList.clear()
        self.totalSum.setText("0")
        orders = Order.fetch_all() 
        self.orderTableWidget.setRowCount(len(orders))
        for row, order in enumerate(orders):
            date_str = order.created_at.strftime("%d.%m.%Y %H:%M")
            id_item = QTableWidgetItem(str(order.id))
            id_item.obj = order 
            self.orderTableWidget.setItem(row, 0, id_item)
            date_item = QTableWidgetItem(date_str)
            self.orderTableWidget.setItem(row, 1, date_item)
            total_item = QTableWidgetItem(f"{order.total}")
            self.orderTableWidget.setItem(row, 2, total_item)

    def show_order_details(self, item):
        self.orderList.clear()
        row = item.row()
        selected_order = self.orderTableWidget.item(row, 0).obj 
        all_order_products = OrderProduct.fetch_all()
        current_order_products = [op for op in all_order_products if op.order.id == selected_order.id]
        for order_product in current_order_products:
            product = order_product.product
            text = f"{product.name} — {order_product.count} шт. x {order_product.price} руб."
            list_item = QListWidgetItem(QIcon(product.image), text)
            self.orderList.addItem(list_item)
        self.totalSum.setText(f"{selected_order.total}")