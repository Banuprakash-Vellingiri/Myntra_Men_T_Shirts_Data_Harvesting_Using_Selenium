#----------------------------------------Myntra Data Harvesting---------------------------------------
#Importing Necessary Libraries
#-----------------------------------------------------------------------------------------------------
import streamlit as st
import mysql.connector
from sqlalchemy import create_engine
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By 
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from tqdm import tqdm
import pandas as pd
import time
import re
from PIL import Image
import requests
from io import BytesIO
#------------------------------------------------------------------------------------------------------
#streamlit environment
#Page Layout
st.set_page_config (
                    page_title="Myntra Data Harvesting",
                    page_icon= "👚",  
                    layout="wide", 
                    initial_sidebar_state="expanded",  
                   )
#------------------------------------------------------------------------------------------------------
#Heading 
st.markdown("# :orange[MYNTRA] Men T-Shirts Data Harvesting 👕")
#-------------------------------------------------------------------------------------------------------
#Creating Tabs 
tab_1,tab_2,tab_3,tab_4 = st.tabs([":orange[⚒️ Extract Product Links]", ":orange[  ⛏️Extract Product Data]",":orange[ 🔎 View Products ]",":orange[ ⚙️Erase Data]"])
#------------------------------------------------------------------------------------------------------
#Extract Product Links
with tab_1:
    col_a, col_b = st.columns(2)
    with col_a:
            #website_url_input
            st.write("###    Enter Myntra's Official Website URL &nbsp; :")
            website_url = st.text_input(label=':blue[URL 🔗]', value='https://www.myntra.com', key=None, type='default', help=None, on_change=None, args=None, kwargs=None, label_visibility='visible')

            #---------------------------------------------------------------------------------
            #Input for number of T-Shirts Data  to be extracted
            st.markdown("###  :orange[ Product URL Links Extraction ]  &nbsp; ")
            st.write("  Enter Number of URL Links  to be Extracted &nbsp; :")
            total_data = st.number_input(label=":blue[Range  &nbsp; (1-123410)]", min_value=1, max_value=123410, step=1, format="%d")
            #--------------------------------------------------------------------------------
            #Store to database checkbox
            store_checkbox=st.checkbox(" &nbsp;   Store Data to MYSQL Database &nbsp; ")
            #---------------------------------------------------------------------------------
            #Load Button
            load_button = st.button(" :red[&nbsp;  Load and Extract &nbsp; ]")
            #---------------------------------------------------------------------------------
            product_link_list=[] #List for storing product link

            if load_button and website_url in ["https://www.myntra.com/","https://www.myntra.com"] and store_checkbox: 
                # product_links=[] #List for storing product link
                try:
                    #Loading the Web Page
                    with st.spinner("Loading Web Page ..."):
                            driver = webdriver.Chrome()  
                            driver.maximize_window()
                            a=driver.get(website_url)
                            driver.set_page_load_timeout(5)
                            st.text("✅ Myntra Home Page Successfully Loaded. ")
                    #Loading Men T-shirt Section
                    with st.spinner("Switching To Men T-shirt Section"):  
                            try:
                                men_tab=driver.find_element(By.CSS_SELECTOR,"div.desktop-navLinks>div.desktop-navContent>div.desktop-navLink>a")
                                action_chain=ActionChains(driver)
                                time.sleep(2)
                                action_chain.move_to_element(men_tab)
                                action_chain.perform()
                                t_shirt_link=driver.find_element(By.CSS_SELECTOR," div:nth-child(1) > div > div > div > div > li:nth-child(1) > ul > li:nth-child(2) > a").click()
                                time.sleep(2)
                                st.text("✅ Switched To Men T-shirt Section.")
                    
                            except Exception as e:
                                print(e) 
                                st.text("Error Occured while loading Men T-shirt Section ☹️") 
            #--------------------------------------------------------------------------------------------------------------------------------     
                    # product_links=[] #List for storing product link                      
                    with st.spinner("Please Wait...Extracting Product links"):
                            import math
                            # Number pages to scrap the data
                            elements_per_page=50
                            total_pages=math.ceil(total_data/elements_per_page)
            #----------------------------------------------------------------------------------------------------------------                 
                            #Code to Harvest Induvidual Product Link
                            try:
                                for page in tqdm(range(total_pages), desc="Processing", unit="iteration"):
                                    elements=driver.find_elements(By.CSS_SELECTOR,"li.product-base>a") #Using CSS_SELECTOR Finding the Required Web element
                                    try:
                                      for element in elements:
                                        if len(product_link_list) >=total_data: #Breaks the loop if the list reaches needed quantity 
                                            break
                                        product_link=element.get_attribute("href") #Getting hyperlink from the web element
                                        product_link_list.append(product_link)
                                    except:
                                         product_link_list.append(None)
                                    #After scraping the product links in a particular page,moving to next page
                                    next_button = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//a[@rel="next"]'))) #Using XPATH Finding the "Next" Button
                                    next_button.click()   
                            except Exception as e:
                                print("Exception_occured",e)
                    st.text("✅ Product Links Extracted")
                    #Converting the data into DataFrame
                    @ st.cache_resource
                    def links_df(product_links):
                        product_link_data={"product_links":product_links}
                        product_link_df=pd.DataFrame(product_link_data)
                        return product_link_df
                    product_link_df=links_df(product_link_list)
                    #----------------------------------------------------------------------------------
                    st.table(product_link_df)    #Table Display
                    #---------------------------------------------------------------------------------------------------
                    #Storing the Extracted Links to Database
                    #Connecting with MYSQL databasefor storing the data
                    with st.spinner("Storing Data Into MYSQL Databse"):
                            mysql_database=mysql.connector.connect( 
                                                                    host="localhost",
                                                                    user="root",
                                                                    password="952427",
                                                                    database="myntra_t_shirts_data"
                                                                    )
                            my_cursor=mysql_database.cursor(buffered=True)
                            #Table Creation
                            my_cursor.execute(
                                                """
                                                CREATE TABLE IF NOT EXISTS product_link_table
                                                (serial_no   INT AUTO_INCREMENT PRIMARY KEY,
                                                product_link VARCHAR(255))"""
                                            )
                            mysql_database.commit()
                            #Insering Links to product_link_table
                            link_insert_query = "INSERT INTO product_link_table (product_link) VALUES (%s)"
                            product_link_df=links_df(product_link_list)
                            for index, row in product_link_df.iterrows():
                                        values = (row['product_links'],)
                                        my_cursor.execute(link_insert_query, values)
                            mysql_database.commit()
                            my_cursor.close()
                            mysql_database.close()
                    st.markdown("### 👍 &nbsp; :green[Product Links Stored Successfully  to MYSQL Database.]")     
            #--------------------------------------------------------------------------------------------------------------------------------
                except Exception as e:
                    print("Excetion Occured :",e)
                    st.text("Sorry, there was an Error in Loading. Please Try Again.☹️",e)   
            elif load_button and website_url not in ["https://www.myntra.com/","https://www.myntra.com"] and store_checkbox:
                print("Invalid URL")
                st.text("☹️  Invalid URL , Kindly Enter Valid URL.")
    with col_b:
         st.image("myntra_logo.png")
