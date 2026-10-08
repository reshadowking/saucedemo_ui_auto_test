"""结账主链路（P0）—— 对应总览 CHECKOUT-001（加购→购物车→填单→完成）。

注：本用例在第二批重构 cart_page.py 时曾因 API 变更（checkout_flow 被拆分为
go_checkout/submit_info/click_finish）而报 AttributeError——教训已记入 README 排错实录：
**改动 pages/ 之后必须跑全量回归**。
"""
from pages.cart_page import CartPage

BACKPACK = "sauce-labs-backpack"


def test_checkout_main_flow(inventory_page):  # CHECKOUT-001 P0
    cart = CartPage(inventory_page.page)

    inventory_page.add_to_cart(BACKPACK)
    inventory_page.open_cart()
    cart.assert_item_count(1)

    cart.go_checkout()
    cart.submit_info("Tong", "Su", "100000")
    cart.click_finish()
    cart.assert_complete_page()
