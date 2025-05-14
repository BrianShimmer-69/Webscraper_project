################################################################################
#                                                                              #  
#                                  Unittests                                   #                                     
#                                                                              #  
#  36122 Python Programming - 1st Semester 2025                                #
#                                                                              #  
#  Dan Hansen                    - Student ID 24718999                         #  
#  Brian Shimmer Bino Deva Kumar - Student ID 25752306                         #  
#  David Pawley                  - Student ID 92072368                         #  
#  Maximus Chandrasekaran        - Student ID 25614189                         #  
#                                                                              #  
################################################################################

import unittest
from unittest.mock import patch, MagicMock
from Assignment_36122_Group_17 import KeyList, NewsAPI_KeyList, NewsScraper
import tkinter as tk
from datetime import datetime
import pandas as pd
from datetime import datetime
from bs4 import BeautifulSoup, Tag

# class TestNewsScraper(unittest.TestCase):

#     def setUp(self):
#         root = tk.Tk()
#         self.app = NewsScraper(root)


class TestNewsScraper(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root = tk.Tk()
        cls.root.withdraw()

    @classmethod
    def tearDownClass(cls):
        cls.root.destroy()

    def setUp(self):
        self.scraper = NewsScraper(self.root)

    def test_get_api_ratio(self):
        self.assertEqual(self.scraper.get_api_ratio(4,6), 0.4)
        self.assertEqual(self.scraper.get_api_ratio(2,6), 0.25)
        self.assertEqual(self.scraper.get_api_ratio(0,0), None)

    def test_get_date_info(self):
        list1 = [datetime(2025, 5, 10, 11, 23), datetime(2025, 5, 9, 10, 23), datetime(2025, 5, 8, 8, 58), datetime(2025, 5, 5, 6, 23)]
        list2 = [datetime.now(), datetime.now()]
        list3 = ['a', 'b', 'c']
        list4 = [datetime(2025, 5, 10, 11, 23)]
        self.assertEqual(self.scraper.get_date_info([]), (None,None))
        self.assertEqual(self.scraper.get_date_info(list1), (datetime(2025, 5, 5, 6, 23),datetime(2025, 5, 10, 11, 23)))
        self.assertEqual(self.scraper.get_date_info(list2), (datetime.now(), datetime.now()))
        self.assertEqual(self.scraper.get_date_info(list3), (None,None))
        self.assertEqual(self.scraper.get_date_info(list4), (datetime(2025, 5, 10, 11, 23),datetime(2025, 5, 10, 11, 23)))

    def test_initialization(self):
        self.assertIsInstance(self.scraper, NewsScraper)
        self.assertIsNotNone(self.scraper.api_key)
        self.assertIsInstance(self.scraper.df_articles, pd.DataFrame)

    def test_get_sources(self):
        sources = self.scraper.get_sources()
        self.assertIsInstance(sources, dict)
        if sources:
            for key, value in sources.items():
                self.assertIsInstance(key, str)
                self.assertIsInstance(value, str)

    def test_get_countries(self):
        countries = self.scraper.get_countries()
        self.assertIsInstance(countries, dict)
        if countries:
            for key, value in countries.items():
                self.assertIsInstance(key, str)
                self.assertIsInstance(value, str)

    def test_get_categories(self):
        categories = self.scraper.get_categories()
        self.assertIsInstance(categories, list)
        if categories:
            for category in categories:
                self.assertIsInstance(category, str)

    @patch('requests.get')
    def test_get_api_news_with_source(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'status': 'ok',
            'articles': [{
                'title': 'Test Article',
                'source': {'name': 'Test Source'},
                'publishedAt': '2023-01-01T00:00:00Z',
                'author': 'Test Author',
                'description': 'Test Description',
                'url': 'http://test.com'
            }]
        }
        mock_get.return_value = mock_response

        self.scraper.answer.set("0")
        self.scraper.source_listbox.insert(0, "Test Source")
        self.scraper.source_listbox.selection_set(0)

        self.scraper.get_api_news()
        self.assertFalse(self.scraper.df_articles.empty)
        self.assertEqual(self.scraper.df_articles.iloc[0]['Title'], 'Test Article')

    @patch('requests.get')
    def test_get_api_news_with_category_country(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'status': 'ok',
            'articles': [{
                'title': 'Test Article',
                'source': {'name': 'Test Source'},
                'publishedAt': '2023-01-01T00:00:00Z',
                'author': 'Test Author',
                'description': 'Test Description',
                'url': 'http://test.com'
            }]
        }
        mock_get.return_value = mock_response

        self.scraper.answer.set("1")
        self.scraper.category_listbox.insert(0, "business")
        self.scraper.country_listbox.insert(0, "Australia")
        self.scraper.category_listbox.selection_set(0)
        self.scraper.country_listbox.selection_set(0)

        self.scraper.get_api_news()
        self.assertFalse(self.scraper.df_articles.empty)
        self.assertEqual(self.scraper.df_articles.iloc[0]['Title'], 'Test Article')

    @patch('requests.get')
    def test_get_ABC_news(self, mock_get):

        main_page_json = """
        {
            "@context": "https://schema.org",
            "@type": "ItemList",
            "mainEntity": {
                "itemListElement": [
                    {"@type": "ListItem", "url": "http://abc.net.au/news/test1"},
                    {"@type": "ListItem", "url": "http://abc.net.au/news/test2"}
                ]
            }
        }
        """

        article_json = """
        {
            "@type": "NewsArticle",
            "headline": "ABC Test Article",
            "datePublished": "2023-01-01T00:00:00Z",
            "publisher": {"name": "ABC News"},
            "author": [{"name": "ABC Author"}],
            "description": "ABC Test Description"
        }
        """
        mock_main_response = MagicMock()
        soup_main = BeautifulSoup(f'<script type="application/ld+json">{main_page_json}</script>', 'lxml')
        mock_main_response.text = str(soup_main)

        mock_article_response = MagicMock()
        soup_article = BeautifulSoup(f'<script type="application/ld+json">{article_json}</script>', 'lxml')
        mock_article_response.text = str(soup_article)

        mock_get.side_effect = [mock_main_response, mock_article_response, mock_article_response]

        self.scraper.get_ABC_news()

        self.assertFalse(self.scraper.df_articles.empty)
        self.assertIn('ABC Test Article', self.scraper.df_articles['Title'].values)
        self.assertEqual(self.scraper.df_articles.iloc[0]['Source'], 'ABC News')

    def test_fill_textbox(self):
        test_data = {
            'Title': ['Test Title'],
            'Source': ['Test Source'],
            'PublishedDate': ['01 Jan 2023 12:00 PM'],
            'Author': ['Test Author'],
            'Description': ['Test Description'],
            'ExtractionMethod': ['Test'],
            'URL': ['http://test.com']
        }
        self.scraper.df_articles = pd.DataFrame(test_data)
        
        self.scraper.fill_textbox()
        textbox_content = self.scraper.output_textbox.get("1.0", tk.END)
        self.assertIn('Test Title', textbox_content)
        self.assertIn('Test Source', textbox_content)

    def test_update_plots(self):
        test_data = {
            'Title': ['Python is great', 'Python testing is important', 'Great Python tools'],
            'Source': ['Test1', 'Test2', 'Test3']
        }
        self.scraper.df_articles = pd.DataFrame(test_data)
        self.scraper.update_plots()
        self.assertTrue(True)  # Just checking for no exceptions

    def test_update_plots_empty_data(self):
        self.scraper.df_articles = pd.DataFrame()
        self.scraper.update_plots()
        self.assertTrue(True)


class TestKeyList(unittest.TestCase):
    def setUp(self):
        self.keylist = NewsAPI_KeyList()
        self.test_key = '513d1d7c31e34a49aeedadeccd4f58e5'
        self.invalid_key = 'shortkey'

    def test_add_valid_key(self):
        self.keylist.add_key(self.test_key)
        self.assertIn(self.test_key, self.keylist._keys)

    def test_add_invalid_key(self):
        with self.assertRaises(ValueError):
            self.keylist.add_key(self.invalid_key)


if __name__ == "__main__":
    unittest.main()
