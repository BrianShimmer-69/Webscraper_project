################################################################################
#                                                                              #  
#                               Main Assignment                                #                                     
#                                                                              #  
#  36122 Python Programming - 1st Semester 2025                                #
#                                                                              #  
#  Dan Hansen                    - Student ID 24718999                         #  
#  Brian Shimmer Bino Deva Kumar - Student ID 25752306                         #  
#  David Pawley                  - Student ID 92072368                         #  
#  Maximus Chandrasekaran        - Student ID 25614189                         #  
#                                                                              #  
################################################################################

import tkinter as tk
from tkinter import messagebox
import tkinter.font as tkfont
import requests
import pycountry
import pandas as pd
from datetime import datetime
from bs4 import BeautifulSoup
import json
import requests as req 
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from collections import Counter
import string
import random
import sys 

# Superclass
class KeyList:
    """
    A class that manages and validates 32-character keys.

    Attributes:
        _keys (list): A list to store valid 32-character string keys.
    """

    def __init__(self):
        self._keys = []

    def add_key(self, key):
        """
        Add a key to the list if it is a valid 32-character string.

        Args:
            key (str): The API key to add.

        Raises:
            ValueError: If the key is not a 32-character string.
        """
        if isinstance(key, str) and len(key) == 32:
            self._keys.append(key)
        else:
            raise ValueError("Key must be a 32-character string.")

    def get_key(self):
        """
        Return a random key from the list of valid keys.

        Returns:
            str: A randomly selected key.

        Raises:
            IndexError: If no keys are available.
        """
        if not self._keys:
            raise IndexError("No keys available.")
        return random.choice(self._keys)

# Subclass
class NewsAPI_KeyList(KeyList):
    """
    A subclass of KeyList for managing and validating 32-character keys
    specifically for the News API.

    Attributes:
        url (str): The URL used to test the validity of the keys.
    """

    def set_url(self, url):
        """
        Set the URL used to test a key's validity.

        Args:
            url (str): The API endpoint to test the keys against.
        """
        self.url = url

    def get_key(self):
        """
        Return the first valid key after checking against the News API URL.

        Returns:
            str: A valid API key if available, otherwise 'Invalid'.
        """
        if not self._keys or not hasattr(self, 'url'):
            return 'Invalid'

        shuffled_keys = self._keys[:]
        random.shuffle(shuffled_keys)

        for key in shuffled_keys:
            try:
                response = requests.get(self.url, params={'apiKey': key}, timeout=5)
                data = response.json()
                if response.status_code == 200 and data.get('status') == 'ok':
                    return key
            except requests.RequestException:
                continue
        return 'Invalid'
    