#--------------------------------------------------------------------------------------------------------
#Extract Product Data
with tab_2:
         st.markdown("### Extracting Product Data :")
                     #Store to database checkbox
         store_checkbox2 = st.checkbox(" &nbsp;   Store Data to MYSQL Database &nbsp; ", key="store_checkbox_sql")
         extract_button=st.button(":red[Click to Extract T-Shirts Data]")
         if extract_button and store_checkbox2 :
                mysql_database=mysql.connector.connect( 
                                                        host="localhost",
                                                        user="root",
                                                        password="952427",
                                                        database="myntra_t_shirts_data"
                                                        )
                my_cursor=mysql_database.cursor(buffered=True)
               
                extract_query ="SELECT product_link FROM product_link_table "
                my_cursor.execute(extract_query)
                #--------------------------------------------------------------------
                product_name=[]
                product_code=[]
                product_image_url=[]
                product_description=[]
                material=[]
                fit_type=[]
                available_sizes=[]
                original_price=[]
                discounted_price=[]
                discount_percentage=[]
                total_ratings=[]
                avg_rating_for_five=[]
                total_text_reviews=[]
                supplier_name=[]
                product_link=[]
                with st.spinner("⏳&nbsp; Data Extraction On Progress..."):
                 for product_url in my_cursor.fetchall() :
                        #Connecting with Google Chrome Browser
                        driver = webdriver.Chrome()
                        #--------------------------------------------------------------------------------------------
                        #Code for disabling the images in webpage to reduce the iteration time for increasing efficiency  
                        chrome_options = webdriver.ChromeOptions()
                        prefs = {"profile.managed_default_content_settings.images": 2}
                        chrome_options.add_experimental_option("prefs", prefs)
                        driver = webdriver.Chrome(options=chrome_options)
                        #---------------------------------------------------------------------------------------------  
                        try:
                            driver.get(product_url[0])
                            driver.minimize_window()
                        except Exception as e:
                            print("Exception_Occured :",e)
                        #product_link
                        product_link.append(product_url[0])
                        #product_name
                        try:
                            product_name_element=driver.find_element(By.CSS_SELECTOR,"h1.pdp-title")
                            product_name.append(product_name_element.text)
                        except:
                            product_name.append(None)
                        #material
                        try:
                            material_element=driver.find_element(By.XPATH,'//div[contains(@class,"index-row") and .//div[@class="index-rowKey" and contains(text(), "Fabric")]]//div[@class="index-rowValue"]')
                            material.append(material_element.text)
                        except:
                            material.append(None)
                        #description
                        try:
                            product_description_element=driver.find_element(By.CSS_SELECTOR,"h1.pdp-name")
                            product_description.append(product_description_element.text)
                        except:
                            product_description.append(None)
                        #original_price
                        try:
                            orginal_price_element=driver.find_element(By.CSS_SELECTOR,"span.pdp-mrp>s")
                            original_price.append(orginal_price_element.text)
                        except:
                            original_price.append(None)
                        #discount_percentage:
                        try:
                            discount_percentage_element=driver.find_element(By.CSS_SELECTOR,"span.pdp-discount") 
                            match = re.search(r'\((.*?)\)', discount_percentage_element.text)
                            if match:
                                result = match.group(1)
                            discount_percentage.append( result)
                        except:
                            discount_percentage.append(None)
                        #discounted_price
                        try:
                            discount_price_element=driver.find_element(By.CSS_SELECTOR,"span.pdp-price>strong")
                            discounted_price.append(discount_price_element.text)
                        except:
                            discounted_price.append(None)
                        #avg_rating_for_five
                        try:
                            customer_rating_element=driver.find_element(By.CSS_SELECTOR,"div.index-flexRow.index-averageRating>span")
                            avg_rating_for_five.append(customer_rating_element.text)
                        except:
                            avg_rating_for_five.append(None)
                        #product_image_url
                        try:
                            image_text=driver.find_element(By.CSS_SELECTOR,"div.image-grid-container.common-clearfix > div:nth-child(1) > div.image-grid-imageContainer> div").get_attribute("style")
                            image_url_match = re.search(r'url\("([^"]+)"\);', image_text)
                            if image_url_match:
                                image_url = image_url_match.group(1)
                                product_image_url.append(image_url)    
                        except Exception as e:
                            print(e)
                            print("error")
                            product_image_url.append(None)
                        #total_ratings
                        try:
                            total_rating_element=driver.find_element(By.CSS_SELECTOR,"div.index-ratingsCount")
                            total_ratings.append(total_rating_element.text[:-8])
                        except:
                            total_ratings.append(None)
                        #available_sizes
                        try:
                            size_element=driver.find_elements(By.CSS_SELECTOR,"div.size-buttons-size-buttons>div.size-buttons-tipAndBtnContainer>div.size-buttons-buttonContainer>button>p")
                            size_text_list=[i.text for i in size_element]
                            available_sizes.append(",".join(map(str,size_text_list)))
                        except:
                            available_sizes.append(None)
                        #fit_type
                        try:
                            fit_element=driver.find_element(By.XPATH,'//div[contains(@class,"index-row") and .//div[@class="index-rowKey" and contains(text(), "Fit")]]//div[@class="index-rowValue"]')
                            fit_type.append(fit_element.text)
                        except:
                            fit_type.append(None)        
                        #total_text_reviews
                        try:
                            total_reviews_element=driver.find_element(By.XPATH, '//*[@id="mountRoot"]/div/div[1]/main/div[2]/div[2]/main/div/div/div[3]')
                            total_reviews_text=(total_reviews_element).text
                            total_reviews=re.findall(r'\((.*?)\)',total_reviews_text)
                            total_text_reviews.append(total_reviews[0])
                        except:
                            total_text_reviews.append(None)
                        #product_code
                        try:
                            product_code_element=driver.find_element(By.CSS_SELECTOR,"div.supplier-supplier>span>span.supplier-styleId")
                            product_code.append(product_code_element.text)
                        except:
                            product_code.append(None)
                        #supplier_name
                        try:
                            supplier_element=driver.find_element(By.CSS_SELECTOR,"span.supplier-productSellerName")
                            supplier_name.append(supplier_element.text)
                        except:
                            supplier_name.append(None)
                        time.sleep(0.1)
                        #finally closing the browser
                        driver.quit()                 
                #------------------------------------------------------------------------------
                #Creating a dictionary of product data
                with st.spinner("Loading to Display...."):
                            product_data={  
                                            "product_code": product_code,
                                            "product_name":product_name,
                                            "product_description": product_description,
                                            "material": material,
                                            "fit_type": fit_type,
                                            "available_sizes": available_sizes,
                                            "original_price": original_price,
                                            "discounted_price": discounted_price,
                                            "discount_percentage": discount_percentage,
                                            "total_ratings": total_ratings,
                                            "avg_rating_for_five": avg_rating_for_five,
                                            "total_text_reviews": total_text_reviews,
                                            "supplier_name": supplier_name,
                                            "product_image_url": product_image_url,
                                            "product_link":product_link
                                        }
                            #Creating DataFrame of product data
                            product_data_df=pd.DataFrame(product_data)
                            st.markdown("### :orange[T-Shirts Information:]")
                            st.table(product_data_df)
 
