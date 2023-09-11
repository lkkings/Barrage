import os
from abc import ABC, abstractmethod
from enum import Enum
import platform

from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait

from .setting import root


# 设置环境变量
os.environ['CHROME_DRIVER'] = os.path.join(root, 'chromedriver.exe')


class DriverClass(Enum):
    CHROME = "谷歌驱动"


class Driver(ABC):

    def __init__(self) -> None:
        self.driver = None
        self.event = {}

    def open(self, url: str):
        self.driver.get(url)

    @abstractmethod
    def inject(self, script: str, *args):
        pass

    def wait(self, css_selector: str, timeout=600):
        wait = WebDriverWait(self.driver, timeout)
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, css_selector)))

    def write(self, css_selector: str, text: str):
        pass

    def click(self, css_selector: str):
        pass

    def close(self):
        if self.driver:
            self.driver.quit()


class ChromeDriver(Driver):

    def __init__(self):
        super().__init__()
        self.driver = webdriver.Chrome()

    def inject(self, script: str, *args):
        if not os.path.exists(script):
            self.driver.execute_script(script, *args)
            return
        with open(script, "r", encoding="utf-8") as f:
            self.driver.execute_script(f.read(), *args)

    def write(self, css_selector: str, text: str):
        self.driver.find_element(By.CSS_SELECTOR, css_selector).send_keys(text)

    def click(self, css_selector: str):
        # 解决元素被覆盖
        wait = WebDriverWait(self.driver, 10)
        element = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, css_selector)))
        self.driver.execute_script("arguments[0].click();", element)


class DriverFactory:

    @staticmethod
    def create(driver: DriverClass) -> Driver:
        if driver.CHROME:
            return ChromeDriver()
