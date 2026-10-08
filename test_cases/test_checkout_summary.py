"""结账概览与完成页 —— 对应 CHECKOUT-002 / 012 / 013 / 014。

实测发现（2026-10-08）：两处 Cancel 去向不同——
  信息填写页 Cancel → /cart.html（与用例原描述一致）
  概览页   Cancel → /inventory.html（用例原描述未区分，本文件按实测行为断言，建议细化用例）
"""
import re

from playwright.sync_api import expect

TAX_RATE = 0.08  # SauceDemo 固定税率 8%


def test_cancel_on_info_returns_to_cart(cart_page):  # CHECKOUT-002（前半）
    cart_page.go_checkout()
    cart_page.page.locator(cart_page.CANCEL).click()
    expect(cart_page.page).to_have_url(re.compile(r".*cart\.html"))
    cart_page.assert_item_count(1)
    # 可再次进入结算
    cart_page.go_checkout()
    expect(cart_page.page.locator(cart_page.FIRST_NAME)).to_be_visible()


def test_cancel_on_overview_returns_to_products(cart_page):
    """实测行为：概览页 Cancel 回商品列表（非购物车）。"""
    cart_page.go_checkout()
    cart_page.submit_info("Tong", "Su", "100000")
    expect(cart_page.page).to_have_url(re.compile(r".*checkout-step-two\.html"))

    cart_page.page.locator(cart_page.CANCEL).click()
    expect(cart_page.page).to_have_url(re.compile(r".*inventory\.html"))


def test_tax_and_total_calculation(cart_page):  # CHECKOUT-014
    """小计应与购物车价格一致；税 = 小计 × 8%；总价 = 小计 + 税（全部用展示值校验，不硬编码）。"""
    cart_price = cart_page.item_prices()[0]
    cart_page.go_checkout()
    cart_page.submit_info("Tong", "Su", "100000")
    expect(cart_page.page.locator(cart_page.TOTAL)).to_be_visible()

    amounts = cart_page.summary_amounts()
    assert abs(amounts["subtotal"] - cart_price) <= 0.01, \
        f"概览页小计 {amounts['subtotal']} 与购物车价格 {cart_price} 不一致"

    expected_tax = round(amounts["subtotal"] * TAX_RATE, 2)
    assert abs(amounts["tax"] - expected_tax) <= 0.01, \
        f"税额不符：显示 {amounts['tax']}，按 8% 应为 {expected_tax}"

    assert abs(amounts["total"] - (amounts["subtotal"] + amounts["tax"])) <= 0.01, \
        f"总价不符：{amounts['total']} ≠ {amounts['subtotal']} + {amounts['tax']}"


def test_complete_page_three_elements(cart_page):  # CHECKOUT-012
    cart_page.go_checkout()
    cart_page.submit_info("Tong", "Su", "100000")
    cart_page.click_finish()
    cart_page.assert_complete_page()


def test_buttons_restored_after_order(cart_page):  # CHECKOUT-013
    """下单完成后回到列表：所有按钮恢复 Add to cart、购物车角标清空。"""
    cart_page.go_checkout()
    cart_page.submit_info("Tong", "Su", "100000")
    cart_page.click_finish()
    cart_page.back_to_products()

    page = cart_page.page
    expect(page.locator('[data-test^="add-to-cart-"]')).to_have_count(6)
    expect(page.locator('[data-test="shopping-cart-badge"]')).to_have_count(0)
