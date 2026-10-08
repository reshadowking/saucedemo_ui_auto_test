"""商品详情页用例 —— 对应总览 DETAIL-001~004。"""
from playwright.sync_api import expect

from conftest import BACKPACK, BIKE_LIGHT, BACKPACK_NAME, BIKE_LIGHT_NAME
from pages.cart_page import CartPage
from pages.inventory_page import InventoryPage


def test_detail_content_and_url(inventory_page):  # DETAIL-001 P1
    expected = inventory_page.item_names()[0]
    detail = inventory_page.open_first_item()
    detail.assert_loaded(expected_name=expected)
    assert detail.url_has_id(), f"详情页 URL 应含商品 ID，实际 {detail.page.url}"
    assert detail.price().startswith("$")


def test_detail_add_to_cart_updates_badge(inventory_page):  # DETAIL-002 P1
    detail = inventory_page.open_first_item()
    detail.add_to_cart()
    expect(inventory_page.page.locator(InventoryPage.CART_BADGE)).to_have_text("1")


def test_detail_add_then_back_keeps_state(inventory_page):  # DETAIL-003 P2
    """详情页加购 → 返回列表，加购状态保持。"""
    detail = inventory_page.open_first_item()
    detail.add_to_cart()
    detail.back_to_products()

    expect(inventory_page.page.locator(f'[data-test="remove-{BACKPACK}"]')).to_be_visible()
    expect(inventory_page.page.locator(InventoryPage.CART_BADGE)).to_have_text("1")


def test_detail_and_list_two_items_in_cart(inventory_page):  # DETAIL-004 P2
    """详情页加 A + 列表页加 B → 购物车应有 2 件。"""
    detail = inventory_page.open_first_item()
    detail.add_to_cart()
    detail.back_to_products()

    inventory_page.add_to_cart(BIKE_LIGHT)
    inventory_page.open_cart()

    cart = CartPage(inventory_page.page)
    cart.assert_item_count(2)
    names = cart.item_names()
    assert BACKPACK_NAME in names and BIKE_LIGHT_NAME in names
