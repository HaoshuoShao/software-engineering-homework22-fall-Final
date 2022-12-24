# 作者：邵豪硕
# 创建：2022-12-19
# 更新：2022-10-24
# 作用：包含了管理物品信息，用户信息数据的类以及图形界面

import sqlite3
import sys
from PyQt5.QtWidgets import QApplication, QLabel, QLineEdit, QPushButton, QVBoxLayout, QWidget, QCheckBox, QListWidget, QMessageBox, QComboBox

class Item:
    def __init__(self, name, description, location, phone, email, category, attributes):
        self.name = name
        self.description = description
        self.location = location
        self.contact_phone = phone
        self.contact_email = email
        self.item_type = category
        self.attributes = attributes

    
class User:
    def __init__(self, username, password, location, contact_phone, contact_email, is_admin=False, is_approved=False):
        self.username = username
        self.password = password
        self.location = location
        self.contact_phone = contact_phone
        self.contact_email = contact_email
        self.is_admin = is_admin
        self.is_approved = is_approved

    def __str__(self):
        return self.name
    

class ItemExchange:
    def __init__(self):
        # 连接数据库
        self.conn = sqlite3.connect("items.db")
        self.cursor = self.conn.cursor()

        # 创建数据表
        self.cursor.execute(
            """CREATE TABLE IF NOT EXISTS items (
                id INTEGER PRIMARY KEY, 
                name TEXT NOT NULL,
                description TEXT NOT NULL,
                location TEXT NOT NULL,
                contact_phone TEXT NOT NULL,
                contact_email TEXT NOT NULL,
                item_type TEXT NOT NULL,
                attributes TEXT NOT NULL
                )"""
                )

        self.conn.commit()

    def add_item(self, item):
        # 向数据表中插入新的物品信息
        self.cursor.execute(
            "INSERT INTO items (name, description, location, contact_phone, contact_email, item_type, attributes) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (item.name, item.description, item.location, item.contact_phone, item.contact_email, item.item_type, item.attributes)
        )
        self.conn.commit()

    def delete_item(self, item_id):
        # 从数据表中删除物品信息
        self.cursor.execute("DELETE FROM items WHERE id=%s"%item_id)
        self.conn.commit()

    def list_items(self):
        # 从数据表中查询物品信息
        self.cursor.execute("SELECT * FROM items")
        return self.cursor.fetchall()

    def search_items(self, item_type, keyword):
        # 从数据表中搜索物品信息
        self.cursor.execute(
            "SELECT * FROM items WHERE item_type=? AND (name LIKE ? OR description LIKE ?)",
            (item_type, f"%{keyword}%", f"%{keyword}%")
        )
        return self.cursor.fetchall()


class UserManage:
    def __init__(self):
        # 连接数据库
        self.conn = sqlite3.connect("users.db")
        self.cursor = self.conn.cursor()

        # 创建数据表
        self.cursor.execute(
            """CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                username TEXT NOT NULL,
                password TEXT NOT NULL,
                location TEXT NOT NULL,
                contact_phone TEXT NOT NULL,
                contact_email TEXT NOT NULL,
                is_admin INTEGER NOT NULL DEFAULT 0,
                is_approved INTEGER NOT NULL DEFAULT 0
            )"""
        )
        self.conn.commit()

    def register(self, user):
        # 向数据表中插入新的用户信息
        # self.cursor.execute(
        #     "INSERT INTO users (username, password, location, contact_phone, contact_email, is_admin, is_approved) VALUES (?, ?, ?, ?, ?, %d, %d)" %(int(user.is_admin), int(user.is_approved)), 
        #     (user.username, user.password, user.location, user.contact_phone, user.contact_email)
        # )
        self.cursor.execute(
            "INSERT INTO users (username, password, location, contact_phone, contact_email, is_admin, is_approved) VALUES (?, ?, ?, ?, ?, ?, ?)", 
            (user.username, user.password, user.location, user.contact_phone, user.contact_email, int(user.is_admin), int(user.is_approved))
        )
        self.conn.commit()

    def login(self, username, password):
        # 验证用户名和密码是否正确
        self.cursor.execute("SELECT * FROM users WHERE username=? AND password=? AND is_approved=1", (username, password))
        user = self.cursor.fetchone()
        if user:
            return True
        else:
            return False
        
    def login_is_admin(self, username, password):
        # 判断是否为管理员账户
        self.cursor.execute("SELECT * FROM users WHERE username=? AND password=? AND is_admin=1", (username, password))
        user = self.cursor.fetchone()
        if user:
            return True
        else:
            return False

    def approve_registration(self, user_id):
        # 审批新用户的注册请求
        self.cursor.execute("UPDATE users SET is_approved=1 WHERE id=?", (user_id,))
        self.conn.commit()

    def get_pending_users(self):
        # 返回全部未批准的用户注册列表
        self.cursor.execute(
            "SELECT * FROM users WHERE is_approved=0"
        )
        return self.cursor.fetchall()
    
    def get_all_users(self):
        # 返回全部未批准的用户注册列表
        self.cursor.execute(
            "SELECT * FROM users"
        )
        return self.cursor.fetchall()