#------------------------------------------------------------------------------------------------------------------
                            with st.spinner("Storing Data Into MYSQL Databse"):
                                create_table_query = """
                                                CREATE TABLE IF NOT EXISTS t_shirts_data (
                                                        product_code INT PRIMARY KEY,
                                                        product_name VARCHAR(255),
                                                        product_description TEXT,
                                                        material VARCHAR(255),
                                                        fit_type VARCHAR(255),
                                                        available_sizes VARCHAR(255),
                                                        original_price VARCHAR(255),
                                                        discounted_price VARCHAR(255),
                                                        discount_percentage VARCHAR(255),
                                                        total_ratings VARCHAR(255),
                                                        avg_rating_for_five FLOAT,
                                                        total_text_reviews VARCHAR(255),
                                                        supplier_name VARCHAR(255),
                                                        product_image_url VARCHAR(255),
                                                        product_link VARCHAR(255)
                                                         ) """
                                my_cursor.execute(create_table_query)
                                mysql_database.commit()
                                for index, row in product_data_df.iterrows():
                                    data_insert_query= """
                                                        INSERT INTO t_shirts_data (
                                                            product_code, product_name, product_description, material, fit_type,
                                                            available_sizes, original_price, discounted_price, discount_percentage,
                                                            total_ratings, avg_rating_for_five, total_text_reviews, supplier_name,
                                                            product_image_url, product_link) 
                                                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                                                        """
                                    data_values = (
                                                            row["product_code"], row["product_name"], row["product_description"],
                                                            row["material"], row["fit_type"], row["available_sizes"],
                                                            row["original_price"], row["discounted_price"], row["discount_percentage"],
                                                            row["total_ratings"], row["avg_rating_for_five"], row["total_text_reviews"],
                                                            row["supplier_name"], row["product_image_url"], row["product_link"]
                                                          )
                                    my_cursor.execute(data_insert_query, data_values)
                                mysql_database.commit()

                            st.markdown("### 👍 &nbsp; :green[T-Shirts Data Stored Successfully  to MYSQL Database.]")     
                                 
