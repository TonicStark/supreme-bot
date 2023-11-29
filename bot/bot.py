# Importing Libraries
from playwright.sync_api import sync_playwright, TimeoutError
import json
import playwright

# Creating the Bot Class


class Bot:

    # Constructor
    def __init__(self) -> None:

        # Opening the Items File
        with open("./config/items.json", "r") as i:

            # Loading the JSON File
            ITEMS: str = json.load(i)

            # Creating the Lists
            self.ITEMS_NAMES: list = []
            self.ITEMS_STYLES: list = []
            self.ITEMS_SIZES: list = []
            self.ITEMS_TYPES: list = []

            # Looping the JSON File
            for item in ITEMS:

                # Appending the Prameters to the Lists
                self.ITEMS_NAMES.append(item["name"])
                self.ITEMS_STYLES.append(item["color"])
                self.ITEMS_SIZES.append(item["size"])
                # Preventing tops/sweaters to make error in the link
                self.ITEMS_TYPES.append(item["category"].replace("/", "-"))

        # Opening the Data File
        with open("./config/pay.config.json", "r") as d:

            # Loading the JSON File
            DATA: str = json.load(d)

            # Looping the JSON File
            for info in DATA:

                # Storing Personal Data
                self.EMAIL: str = info["email"]
                self.COUNTRY: str = info["country"]
                self.FIRST_NAME: str = info["first_name"]
                self.LAST_NAME: str = info["last_name"]
                self.ADDRESS: str = info["address"]
                self.POSTAL_CODE: str = info["postal_code"]
                self.CITY: str = info["city"]
                self.PHONE: str = info["phone"]
                self.CARD_NUMBER: str = info["card_number"]
                self.MONTH_EXP: str = info["expiration_month"]
                self.YEAR_EXP: str = info["expiration_year"]
                self.CVV: str = info["cvv"]
                self.NAME_ON_CARD: str = info["name_on_card"]
                try:
                    self.ZONE: str = info["zone"]
                except Exception:
                    pass

        # Creating the Link's List
        self.links_list: list = []

    # Scrape Method for Saving the URLs
    def scrape(self) -> None:
        for i in range(len(self.ITEMS_NAMES)):
            url: str = f"https://jp.supreme.com/collections/{self.ITEMS_TYPES[i]}"
            print(f"Processing {self.ITEMS_NAMES[i]}...")

            with sync_playwright() as p:
                browser: playwright.sync_api._generated.Browser = p.chromium.launch(
                    headless=True, args=["--no-images"])
                page: playwright.sync_api._generated.Browser = browser.new_page()
                page.goto(url)  # Navigate to the URL

                # Wait for dynamic content to load (adjust the wait time as needed)
                page.wait_for_selector("a[data-cy-title]")

                # Extract the links using Playwright
                links: list = page.query_selector_all("a[data-cy-title]")
                links_list: list = [
                    link.get_attribute("href") for link in links]

                # Checking for the Right Links
                for link in links_list:
                    complete_link: str = f"https://jp.supreme.com{link}"
                    page.goto(complete_link)  # Navigate to the link

                    # Wait for the product info to load (adjust the wait time as needed)
                    page.wait_for_selector(
                        "#product-root > div > div.Product.width-100.js-product.routing-transition.fade-on-routing > div.product-column-right > form > div.width-100 > div > h1")

                    if product_name := page.query_selector(
                        "#product-root > div > div.Product.width-100.js-product.routing-transition.fade-on-routing > div.product-column-right > form > div.width-100 > div > h1"
                    ).inner_text():

                        product_style: str = page.query_selector(
                            "#product-root > div > div.Product.width-100.js-product.routing-transition.fade-on-routing > div.product-column-right > form > div.width-100 > div > div.display-flex.flexWrap-wrap.bpS-bg-none.bg-white.mobile-shadow.pt-m.pb-m.bpS-p-0.flexDirection-columnReverse.bpS-flexDirection-column > div.fontWeight-bold.mb-s.display-none.bpS-display-block.js-variant").inner_text()
                        if len(product_style) >= 2 and product_name == self.ITEMS_NAMES[i] and product_style == self.ITEMS_STYLES[i]:
                            self.links_list.append(complete_link)
                            break

                browser.close()

    # Method for Add to the Cart the founded Items

    def add_to_basket(self, page) -> None:

        # Looping the Element's to Buy List
        for i in range(len(self.links_list)):
            page.goto(self.links_list[i])
            if self.ITEMS_TYPES[i] == "bags":
                page.click("input[data-type='product-add']")
                page.wait_for_timeout(1000)
                continue
            page.wait_for_selector("select[data-cy='size-selector']")
            options = page.locator("select[data-cy='size-selector']")
            options.select_option(label=f"{self.ITEMS_SIZES[i]}")
            page.click("input[data-type='product-add']")
            page.wait_for_timeout(1000)

    # Method for Compiling the Checkout Form

    def checkout(self, page) -> None:

        # Going to the Checkout
        try:
            # Increased timeout
            page.click('#product-root > div > div.collection-nav.display-none.bpS-display-block > div > div > div > a.button.button--s.c-white.width-100.display-flex.bg-red--aa', timeout=60000)
        except TimeoutError:
            pass

        # Using Data to Compile the Form
        page.fill("input[id='email']", self.EMAIL)
        page.fill("input[name='firstName']", self.FIRST_NAME)
        page.fill("input[name='lastName']", self.LAST_NAME)
        page.fill("input[id='postalCode']", self.POSTAL_CODE)
        page.fill("input[name='address1']", self.ADDRESS)
        page.fill("input[name='address2']", "建物番号")
        page.fill("input[name='city']", self.CITY)
        page.fill("input[name='phone']", self.PHONE)
        try:
            page.wait_for_selector("select[name='zone']")
            options = page.locator("select[name='zone']")
            options.select_option(value="JP-13")  # 例として "JP-13" を選択
            page.wait_for_timeout(1500)  # 配送情報を待機
        except Exception as e:
            print(e)

       # カード番号のiframeを特定して、iframe内の要素にアクセスして値を入力
        page.frame_locator(
            "iframe[src*='checkout.shopifycs.com/number']").locator("input[name='number']").fill(self.CARD_NUMBER)
        # 有効期限のiframeを特定して、iframe内の要素にアクセスして値を入力
        page.frame_locator("iframe[src*='checkout.shopifycs.com/expiry']").locator(
            "input[name='expiry']").fill(f"{self.MONTH_EXP}/{self.YEAR_EXP}")
        # CVV番号のiframeを特定して、iframe内の要素にアクセスして値を入力
        page.frame_locator("iframe[src*='checkout.shopifycs.com/verification_value']").locator(
            "input[name='verification_value']").fill(self.CVV)
        # カード名義人の名前のiframeを特定して、iframe内の要素にアクセスして値を入力
        page.frame_locator(
            "iframe[src*='checkout.shopifycs.com/name']").locator("input[name='name']").fill(self.NAME_ON_CARD)
        # 入力されないことがあるので改め入力
        page.fill("input[name='firstName']", self.FIRST_NAME)
        # チェックボックスを特定してチェックを入れる
        # チェックボックスのラベルテキストを使って要素を特定してチェックを入れる
        page.evaluate(
            "() => document.querySelectorAll('input[type=checkbox]')[1].click()")

        # '購入する' ボタンをクリック
        page.click("button[type='submit']")
