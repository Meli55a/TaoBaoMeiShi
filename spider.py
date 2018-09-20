import re

from pyquery import PyQuery as pq
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

# 不打开浏览器
options = Options()
options.add_argument('--headless')
options.add_argument('--disable-gpu')

browser = webdriver.Chrome(chrome_options=options)  # 创建一个Chrome浏览器实例
wait = WebDriverWait(browser, 10)


def search():
    """
    搜索
    """
    try:
        browser.get("https://www.taobao.com")  # 打开页面
        # 等待搜索框加载出来
        input_element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#q')))
        # 等待搜索按钮加载出来
        submit = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#J_TSearchForm > div.search-button > button')))
        input_element.send_keys("美食")
        submit.click()
        # 等待总页数加载出来
        total = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#mainsrp-pager > div > div > div > div.total')))
        get_products()
        return total.text
    except TimeoutException:
        return search()


def next_page(page_number):
    """
    获取的page_number数据
    :param page_number: 页码
    """
    try:
        # 获取下一页的input输入框
        next_page_input_element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#mainsrp-pager > div > div > div > div.form > input")))
        # 获取下一页的按钮
        submit = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#mainsrp-pager > div > div > div > div.form > span.btn.J_Submit")))
        # 清空输入框内容
        next_page_input_element.clear()
        # 输入框添加当前页
        next_page_input_element.send_keys(page_number)
        # 点击
        submit.click()
        # 等待数据列加载出来
        wait.until(EC.text_to_be_present_in_element(
            (By.CSS_SELECTOR, "#mainsrp-pager > div > div > div > ul > li.item.active > span"), str(page_number))
        )
        get_products()
    except TimeoutException:
        next_page(page_number)


def get_products():
    """
    解析
    """
    # 等待加载每个商品信息
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#mainsrp-itemlist .items .item")))
    # 获取页面源代码
    html = browser.page_source
    # 创建pq对象
    doc = pq(html)
    # 找到每一个商品
    items = doc("#mainsrp-itemlist .items .item").items()
    # 便利商品的信息
    for item in items:
        product = {
            "image": item.find(".pic .img").attr("src"),
            "price": item.find(".price").text(),
            "deal": item.find(".deal-cnt").text()[:-3],
            "title": item.find(".title").text(),
            "shop": item.find(".shop").text(),
            "location": item.find(".location").text(),
        }
        print(product)


def main():
    try:
        total = search()
        total = int(re.compile('(\d+)').search(total).group(1))
        for i in range(2, total + 1):
            next_page(i)
    except Exception as e:
        print(e)
    finally:
        browser.close()


if __name__ == '__main__':
    main()