with tab_3:
        mysql_database=mysql.connector.connect( 
                                                host="localhost",
                                                user="root",
                                                password="952427",
                                                database="myntra_t_shirts_data"
                                                )
        my_cursor=mysql_database.cursor(buffered=True)
        #Product namequery
        select_brand_query = "SELECT product_code ,product_name FROM t_shirts_data"
        my_cursor.execute(select_brand_query )
        brand_selections = my_cursor.fetchall()
        brand_list=[brand[1] for brand in brand_selections]
        select_brand = st.selectbox("⭐  &nbsp; Select Brand   &nbsp; : ",  brand_list)
        #Product code query
        product_code_query="SELECT product_code FROM t_shirts_data WHERE product_name=%s "
        my_cursor.execute(product_code_query,(select_brand,))
        product_code_selections=my_cursor.fetchall()
        product_codes_list = [code[0] for code in product_code_selections]
        select_product_code = st.selectbox("⭐  &nbsp; Select Product Code &nbsp; :", product_codes_list)
        #View_Button
        View_data_button=st.button(":red[View Product Information]")
        col_1, col_2 = st.columns(2)
        if View_data_button: 
                    #Product Information
                    with col_2:
                            view_query="SELECT * FROM t_shirts_data WHERE product_name=%s AND  product_code=%s "
                            values=(select_brand,select_product_code)
                            my_cursor.execute(view_query,values)
                            data=my_cursor.fetchall()
                            st.markdown(" ### 📋 :orange[Product Details:]")
                            for row in data:  
                                product_info = [
                                                    ("Product Name", row[1]),
                                                    ("Product Description", row[2]),
                                                    ("Material", row[3]),
                                                    ("Fit Type", row[4]),
                                                    ("Available Sizes", row[5]),
                                                    ("Original Price", row[6]),
                                                    ("Discounted Price", row[7]),
                                                    ("Discount Percentage", row[8]),
                                                    ("Total Ratings", row[9]),
                                                    ("Avg Rating for Five", row[10]),
                                                    ("Total Text Reviews", row[11]),
                                                    ("Product Code", row[0]),
                                                    ("Supplier Name", row[12]),
                                                    # ("Product Image URL", row[13]),
                                                    # ("Product Link", row[14]),
                                                 ]
                                st.table(product_info)
                                st.info("### 🔗 :orange[ [Link to Product  ]({})] ".format(row[14]))
                    #Product Image
                    with col_1:
                            st.markdown(" ### 🖼️ :orange[Product Image:]")
                            view_query="SELECT * FROM t_shirts_data WHERE product_name=%s AND  product_code=%s "
                            values=(select_brand,select_product_code)
                            my_cursor.execute(view_query,values)
                            data=my_cursor.fetchall()
                            for row in data:
                                 image_url=row[13]
                                 st.image(image_url, caption='', use_column_width=True)
