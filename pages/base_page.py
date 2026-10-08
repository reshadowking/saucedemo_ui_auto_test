"""PO 基类：站点公共部分（顶栏汉堡菜单）+ 通用跳转。
注意：本类是全部页面的父类，改动它影响面最大——改完必须跑全量回归。"""
from playwright.sync_api import expect


class BasePage:
    # 顶栏菜单（所有登录后页面共用）
    BURGER = "#react-burger-menu-btn"
    MENU_CLOSE = "#react-burger-cross-btn"
    MENU_PANEL = ".bm-item-list"
    MENU_ITEMS = {
        "All Items": '[data-test="inventory-sidebar-link"]',
        "About": '[data-test="about-sidebar-link"]',
        "Logout": '[data-test="logout-sidebar-link"]',
        "Reset App State": '[data-test="reset-sidebar-link"]',
    }

    def __init__(self, page):
        self.page = page

    def open(self, path: str = "/"):
        """基于 pytest.ini 的 --base-url 跳转，换环境只改配置。"""
        self.page.goto(path)

    # ---------------- 顶栏菜单 ----------------
    def open_menu(self):
        self.page.locator(self.BURGER).click()
        expect(self.page.locator(self.MENU_PANEL)).to_be_visible()

    def assert_menu_items(self):
        for sel in self.MENU_ITEMS.values():
            expect(self.page.locator(sel)).to_be_visible()

    def close_menu(self):
        self.page.locator(self.MENU_CLOSE).click()
        expect(self.page.locator(self.MENU_PANEL)).to_be_hidden()

    def click_menu(self, label: str):
        self.page.locator(self.MENU_ITEMS[label]).click()
