#import selenium drivers
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException

#import helper libraries
import time
import urllib.request
from urllib.parse import urlparse
import os
import requests
import io
from PIL import Image
import re

#custom patch libraries
import patch

class GoogleImageScraper():
    def __init__(self, webdriver_path, image_path, search_key, number_of_images=1, headless=True, min_resolution=(0, 0), max_resolution=(5000, 5000), max_missed=30):
        #check parameter types
        image_path = os.path.join(image_path, search_key)
        if (type(number_of_images)!=int):
            print("ERROR!!! Number of images must be integer value.")
            return
        if not os.path.exists(image_path):
            print("Image path not found. Creating a new folder.")
            os.makedirs(image_path)

        #change extension here to save        
        extens = "png"
        
        for i in range(1):
            try:
                options = Options()
                if(headless):
                    options.add_argument('--headless=new')
                driver = webdriver.Chrome(webdriver_path, options=options)
                driver.set_window_size(1400,1050)
                driver.get("https://www.google.com")
                try:
                    WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.ID, "W0wltc"))).click()
                except Exception as e:
                    continue
            except Exception as e:
                print("Update your chrome driver!!!")

        self.driver = driver
        self.search_key = search_key
        self.number_of_images = number_of_images
        self.webdriver_path = webdriver_path
        self.image_path = image_path
        self.url = "https://www.google.com/search?q=%s&source=lnms&tbm=isch&sa=X&ved=2ahUKEwie44_AnqLpAhUhBWMBHUFGD90Q_AUoAXoECBUQAw&biw=1920&bih=947"%(search_key)
        self.headless=headless
        self.min_resolution = min_resolution
        self.max_resolution = max_resolution
        self.max_missed = max_missed

    def find_image_urls(self):
        print("*** Gathering image links ***")
        self.driver.get(self.url)
        image_urls=[]
        count = 0
        missed_count = 0
        indx_1 = 0
        indx_2 = 0
        search_string = '//*[@id="islrg"]/div[1]/div[%s]/a[1]/div[1]/img'
        time.sleep(3)
        indx = 1

        while self.number_of_images > count and missed_count < self.max_missed:
            #CLICKING ON THE IMAGES ONE BY ONE
            if indx_2 > 0:
                try:
                    imgurl = self.driver.find_element(By.XPATH, search_string%(indx_1,indx_2+1))
                    imgurl.click()
                    indx_2 = indx_2 + 1
                    missed_count = 0
                except Exception:
                    try:
                        imgurl = self.driver.find_element(By.XPATH, search_string%(indx_1+1,1))
                        imgurl.click()
                        indx_2 = 1
                        indx_1 = indx_1 + 1
                    except:
                        indx_2 = indx_2 + 1
                        missed_count = missed_count + 1
            else:
                try:
                    imgurl = self.driver.find_element(By.XPATH, search_string%(indx_1+1))
                    imgurl.click()
                    missed_count = 0
                    indx_1 = indx_1 + 1    
                except Exception:
                    try:
                        imgurl = self.driver.find_element(By.XPATH, '//*[@id="islrg"]/div[1]/div[%s]/div[%s]/a[1]/div[1]/img'%(indx_1,indx_2+1))
                        imgurl.click()
                        missed_count = 0
                        indx_2 = indx_2 + 1
                        search_string = '//*[@id="islrg"]/div[1]/div[%s]/div[%s]/a[1]/div[1]/img'
                    except Exception:
                        indx_1 = indx_1 + 1
                        missed_count = missed_count + 1

            try:
                #SELECTING THE IMAGE CLICKED
                time.sleep(4)
                # class_names = ["n3VNCb"]
                class_names = ["n3VNCb","iPVvYb","r48jcc","pT0Scc"]
                images = [self.driver.find_elements(By.CLASS_NAME, class_name) for class_name in class_names if len(self.driver.find_elements(By.CLASS_NAME, class_name)) != 0 ][0]
                for image in images:
                    src_link = image.get_attribute("src")
                    if(("http" in src_link) and (not "encrypted" in src_link)):
                        print(
                            f"QUERY - {self.search_key} \t #{count} \t {src_link}")
                        image_urls.append(src_link)
                        count +=1
                        break
            except Exception:
                print("Unable to get link!")

            try:
                #scroll page to load next image
                time.sleep(3)
                if(count%3==0):
                    self.driver.execute_script("window.scrollTo(0, "+str(indx_1*60)+");")
                element = self.driver.find_element(By.CLASS_NAME,"LZ4I")
                element.click()
                print("[INFO] Loading next page")
                time.sleep(5)
            except Exception:
                time.sleep(3)

            #For clicking - Show more results!!!
            try:
                WebDriverWait(self.driver, 20).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input[value='Show more results']"))).click()
                self.driver.implicitly_wait(10)
            except:
                time.sleep(2)
            
            indx += 1

        self.driver.quit()
        print("[INFO] Google search ended")
        return image_urls

    def save_images(self,image_urls, keep_filenames):
        extension = "jpg"
        #saving images to the directory
        print("Saving images now")
        for indx,image_url in enumerate(image_urls):
            try:
                print("--> Image url:%s"%(image_url))
                search_string = ''.join(e for e in self.search_key if e.isalnum())
                image = requests.get(image_url,timeout=5)
                if image.status_code == 200:
                    with Image.open(io.BytesIO(image.content)) as image_from_web:
                        try:
                            if (keep_filenames):
                                #extracting filename without extension from URL
                                o = urlparse(image_url)
                                image_url = o.scheme + "://" + o.netloc + o.path
                                name = os.path.splitext(os.path.basename(image_url))[0]
                                filename = "%s.%s"%(name,extension)
                            else:
                                filename = "%s%s.%s"%(search_string,str(indx),extension)

                            image_path = os.path.join(self.image_path, filename)
                            print(
                                f"--> {self.search_key} \t {indx} \t Image saved at: {image_path}")
                            image_from_web.save(image_path)
                        except OSError:
                            rgb_im = image_from_web.convert('RGB')
                            rgb_im.save(image_path)
                        image_resolution = image_from_web.size
                        if image_resolution != None:
                            if image_resolution[0]<self.min_resolution[0] or image_resolution[1]<self.min_resolution[1] or image_resolution[0]>self.max_resolution[0] or image_resolution[1]>self.max_resolution[1]:
                                image_from_web.close()
                                os.remove(image_path)

                        image_from_web.close()
            except Exception as e:
                print("ERROR!!! Download failed: ",e)
                pass
        