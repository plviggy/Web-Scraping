########   CODE TO WEBSCRAPE RENTAL CAR TAX INFORMATION    ########
#Date: 2020/01/10
#Time: 12:59 PM
#Author: Viggy Palaniappan, Jacobs

#Step-I Importing the modules required for the analysis
import time
tic = time.perf_counter()

import selenium
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
import threading

import numpy as np
import csv
from pathlib import Path
import os.path

import datetime
import time
from datetime import datetime, date, timedelta

import lxml.html
from lxml.html import parse
import pdb


from contextlib import suppress
from selenium.common.exceptions import NoSuchElementException
#----------------------------End of Step-I------------------------------

#Step-II Creating a function that does web scraping and collects information about the rental fees involved

#The exception array contains all the airports not analyzed
Exception_Array = []


#Defining the function. The parameters for this function include following parameters
#1.The path to the chromedriver (driver)
#2.The airport to be analyzed (Airport)
#3.The pickup date (d1)
#4.The return date (d2)

chromepath =r"C:\Users\PalaniV\Downloads\chromedriver_win32\chromedriver.exe"
driver = webdriver.Chrome(chromepath)

#-------------------------Function-------------------------------------
def Avis(Airport, d1, d2, Trial_Counter):

#The global temp variable keeps track of airports whose analysis is complete. The completed
#airports have temp_0 = 1.

    global temp_0
    temp_0 = 0

#Opening the webpage in the google chrome.
    driver.get("https://www.avis.com/en/home")
    driver.maximize_window()

#Giving a rest time of 3 sec for the code to load the webpage.
    time.sleep(2)

#Giving a wait time of 20 sec for the code
    wait = WebDriverWait(driver, 20)
#Assigining a temp variable to click the pick up location on the webpage.
    #temp = wait.until(EC.visibility_of_element_located((By.ID,"PicLoc_value")))
    temp = driver.find_element_by_xpath("//*[@id= 'PicLoc_value']")
#Clicked the pick up location
    temp.click()
#Clear the previous entries in the pick up location
    temp.clear()
#Giving the airport name in the pick up location
    temp.send_keys(Airport)
    time.sleep(2)
#Assigining a temp variable to click the pick up date
    temp = driver.find_element_by_xpath("//*[@id='from']")
    temp.click()
    temp.clear()
#Giving the pick up date value from d1 parameter
    temp.send_keys(d1)
    time.sleep(2)
    temp = driver.find_element_by_xpath("//*[@id='to']")
    temp.click()
    temp.clear()
    temp.send_keys(d2)
    time.sleep(5)
#Submit button is a parameter used to click on the submit button after selecting the location
# pick up date and drop off date
    submitButton = driver.find_element_by_xpath(".//*[@id='res-home-select-car']")
# clicking on the submit button
    driver.execute_script("arguments[0].click();", submitButton)


# letting the webpage load for 15 sec
    time.sleep(5)


