"""商品详情页 PO。
注意：详情页的加购按钮 data-test 是通用的 `add-to-cart`（无商品 slug，因页面只有一件商品），
加购后变为 `remove`——与列表页 `add-to-cart-<slug>` 的命名规则不同。"""
from playwright.sync_api import expect

from pages.base_page import BasePage


class DetailPage(BasePage):
    NAME = ".inventory_details_name"
    DESC = ".inventory_details_desc"
    PRICE = ".inventory_details_price"
    IMG = ".inventory_details_img"
    ADD = '[data-test="add-to-cart"]'
    REMOVE = '[data-test="remove"]'
    BACK = '[data-test="back-to-products"]'

    def assert_loaded(self, expected_name: str = None):
        expect(self.page.locator(self.NAME)).to_be_visible()
        expect(self.page.locator(self.DESC)).to_be_visible()
        expect(self.page.locator(self.PRICE)).to_be_visible()
        expect(self.page.locator(self.IMG)).to_be_visible()
        if expected_name is not None:
            expect(self.page.locator(self.NAME)).to_have_text(expected_name)

    def name(self) -> str:
        return self.page.locator(self.NAME).inner_text()

    def price(self) -> str:
        return self.page.locator(self.PRICE).inner_text()

    def url_has_id(self) -> bool:
        return "id=" in self.page.url

    def add_to_cart(self):
        self.page.locator(self.ADD).click()
        expect(self.page.locator(self.REMOVE)).to_be_visible()

    def back_to_products(self):
        self.page.locator(self.BACK).click()
        expect(self.page.locator(".inventory_list")).to_be_visible()
