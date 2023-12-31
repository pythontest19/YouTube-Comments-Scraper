"""
Main script for scraping comments from a YouTube video.

Usage:
    $ python main.py YOUTUBE_VIDEO_URL
"""

import csv
import io
from selenium import webdriver
from selenium.common import exceptions
import sys
import time

def scrape(url):
    """
    Extracts comments from a YouTube video given its URL.

    Args:
        url (str): The URL of the YouTube video.

    Raises:
        selenium.common.exceptions.NoSuchElementException:
        When certain elements to look for cannot be found.
    """

    # Note: Download and replace the argument with the path to the driver executable.
    # Download the executable and move it into the webdrivers folder.
    driver = webdriver.Chrome('./webdrivers/chromedriver')

    # Navigate to the URL, maximize the current window, and
    # pause execution for at least 5 seconds to allow the page to load.
    driver.get(url)
    driver.maximize_window()
    time.sleep(5)

    try:
        # Extract the elements storing the video title and comment section.
        title = driver.find_element_by_xpath('//*[@id="container"]/h1/yt-formatted-string').text
        comment_section = driver.find_element_by_xpath('//*[@id="comments"]')
    except exceptions.NoSuchElementException:
        # Handle the case where the elements cannot be found.
        error = "Error: Double-check the selector OR "
        error += "the element may not be on the screen at the time of the find operation"
        print(error)
        driver.quit()
        return

    # Scroll into view the comment section, then allow some time
    # for everything to load.
    driver.execute_script("arguments[0].scrollIntoView();", comment_section)
    time.sleep(7)

    # Scroll all the way down to the bottom to load all comments.
    last_height = driver.execute_script("return document.documentElement.scrollHeight")

    while True:
        # Scroll down to trigger the next load.
        driver.execute_script("window.scrollTo(0, document.documentElement.scrollHeight);")
        time.sleep(2)

        # Calculate new scroll height and compare with the last scroll height.
        new_height = driver.execute_script("return document.documentElement.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

    # One last scroll just in case.
    driver.execute_script("window.scrollTo(0, document.documentElement.scrollHeight);")

    try:
        # Extract the elements storing the usernames and comments.
        username_elems = driver.find_elements_by_xpath('//*[@id="author-text"]')
        comment_elems = driver.find_elements_by_xpath('//*[@id="content-text"]')
    except exceptions.NoSuchElementException:
        error = "Error: Double-check selector OR "
        error += "element may not yet be on the screen at the time of the find operation"
        print(error)
        driver.quit()
        return

    print("> VIDEO TITLE: " + title + "\n")

    with io.open('results.csv', 'w', newline='', encoding="utf-16") as file:
        writer = csv.writer(file, delimiter=",", quoting=csv.QUOTE_ALL)
        writer.writerow(["Username", "Comment"])
        for username, comment in zip(username_elems, comment_elems):
            writer.writerow([username.text, comment.text])

    driver.quit()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python main.py YOUTUBE_VIDEO_URL")
    else:
        scrape(sys.argv[1])
