from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
import json

chrome_options = Options()
chrome_options.add_argument("--headless")

driver = webdriver.Chrome(options=chrome_options)

course_links = [
    "https://sunbeaminfo.in/modular-courses/apache-spark-mastery-data-engineering-pyspark",
    "https://sunbeaminfo.in/modular-courses/aptitude-course-in-pune",
    "https://sunbeaminfo.in/modular-courses/core-java-classes",
    "https://sunbeaminfo.in/modular-courses/data-structure-algorithms-using-java",
    "https://sunbeaminfo.in/modular-courses/Devops-training-institute",
    "https://sunbeaminfo.in/modular-courses/dreamllm-training-institute-pune",
    "https://sunbeaminfo.in/modular-courses/machine-learning-classes",
    "https://sunbeaminfo.in/modular-courses/mastering-generative-ai",
    "https://sunbeaminfo.in/modular-courses.php?mdid=57",
    "https://sunbeaminfo.in/modular-courses/mern-full-stack-developer-course",
    "https://sunbeaminfo.in/modular-courses/mlops-llmops-training-institute-pune",
    "https://sunbeaminfo.in/modular-courses/python-classes-in-pune"
]

all_courses = []

for link in course_links:
    driver.get(link)
    time.sleep(3)

    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(2)

    course_data = {"url": link}

    try:
        course_data["course_name"] = driver.find_element(By.TAG_NAME, "h1").text
    except:
        course_data["course_name"] = ""

    details = {}
    paragraphs = driver.find_elements(By.XPATH, "//p[contains(text(),':')]")
    for p in paragraphs:
        text = p.text.strip()
        if ":" in text:
            k, v = text.split(":", 1)
            details[k.strip()] = v.strip()

    course_data["basic_details"] = details

    sections = {}
    plus_buttons = driver.find_elements(By.XPATH, "//a[contains(@href,'#collapse')]")

    for btn in plus_buttons:
        title = btn.text.strip()
        try:
            driver.execute_script("arguments[0].scrollIntoView(true);", btn)
            time.sleep(1)
            btn.click()
            time.sleep(1)

            cid = btn.get_attribute("href").split("#")[-1]
            sections[title] = driver.find_element(By.ID, cid).text
        except:
            sections[title] = ""

    course_data["sections"] = sections
    all_courses.append(course_data)

driver.quit()

with open("data/modular_courses.json", "w", encoding="utf-8") as f:
    json.dump(all_courses, f, indent=4, ensure_ascii=False)

print("Scraping completed successfully")