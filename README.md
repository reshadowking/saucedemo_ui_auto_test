# SauceDemo UI 自动化（pytest-playwright + PO 模式）

> 隶属「SauceDemo 电商网站功能测试实践」项目：把功能测试阶段沉淀的 57 条用例中 P0/P1 核心链路自动化。
> 用例编号与《SauceDemo-57条用例总览.md》一一对应。

## 目录结构

```
playwright_ui/
├── pytest.ini            # base_url 配置
├── conftest.py           # 业务 fixture：login_page / inventory_page / cart_page
├── pages/                # PO 层：元素 + 行为封装，用例层不出现 selector
│   ├── base_page.py      # 基类：跳转 + 顶栏汉堡菜单（所有登录后页面共用）
│   ├── login_page.py
│   ├── inventory_page.py # 列表、排序、打开详情
│   ├── detail_page.py    # 商品详情页
│   └── cart_page.py      # 购物车 + 结账三页（信息页/概览页/完成页）
├── test_cases/           # 用例层：只有业务语言（共 58 条）
│   ├── test_login.py               # TC-LOGIN-001~015 全 15 条
│   ├── test_inventory.py           # INV-001~004 + SORT-001~005
│   ├── test_detail.py              # DETAIL-001~004
│   ├── test_cart.py                # CART-001~005
│   ├── test_menu.py                # MENU-001~006
│   ├── test_problem_user.py        # problem_user 缺陷基线（INV-005/006/007 + CHECKOUT-PU）
│   ├── test_checkout.py            # 结账主链路 P0
│   ├── test_checkout_validation.py # 校验矩阵（参数化 12 条 → 3 个函数）
│   └── test_checkout_summary.py    # Cancel 行为 / 税额 / 完成页 / 按钮恢复
└── requirements.txt
```

## 环境准备（一次性）

```bash
pip install -r requirements.txt
playwright install chromium
```

## 运行

> ⚠️ 以下命令必须在 `playwright_ui` 目录内执行（`pytest.ini` 与 `conftest.py` 都在这层）。
> 在上层目录裸跑 `pytest` 会导致配置不加载、`--base-url` 失效，全部用例在 setup 阶段 ERROR。

```bash
cd playwright_ui             # 先切到本目录！

pytest                       # 无头跑全部
pytest --headed              # 有头，肉眼看浏览器操作
pytest test_cases/test_login.py -v
pytest --tracing=retain-on-failure          # 失败留 trace
playwright show-trace <test-results下的trace.zip>   # 回放失败步骤
```

在 `playwright_ui` 目录内运行时，日志头部应能看到这两行才算配置生效：

```
baseurl: https://www.saucedemo.com
configfile: pytest.ini
```

失败用例的截图/录像自动存 `test-results/`。

## 用例映射表

| 脚本用例 | 总览编号 | 优先级 | 说明 |
| --- | --- | --- | --- |
| test_login_success | TC-LOGIN-001 | P0 | 标准登录 → /inventory.html |
| test_login_failure[locked] | TC-LOGIN-002 | P1 | 锁定账号提示 |
| test_login_failure[wrong_pass] | TC-LOGIN-003 | P1 | 密码错误提示 |
| test_login_failure[empty_user] | TC-LOGIN-004 | P1 | 用户名为空提示 |
| test_login_failure[empty_pwd] | TC-LOGIN-005 | P1 | 密码为空提示 |
| test_login_failure[both_empty] | TC-LOGIN-006 | P2 | 都为空提示 |
| test_password_masked | TC-LOGIN-012 | P3 | 密码框掩码 |
| test_enter_key_triggers_login | TC-LOGIN-014 | P2 | Enter 触发登录 |
| test_add_to_cart_badge_shows_1 | INV-002 | P0 | 加购 → 角标 1 |
| test_remove_badge_disappears | INV-003 | P0 | 移除 → 角标消失 |
| test_add_two_badge_shows_2 | INV-004 | P0 | 加两件 → 角标 2 |
| test_sort_name_asc | SORT-001 | P1 | 名称 A→Z |
| test_sort_price_low_to_high | SORT-003 | P1 | 价格低→高 |
| test_checkout_main_flow | CART+CHECKOUT | P0 | 加购→购物车→结账→完成页 |
| test_checkout_required_field | CHECKOUT-003/004/005/010 | P1 | 必填校验矩阵（缺哪项报哪项，不放行） |
| test_checkout_invalid_value_accepted | CHECKOUT-006/007/008/009 | P2 | 非法/边界值被放行 → 缺陷基线 |
| test_checkout_xss_escaped | CHECKOUT-006-X | — | 脚本 payload 按字面处理、无弹窗 |
| test_cancel_on_info_returns_to_cart | CHECKOUT-002 | P1 | 信息页 Cancel → 回购物车 |
| test_cancel_on_overview_returns_to_products | 实测补充 | — | **概览页 Cancel → 回商品列表**（与用例原描述不同） |
| test_tax_and_total_calculation | CHECKOUT-014 | P1 | 小计=车内价格；税=8%；总价=小计+税 |
| test_complete_page_three_elements | CHECKOUT-012 | P1 | 完成页三要素（文案/Back Home/Pony 图） |
| test_buttons_restored_after_order | CHECKOUT-013 | P2 | 下单后 6 个按钮恢复、角标清空 |

