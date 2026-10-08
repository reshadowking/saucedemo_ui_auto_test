"""登录模块自动化用例 —— 对应《SauceDemo-57条用例总览》TC-LOGIN 系列（15 条全覆盖，
其中 009 为降级自动化：只断言登录成功，耗时不作断言）。"""
import re

import pytest
from playwright.sync_api import expect

from conftest import STANDARD_USER, VALID_PASSWORD
from pages.login_page import LoginPage

SUCCESS_CASES = [
    (STANDARD_USER, "TC-LOGIN-001"),
    ("problem_user", "TC-LOGIN-008"),             # 预设缺陷账号：登录环节本身正常
    ("performance_glitch_user", "TC-LOGIN-009"),  # 降级：登录成功即可，不做耗时断言（属性能范畴）
]
FAILURE_CASES = [
    # (用户名, 密码, 期望错误提示, 用例编号)
    ("locked_out_user", VALID_PASSWORD, "locked out", "TC-LOGIN-002"),
    (STANDARD_USER, "wrong_pass", "do not match", "TC-LOGIN-003"),
    ("", VALID_PASSWORD, "Username is required", "TC-LOGIN-004"),
    (STANDARD_USER, "", "Password is required", "TC-LOGIN-005"),
    ("", "", "Username is required", "TC-LOGIN-006"),
    ("bad_user", "bad_pass", "do not match", "TC-LOGIN-007"),
]


@pytest.mark.parametrize("user,tc", SUCCESS_CASES, ids=[c[1] for c in SUCCESS_CASES])
def test_login_success(login_page, user, tc):
    login_page.login_expect_success(user, VALID_PASSWORD)


@pytest.mark.parametrize(
    "user,pwd,msg,tc", FAILURE_CASES, ids=[c[3] for c in FAILURE_CASES]
)
def test_login_failure(login_page, user, pwd, msg, tc):
    login_page.login_expect_error(user, pwd, msg)


def test_password_masked(login_page):  # TC-LOGIN-012 P3
    assert login_page.password_masked()


def test_enter_key_triggers_login(login_page):  # TC-LOGIN-014 P2
    page = login_page.page
    page.locator(LoginPage.USERNAME).fill(STANDARD_USER)
    page.locator(LoginPage.PASSWORD).fill(VALID_PASSWORD)
    page.locator(LoginPage.PASSWORD).press("Enter")
    expect(page).to_have_url(re.compile(r".*inventory\.html"))


def test_direct_access_blocked_when_not_logged_in(login_page):  # TC-LOGIN-010 P1
    """未登录直接访问商品页 → 被拦回登录页（首页）。"""
    page = login_page.page
    page.goto("/inventory.html")
    expect(page).to_have_url("https://www.saucedemo.com/")
    expect(page.locator(LoginPage.LOGIN_BTN)).to_be_visible()


def test_direct_access_blocked_after_logout(inventory_page):  # TC-LOGIN-011 P2
    page = inventory_page.page
    inventory_page.open_menu()
    inventory_page.click_menu("Logout")
    expect(page).to_have_url("https://www.saucedemo.com/")

    page.goto("/inventory.html")
    expect(page).to_have_url("https://www.saucedemo.com/")


def test_tab_focus_moves_to_password(login_page):  # TC-LOGIN-013 P3
    page = login_page.page
    page.locator(LoginPage.USERNAME).click()
    page.keyboard.press("Tab")
    assert login_page.focused_field() == "password"


def test_error_can_be_closed(login_page):  # TC-LOGIN-015 P3
    login_page.login("", "")            # 先触发错误提示条
    expect(login_page.page.locator(LoginPage.ERROR)).to_be_visible()
    login_page.close_error()            # 点 × 关闭