# Initiating a for loop to find the intermediate car. This for loop is designed for dates which are nearby to the today's date.
# The structure of the webpage changes with the dates selected. The nearby dates have no offers posted on the website. So, the
# structure is bit different.
    for i in range(20):
        try:
            #The indexing for the cars start for 2. However the for loop starts from i = 0. To accomodate such difference in indexing,
            #another variable called p is initiated.
            p = i
            #This temp variable finds the location of the "Intermediate" text in the html page.
            temp = driver.find_elements_by_xpath("//h3[@ng-bind = 'car.carGroup']")[p]
            #Introducing an if statement to select the intermediate car in the webpage
            if temp.text == "Intermediate":
                #print(i+1)
                #The global variable temp_0 is assigned 1 if the "Intermediate" car is found on the webpage
                temp_0 = 1
                try:
                    #Clicking on submit button takes you to pay later option.
                    submitButton = driver.find_elements_by_xpath("//*[@id='res-vehicles-pay-later']")[p]
                    driver.execute_script("arguments[0].click();", submitButton)
                    time.sleep (5)
                    #Clicks on the modify link in the webpage
                    temp = driver.find_element_by_xpath(".//*[@id='modify_link']")
                    temp.click()
                    #This gives the location of the taxes information in the webpage.
                    temp_2 = driver.find_element_by_xpath("//*[@id='vehicleTeaser']/div[2]/div/div[1]/div/section/div/div[2]/div[2]/div[5]")
                    #This gives the location of the base rate for one/two days in the webpage.
                    temp_3 = driver.find_element_by_xpath("//*[@id='vehicleTeaser']/div[2]/div/div[1]/div/section/div/div[2]/div[2]/div[2]")

                    #Printing the name of the airport, base rate and the taxes
                    print (Airport)
                    print (temp_3.text)
                    print (temp_2.text)
                    break

                    #This exception is to handle with airports having only pay now option. The steps are same. However, the id for the first step
                    #(selecting the pay now option) changes.
                except:
                    submitButton = driver.find_elements_by_xpath("//*[@id='res-vehicles-select']")[p]
                    driver.execute_script("arguments[0].click();", submitButton)
                    time.sleep(5)
                    temp = driver.find_element_by_xpath(".//*[@id='modify_link']")
                    temp.click()
                    temp_2 = driver.find_element_by_xpath("//*[@id='vehicleTeaser']/div[2]/div/div[1]/div/section/div/div[2]/div[2]/div[5]")
                    temp_3 = driver.find_element_by_xpath("//*[@id='vehicleTeaser']/div[2]/div/div[1]/div/section/div/div[2]/div[2]/div[1]")
                    print (Airport)
                    print (temp_3.text)
                    print (temp_2.text)
                    break

        except IndexError as e:
            pass
        #Any other exceptions would be bypassed using the following steps
        except NoSuchElementException:
            pass

# This part of the code checks if the tax information is collected from the airport
#temp_0 = 0 implies the intermediate car is not found at the airport
    if temp_0 ==0:
        try:
            # Introducing a trial counter to limit the number of times an airport is
            #reanalyzed. When "Trial_Counter" = 1, the code stops reanalyzing the airport
            #By default, the previous for loops analyze an airport once. Consequently, if
            # it's not analyzed, it goes through this loop once with "Trial_Counter =0".
            #After completing this loop once, the code gives up on the airport if the tax
            #information is not collected.
            if Trial_Counter ==0:
                try:

                    Trial_Counter = Trial_Counter + 1
                    #Rerunning the avis function for the airport to see if tax information
                    #can be extracted the second time.
                    Avis(Airport, d1, d2, Trial_Counter)
                    if temp_0 ==0:
                        try:
                            #If the airport doesn't go through the second time, it is added
                            #into the exception array. This exception array has a list of
                            #all airports not analyzed by this code. THis list can be used
                            #once again to see if these airports can go through next time.
                            Exception_Array.append(Airport)
                         #Exceptions are bypassed
                        except NoSuchElementException:
                            pass
                except NoSuchElementException:
                    pass
        except NoSuchElementException:
            pass

#-------------------------Input Parameters-------------------------------------

# Creating a function having a list of all the airports.
def main():

    apts = ["ATL","BOS","BWI","CLT","DCA","DEN","DFW","DTW","EWR","FLL","HNL","IAD","IAH","JFK","LAS","LAX","LGA","MCO","MDW","MIA",
    "MSP","ORD","PDX","PHL","PHX","SAN","SEA","SFO","SLC","TPA"]

    #apts = ["BWI"]

    Exception_Airports = []

    #pick up date is "d1" This parameter is used in "Avis{}" function.
    d1 = "02/25/2021"
    #Drop off date is "d2" This parameter is used in "Avis()" function.
    d2 = "02/25/2021"
    #Initiating "Trial_Counter" here. Everytime an airport is analyzed, this parameter is reassigned to "0"
    Trial_Counter = 0

    #Running a for loop over the list of the airports
    for apt in apts:
        Avis(apt, d1, d2, Trial_Counter)

#Syntax of the function. I don't have much idea about this. If you have any valuable input about this,
#kindly, mention in the comments section here.
if __name__ == "__main__":
    main()

#prints the airports not analyzed by this code.
print ("This code couldn't extract rental information for the following airports. Kindly, try this code once more for the following airports")
print (Exception_Array)
toc = time.perf_counter()
print("Code run time:",toc-tic," seconds")
