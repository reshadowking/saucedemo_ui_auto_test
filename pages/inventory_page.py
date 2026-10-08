"""商品列表页 PO。item_slug 是商品 URL 代号，如 sauce-labs-backpack。
顶栏菜单方法来自 BasePage（open_menu/click_menu 等）。"""
import re

from playwright.sync_api import expect

from pages.base_page import BasePage
from pages.detail_page import DetailPage


class InventoryPage(BasePage):
    TITLE = "span.title"
    CART_BADGE = '[data-test="shopping-cart-badge"]'
    CART_LINK = '[data-test="shopping-cart-link"]'
    SORT = '[data-test="product-sort-container"]'
    ITEM_NAME = ".inventory_item_name"
    ITEM_DESC = ".inventory_item_desc"
    ITEM_PRICE = ".inventory_item_price"
    ITEM_IMG = ".inventory_item_img img"

    def assert_loaded(self):
        """页面加载完成的判据：URL + 标题（INV-001）。"""
        expect(self.page).to_have_url(re.compile(r".*inventory\.html"))
        expect(self.page.locator(self.TITLE)).to_have_text("Products")

    def add_to_cart(self, item_slug: str):
        self.page.locator(f'[data-test="add-to-cart-{item_slug}"]').click()

    def remove_from_cart(self, item_slug: str):
        self.page.locator(f'[data-test="remove-{item_slug}"]').click()

    def badge_text(self) -> str:
        """购物车角标数字；未加购时角标不存在，返回空串。"""
        badge = self.page.locator(self.CART_BADGE)
        return badge.inner_text() if badge.is_visible() else ""

    def sort_by(self, option: str):
        """option 取值：az / za / lohi / hilo。"""
        self.page.locator(self.SORT).select_option(option)

    def item_names(self) -> list:
        return self.page.locator(self.ITEM_NAME).all_inner_texts()

    def item_descs(self) -> list:
        return self.page.locator(self.ITEM_DESC).all_inner_texts()

    def item_prices(self) -> list:
        return [float(t.replace("$", "")) for t in self.page.locator(self.ITEM_PRICE).all_inner_texts()]

    def item_images(self) -> list:
        """所有商品图片的 src（用于 problem_user 同图缺陷断言）。"""
        return self.page.locator(self.ITEM_IMG).evaluate_all("els => els.map(e => e.getAttribute('src'))")

    def images_have_src(self) -> bool:
        """6 张图片元素都存在且 src 非空。

        注意：**不要**用 naturalWidth>0 断言"图片加载完成"——无头/CI 环境可能根本不下载图片
        资源（实测 6 张全部 complete=False），这样断言会制造假失败。
        "图片显示是否正确"属视觉回归范畴，交给截图比对工具；这里只保证元素与 src 有效。
        """
        srcs = self.item_images()
        return len(srcs) == 6 and all(s and s.strip() for s in srcs)

    def open_first_item(self) -> DetailPage:
        self.page.locator(self.ITEM_NAME).first.click()
        detail = DetailPage(self.page)
        detail.assert_loaded()
        return detail

    def open_item(self, name: str) -> DetailPage:
        self.page.locator(self.ITEM_NAME, has_text=name).click()
        detail = DetailPage(self.page)
        detail.assert_loaded()
        return detail

    def open_cart(self):
        self.page.locator(self.CART_LINK).click()
        expect(self.page.locator(".cart_list")).to_be_visible()
