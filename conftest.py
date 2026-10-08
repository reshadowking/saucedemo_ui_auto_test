"""全局 fixture：pytest-playwright 已自动提供 page / context / browser，
这里只封装业务级 fixture——和你接口框架 conftest 里"造数 fixture"同一思路。"""
import re

import pytest
from playwright.sync_api import Page, expect

from pages.login_page import LoginPage
from pages.inventory_page import InventoryPage
from pages.cart_page import CartPage

STANDARD_USER = "standard_user"
VALID_PASSWORD = "secret_sauce"
PROBLEM_USER = "problem_user"

# 商品 slug（列表页按钮选择器用）
BACKPACK = "sauce-labs-backpack"
BIKE_LIGHT = "sauce-labs-bike-light"
BOLT_TSHIRT = "sauce-labs-bolt-t-shirt"
# 商品显示名（购物车/详情断言用）
BACKPACK_NAME = "Sauce Labs Backpack"
BIKE_LIGHT_NAME = "Sauce Labs Bike Light"


@pytest.fixture
def login_page(page: Page) -> LoginPage:
    """未登录状态，停在登录页。"""
    lp = LoginPage(page)
    lp.open()
    return lp


@pytest.fixture
def inventory_page(page: Page) -> InventoryPage:
    """已登录商品列表页。UI 登录较贵，用例间必须隔离，所以是函数级。"""
    lp = LoginPage(page)
    lp.open()  # 别忘了先打开站点，否则在空白页上定位元素必然超时
    lp.login(STANDARD_USER, VALID_PASSWORD)
    inv = InventoryPage(page)
    inv.assert_loaded()
    return inv


@pytest.fixture
def cart_page(inventory_page) -> CartPage:
    """已登录 + 购物车内 1 件背包，停在购物车页（结账系列用例的公共起点）。"""
    inventory_page.add_to_cart(BACKPACK)
    inventory_page.open_cart()
    cart = CartPage(inventory_page.page)
    cart.assert_item_count(1)
    return cart


@pytest.fixture
def problem_user_page(page: Page) -> InventoryPage:
    """problem_user 登录后的商品列表页（预设缺陷账号，用于缺陷基线用例）。"""
    lp = LoginPage(page)
    lp.open()
    lp.login(PROBLEM_USER, VALID_PASSWORD)
    inv = InventoryPage(page)
    inv.assert_loaded()
    return inv