class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()

        # 创建用户名标签和文本框
        self.username_label = QLabel("Username:")
        self.username_edit = QLineEdit()

        # 创建密码标签和文本框
        self.password_label = QLabel("Password:")
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.Password)

        # 创建登录按钮
        self.login_button = QPushButton("Login")

        # 创建注册按钮
        self.register_button = QPushButton("Register")

        # 使用垂直布局管理器将所有控件布置在窗口中
        layout = QVBoxLayout()
        layout.addWidget(self.username_label)
        layout.addWidget(self.username_edit)
        layout.addWidget(self.password_label)
        layout.addWidget(self.password_edit)
        layout.addWidget(self.login_button)
        layout.addWidget(self.register_button)
        self.setLayout(layout)

        # 创建 UserManage 对象
        self.user_manage = UserManage()

        # 为登录按钮绑定点击事件处理函数
        self.login_button.clicked.connect(self.handle_login)

        # 为注册按钮绑定点击事件处理函数
        self.register_button.clicked.connect(self.handle_register)

        # 创建错误信息提示
        self.error_window = ErrorWindow()
        
        # 创建用户注册界面
        self.register_window = RegisterWindow()

        # 创建管理员操作界面
        self.admin_window = AdminWindow()

        # 创建普通用户操作界面
        self.normal_window = NormalWindow()

    def handle_login(self):
        # 获取用户名和密码
        username = self.username_edit.text()
        password = self.password_edit.text()

        # 调用 UserManage 的 login 方法验证用户名和密码
        if self.user_manage.login(username, password):
            # 登陆成功
            # 如果需要，可以在这里判断用户是否是管理员或已被批准注册，然后打开相应的界面
            if self.user_manage.login_is_admin(username, password):
                self.admin_window.show()

            else:
                self.normal_window.get_user_info(str(username))
                self.normal_window.show()

        else:
            # 登录失败
            self.error_window.show()

    def handle_register(self):
    # 打开注册界面
        
        # 显示用户注册界面
        self.register_window.show()
         