#Deleting the Database Entries
with tab_4:
        mysql_database=mysql.connector.connect( 
                                                host="localhost",
                                                user="root",
                                                password="952427",
                                                database="myntra_t_shirts_data"
                                                )
        pass_key=st.text_input("Enter Password")
        my_cursor=mysql_database.cursor(buffered=True)
        confirm_checkbox_1=st.checkbox("Confirm")
        delete_link_table=st.button(":red[Click to Delete Product Links]")
        confirm_checkbox_2=st.checkbox("Confirm",key="checkbox2")
        delete_data_table=st.button(":red[Click to Delete Tshirt Data]")
        if delete_link_table and confirm_checkbox_1 and pass_key=="123123":
            drop_table_query_1 ="TRUNCATE TABLE product_link_table"
            my_cursor.execute(drop_table_query_1)
            st.text("✅ Links Data Deleted Succesfully")        
        if delete_data_table and confirm_checkbox_2 and pass_key=="123123":
            drop_table_query_2 ="TRUNCATE TABLE t_shirts_data"
            my_cursor.execute(drop_table_query_2)
            st.text("✅ Product Data Deleted Succesfully") 
        mysql_database.commit()
        my_cursor.close()
        mysql_database.close()

st.markdown("#")
st.text("created by banuprakash vellingiri ❤️                                                                                                           credits:myntra.com")       
