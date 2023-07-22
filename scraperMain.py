#Import libraries
import os
import concurrent.futures
from GoogleImageScraper import GoogleImageScraper
from BingImageScrapper import BingImageScraper
# from patch import webdriver_executable
# from selenium import webdriver
# from selenium.webdriver.common.keys import Keys
# from selenium.common.exceptions import WebDriverException, SessionNotCreatedException
# import sys
import os
# import urllib.request
# import re
# import zipfile
# import stat
from sys import platform


def worker_thread(search_key):
    image_scraper = GoogleImageScraper(
        webdriver_path, 
        image_path, 
        search_key, 
        number_of_images, 
        headless, 
        min_resolution, 
        max_resolution, 
        max_missed)
    # image_scraper = BingImageScraper(webdriver_path,image_path,search_key,number_of_images,headless,min_resolution,max_resolution,max_missed)
    image_urls = image_scraper.find_image_urls()
    image_scraper.save_images(image_urls, keep_filenames)

    #Release resources
    del image_scraper

def webdriver_executable():
    if platform == "linux" or platform == "linux2" or platform == "darwin":
        return 'chromedriver'
    return 'chromedriver.exe'

if __name__ == "__main__":
    #Defining file path
    webdriver_path = os.path.normpath(os.path.join(os.getcwd(), 'webdriver', webdriver_executable()))
    image_path = os.path.normpath(os.path.join(os.getcwd(), 'photos'))
    keyword = input("Enter the keyword - ")
    search_keys = list()
    search_keys.append(keyword)

    #Parameters
    number_of_images = int(input("Enter the number of images - "))
    headless = True                     
    min_resolution = (0, 0)            
    max_resolution = (9999, 9999)       
    max_missed = 30                   
    number_of_workers = 1               
    keep_filenames = False              

    #Runs each searchkey in a separate thread
    with concurrent.futures.ThreadPoolExecutor(max_workers=number_of_workers) as executor:
        executor.map(worker_thread, search_keys)
