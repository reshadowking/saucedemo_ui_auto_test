"""侧边菜单用例 —— 对应总览 MENU-001~006（003 为降级自动化：只断言新标签打开）。"""
import re

from playwright.sync_api import expect

from conftest import BACKPACK
from pages.cart_page import CartPage


def test_menu_items_display_and_collapse(inventory_page):  # MENU-001 P2
    inventory_page.open_menu()
    inventory_page.assert_menu_items()   # 4 个菜单项齐全
    inventory_page.close_menu()          # 可收起


def test_all_items_returns_to_list(cart_page):  # MENU-002 P2
    cart_page.open_menu()
    cart_page.click_menu("All Items")
    expect(cart_page.page).to_have_url(re.compile(r".*inventory\.html"))


def test_about_link_target(inventory_page):  # MENU-003 P3（降级）
    """只断言 About 菜单项的链接目标，不点击、不断言外站内容。

    实测（2026-10-08）：点击 About 是**同页跳转**到 https://saucelabs.com/（并非新标签页，
    用例原描述需修正）；且外站曾返回 403，内容不可控——故只校验 href，不发起外站请求。
    """
    inventory_page.open_menu()
    href = inventory_page.page.locator(inventory_page.MENU_ITEMS["About"]).get_attribute("href")
    assert href and "saucelabs.com" in href, f"About 链接目标异常：{href}"


def test_logout_returns_to_login(inventory_page):  # MENU-004 P1
    page = inventory_page.page
    inventory_page.open_menu()
    inventory_page.click_menu("Logout")
    expect(page).to_have_url("https://www.saucedemo.com/")


def test_reset_app_state_ui_not_synced_defect(inventory_page):  # MENU-005 P2（缺陷基线）
    """实测（2026-10-08）：Reset 后角标清空，但已挂载页面的按钮仍是 Remove——UI 未同步；
    刷新后才恢复为 Add to cart。产品若修复此缺陷，本用例会转红，需同步更新。"""
    page = inventory_page.page
    inventory_page.add_to_cart(BACKPACK)
    expect(page.locator(inventory_page.CART_BADGE)).to_have_text("1")

    inventory_page.open_menu()
    inventory_page.click_menu("Reset App State")

    expect(page.locator(inventory_page.CART_BADGE)).to_have_count(0)      # 角标已清
    expect(page.locator(f'[data-test="remove-{BACKPACK}"]')).to_be_visible()  # 但按钮未同步

    page.reload()                                                          # 刷新后恢复
    expect(page.locator(".inventory_list")).to_be_visible()
    expect(page.locator(f'[data-test="add-to-cart-{BACKPACK}"]')).to_be_visible()


def test_cart_empty_after_reset(inventory_page):  # MENU-006 P3
    page = inventory_page.page
    inventory_page.add_to_cart(BACKPACK)
    inventory_page.open_menu()
    inventory_page.click_menu("Reset App State")
    page.reload()
    expect(page.locator(".inventory_list")).to_be_visible()

    inventory_page.open_cart()
    CartPage(page).assert_item_count(0)
