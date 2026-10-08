"""登录页 Page Object：元素 = 类常量，行为 = 方法，用例层看不到任何 selector。"""
import re

from playwright.sync_api import expect

from pages.base_page import BasePage


class LoginPage(BasePage):
    USERNAME = '[data-test="username"]'
    PASSWORD = '[data-test="password"]'
    LOGIN_BTN = '[data-test="login-button"]'
    ERROR = '[data-test="error"]'
    ERROR_BUTTON = '[data-test="error-button"]'

    def login(self, username: str, password: str):
        self.page.locator(self.USERNAME).fill(username)
        self.page.locator(self.PASSWORD).fill(password)
        self.page.locator(self.LOGIN_BTN).click()

    def login_expect_success(self, username: str, password: str):
        """登录成功应跳到 /inventory.html（TC-LOGIN-001）。"""
        self.login(username, password)
        expect(self.page).to_have_url(re.compile(r".*inventory\.html"))

    def login_expect_error(self, username: str, password: str, message: str):
        """登录失败应弹出含 message 的错误条（TC-LOGIN-002~005）。"""
        self.login(username, password)
        expect(self.page.locator(self.ERROR)).to_be_visible()
        expect(self.page.locator(self.ERROR)).to_contain_text(message)

    def password_masked(self) -> bool:
        """密码框应为掩码输入（TC-LOGIN-012）。"""
        return self.page.locator(self.PASSWORD).get_attribute("type") == "password"

    def close_error(self):
        """手动关闭错误提示条（TC-LOGIN-015）。"""
        self.page.locator(self.ERROR_BUTTON).click()
        expect(self.page.locator(self.ERROR)).to_be_hidden()

    def focused_field(self) -> str:
        """当前焦点元素的 data-test（TC-LOGIN-013 校验 Tab 切换）。"""
        return self.page.evaluate("document.activeElement.getAttribute('data-test')")
