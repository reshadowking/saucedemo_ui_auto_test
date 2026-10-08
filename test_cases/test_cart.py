"""购物车用例 —— 对应总览 CART-001~005。"""
import re

from playwright.sync_api import expect

from conftest import BACKPACK, BIKE_LIGHT, BOLT_TSHIRT, BACKPACK_NAME, BIKE_LIGHT_NAME
from pages.cart_page import CartPage


def test_cart_content_matches_list(inventory_page):  # CART-001 P0
    """购物车内的名称/数量/价格与列表页一致。"""
    names = inventory_page.item_names()
    prices = inventory_page.item_prices()
    idx = names.index(BACKPACK_NAME)

    inventory_page.add_to_cart(BACKPACK)
    inventory_page.open_cart()
    cart = CartPage(inventory_page.page)

    cart.assert_item_count(1)
    assert cart.item_names() == [BACKPACK_NAME]
    assert cart.item_prices() == [prices[idx]], "购物车价格与列表页不一致"
    assert cart.cart_quantities() == ["1"]


def test_remove_one_of_two(inventory_page):  # CART-002 P1
    inventory_page.add_to_cart(BACKPACK)
    inventory_page.add_to_cart(BIKE_LIGHT)
    inventory_page.open_cart()

    cart = CartPage(inventory_page.page)
    cart.assert_item_count(2)

    cart.page.locator(f'[data-test="remove-{BACKPACK}"]').click()
    cart.assert_item_count(1)
    assert cart.item_names() == [BIKE_LIGHT_NAME]


def test_continue_shopping_keeps_state(cart_page):  # CART-003 P1
    cart_page.continue_shopping()
    expect(cart_page.page.locator(f'[data-test="remove-{BACKPACK}"]')).to_be_visible()
    expect(cart_page.page.locator('[data-test="shopping-cart-badge"]')).to_have_text("1")


def test_empty_cart_checkout_behavior(inventory_page):  # CART-004 P2
    """实测行为：空车点 Checkout 仍可进入信息填写页（无拦截、无提示）。
    注：手工记录中"结账页为空"是 Reset 缺陷场景下的现象，与纯空车不同。"""
    inventory_page.open_cart()
    cart = CartPage(inventory_page.page)
    cart.assert_item_count(0)

    cart.go_checkout()
    expect(cart.page).to_have_url(re.compile(r".*checkout-step-one\.html"))


def test_three_items_in_cart(inventory_page):  # CART-005 P2
    for slug in (BACKPACK, BIKE_LIGHT, BOLT_TSHIRT):
        inventory_page.add_to_cart(slug)
    expect(inventory_page.page.locator(inventory_page.CART_BADGE)).to_have_text("3")

    inventory_page.open_cart()
    CartPage(inventory_page.page).assert_item_count(3)
