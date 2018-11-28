from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pymongo
from lxml import etree
from urllib.parse import quote


KEYWORD = '包'


chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--headless')
browser = webdriver.Chrome(chrome_options=chrome_options)  # 声明浏览器
wait = WebDriverWait(browser, 10)

def get_page(page):
    print('...开始解析第%d页...' % page)
    '''
    翻页
    :return:
    '''
    try:
        if page > 1:
            bottonpage = wait.until(
                EC.presence_of_element_located((By.XPATH, '//div[@id="J_bottomPage"]/span[2]//input[@class="input-txt"]')))
            onclick = wait.until(
                EC.element_to_be_clickable((By.XPATH, '//div[@id="J_bottomPage"]/span[2]//a[@class="btn btn-default"]')))
            bottonpage.click()
            bottonpage.clear()
            bottonpage.send_keys(str(page))
            onclick.click()
            # time.sleep(5)
            wait.until(EC.presence_of_element_located((By.XPATH, '//ul[@class="gl-warp clearfix"]')))
            toss_page()
        else:
            browser.get(
                'https://search.jd.com/Search?keyword=' + quote(KEYWORD) + '=utf-8&qrst=1&rt=1&stop=1&vt=2&page=1&s=1&click=0')
            toss_page()
    except:
        print('...出错重新调用...')
        get_page(page)

def toss_page():
    '''
    实现页面下拉到最下面，并且解析
    :return:
    '''
    # print('...开始解析...')
    count = 0  # 设置默认循环次数
    while True:
        count += 1  # 设置循环一次
        if 0 < count <= 2:
            js = "document.documentElement.scrollTop=500000"  # 拖到最下面
            browser.execute_script(js)    # 拖拽动作
            html = browser.page_source
            html = etree.HTML(html)
            datas = html.xpath('//li[@class="gl-item"]')
            for data in datas:
                title = data.xpath('div/div[1]/a/@title')  #  商品名
                # print(title)
                price = data.xpath('div/div[3]//i/text()')     # 价格
                # print(price)
                comment = data.xpath('div/div[5]/strong/a/text()')   # 评论数
                # print(comment)
                shop = data.xpath('div/div[7]/span/a/text()')   # 商店名
                # print(shop)
                results = {
                    '商品名': ''.join(title),   # 用join 的原因是有些商品为空，容易报错，join同样可以达到索引的效果
                    '价格': ''.join(price),
                    '评论数': ''.join(comment),
                    '商店名': ''.join(shop)
                    }
                save_results(results)
        else:
            break

def save_results(res):
    '''
    保存到数据库
    MongDB
    '''
    client = pymongo.MongoClient(host='localhost', port=27017)    # 连接登录本地数据库
    db = client['JD']
    collection = db['bag']
    collection.insert(res)

if __name__ == '__main__':
    for i in range(1, 101):
        get_page(page=i)
        print('...保存完毕第%d页内容...' % i)
    browser.close()


