"""商品列表 + 排序自动化用例 —— 对应总览 INV / SORT 系列（除 INV-008 环境干扰外全覆盖）。"""
from playwright.sync_api import expect

from conftest import BACKPACK, BIKE_LIGHT


def test_inventory_list_content(inventory_page):  # INV-001 P0
    """列表 6 件商品：名称/描述/价格齐全，图片元素与 src 有效。

    注：不断言"图片加载完成"（naturalWidth）——实测无头环境下 6 张图全部未下载，
    用加载状态断言会产生假失败；图片显示正确性属视觉回归，交截图比对工具。
    """
    names = inventory_page.item_names()
    descs = inventory_page.item_descs()
    prices = inventory_page.item_prices()

    assert len(names) == 6, f"商品数应为 6，实际 {len(names)}"
    assert all(n.strip() for n in names), "存在空商品名"
    assert len(descs) == 6 and all(d.strip() for d in descs), "存在空描述"
    assert len(prices) == 6 and all(0 < p < 1000 for p in prices), f"价格异常：{prices}"
    assert inventory_page.images_have_src(), "存在 src 为空/缺失的商品图片"
    expect(inventory_page.page.locator(inventory_page.ITEM_IMG)).to_have_count(6)


def test_add_to_cart_badge_shows_1(inventory_page):  # INV-002 P0
    inventory_page.add_to_cart(BACKPACK)
    expect(inventory_page.page.locator(inventory_page.CART_BADGE)).to_have_text("1")


def test_remove_badge_disappears(inventory_page):  # INV-003 P0
    inventory_page.add_to_cart(BACKPACK)
    inventory_page.remove_from_cart(BACKPACK)
    assert inventory_page.badge_text() == ""


def test_add_two_badge_shows_2(inventory_page):  # INV-004 P0
    inventory_page.add_to_cart(BACKPACK)
    inventory_page.add_to_cart(BIKE_LIGHT)
    expect(inventory_page.page.locator(inventory_page.CART_BADGE)).to_have_text("2")


def test_sort_name_asc(inventory_page):  # SORT-001 P1
    inventory_page.sort_by("az")
    names = inventory_page.item_names()
    assert names == sorted(names), f"A→Z 排序错误，实际顺序：{names}"


def test_sort_name_desc(inventory_page):  # SORT-002 P1
    inventory_page.sort_by("za")
    names = inventory_page.item_names()
    assert names == sorted(names, reverse=True), f"Z→A 排序错误，实际顺序：{names}"


def test_sort_price_low_to_high(inventory_page):  # SORT-003 P1
    inventory_page.sort_by("lohi")
    prices = inventory_page.item_prices()
    assert prices == sorted(prices), f"价格低→高排序错误，实际：{prices}"


def test_sort_price_high_to_low(inventory_page):  # SORT-004 P1
    inventory_page.sort_by("hilo")
    prices = inventory_page.item_prices()
    assert prices == sorted(prices, reverse=True), f"价格高→低排序错误，实际：{prices}"


def test_sort_keeps_cart_button_state(inventory_page):  # SORT-005 P2
    """排序不应影响已加购商品的按钮状态与角标。"""
    page = inventory_page.page
    inventory_page.add_to_cart(BACKPACK)
    inventory_page.sort_by("lohi")

    expect(page.locator(f'[data-test="remove-{BACKPACK}"]')).to_be_visible()
    expect(page.locator(inventory_page.CART_BADGE)).to_have_text("1")
