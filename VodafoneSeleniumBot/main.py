import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support import expected_conditions as EC
from time import sleep
import io
from PIL import Image
import img2pdf
import json


class Scrapper:
    def __init__(self):
        self.driver = webdriver.Chrome(ChromeDriverManager().install())

    def start_login(self):
        """
        Login method for passing OTP
        """
        self.driver.get("https://www.vodafone.com.tr/login")
        sleep(5)
        button_id = self.driver.find_element(By.ID, "onetrust-accept-btn-handler")
        button_id.click()
        sleep(5)
        username_field = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "input[name='data[1][msisdn]']")))
        password_field = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "input[name='data[1][password]']")))
        username = input("Telefon Numaranız: 05")
        password = input("Şifre: ")

        username_field.send_keys(username)
        password_field.send_keys(password)

        WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//*[@id='login_form_1']/div[5]/button"))).click()
        sleep(5)
        try:
            verification_code = input("Lütfen Telefonunuza Gelen Doğrulama Kodunu Giriniz: ")
            verification_code_field = WebDriverWait(self.driver, 15).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "input[name='data[2][otpCode]']"))
            )
            verification_code_field.send_keys(verification_code)
            submit_button = WebDriverWait(self.driver, 15).until(
                EC.element_to_be_clickable((By.XPATH, "//*[@id='login_form_2']/div[6]/button"))
            )

            submit_button.click()
        except Exception as e:
            print(f"Some error occurred {e}")

    def get_data(self):
        self.driver.get("https://online.vodafone.com.tr/yanimda/#/web/tarife-ve-kullanimlar")
        sleep(10)

    def save_data_as_pdf(self):
        self.driver.execute_script("window.scrollTo(0, 200);")
        sleep(5)
        self.driver.execute_script("document.body.style.zoom='60%';")
        self.driver.save_screenshot('screenshot.png')
        image = Image.open('screenshot.png')
        bytes_io = io.BytesIO()
        image.save(bytes_io, 'PNG')
        with open('output.pdf', 'wb') as f:
            f.write(img2pdf.convert(bytes_io.getvalue()))

    def parse_data(self):
        """
        Parse scraping content
        """
        categories = self.driver.find_elements(By.CLASS_NAME, "tariff__uses--content")
        my_list = []
        for category in categories:
            inner_dict = {}
            if category.text != "":
                split_list = category.text.split("\n")
                inner_dict[split_list[0]] = split_list[1]
                inner_dict["Kalan Kullanim"] = split_list[2]
                inner_dict["Status"] = split_list[3]
                inner_dict[split_list[4]] = split_list[5]
                inner_dict[split_list[6]] = split_list[7]
            if inner_dict != {}:
                my_list.append(inner_dict)
        encoded_json = self.json_encoder(my_list)
        self.save_file(encoded_json)

    def json_encoder(self, data):
        """
            Encode json data
        """
        encoded_json = json.dumps(data, ensure_ascii=False)
        return encoded_json.replace("\\n", "")

    def save_file(self, data):
        """
            It saves data to the file system
        """
        current_date = datetime.datetime.now()
        with open(f'data_{current_date}.json', 'w', encoding='utf-8') as f:
            json.dump(json.loads(data), f, ensure_ascii=False, indent=4)


scrapper = Scrapper()
scrapper.start_login()
sleep(10)
scrapper.get_data()
scrapper.save_data_as_pdf()
sleep(2)
scrapper.parse_data()
