# pylint: disable=line-too-long, no-member
# -*- coding: utf-8 -*-

from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.wait import WebDriverWait

from django.contrib.auth import get_user_model
from django.contrib.staticfiles.testing import StaticLiveServerTestCase

class BasicBrowserTests(StaticLiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        options = Options()
        options.add_argument('-headless')

        cls.selenium = webdriver.Firefox(options=options)
        cls.selenium.implicitly_wait(10)

        get_user_model().objects.create_user(username='selenium', email='selenium@example.com', password='browsertesting', is_superuser=True) # nosec

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super().tearDownClass()

    def test_login(self):
        self.selenium.get('%s%s' % (self.live_server_url, '/accounts/login/'))

        self.assertEqual('Login | Hive Mechanic', self.selenium.title)

        username_input = self.selenium.find_element_by_name("username")
        username_input.send_keys('selenium')

        password_input = self.selenium.find_element_by_name("password")
        password_input.send_keys('browsertesting')

        self.selenium.find_element_by_xpath('//button[@type="submit"]').click()

        WebDriverWait(self.selenium, 5).until(lambda driver: driver.find_element_by_class_name('mdc-top-app-bar__title'))
