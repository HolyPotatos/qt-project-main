import sys
import time
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QMainWindow, QListWidgetItem, QListWidget

from init import CATEGORIES
from models.category import Category
from models.order import Order, OrderProduct
from models.product import Product
from ui.MainWindow import Ui_MainWindow
from widgets.CategoryDialog import CategoryDialog
from widgets.ChoicePile import ChoicePile
from widgets.ProductDialog import ProductDialog
from widgets.OrderDialog import OrderDialog


def init_db():
    # Инициализация БД
    for table in [Category, Product, Order, OrderProduct]:
        table._create_table()
    pass

 
class MyWindow(Ui_MainWindow, QMainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        init_db()
        self.show()
        self.setup_categories()
        self.exitMenu.triggered.connect(self.close)
        self.addCategoryMenu.triggered.connect(self.open_category_dialog)
        self.addProductMenu.triggered.connect(self.open_product_dialog)
        self.pushButton.clicked.connect(self.clear_cart)
        self.orderButton.clicked.connect(self.open_order_dialog)
        self.toCategoriesButton.clicked.connect(self.setup_categories)
        self.initTestData.triggered.connect(self.init_test_data)
        self.orderList.itemDoubleClicked.connect(self.remove_from_cart)
        self.orderList.model().rowsInserted.connect(self.calc_total)
        self.orderList.model().rowsRemoved.connect(self.calc_total)
        self.submit.clicked.connect(self.submit_order)

    def open_category_dialog(self):
        dlg = CategoryDialog(self)
        dlg.setWindowTitle('Добавить новую категорию')
        dlg.accepted.connect(self.setup_categories)
        dlg.exec()

    def open_order_dialog(self):
        dlg = OrderDialog(self)
        dlg.show()

    def open_product_dialog(self):
        dlg = ProductDialog(self)
        dlg.setWindowTitle('Добавить блюдо')
        dlg.accepted.connect(self.setup_categories)
        dlg.exec()

    def setup_categories(self):
        """ Выводим список категорий из БД """
        piles = self.pilesGrid
        for i in reversed(range(piles.count())):
            piles.itemAt(i).widget().setParent(None)
        categories = Category.fetch_all()
        for i, category in enumerate(categories):
            row = i // 3
            col = i % 3
            pile = ChoicePile(category.label, category.image, category)
            piles.addWidget(pile, row, col)
            pile.show()
            pile.clicked.connect(self.setup_products)
        self.toCategoriesButton.setEnabled(False)

    def setup_products(self):
        """ Выводим список товаров для категории из БД """
        piles = self.pilesGrid
        for i in reversed(range(piles.count())):
            piles.itemAt(i).widget().setParent(None)
        for widget in piles.children():
            piles.removeWidget(widget)
        products = Product.fetch_all()
        for i, product in enumerate(product for product in products if
                                    product.category.id == self.sender().obj.id):
            row = i // 3
            col = i % 3
            pile = ChoicePile(product.name, product.image, product)
            piles.addWidget(pile, row, col)
            pile.show()
            pile.clicked.connect(self.add_to_cart)
        self.toCategoriesButton.setEnabled(True)

    def add_to_cart(self):
        product: Product = self.sender().obj
        list_item = QListWidgetItem(QIcon(product.image), f'{product.name} x {product.price}')
        list_item.obj = product
        self.orderList.addItem(list_item)

    def remove_from_cart(self, item):
        self.orderList.takeItem(self.orderList.indexFromItem(item).row())

    def calc_total(self):
        """ Подсчитываем и выводим итоговую сумму заказа """
        qlist: QListWidget = self.orderList
        total = sum([qlist.item(i).obj.price for i in range(qlist.count())])
        self.totalSum.setText(str(total))

    def init_test_data(self):
        """ Добавляем тестовые данные """
        for category, products in CATEGORIES:
            category.save()
            for product in products:
                product.category = category
                product.save()
        self.setup_categories()
    
    def clear_cart(self):
        """Очищает корзину"""
        self.orderList.clear()
        self.calc_total()

    def submit_order(self):
        """ Завершаем выполнения заказа """
        if self.orderList.count() == 0:
            return
        
        cart_items = {}
        total_sum = 0
        
        for i in range(self.orderList.count()):
            item = self.orderList.item(i)
            product = item.obj 
            if product.id in cart_items:
                cart_items[product.id]['count'] += 1
            else:
                cart_items[product.id] = {
                    'product': product,
                    'count': 1,
                    'price': product.price
                }
            total_sum += product.price

        current_time = int(time.time())
        new_order = Order(None, current_time, total_sum)
        new_order.save()

        for data in cart_items.values():
            prod = data['product']
            count = data['count']
            price = data['price']
            order_product = OrderProduct(None, prod, price, count, new_order)
            order_product.save()

        self.clear_cart()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    mw = MyWindow()
    sys.exit(app.exec_())
