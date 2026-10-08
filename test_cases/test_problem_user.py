"""problem_user 预设缺陷账号的缺陷基线用例（INV-005/006/007 + CHECKOUT-PU）。

注意：这些用例断言的是"官方预设的缺陷行为"。产品若修复或行为变更，用例会转红——
这是设计如此（锁住缺陷现状），届时需评估是否更新用例。
"""
import re

from playwright.sync_api import expect

from conftest import BACKPACK
from pages.cart_page import CartPage


def test_all_product_images_are_same(problem_user_page):  # INV-005 P1
    srcs = problem_user_page.item_images()
    assert len(srcs) == 6, f"商品数应为 6，实际 {len(srcs)}"
    assert len(set(srcs)) == 1, f"预期所有图片为同一张，实际 {len(set(srcs))} 种：{set(srcs)}"


def test_list_detail_data_mismatch(problem_user_page):  # INV-006 P1
    list_name = problem_user_page.item_names()[0]
    detail = problem_user_page.open_first_item()
    detail.assert_loaded()
    assert detail.name() != list_name, f"预期列表/详情数据错位，实际一致（{list_name}）"


def test_can_open_detail(problem_user_page):  # INV-007 P1
    detail = problem_user_page.open_first_item()
    assert detail.url_has_id(), "详情页 URL 未携带商品 ID"


def test_lastname_locked_blocks_checkout(problem_user_page):  # CHECKOUT-PU
    """预设缺陷：lastname 输入框被锁定 → 无法进入结算（等价于"特定账号被阻断主流程"）。"""
    page = problem_user_page.page
    problem_user_page.add_to_cart(BACKPACK)
    problem_user_page.open_cart()

    cart = CartPage(page)
    cart.assert_item_count(1)
    cart.go_checkout()
    cart.fill_info("Tong", "Su", "100000")

    assert page.locator(cart.LAST_NAME).input_value() == "", "预期 lastname 无法输入（锁定）"

    cart.click_continue()
    expect(page).to_have_url(re.compile(r".*checkout-step-one\.html"))
    cart.expect_error("Last Name is required")