class RegisterWindow(QWidget):
    def __init__(self):
        super().__init__()

        # 创建用户名标签和文本框
        self.username_label = QLabel("Username:")
        self.username_edit = QLineEdit()

        # 创建密码标签和文本框
        self.password_label = QLabel("Password:")
        self.password_edit = QLineEdit()

        # 创建地址标签和文本框
        self.location_label = QLabel("Location:")
        self.location_edit = QLineEdit()

        # 创建联系电话标签和文本框
        self.contact_phone_label = QLabel("Contact Phone:")
        self.contact_phone_edit = QLineEdit()

        # 创建联系邮箱标签和文本框
        self.contact_email_label = QLabel("Contact Email:")
        self.contact_email_edit = QLineEdit()

        # 创建注册管理员账户复选框
        self.is_admin_checkbox = QCheckBox("Register as admin")

        # 创建提交注册申请按钮
        self.submit_button = QPushButton("Submit Registration")
        self.submit_button.clicked.connect(self.handle_submit)

        # 使用垂直布局管理器将所有控件布置在窗口中
        layout = QVBoxLayout()
        layout.addWidget(self.username_label)
        layout.addWidget(self.username_edit)
        layout.addWidget(self.password_label)
        layout.addWidget(self.password_edit)
        layout.addWidget(self.location_label)
        layout.addWidget(self.location_edit)
        layout.addWidget(self.contact_phone_label)
        layout.addWidget(self.contact_phone_edit)
        layout.addWidget(self.contact_email_label)
        layout.addWidget(self.contact_email_edit)
        layout.addWidget(self.is_admin_checkbox)
        layout.addWidget(self.submit_button)
        self.setLayout(layout)

        # 创建 UserManage 对象
        self.register_user_manage = UserManage()

    def handle_submit(self):
    # 获取用户名和密码

        # 获取复选框的状态
        is_admin_state = self.is_admin_checkbox.isChecked()

        # 创建User类
        register_user = User(
            self.username_edit.text(), 
            self.password_edit.text(), 
            self.location_edit.text(),
            self.contact_phone_edit.text(), 
            self.contact_email_edit.text(), 
            False, 
            is_admin_state
            )

        # 将注册信息写入users.db
        self.register_user_manage.register(register_user)

        self.close()


class AdminWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.user_manage = UserManage()

        # 连接数据库
        self.conn = sqlite3.connect("items.db")
        self.cursor = self.conn.cursor()

        # 创建数据表
        self.cursor.execute(
            """CREATE TABLE IF NOT EXISTS item_types (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL
            )"""
        )
        self.conn.commit()

        # 创建物品类型列表控件
        self.item_type_list = QListWidget()
        self.refresh_item_type_list()

        # 创建/删除新的物品类型输入框和创建按钮
        self.new_item_type_edit = QLineEdit()
        self.create_item_type_button = QPushButton("Create Item Type")
        self.create_item_type_button.clicked.connect(self.handle_create_item_type)
        self.delete_item_type_button = QPushButton("Delete Item Type")
        self.delete_item_type_button.clicked.connect(self.handle_delete_item_type)

        # 创建未被批准用户列表控件
        self.pending_user_list = QListWidget()
        self.refresh_pending_user_list()

        # 创建批准用户申请按钮
        self.approve_user_button = QPushButton("Approve User")
        self.approve_user_button.clicked.connect(self.handle_approve_user)

        # 使用垂直布局管理器将所有控件布置在窗口中
        layout = QVBoxLayout()
        layout.addWidget(self.item_type_list)
        layout.addWidget(self.new_item_type_edit)
        layout.addWidget(self.create_item_type_button)
        layout.addWidget(self.delete_item_type_button)
        layout.addWidget(self.pending_user_list)
        layout.addWidget(self.approve_user_button)
        self.setLayout(layout)

    def refresh_pending_user_list(self):
    # 使用数据库API查询数据库中的未被批准用户
        users = self.user_manage.get_pending_users()

    # 更新未被批准用户列表
        self.pending_user_list.clear()
        for user in users:
            self.pending_user_list.addItem(str(user[0])+' '+user[1])

    def handle_approve_user(self):
        # 获取当前选中的用户
        selected_users = self.pending_user_list.selectedItems()
        if not selected_users:
            # 如果没有选中任何用户，显示提示信息
            QMessageBox.warning(self, "Warning", "No user selected.")
            return

        # 获取选中用户的用户名
        userid_and_name = selected_users[0].text()

        # 使用切片操作提取字符串开头的数字
        userid = ''
        for c in userid_and_name:
            if not c.isdigit():
                break
            userid += c

        # 使用 UserManage 类的 approve_registration 方法批准用户申请
        self.user_manage.approve_registration(userid)

        # 刷新未被批准用户列表
        self.refresh_pending_user_list()

    def handle_create_item_type(self):
        # 获取新的物品类型名称
        new_item_type_name = self.new_item_type_edit.text()

        # 将新的物品类型添加到数据库中
        self.conn = sqlite3.connect("items.db")
        self.cursor = self.conn.cursor()

        self.cursor.execute("INSERT INTO item_types (name) VALUES (?)", (new_item_type_name,))
        self.conn.commit()

        # 清空新的物品类型输入框
        self.new_item_type_edit.setText("")

        # 刷新物品类型列表
        self.refresh_item_type_list()

    def handle_delete_item_type(self):
        # 获取当前选中的物品类型名称
        selected_item_type = self.item_type_list.currentItem().text()

        # 使用DELETE语句从item_type数据表中删除物品类型
        self.cursor.execute("DELETE FROM item_types WHERE name=?", (selected_item_type,))
        self.conn.commit()

        # 刷新物品类型列表
        self.refresh_item_type_list()

    def refresh_item_type_list(self):
        # 从数据库中查询所有物品类型
        self.conn = sqlite3.connect("items.db")
        self.cursor = self.conn.cursor()

        self.cursor.execute("SELECT * FROM item_types")
        item_types = self.cursor.fetchall()

        # 清空物品类型列表
        self.item_type_list.clear()

        # 将物品类型添加到物品类型列表中
        for item_type in item_types:
            item_type_id, item_type_name = item_type
            self.item_type_list.addItem(item_type_name)