> 第三批已完成（2026-10-08）：登录补齐 15/15、列表/排序/详情/购物车/菜单全模块 + problem_user 缺陷基线。
> 累计 **58 条自动化用例**：覆盖 57 条用例中的 **55 条**（另 2 条环境干扰类手工保留）+ 2 条附加缺陷基线实验 + 1 条实测补充。
> 模块分布：登录 15 / 列表 4 / 排序 5 / 详情 4 / 购物车 5 / 菜单 6 / 结账 15 / problem_user 基线 4。

## 调试观察：把自动化"跑给你看"（学习期常用）

默认无头模式一~两分钟跑完 58 条，看着"一闪一闪"是正常现象（无 sleep + 自动等待 + 每用例独立 context）。
想看清每一步，按需组合：

```bash
pytest -v                                   # 打印每条用例名（不再只有点）
pytest --headed -v                          # 有头 + 用例名
pytest --headed --slowmo=1000               # 慢动作：每次操作前停顿 1 秒，肉眼逐步跟
pytest test_cases/test_checkout.py --headed --slowmo=800 -v   # 单条调试推荐组合
pytest -s                                   # 显示代码里的 print 输出（打日志用）
pytest --tracing=on --headed                # 录制全链路 trace，事后回放
playwright show-trace test-results/<用例目录>/trace.zip   # 事后逐步回放：DOM 快照+网络+控制台
```

学习期建议：先 `--headed --slowmo=800 -v` 单条跟一遍业务流，再用 `--tracing` 回放看每一步 DOM。
CI/回归阶段则保持默认无头——快才是自动化的价值。

## 排错实录（新人教材，真实案例）

1. **6 条用例 ERROR、全套件跑 5 分钟**：fixture 里忘了先 `open()`，在 about:blank 上定位元素，每条烧满 30s 自动等待超时。教训：fixture 也要走完整业务前置；"等待超时 30s" 要看是不是定位在错误的页面上。
2. **排序下拉框定位不到**：data-test 值是连字符 `product-sort-container`，写成下划线即失配。教训：选择器拿不准时用 `locator.count()` 即时验证（不触发等待）。
3. **测试跑完进程退出慢**：Windows + Chromium 驱动的已知现象（超时错误后驱动连接会楔死），不影响用例结果。判别方法：看日志是否已输出到 100%——到了就是全部执行完，直接看结果即可。
4. **全部 14 条 ERROR，报错 `Cannot navigate to invalid URL`**：在上层目录裸跑 `pytest`，`pytest.ini` 没被加载，`--base-url` 失效，`page.goto("/")` 变成非法 URL。教训：**pytest 的根目录由参数/当前目录决定，配置文件必须是"被找到的那一个"**——先 `cd playwright_ui`，或看日志头有无 `baseurl` / `configfile` 两行自检。
5. **重构 PO 后旧用例 FAILED：`AttributeError: 'CartPage' object has no attribute 'checkout_flow'`**：第二批重写 `cart_page.py` 时把 `checkout_flow()` 拆成了 `go_checkout/submit_info/click_finish`，但 `test_checkout.py` 仍在调用老方法；当时只跑了新增的两个文件、没跑全量，所以第一次跑全量才暴露。教训：**改 `pages/` 属于影响面不确定的改动，必须跑全量回归**——这正是 CI 跑全量而不仅跑改动文件的原因。
6. **断言"图片加载完成"造成假失败**：INV-001 用 `naturalWidth > 0` 判断图片是否显示，无头环境下 6 张图全部 `complete=False`（资源未下载）→ FAILED。教训：**断言要断业务事实，不要断资源加载状态**；"图片显示是否正确"属视觉回归，交截图比对工具。
7. **拿外部依赖做断言**：MENU-003 原写法为"点击 About 后断言打开了新标签页"，实测是**同页跳转**到外站 saucelabs.com → popup 等待超时；且外站曾返回 403。教训：**外站内容与跳转方式都不可控**（外站改个 `target` 就能让你变红），断言改为校验链接 `href` 目标，不发起外站请求。
8. **公共常量到处重复定义**：新增 `test_detail.py` 时从 conftest 导入未定义的 `BIKE_LIGHT` → 收集期 ImportError、整套件中断。教训：**商品 slug / 账号等公共常量统一放 conftest**，别在各测试文件里各写一份；提交前用 `pytest --collect-only -q` 秒验导入与收集。

> 排错通用套路：先看**失败类型**——`FAILED` 是用例断言/代码错，`ERROR` 是 fixture 或 teardown 错；再用 `--tb=line` 一行定位出错行；涉及 DOM 就 `locator.count()` 秒验选择器；涉及时序就 `--headed --slowmo` 或 trace 回放；提交前用 `pytest --collect-only -q` 秒验导入与收集。

## 面试锚点

- PO 分层：页面改版只改 `pages/`，用例层零改动；公共顶栏（菜单）沉到 `BasePage`，避免每个页面重复实现。
- 自动等待：无一处 sleep，等待语义由 actionability 检查内建。
- 排错：失败自动截图/录像 + trace 回放（每步 DOM 快照）。
- 数据驱动：parametrize 复用同一条断言逻辑覆盖 12 组校验输入。
- **缺陷基线用例**：把 problem_user 预设缺陷、Reset 状态不同步、结账无格式校验固化为"锁缺陷"用例——产品一变更立刻转红。
- **实测修正用例**：写自动化时实测发现两处 Cancel 去向不同、About 实为同页跳转，回头修正了手工用例的描述偏差。
- **断言边界感**：断言业务事实而非资源加载/外站页面，避免假失败。
