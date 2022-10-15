import unittest
from selenium import webdriver
from selenium.webdriver.common.keys import Keys


class PythonOrgSearch(unittest.TestCase):

    def setUp(self):
        self.driver = webdriver.Firefox(
            executable_path=r'C:\Program Files\Mozilla Firefox\geckodriver.exe',
            firefox_binary=r'C:\Program Files\Mozilla Firefox\firefox.exe'
        )

    def test_search_in_python_org(self):
        driver = self.driver
        driver.get("https://www.python.org")
        self.assertIn("Python", driver.title)
        elem = driver.find_element("name", "q")
        elem.send_keys("pycon")
        assert "No results found." not in driver.page_source
        elem.send_keys(Keys.RETURN)

    def tearDown(self):
        self.driver.close()


if __name__ == "__main__":
    unittest.main()