class ErrorWindow(QWidget):
    def __init__(self):
        super().__init__()

        # 创建错误提示文本框
        self.error_label = QLabel("Error: Invalid User or Password doesn\'t match")

        # 创建提交注册申请按钮
        self.close_button = QPushButton("Try Again")
        self.close_button.clicked.connect(self.close)

        # 使用垂直布局管理器将所有控件布置在窗口中
        layout = QVBoxLayout()
        layout.addWidget(self.error_label)
        layout.addWidget(self.close_button)
        self.setLayout(layout)


class NormalWindow(QWidget):
    def __init__(self):
        super().__init__()

        # 创建物品类型选择框
        self.item_type_label = QLabel("Item Type:")
        self.item_type_combobox = QComboBox()
        for item_type in self.get_item_types():
            self.item_type_combobox.addItem(item_type[0])

        # 创建物品名称标签和文本框
        self.item_name_label = QLabel("Item Name:")
        self.item_name_edit = QLineEdit()

        # 创建物品描述标签和文本框
        self.item_description_label = QLabel("Item Description:")
        self.item_description_edit = QLineEdit()

        # 创建物品属性标签和文本框
        self.item_attributes_label = QLabel("Item Attributes:")
        self.item_attributes_edit = QLineEdit()

        # 创建添加物品按钮
        self.add_item_button = QPushButton("Add Item")
        self.add_item_button.clicked.connect(self.handle_add_item)

        # 创建物品搜索范围类型选择框
        self.search_item_type_label = QLabel("Search Item Type:")
        self.search_item_type_combobox = QComboBox()
        for item_type in self.get_item_types():
            self.search_item_type_combobox.addItem(item_type[0])

        # 创建物品搜索标签和文本框
        self.search_label = QLabel("Search:")
        self.search_edit = QLineEdit()

        # 创建搜索按钮
        self.search_button = QPushButton("Search")
        self.search_button.clicked.connect(self.handle_search)

        # 创建物品列表
        self.item_list = QListWidget()

        # 创建删除物品按钮
        self.delete_item_button = QPushButton("Delete Item")
        self.delete_item_button.clicked.connect(self.handle_delete_item)

        # 创建更新列表按钮
        self.update_item_button = QPushButton("Update Item")
        self.update_item_button.clicked.connect(self.refresh_item_list)

        # 使用垂直布局管理器将所有控件布置在窗口中
        layout = QVBoxLayout()
        layout.addWidget(self.item_type_label)
        layout.addWidget(self.item_type_combobox)
        layout.addWidget(self.item_name_label)
        layout.addWidget(self.item_name_edit)
        layout.addWidget(self.item_description_label)
        layout.addWidget(self.item_description_edit)
        layout.addWidget(self.item_attributes_label)
        layout.addWidget(self.item_attributes_edit)
        layout.addWidget(self.add_item_button)
        layout.addWidget(self.search_item_type_label)
        layout.addWidget(self.search_item_type_combobox)
        layout.addWidget(self.search_label)
        layout.addWidget(self.search_edit)
        layout.addWidget(self.search_button)
        layout.addWidget(self.item_list)
        layout.addWidget(self.delete_item_button)
        layout.addWidget(self.update_item_button)
        self.setLayout(layout)

        # 创建ItemExchange实例
        self.item_exchange = ItemExchange()
        self.user_manage = UserManage()
        self.current_user = User('', '', '', '', '')

    def refresh_item_list(self):
        # 获取物品列表
        items_list = []
        items_attr = ['Name: ', 'Des: ', 'Address: ', 'Phone: ', 'Email: ', 'Type: ', 'Remarks: ', '']
        
        for tuple_items in self.item_exchange.list_items():
            tmp = ''
            j = 0
            for attr in tuple_items:
                tmp += (str(attr)+'    '+items_attr[j])
                j += 1
            items_list.append(tmp)

        # 清空物品列表控件
        self.item_list.clear()

        # 将物品添加到物品列表控件中
        for item in items_list:
            self.item_list.addItem(item)

    def get_user_info(self, name_user):
        #TODO 有bug
        list_user = self.user_manage.get_all_users()

        for user in list_user:
            if user[1] == name_user:
                (username, 
                password, 
                location, 
                contact_phone, 
                contact_email, 
                is_admin, 
                is_approved) = user[1:]
                break
        
        self.current_user = \
                  User(username, 
                    password, 
                    location, 
                    contact_phone, 
                    contact_email, 
                    is_admin, 
                    is_approved)
        
    def get_item_types(self):
        # 从数据库中查询所有物品类型
        self.conn = sqlite3.connect("items.db")
        self.cursor = self.conn.cursor()

        self.cursor.execute("SELECT name FROM item_types")
        return self.cursor.fetchall()
        
    def handle_add_item(self):
        # 获取用户输入的物品信息
        item_type = self.item_type_combobox.currentText()
        item_name = self.item_name_edit.text()
        item_description = self.item_description_edit.text()
        item_attributes = self.item_attributes_edit.text()

        # 使用 ItemExchange 类的 add_item() 方法将物品信息添加到数据库中
        new_item = Item(item_name, 
                item_description, 
                self.current_user.location, 
                self.current_user.contact_phone, 
                self.current_user.contact_email,
                item_type, 
                item_attributes
                )
        self.item_exchange.add_item(new_item)

        # 刷新物品列表
        self.refresh_item_list()

    def handle_search(self):
        # 获取搜索框中的文本
        search_item_type = self.search_item_type_combobox.currentText()
        search_text = self.search_edit.text()

        # 使用 ItemExchange 类的 search_items() 方法搜索符合条件的物品
        items = self.item_exchange.search_items(search_item_type, search_text)

        # 清空物品列表
        self.item_list.clear()

        # 将搜索结果添加到物品列表中
        items_list = []
        for tuple_items in items:
            tmp = ''
            for attr in tuple_items:
                tmp += (str(attr)+' ')
            items_list.append(tmp)

        for item_str in items_list:
            self.item_list.addItem(item_str)

    def handle_delete_item(self):
        # 获取当前选中的物品名称
        selected_item = self.item_list.currentItem().text()

        # 使用切片操作提取字符串开头的数字
        item_id = ''
        for c in selected_item:
            if not c.isdigit():
                break
            item_id += c

        # 调用ItemExchange的
        self.item_exchange.delete_item(item_id)

        # 刷新物品类型列表
        self.refresh_item_list()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LoginWindow()
    window.show()
    sys.exit(app.exec_())