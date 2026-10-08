"""购物车 + 结账三页 Page Object。
选择器全部经实测验证（含两处 Cancel 的真实去向差异）。"""
from playwright.sync_api import expect

from pages.base_page import BasePage


class CartPage(BasePage):
    # --- 购物车页 ---
    CART_ITEM = ".cart_item"
    CART_QUANTITY = ".cart_quantity"
    ITEM_NAME = ".inventory_item_name"
    ITEM_PRICE = ".inventory_item_price"
    CONTINUE_SHOPPING = '[data-test="continue-shopping"]'
    CHECKOUT_BTN = '[data-test="checkout"]'

    # --- 信息填写页（step one）---
    FIRST_NAME = '[data-test="firstName"]'
    LAST_NAME = '[data-test="lastName"]'
    POSTAL = '[data-test="postalCode"]'
    CONTINUE = '[data-test="continue"]'
    ERROR = '[data-test="error"]'

    # --- 概览页（step two）---
    SUBTOTAL = ".summary_subtotal_label"
    TAX = ".summary_tax_label"
    TOTAL = ".summary_total_label"
    FINISH = '[data-test="finish"]'

    # --- 完成页 ---
    COMPLETE_HEADER = ".complete-header"
    COMPLETE_TEXT = ".complete-text"
    PONY_IMAGE = ".pony_express"
    BACK_TO_PRODUCTS = '[data-test="back-to-products"]'

    # Cancel 按钮三页都有，用同一个选择器
    CANCEL = '[data-test="cancel"]'

    # ---------------- 购物车页 ----------------
    def assert_item_count(self, count: int):
        expect(self.page.locator(self.CART_ITEM)).to_have_count(count)

    def item_names(self) -> list:
        return self.page.locator(self.ITEM_NAME).all_inner_texts()

    def item_prices(self) -> list:
        return [float(t.replace("$", "")) for t in self.page.locator(self.ITEM_PRICE).all_inner_texts()]

    def cart_quantities(self) -> list:
        return self.page.locator(self.CART_QUANTITY).all_inner_texts()

    def continue_shopping(self):
        self.page.locator(self.CONTINUE_SHOPPING).click()
        expect(self.page.locator(".inventory_list")).to_be_visible()

    def go_checkout(self):
        self.page.locator(self.CHECKOUT_BTN).click()
        expect(self.page.locator(self.FIRST_NAME)).to_be_visible()

    # ---------------- 信息填写页 ----------------
    def fill_info(self, first: str, last: str, postal: str):
        self.page.locator(self.FIRST_NAME).fill(first)
        self.page.locator(self.LAST_NAME).fill(last)
        self.page.locator(self.POSTAL).fill(postal)

    def click_continue(self):
        self.page.locator(self.CONTINUE).click()

    def submit_info(self, first: str, last: str, postal: str):
        self.fill_info(first, last, postal)
        self.click_continue()

    def error_text(self) -> str:
        return self.page.locator(self.ERROR).inner_text()

    def expect_error(self, message: str):
        expect(self.page.locator(self.ERROR)).to_be_visible()
        expect(self.page.locator(self.ERROR)).to_contain_text(message)

    # ---------------- 概览页 ----------------
    def summary_amounts(self) -> dict:
        """返回 {'subtotal': 29.99, 'tax': 2.40, 'total': 32.39}（从 'Item total: $29.99' 解析）。"""
        def amount(sel: str) -> float:
            return float(self.page.locator(sel).inner_text().split("$")[1])

        return {
            "subtotal": amount(self.SUBTOTAL),
            "tax": amount(self.TAX),
            "total": amount(self.TOTAL),
        }

    def click_finish(self):
        self.page.locator(self.FINISH).click()
        expect(self.page.locator(self.COMPLETE_HEADER)).to_be_visible()

    # ---------------- 完成页 ----------------
    def assert_complete_page(self):
        """CHECKOUT-012：完成页三要素。"""
        expect(self.page.locator(self.COMPLETE_HEADER)).to_have_text("Thank you for your order!")
        expect(self.page.locator(self.COMPLETE_TEXT)).to_contain_text("has been dispatched")
        expect(self.page.locator(self.PONY_IMAGE)).to_be_visible()

    def back_to_products(self):
        self.page.locator(self.BACK_TO_PRODUCTS).click()
        expect(self.page.locator(".inventory_list")).to_be_visible()