class NewsScraper:
    """
    A class to create and manage a GUI for extracting and visualizing news data.

    Attributes:
        master (tk.Tk): Root tkinter window.
        url (str): News API sources endpoint used for key validation.
    """

    
    def __init__(self, master):
        self.master = master
        self.master.withdraw()  # Hide the window until after the keys have been verified
        self.url = 'https://newsapi.org/v2/top-headlines/sources'

        api_keys = NewsAPI_KeyList()
        api_keys.set_url(self.url)
        try:
            # api_keys.add_key('513d1d7c31e34a49aeedadeccd4f58e5')     
            # api_keys.add_key('65239d2b12b548b99319b46acd217ae9')     
            # api_keys.add_key('fbe85cf88f68401ca9d651c0f9001e25')     
            # api_keys.add_key('cdcb845692684e7196b78ec4262edca2')     
            api_keys.add_key('4183db2e20db4b18bb05e23f5bf7c548')     
        except Exception as e:
            messagebox.showwarning("Warning", str(e))
            self.master.destroy()
            sys.exit()

        self.api_key = api_keys.get_key()
        if self.api_key == 'Invalid': 
            messagebox.showwarning("Warning",'No valid keys ...')
            self.master.destroy()
            sys.exit()

        self.master.deiconify()  # Show the main window

        self.available_countries = self.get_countries()
        self.available_categories = self.get_categories()
        self.available_sources = self.get_sources()
        self.unwanted_words = "a; and; as; at; be; by; do; for; have; he; I; in; is; it; not; of; on; that; the; to; with; you"

        self.master.geometry('1500x900') 
        self.master.title("News API Extractor and Web Scraper")
        self.df_articles = pd.DataFrame()

        # Radio Button Frame
        self.radio_frame = tk.LabelFrame(master, text="API Options", padx=10, pady=10)
        self.radio_frame.grid(row=0, column=0, padx=20, pady=20, sticky="w")

        consoles = ['Source', 'Category/Country']
        self.answer = tk.StringVar(value="0")  # Default selection

        # Create and place each radio button with a command
        for count, console in enumerate(consoles):
            rb = tk.Radiobutton(
                self.radio_frame, 
                text=console, 
                value=str(count), 
                variable=self.answer, 
                command=self.toggle_listboxes
            )
            rb.grid(row=count + 1, column=0, padx=20, pady=5, sticky="w")

        # Source listbox
        self.source_frame = tk.LabelFrame(master, text="Source", padx=10, pady=10)
        self.source_lb_frame = tk.Frame(self.source_frame)
        self.source_lb_frame.grid(row=1, column=0, columnspan=2, pady=10)
        self.source_listbox = tk.Listbox(self.source_lb_frame, width=24, selectmode="browse",  exportselection=False)
        self.source_listbox.pack(side=tk.LEFT, fill=tk.BOTH)
        self.source_sb = tk.Scrollbar(self.source_lb_frame, orient=tk.VERTICAL, command=self.source_listbox.yview)
        self.source_sb.pack(side=tk.RIGHT, fill=tk.Y)
        self.source_listbox.config(yscrollcommand=self.source_sb.set)

        # Populate source listbox
        for source_name in self.available_sources.values():
            self.source_listbox.insert(tk.END, source_name)

        # Category/Country frame
        self.category_frame = tk.LabelFrame(master, text="Category and Country", padx=10, pady=10)
        self.lb2_frame = tk.Frame(self.category_frame)
        self.lb2_frame.grid(row=1, column=0, pady=10)

        # Category listbox and scrollbar (top)
        self.category_pair_frame = tk.Frame(self.lb2_frame)
        self.category_pair_frame.pack(pady=(0, 10))  # Padding below category

        self.category_label = tk.Label(self.category_pair_frame, text="Category")
        self.category_label.pack(anchor='w')
        self.category_listbox = tk.Listbox(self.category_pair_frame, width=24, height=6, selectmode="browse",  exportselection=False)
        self.category_listbox.pack(side=tk.LEFT, fill=tk.BOTH)
        self.category_sb = tk.Scrollbar(self.category_pair_frame, orient=tk.VERTICAL, command=self.category_listbox.yview)
        self.category_sb.pack(side=tk.RIGHT, fill=tk.Y)
        self.category_listbox.config(yscrollcommand=self.category_sb.set)

        # Populate category listbox
        for category in self.available_categories:
            self.category_listbox.insert(tk.END, category.title())

        # Country listbox and scrollbar (bottom)
        self.country_pair_frame = tk.Frame(self.lb2_frame)
        self.country_pair_frame.pack()

        self.country_label = tk.Label(self.country_pair_frame, text="Country")
        self.country_label.pack(anchor='w')
        self.country_listbox = tk.Listbox(self.country_pair_frame, width=24, selectmode="browse")
        self.country_listbox.pack(side=tk.LEFT, fill=tk.BOTH)
        self.country_sb = tk.Scrollbar(self.country_pair_frame, orient=tk.VERTICAL, command=self.country_listbox.yview)
        self.country_sb.pack(side=tk.RIGHT, fill=tk.Y)
        self.country_listbox.config(yscrollcommand=self.country_sb.set)

        # Populate country listbox
        for country_name in self.available_countries:  # available_countries['Australia']
            self.country_listbox.insert(tk.END, country_name)

        # Initially show only Source
        self.source_frame.grid(row=1, column=0, padx=20, pady=20, sticky="w")
        self.category_frame.grid_remove()

        self.API_button = tk.Button(master, text="Get API News", command=self.get_api_news, width=25)
        self.API_button.grid(row=2, column=0, columnspan=2, pady=10)

        self.API_label = tk.Label(master, wraplength=190, justify="left", anchor="w")
        self.API_label.grid(row=3, column=0, columnspan=2, pady=5, sticky='w', padx=20)

        self.ABC_button = tk.Button(master, text="Get ABC Australia News", command=self.get_ABC_news, width=25)
        self.ABC_button.grid(row=4, column=0, columnspan=2, pady=10)

        self.ABC_label = tk.Label(master, wraplength=190, justify="left", anchor="w")
        self.ABC_label.grid(row=5, column=0, columnspan=2, pady=5, sticky='w', padx=20)

        # Info Label Frame
        self.info_frame = tk.LabelFrame(master, text="Extract Information", padx=10, pady=10)
        self.info_frame.grid(row=6, column=0, columnspan=2, padx=20, pady=10, sticky="w")

        self.info_label = tk.Label(
            self.info_frame,
            text="No articles extracted.",
            wraplength=200,
            justify="left",
            anchor="w"
        )
        self.info_label.grid(row=0, column=0, pady=5, sticky='w')

        # Output frame 
        self.output_frame = tk.LabelFrame(master, text="Extracted News Stories", padx=10, pady=10)
        self.output_frame.place(x=250, y=10, width=1220, height=400) 
        self.output_textbox = tk.Text(self.output_frame, wrap="word")
        self.output_textbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.output_scrollbar = tk.Scrollbar(self.output_frame, command=self.output_textbox.yview)
        self.output_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.output_textbox.config(yscrollcommand=self.output_scrollbar.set)

        # Plot frame 
        self.plot_frame = tk.LabelFrame(master, text="Common Title Words", padx=10, pady=10)
        self.plot_frame.place(x=250, y=410, width=1220, height=480)  
        self.fig = Figure(figsize=(12, 3.5), dpi=100)
        self.plot = self.fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.plot_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.control_frame = tk.Frame(self.plot_frame)
        self.control_frame.pack(side=tk.TOP, fill=tk.X, pady=(10, 0))
        self.omitted_label = tk.Label(self.control_frame, text="Omitted Words")
        self.omitted_label.pack(side=tk.LEFT, padx=(10, 5))
        self.omitted_words = tk.Entry(self.control_frame, width=120)
        self.omitted_words.pack(side=tk.LEFT, padx=(0, 10), fill=tk.X, expand=True)
        self.omitted_words.insert(0, self.unwanted_words)
        self.replot_button = tk.Button(self.control_frame, text="Replot", command=self.update_plots)
        self.replot_button.pack(side=tk.LEFT, padx=(0, 10))


    def get_sources(self):
        """
        A function which returns a data dictionary of all possible currently available sources from the News API website.
            Key: Source ID
            Value: Source Name

        Uses the following class attributes:
            self.url: The News API endpoint URL.
            self.api_key: Your registered API key for accessing the News API.
        """    
        
        params = {'apiKey': self.api_key}
        response = requests.get(self.url, params=params)
        data = response.json()
        sources_dict = {}

        if data.get('status') == 'ok':
            for source in data['sources']:
                source_id = source['id']
                source_name = source['name']
                sources_dict[source_id] = source_name
        
        return sources_dict

    def get_countries(self):
        """
        Retrieves a dictionary of available countries or languages from the News API source list.

        Returns:
            dict: A dictionary where:
                - Key: country name or language name.
                - Value: country code or language code.

        Uses:
            self.api_key (str): The API key for authentication.
            self.url (str): The endpoint URL for retreiving information.
        """

        params = {'apiKey': self.api_key}
        response = requests.get(self.url, params=params)
        data = response.json()
        country_dict = {}

        if data.get('status') == 'ok':
            for source in data['sources']:
                code = source.get('country')
                code_upper = code.upper()
                country = pycountry.countries.get(alpha_2=code_upper)
                if country:
                    country_dict[country.name] = code
                else:
                    language = pycountry.languages.get(alpha_2=code_upper)
                    if language:
                        name = f"{language.name} Language"
                        country_dict[name] = code
                    else:
                        country_dict[code_upper] = code

        return dict(sorted(country_dict.items()))

    def get_categories(self):
        """
        Retrieves a dictionary of countries or languages from available news sources.

        Returns:
            dict: A dictionary where the key is the full name of the country/language and
                the value is its corresponding lowercase country/language code.

        Uses:
            self.api_key (str): The active NewsAPI key.
            self.url (str): The NewsAPI endpoint for top-headline sources.
        """        
        params = {'apiKey': self.api_key}
        response = requests.get(self.url, params=params)
        data = response.json()
        categories = set()  

        if data.get('status') == 'ok':
            for source in data['sources']:
                categories.add(source.get('category'))

        return sorted(categories)

    def toggle_listboxes(self):
        """
        Show or hide source and category/country listboxes based on selected radio button.

        Uses:
            self.answer (tk.StringVar): Holds the value of the selected radio button.
            self.source_frame (tk.LabelFrame): Frame containing the source listbox.
            self.category_frame (tk.LabelFrame): Frame containing the category/country listboxes.
        """
        if self.answer.get() == "0":  # Source selected
            self.source_frame.grid(row=1, column=0, padx=20, pady=20, sticky="w")
            self.category_frame.grid_remove()
        else:  # Category/Country selected
            self.source_frame.grid_remove()
            self.category_frame.grid(row=1, column=0, padx=20, pady=20, sticky="w")

    def fill_textbox(self):
        """
        Populate the output textbox with formatted article entries from the dataframe.

        Iterates through self.df_articles and inserts formatted text into
        self.output_textbox for each article.

        Uses:
            self.df_articles (pd.DataFrame): DataFrame containing article information.
            self.output_textbox (tk.Text): Text widget where article info is displayed.
        """        
        self.output_textbox.delete(1.0, tk.END)  
        for i, row in self.df_articles.iterrows():
            self.output_textbox.insert(tk.END, f"{i+1}. Title: {row['Title']}\n")
            self.output_textbox.insert(tk.END, f"   Source: {row['Source']}\n")
            self.output_textbox.insert(tk.END, f"   Published Date: {row['PublishedDate']}\n")
            self.output_textbox.insert(tk.END, f"   Author: {row['Author']}\n")
            self.output_textbox.insert(tk.END, f"   Description: {row['Description']}\n")
            self.output_textbox.insert(tk.END, f"   Extraction: {row['ExtractionMethod']}\n")
            self.output_textbox.insert(tk.END, f"   URL: {row['URL']}\n\n")

    def get_api_ratio(self, api_num, abc_num):
        """
        Calculate the ratio of API-extracted articles to the total number of articles.

        Args:
            api_num (int): Number of articles extracted via News API.
            abc_num (int): Number of articles extracted via ABC News web scraping.

        Returns:
            None or float: Ratio of API articles to total articles, or None if invalid input.
        """
        try:
            if any([
                pd.isna(api_num),
                pd.isna(abc_num),
                api_num < 0,
                abc_num < 0,
                api_num + abc_num == 0
            ]):
                return None
            else:
                return float(api_num) / float(api_num + abc_num)
        except Exception:
            return None

    def get_date_info(self, all_dates):
        """
        Calculate the minimum and maximum datetime values from a list.

        Args:
            all_dates (list of datetime): List of datetime objects.

        Returns:
            tuple: (min_date, max_date) if valid, otherwise (None, None).
        """
        try:
            if not all_dates:  # Checks for empty list
                return None, None
            if not all(isinstance(d, datetime) for d in all_dates):
                return None, None
            return min(all_dates), max(all_dates)
        except Exception:
            return None, None

    def update_info_label(self):
        """
        Updates the information label with article statistics including source ratios and publication dates.
        """
        if self.df_articles.empty or "Title" not in self.df_articles.columns:
            self.info_label.config(text="No articles extracted") 
            return

        api_articles = len(self.df_articles[self.df_articles['ExtractionMethod'] == 'API'])
        abc_articles = len(self.df_articles[self.df_articles['ExtractionMethod'] == 'ABC Scrape'])
        labeltext = "There are a total {article_num} articles".format(article_num = api_articles+abc_articles)
        api_ratio = self.get_api_ratio(api_articles, abc_articles)

        if api_ratio is None:
            pass
        elif api_ratio >= 0.5:
            labeltext += " and {perc:.1f}% of the articles were sourced from the API scrape".format(perc=api_ratio*100)               
        else:
            labeltext += " and {perc:.1f}% of the articles were sourced from the ABC News scrape".format(perc=(1-api_ratio)*100)               

        date_list = pd.to_datetime(self.df_articles['PublishedDate'], format='%d %b %Y %I:%M %p').tolist()
        min_date, max_date = self.get_date_info(date_list)
        if min_date is None or max_date is None:
            pass
        elif min_date == max_date:
            labeltext += ", with the articles published at {mindate}".format(mindate=min_date.strftime('%#d %b %Y'))               
        elif min_date.date() == max_date.date():
            labeltext += ", with the articles published on {pubdate} between {mintime} and {maxtime}".format(pubdate=min_date.strftime('%#d %b %Y'), 
                                                                                                             mintime = min_date.strftime('%#I:%M %p').lower(), 
                                                                                                             maxtime = max_date.strftime('%#I:%M %p').lower())               
        else:
            labeltext += ", with the articles published between {mindate} and {maxdate}".format(mindate = min_date.strftime('%#d %b %Y'), maxdate = max_date.strftime('%#d %b %Y'))               

        labeltext += "."
        self.info_label.config(text=labeltext) 

    def update_plots(self):
        """
        Updates the bar graph showing the most common words in article titles.
        """

        if self.df_articles.empty or "Title" not in self.df_articles.columns:
            self.plot.clear()
            self.plot.set_title("No Data Available")
            self.canvas.draw()
            return
        
        self.unwanted_words = self.omitted_words.get()
        unwanted = set(word.strip().lower() for word in self.unwanted_words.split(';'))

        titles = self.df_articles["Title"].dropna().astype(str).str.lower()
        all_words = []

        for title in titles:
            words = title.translate(str.maketrans('', '', string.punctuation)).split()
            filtered_words = [word for word in words if word not in unwanted]
            all_words.extend(filtered_words)

        word_counts = Counter(all_words)
        if not word_counts:
            self.plot.clear()
            self.plot.set_title("No Words Found in Titles")
            self.canvas.draw()
            return

        common_words = word_counts.most_common(20)
        words, counts = zip(*common_words)

        self.plot.clear()
        self.plot.bar(words, counts, color='skyblue')
        self.plot.set_title("Most Common Words in Article Titles")
        self.plot.set_ylabel("Frequency")
        self.plot.tick_params(axis='x', labelsize=8, rotation=45)
        self.fig.subplots_adjust(bottom=0.25)
        self.canvas.draw()

    def get_api_news(self):
        """
        Performs a scrape of the News API website based on the selected paramters and stores the data in a dataframe.
        """

        if not self.df_articles.empty:
            has_api_articles = not self.df_articles[self.df_articles['ExtractionMethod'] == 'API'].empty
            if has_api_articles:
                # Clear API articles
                self.df_articles = self.df_articles[self.df_articles['ExtractionMethod'] != 'API']
                self.API_label.config(text="API news articles cleared.")
                self.API_button.config(text="Get API News")
                self.update_info_label()
                self.fill_textbox()
                self.update_plots()
                return

        url = self.url.replace('/sources','')
        if self.answer.get() == "0":  # Source selected
            source = self.source_listbox.curselection()

            if source:
                parameters = {'apiKey': self.api_key, 
                              'sources': self.source_listbox.get(source[0]), 
                              'pageSize': 50
                }
            else:
                self.update_info_label()
                messagebox.showwarning("Warning", "Please select a scource.")
                return
        else:  # Category/Country selected  
            category = self.category_listbox.curselection() 
            country = self.country_listbox.curselection()
            if category and country:
                parameters =  {'apiKey': self.api_key,
                               'country': self.available_countries[self.country_listbox.get(country[0])],
                               'category': self.category_listbox.get(category[0]).lower(),
                               'pageSize': 50
                }
            elif category:    
                self.update_info_label()
                messagebox.showwarning("Warning", "Please select a country.")
                return
            elif country:    
                self.update_info_label()
                messagebox.showwarning("Warning", "Please select a category.")
                return
            else:    
                self.update_info_label()
                messagebox.showwarning("Warning", "Please select a country and a category.")
                return

        response = requests.get(url, params = parameters)
        data = response.json()

        found = 0
        if data.get('status') == 'ok':
            if not self.df_articles.empty:
                self.df_articles = self.df_articles[self.df_articles['ExtractionMethod'] != 'API']
            for i, article in enumerate(data['articles'], 1):
                found += 1
                iso_str = article['publishedAt'].replace('Z', '+00:00')
                dot_index = iso_str.find('.')
                if dot_index != -1:
                    iso_str = iso_str[:dot_index+7] + '+00:00'  # Only 6 digits is required
                dt = datetime.fromisoformat(iso_str)
                formatted_date = dt.strftime("%#d %b %Y  %#I:%M %p")

                news_article = {
                    'ExtractionMethod': 'API',
                    'Title': article['title'],
                    'Source': article['source']['name'],
                    'PublishedDate': formatted_date,
                    'Author': article['author'],
                    'Description': article['description'],
                    'URL': article['url']
                }
                if self.df_articles.empty:
                    self.df_articles = pd.DataFrame([news_article])
                else:
                    self.df_articles = pd.concat([self.df_articles, pd.DataFrame([news_article])], ignore_index=True)
        else:
            self.API_label.config(text=f"No news was scraped: {data.get('message')}")
        
        if self.answer.get() == "0":
            source_name = self.source_listbox.get(source[0])
            if found == 0:
                msg = f"No news from {source_name}"
            else:
                msg = f"There were {found} articles from {source_name} added"
        else:
            category = self.category_listbox.get(category[0]).lower()
            country = self.country_listbox.get(country[0])
            if found == 0:
                msg = f"No {category} news from {country}"
            else:
                msg = f"There were {found} {category} articles from {country} added"

        self.API_label.config(text=msg)
        buttontext = "Get API News"
        if not self.df_articles.empty:
            if not self.df_articles[self.df_articles['ExtractionMethod'] == 'API'].empty:
                buttontext = "Clear API News"
        self.API_button.config(text=buttontext)
        self.update_info_label()
        self.fill_textbox() 
        self.update_plots()

    def get_ABC_news(self):
        """
        Performs a scrape of the ABC Australia news website and stores the data in a dataframe.
        """
        if not self.df_articles.empty:
            has_abc_articles = not self.df_articles[self.df_articles['ExtractionMethod'] == 'ABC Scrape'].empty

            if has_abc_articles:
                # Clear ABC Scrape articles
                self.df_articles = self.df_articles[self.df_articles['ExtractionMethod'] != 'ABC Scrape']
                self.ABC_label.config(text="ABC Australia articles cleared.")
                self.ABC_button.config(text="Get ABC Australia News")
                self.fill_textbox()
                self.update_plots()
                self.update_info_label()
                return

        try:
            web = req.get('https://www.abc.net.au/news')
            soup = BeautifulSoup(web.text, 'lxml')

            abc_urls = []
            for script in soup.find_all("script", type="application/ld+json"):
                try:
                    data = json.loads(script.string)
                    if isinstance(data, dict) and "mainEntity" in data:
                        abc_urls = [item.get("url", "") for item in data["mainEntity"].get("itemListElement", [])]
                except (json.JSONDecodeError, TypeError):
                    messagebox.showwarning("Warning", "Unable to scrape news from ABC Australia.")
                    self.update_info_label()
                    return

            if not self.df_articles.empty:
                self.df_articles = self.df_articles[self.df_articles['ExtractionMethod'] != 'ABC Scrape']

            found = 0
            for url in abc_urls:
                try:
                    res = req.get(url)
                    soup = BeautifulSoup(res.text, 'lxml')

                    for script in soup.find_all("script", type="application/ld+json"):
                        try:
                            data = json.loads(script.string)
                            if data.get('@type') == 'NewsArticle':

                                dt = datetime.fromisoformat(data.get("datePublished").replace('Z', '+00:00'))
                                formatted_date = dt.strftime("%d %b %Y  %#I:%M %p")

                                article = {
                                    'ExtractionMethod': 'ABC Scrape',
                                    'Title': data.get("headline"),
                                    'Source': data.get("publisher").get("name"),
                                    'PublishedDate': formatted_date,
                                    'Author': ", ".join(author["name"] for author in data.get("author", []) if "name" in author),
                                    'Description': data.get("description"),
                                    'URL': url 
                                }

                                if article["Title"]:  
                                    found += 1
                                    if self.df_articles.empty:
                                        self.df_articles = pd.DataFrame([article])
                                    else:
                                        self.df_articles = pd.concat([self.df_articles, pd.DataFrame([article])], ignore_index=True)

                        except (json.JSONDecodeError, TypeError):
                            continue
                except req.RequestException:
                    continue


            if found == 0:
                msg = f"No news was fetched from ABC Australia"
            else:
                msg = f"There were {found} articles from ABC Australia added"

            self.ABC_label.config(text=msg)
            self.ABC_button.config(text="Clear ABC Australia News")
            self.fill_textbox()        
            self.update_plots()
            self.update_info_label()
            
        except Exception as e:
            messagebox.showwarning("Warning", f"Error fetching ABC news: {e}")
            self.ABC_label.config(text="Error fetching ABC Australia news")
            self.update_info_label()

def main():
    root = tk.Tk()
    # Create an instance of the class
    app = NewsScraper(root)
    root.mainloop()  

##### Run the program ####
if __name__ == "__main__":
    main()

