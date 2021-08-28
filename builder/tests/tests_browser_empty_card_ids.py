# pylint: disable=line-too-long, no-member
# -*- coding: utf-8 -*-

from builtins import super # pylint: disable=redefined-builtin

import six
import sys

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.wait import WebDriverWait

from django.contrib.auth import get_user_model
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.core.management import call_command

from ..models import InteractionCard

class BrowserEmptyCardIdTests(StaticLiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        super(BrowserEmptyCardIdTests, cls).setUpClass()

        options = Options()
        options.add_argument('-headless')

        cls.selenium = webdriver.Firefox(options=options)
        cls.selenium.implicitly_wait(10)

        get_user_model().objects.create_user(username='selenium', email='selenium@example.com', password='browsertesting', is_superuser=True) # nosec

        call_command('install_default_repository', silent=True)

        InteractionCard.objects.all().update(enabled=True)

        for card in InteractionCard.objects.all():
            card.update_card()

        InteractionCard.objects.all().delete()

        call_command('loaddata', '-v', '0', 'builder/fixtures/tests_browser_empty_card.json')

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()

        super(BrowserEmptyCardIdTests, cls).tearDownClass()

    def test_empty_card_ids(self): # pylint: disable=too-many-locals, too-many-statements
        try:
            self.selenium.get('%s%s' % (self.live_server_url, '/accounts/login/'))

            self.assertEqual('Login | Hive Mechanic', self.selenium.title)

            username_input = self.selenium.find_element_by_name("username")
            username_input.send_keys('selenium')

            password_input = self.selenium.find_element_by_name("password")
            password_input.send_keys('browsertesting')

            self.selenium.find_element_by_xpath('//button[@type="submit"]').click()

            WebDriverWait(self.selenium, 5).until(lambda driver: driver.find_element_by_class_name('mdc-top-app-bar__title'))

            WebDriverWait(self.selenium, 5).until(lambda driver: driver.find_element_by_xpath('//li[@data-href="/builder/games"]'))

            # Investigate why unable to click this link in Selenium...

            self.selenium.get('%s%s' % (self.live_server_url, '/builder/games'))

            WebDriverWait(self.selenium, 15).until(lambda driver: driver.find_element_by_xpath('//a[@href="/builder/activity/empty-id-test"]'))

            self.selenium.find_element_by_xpath('//a[@href="/builder/activity/empty-id-test"]').click()

            WebDriverWait(self.selenium, 15).until(lambda driver: driver.find_element_by_xpath('//span[@id="sequence_breadcrumbs"]'))

            self.assertEqual('Hive Mechanic', self.selenium.title)

            next_nodes = self.selenium.find_element_by_xpath('//div[@id="builder_next_nodes"]')

            WebDriverWait(self.selenium, 15).until(lambda driver: driver.find_element_by_xpath('//div[@data-node-id="response-test-2"]'))

            next_nodes.find_element_by_xpath('//div[@data-node-id="response-test-2"]').click()

            current_node = self.selenium.find_element_by_xpath('//div[@id="builder_current_node"]')

            current_card = current_node.find_element_by_xpath('//div[@data-node-id="response-test-2"]')

            name_input = current_card.find_element_by_css_selector('input[id$="_name_value"]')

            self.assertEqual(name_input.get_attribute('value'), 'Response Test')

            first_link = current_card.find_element_by_css_selector('button[id$="_patterns__action__0_edit"]')

            first_link.click()

            WebDriverWait(self.selenium, 15).until(lambda driver: driver.find_element_by_xpath('//div[@class="mdc-dialog mdc-dialog--open"]'))

            add_dialog = self.selenium.find_element_by_xpath('//div[@class="mdc-dialog mdc-dialog--open"]')
            add_item = add_dialog.find_element_by_css_selector('li[id$="choose_destination_item_add_card"]')

            add_item.click()

            WebDriverWait(self.selenium, 15).until(lambda driver: driver.find_element_by_xpath('//div[@id="add-card-dialog"]'))

            new_card_dialog = self.selenium.find_element_by_xpath('//div[@id="add-card-dialog"]')
            new_card_dialog_title = new_card_dialog.find_element_by_xpath('//div[@id="add-card-dialog"]//h2')

            self.assertEqual(new_card_dialog_title.get_attribute('innerHTML'), 'Add Card')

            card_title_name = new_card_dialog.find_element_by_xpath('//input[@id="add-card-name-value"]')

            self.assertEqual(card_title_name.get_attribute('value'), '')

            send_message_radio = new_card_dialog.find_element_by_xpath('//input[@type="radio"][@value="send-message"]')

            send_message_radio.click()

            self.assertEqual(card_title_name.get_attribute('value'), 'New Send Message Card')

            branch_radio = new_card_dialog.find_element_by_xpath('//input[@type="radio"][@value="branch"]')

            branch_radio.click()

            self.assertEqual(card_title_name.get_attribute('value'), 'New Branch Card')

            send_message_radio.click()

            self.assertEqual(card_title_name.get_attribute('value'), 'New Send Message Card')

            add_button = new_card_dialog.find_element_by_xpath('//button[@data-mdc-dialog-action="add_card"]')

            add_button.click()

            new_send_title = next_nodes.find_element_by_xpath('//div[@data-node-id="new-send-message-card"]/h6')

            self.assertEqual(new_send_title.text, 'New Send Message Card')

            # Testing second card

            current_card = current_node.find_element_by_xpath('//div[@data-node-id="response-test-2"]')

            second_link = current_card.find_element_by_css_selector('button[id$="_patterns__action__1_edit"]')

            second_link.click()

            WebDriverWait(self.selenium, 15).until(lambda driver: driver.find_element_by_xpath('//div[@class="mdc-dialog mdc-dialog--open"]'))

            add_dialog = self.selenium.find_element_by_xpath('//div[@class="mdc-dialog mdc-dialog--open"]')
            add_item = add_dialog.find_element_by_css_selector('li[id$="choose_destination_item_add_card"]')

            add_item.click()

            WebDriverWait(self.selenium, 15).until(lambda driver: driver.find_element_by_xpath('//div[@id="add-card-dialog"]'))

            new_card_dialog = self.selenium.find_element_by_xpath('//div[@id="add-card-dialog"]')
            new_card_dialog_title = new_card_dialog.find_element_by_xpath('//div[@id="add-card-dialog"]//h2')

            self.assertEqual(new_card_dialog_title.get_attribute('innerHTML'), 'Add Card')

            card_title_name = new_card_dialog.find_element_by_xpath('//input[@id="add-card-name-value"]')

            self.assertEqual(card_title_name.get_attribute('value'), '')

            send_message_radio = new_card_dialog.find_element_by_xpath('//input[@type="radio"][@value="send-message"]')

            branch_radio = new_card_dialog.find_element_by_xpath('//input[@type="radio"][@value="branch"]')

            branch_radio.click()

            self.assertEqual(card_title_name.get_attribute('value'), 'New Branch Card')

            send_message_radio.click()

            self.assertEqual(card_title_name.get_attribute('value'), 'New Send Message Card')

            add_button = new_card_dialog.find_element_by_xpath('//button[@data-mdc-dialog-action="add_card"]')

            add_button.click()

            next_send_title = next_nodes.find_element_by_xpath('//div[@data-node-id="new-send-message-card-1"]/h6')

            self.assertEqual(next_send_title.text, 'New Send Message Card')

            # Testing final card

            current_card = current_node.find_element_by_xpath('//div[@data-node-id="response-test-2"]')

            not_found_link = current_card.find_element_by_css_selector('button[id$="_not_found_action_edit"]')

            not_found_link.click()

            WebDriverWait(self.selenium, 15).until(lambda driver: driver.find_element_by_xpath('//div[@class="mdc-dialog mdc-dialog--open"]'))

            add_dialog = self.selenium.find_element_by_xpath('//div[@class="mdc-dialog mdc-dialog--open"]')
            add_item = add_dialog.find_element_by_css_selector('li[id$="choose_destination_item_add_card"]')

            add_item.click()

            WebDriverWait(self.selenium, 15).until(lambda driver: driver.find_element_by_xpath('//div[@id="add-card-dialog"]'))

            new_card_dialog = self.selenium.find_element_by_xpath('//div[@id="add-card-dialog"]')
            new_card_dialog_title = new_card_dialog.find_element_by_xpath('//div[@id="add-card-dialog"]//h2')

            self.assertEqual(new_card_dialog_title.get_attribute('innerHTML'), 'Add Card')

            card_title_name = new_card_dialog.find_element_by_xpath('//input[@id="add-card-name-value"]')

            self.assertEqual(card_title_name.get_attribute('value'), '')

            send_message_radio = new_card_dialog.find_element_by_xpath('//input[@type="radio"][@value="send-message"]')

            send_message_radio.click()

            self.assertEqual(card_title_name.get_attribute('value'), '')

            branch_radio = new_card_dialog.find_element_by_xpath('//input[@type="radio"][@value="branch"]')

            branch_radio.click()

            self.assertEqual(card_title_name.get_attribute('value'), 'New Branch Card')

            send_message_radio.click()

            self.assertEqual(card_title_name.get_attribute('value'), 'New Send Message Card')

            card_title_name.clear()

            self.assertEqual(card_title_name.get_attribute('value'), '')

            add_button = new_card_dialog.find_element_by_xpath('//button[@data-mdc-dialog-action="add_card"]')

            add_button.click()

            next_send_title = next_nodes.find_element_by_xpath('//div[@data-node-id="new-send-message-card-2"]/h6')

            self.assertEqual(next_send_title.text, 'New Send Message Card')
        except TimeoutException:
            print(self.selenium.execute_script("return document.body.outerHTML;"))

            print('--------')

            print(self.selenium.get_log('browser'))

            ex_type, ex_value, ex_traceback = sys.exc_info()

            six.reraise(ex_type, ex_value, ex_traceback)
