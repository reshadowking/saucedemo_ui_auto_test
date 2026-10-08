"""结账输入校验系列 —— 参数化合并式写法（12 条用例 → 1 个文件）。

对应总览：CHECKOUT-003/004/005/010（必填校验）、006/007/008/009（格式与边界）、006-X（XSS）。
说明：CHECKOUT-006~009 的结论是"无任何格式校验"，因此断言的是**缺陷基线**——
      用例在"能进入概览页"时通过；一旦产品加了校验，这些用例会转红，提示回归需同步。
"""
import re

import pytest
from playwright.sync_api import expect

# (first, last, zip, 期望错误文案, 用例编号)
REQUIRED_CASES = [
    ("", "Su", "100000", "First Name is required", "CHECKOUT-003"),
    ("Tong", "", "100000", "Last Name is required", "CHECKOUT-004"),
    ("Tong", "Su", "", "Postal Code is required", "CHECKOUT-005"),
    ("", "", "", "First Name is required", "CHECKOUT-010"),
]

# (first, last, zip, 说明) —— 非法值当前被全部放行（无校验实锤，缺陷基线）
INVALID_CASES = [
    ("@@@", "Su", "abc", "CHECKOUT-006/008 特殊字符+字母邮编"),
    ("😀", "Su", "123", "CHECKOUT-006 emoji"),
    ("A" * 500, "Su", "100000", "CHECKOUT-009 超长 500 字符"),
    ("Tong", "Su", "123456", "CHECKOUT-007 邮编上边界 6 位"),
]


@pytest.mark.parametrize("first,last,zip_code,msg,tc", REQUIRED_CASES, ids=[c[4] for c in REQUIRED_CASES])
def test_checkout_required_field(cart_page, first, last, zip_code, msg, tc):
    """必填校验：缺哪项就提示哪项，且不放行到概览页。"""
    cart_page.go_checkout()
    cart_page.submit_info(first, last, zip_code)
    cart_page.expect_error(msg)
    expect(cart_page.page).to_have_url(re.compile(r".*checkout-step-one\.html"))


@pytest.mark.parametrize("first,last,zip_code,desc", INVALID_CASES, ids=[c[3] for c in INVALID_CASES])
def test_checkout_invalid_value_accepted(cart_page, first, last, zip_code, desc):
    """缺陷基线：非法/边界值被系统接受并流转到概览页（无格式校验）。"""
    cart_page.go_checkout()
    cart_page.submit_info(first, last, zip_code)
    expect(cart_page.page).to_have_url(re.compile(r".*checkout-step-two\.html"))
    expect(cart_page.page.locator(cart_page.TOTAL)).to_be_visible()


def test_checkout_xss_escaped(cart_page):
    """CHECKOUT-006-X：脚本 payload 被按字面处理，不弹窗、不执行，且流程照常流转。"""
    dialogs = []
    cart_page.page.on("dialog", lambda d: (dialogs.append(d.message), d.dismiss()))

    payload = "<script>alert(1)</script>"
    cart_page.go_checkout()
    cart_page.fill_info(payload, "Su", "100000")
    # 输入框内按字面保存，未被当作 HTML 执行
    assert cart_page.page.locator(cart_page.FIRST_NAME).input_value() == payload

    cart_page.click_continue()
    expect(cart_page.page).to_have_url(re.compile(r".*checkout-step-two\.html"))
    assert dialogs == [], f"出现弹窗，疑似 XSS 生效：{dialogs}"
