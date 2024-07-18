import streamlit as st
import mysql.connector
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import StaleElementReferenceException, ElementClickInterceptedException, TimeoutException
st.title("redbus")

connection = mysql.connector.connect(
    host="localhost",
    user="root",
    password="chris",
    database="redbus"
)
datas = connection.cursor()
driver = webdriver.Chrome()
driver.get("https://www.redbus.in/")
driver.maximize_window()
time.sleep(4)
driver.execute_script("window.scrollTo(0, 700);")
time.sleep(3)

listOfBus = []

def get_govt_buses():
    return driver.find_elements(By.CLASS_NAME, "rtcName")

finalwidth = 480
gov_bus = get_govt_buses()

def clear_input(element):
    driver.execute_script("arguments[0].value = '';", element)
    element.clear()

def select_specific_dropdown_option(text):
    dropdown = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "C120_suggestion-wrap"))
    )
    options = dropdown.find_elements(By.CLASS_NAME, "C120_suggestions_list")
    for option in options:
        if text.lower() in option.text.lower():
            option.click()
            break

for i in range(len(gov_bus)):
    for _ in range(3):  # Retry up to 3 times
        try:
            gov_bus = get_govt_buses()
            govt_bus = gov_bus[i]
            busOp = govt_bus.text
            print(busOp)
            if busOp not in listOfBus:
                govt_bus.click()
                time.sleep(5)
                listOfBus.append(busOp)
                busDetails = driver.find_element(By.CLASS_NAME, "route").text.split(" to ")
                src = busDetails[0]
                dest = busDetails[1]

                # Clear and setting departure location
                departure_search = driver.find_element(By.ID, 'txtSource')
                clear_input(departure_search)
                departure_search.send_keys(src)
                time.sleep(2)
                select_specific_dropdown_option(src)  # Select specific dropdown option

                # Clear and setting destination location
                destination_search = driver.find_element(By.ID, 'txtDestination')
                clear_input(destination_search)
                destination_search.send_keys(dest)
                time.sleep(2)
                select_specific_dropdown_option(dest)  # Select specific dropdown option

                calendar_el = driver.find_element(By.ID, 'txtOnwardCalendar')
                calendar_el.click()
                time.sleep(5)
                today_day = datetime.today().strftime('%d')
                date_element = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, f'//*[@id="rb-calmiddle"]/ul[2]/li[{today_day}]/span'))
                )
                date_element.click()
                time.sleep(2)
                print("Entering into search button")
                search_box = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.CLASS_NAME, "searchBuses"))
                )
                print("Found button and name: " + search_box.text)
                search_box.click()
                print('Search clicked')
                time.sleep(5)

                # Scroll to the bottom of the page to load all bus items
                last_page = driver.execute_script("return document.body.scrollHeight")
                while True:
                    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    time.sleep(2)  # Wait for the page to load
                    new_page = driver.execute_script("return document.body.scrollHeight")
                    if new_page == last_page:
                        break
                    last_page = new_page

                bus_list = driver.find_elements(By.CLASS_NAME, "bus-item")
                print("=====================================================")

                for bus in bus_list:
                    busRoute = src + " To " + dest
                    busName = bus.find_element(By.CLASS_NAME, "travels").text
                    depTime = bus.find_element(By.CLASS_NAME, "dp-time").text
                    farePrice = bus.find_element(By.CLASS_NAME, "fare").text
                    farePrice = farePrice.replace("INR ", "")
                    ratings = bus.find_element(By.CLASS_NAME, "rating-sec").text
                    seat = bus.find_element(By.CLASS_NAME, "seat-left").text
                    seat = seat.split(' ')[0]
                    busType = bus.find_element(By.CLASS_NAME, "bus-type").text
                    duration = bus.find_element(By.CLASS_NAME, "dur").text
                    busLink = driver.current_url
                    depTime = datetime.today().strftime("%Y-%m-%d") + " " + depTime

                    time_str = bus.find_element(By.CLASS_NAME, "bp-time").text
                    date_str = "18 Jul " + datetime.today().strftime("%y")
                    date_obj = datetime.strptime(date_str, "%d %b %y")
                    time_obj = datetime.strptime(time_str, "%H:%M").time()
                    reachingTime = datetime.combine(date_obj, time_obj)
                    owner = "Government"

                    print(f"Bus Name = {busName}, DepTime = {depTime}, FarePrice = {farePrice}, "
                          f"Rating = {ratings}, Seat = {seat}, Bustype = {busType}, "
                          f"Duration = {duration}, ReachingTime = {reachingTime}, "
                          f"Buslink = {busLink}, Owner = {owner}")
                    sql = "INSERT INTO bus_routes (route_name,route_link,busname,bustype,departing_time,duration,reaching_time,star_rating,price,seats_available,owner) VALUES (%s, %s ,%s, %s, %s, %s, %s,%s,%s,%s,%s)"
                    val = (busRoute,busLink,busName,busType,depTime,duration,reachingTime,ratings,farePrice,seat,owner)
                    datas.execute(sql, val)
                    connection.commit()
                    print(datas.rowcount, "record inserted.")
                    break

                driver.back()
                time.sleep(5)
                driver.back()
                # Clear all local storage
                driver.execute_script("window.localStorage.clear();")
                time.sleep(5)
                driver.execute_script("window.scrollTo(0, 700);")
                carousel = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.ID, "Carousel"))
                )
                driver.execute_script(f"arguments[0].scrollBy({finalwidth}, 0);", carousel)
                finalwidth += 480
                time.sleep(5)
                time.sleep(3)

        except StaleElementReferenceException:
            print('StaleElementReferenceException encountered. Retrying...')
            time.sleep(1)  # Wait a bit before retrying
            continue
        except ElementClickInterceptedException:
            print('ElementClickInterceptedException encountered. Retrying...')
            time.sleep(1)  # Wait a bit before retrying
            continue
        except TimeoutException:
            print('TimeoutException encountered. Retrying...')
            time.sleep(1)  # Wait a bit before retrying
            continue
        except Exception as e:
            print(f'An error occurred: {e}')
            break

driver.quit()
