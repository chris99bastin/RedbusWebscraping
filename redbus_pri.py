import mysql.connector


import time
from datetime import datetime
#from time import sleep
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys

connection = mysql.connector.connect(
    host="localhost",
    user="root",                
    password="chris",
    database="redbus"
)
datas=connection.cursor()
driver=webdriver.Chrome()
driver.get("https://www.redbus.in/")
driver.maximize_window()
time.sleep(4)
bus_routes=[
     {"src":"Chennai","Des":"Karaikudi"},
     {"src":"Chennai","Des":"Kalayarkoil"}
     ]
for route in bus_routes:
    departure_search=driver.find_element(By.ID,'src')
    departure_search.send_keys(route.get('src'))
    time.sleep(1)
    destination_search=driver.find_element(By.ID,'dest') 
    destination_search.send_keys(route.get('Des'))
    time.sleep(2)
    date_input=driver.find_element(By.ID,"onwardCal")
    date_input.click()
    time.sleep(3)
    calendar= WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.CLASS_NAME, 'DatePicker__CalendarContainer-sc-1kf43k8-0'))
    )

        # Locate and click the desired date
        # Replace '15' with the desired day of the month
    today_day = datetime.today().strftime('%d')
    today_date = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, f"//span[text()='{today_day}']/ancestor::div[contains(@class, 'DayTiles__CalendarDaysBlock-sc-1xum02u-0')]"))
    )
    today_date.click()
    time.sleep(2)
    search=driver.find_element(By.ID,'search_button') 
    search.click()
    time.sleep(5)
    #Scroll to the bottom of the page to load all bus items
    last_page = driver.execute_script("return document.body.scrollHeight")
    while True:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)  # Wait for the page to load
            new_page = driver.execute_script("return document.body.scrollHeight")
            if new_page == last_page:
                break
            last_page = new_page
    bus_list = driver.find_elements(By.CLASS_NAME,"bus-item")
    print("=====================================================")
    print("dep= " +route.get("src") + " des = "+ route.get("Des") )
    for bus in bus_list :
        busRoute=route.get("src") + " To " +route.get("Des")
        busName = bus.find_element(By.CLASS_NAME,"travels").text
        depTime = bus.find_element(By.CLASS_NAME,"dp-time").text
        farePrice = bus.find_element(By.CLASS_NAME,"fare").text
        farePrice=farePrice.replace("INR ","")
        ratings=bus.find_element(By.CLASS_NAME,"rating-sec").text
        seat=bus.find_element(By.CLASS_NAME,"seat-left").text
        seat = seat.split(' ')[0]
        busType=bus.find_element(By.CLASS_NAME,"bus-type").text
        duration=bus.find_element(By.CLASS_NAME,"dur").text
        busLink=driver.current_url
        depTime = datetime.today().strftime("%Y-%m-%d") + " " + depTime

        time_str = bus.find_element(By.CLASS_NAME,"bp-time").text
        date_str = bus.find_element(By.CLASS_NAME,"next-day-dp-lbl").text.replace("-"," ") + " " + datetime.today().strftime("%y")
        date_obj = datetime.strptime(date_str, "%d %b %y")
        time_obj = datetime.strptime(time_str, "%H:%M").time()
        reachingTime = datetime.combine(date_obj, time_obj)
        
        owner="Private"
        print("BusRoute=" + busRoute +", Bus Name = " + busName +  ", DepTime = " + depTime + ", FarePrice="+ farePrice +
               " ,Rating = " + ratings +", seat= " + seat +" , Bustype=" + busType +
               ", Duration=" + duration+ ", ReachingTime=" + "" +  ", Buslink= " + busLink +",Owner="+ owner)
                    
        # insert date into tableb
        sql = "INSERT INTO bus_routes (route_name,route_link,busname,bustype,departing_time,duration,reaching_time,star_rating,price,seats_available,owner) VALUES (%s, %s ,%s, %s, %s, %s, %s,%s,%s,%s,%s)"
        val = (busRoute,busLink,busName,busType,depTime,duration,reachingTime,ratings,farePrice,seat,owner)
        datas.execute(sql, val)
        connection.commit()
        print(datas.rowcount, "record inserted.")
        
    time.sleep(2)
    driver.execute_script("window.localStorage.clear();")
    driver.back()
    

