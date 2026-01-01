from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

class SunbeamScraper:

    def __init__(self):
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")
        self.driver = webdriver.Chrome(options=options)
        self.base_url = "https://sunbeaminfo.in"
        self.final_data = {}

        self.course_links = []
        self.internship_links = []
        self.about_links = []
        self.precat_links = []

    # Scrape all links
    def scrape_all_links(self):
        self.driver.get(self.base_url)
        time.sleep(5)

        links = set()
        anchors = self.driver.find_elements(By.TAG_NAME, "a")
        for a in anchors:
            href = a.get_attribute("href")
            if href and href.startswith(self.base_url):
                if not any(x in href for x in ["#", ".pdf", ".jpg", ".png", "mailto", "tel"]):
                    links.add(href)

        self.course_links = sorted([l for l in links if "modular-courses" in l])
        self.internship_links = [l for l in links if "internship" in l]
        self.about_links = [l for l in links if "about-us" in l]
        self.precat_links = [l for l in links if "pre-cat" in l]

    # Scrape courses
    def scrape_courses(self):
        courses = []

        for link in self.course_links:
            self.driver.get(link)

            try:
                course_name = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.TAG_NAME, "h1"))
                ).text
            except:
                course_name = ""

            try:
                while True:
                    view_more = self.driver.find_element(By.XPATH, "//a[text()='View More']")
                    self.driver.execute_script("arguments[0].click();", view_more)
                    time.sleep(1)
            except:
                pass

            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)

            course = {"url": link, "course_name": course_name}

            details = {}
            paragraphs = self.driver.find_elements(By.XPATH, "//p[contains(text(),':')]")
            for p in paragraphs:
                if ":" in p.text:
                    k, v = p.text.split(":", 1)
                    details[k.strip()] = v.strip()
            course["basic_details"] = details

            sections = {}
            accordions = self.driver.find_elements(By.XPATH, "//a[contains(@href,'#collapse')]")
            for acc in accordions:
                title = acc.text.strip()
                try:
                    self.driver.execute_script("arguments[0].scrollIntoView(true);", acc)
                    self.driver.execute_script("arguments[0].click();", acc)
                    time.sleep(1)
                    cid = acc.get_attribute("href").split("#")[-1]
                    sections[title] = self.driver.find_element(By.ID, cid).text.strip()
                except:
                    sections[title] = ""
            course["sections"] = sections

            courses.append(course)
            print(f"Scraped course: {course_name}")

        self.final_data["Modular Courses"] = courses

    # Scrape internship data
    def scrape_internship(self):
        if not self.internship_links:
            return

        self.driver.get(self.internship_links[0])
        time.sleep(4)

        overview = [b.text.strip() for b in self.driver.find_elements(By.CSS_SELECTOR, ".main_info") if b.text.strip()]
        self.final_data["Internship Overview"] = overview

        accordion_data = {}
        accordions = self.driver.find_elements(By.CSS_SELECTOR, ".panel-heading a[href^='#collapse']")
        for acc in accordions:
            title = acc.text.strip()
            self.driver.execute_script("arguments[0].scrollIntoView(true);", acc)
            self.driver.execute_script("arguments[0].click();", acc)
            time.sleep(1)
            panel_id = acc.get_attribute("href").split("#")[-1]
            panel = self.driver.find_element(By.ID, panel_id)
            table = panel.find_elements(By.TAG_NAME, "table")

            if table:
                rows = table[0].find_elements(By.TAG_NAME, "tr")[1:]
                table_data = []
                for r in rows:
                    cols = r.find_elements(By.TAG_NAME, "td")
                    if len(cols) == 5:
                        table_data.append({
                            "technology": cols[0].text.strip(),
                            "aim": cols[1].text.strip(),
                            "prerequisite": cols[2].text.strip(),
                            "learning": cols[3].text.strip(),
                            "location": cols[4].text.strip()
                        })
                accordion_data[title] = table_data
            else:
                accordion_data[title] = panel.text.strip()

        self.final_data["Internship Accordion Information"] = accordion_data

        batches = []
        tables = self.driver.find_elements(By.XPATH, "//div[contains(@class,'table-responsive')]//table")
        for table in tables:
            for row in table.find_elements(By.TAG_NAME, "tr")[1:]:
                cols = row.find_elements(By.TAG_NAME, "td")
                if len(cols) >= 8:
                    batches.append({
                        "sr": cols[0].text.strip(),
                        "batch": cols[1].text.strip(),
                        "batch_duration": cols[2].text.strip(),
                        "start_date": cols[3].text.strip(),
                        "end_date": cols[4].text.strip(),
                        "time": cols[5].text.strip(),
                        "fees": cols[6].text.strip(),
                        "download": cols[7].text.strip()
                    })

        self.final_data["Internship Batch Schedule"] = batches

    # Scrape About Us
    def scrape_about(self):
        if not self.about_links:
            return

        self.driver.get(self.about_links[0])
        time.sleep(3)
        about = []
        sections = self.driver.find_elements(By.CSS_SELECTOR, "section")
        for sec in sections:
            if sec.text.strip():
                about.append(sec.text.strip())
        self.final_data["About Us"] = about

    # ⬇⬇⬇ **Save as TXT instead of JSON**
    def save(self):
        with open("data/sunbeam_complete_data.txt", "w", encoding="utf-8") as f:
            for section, content in self.final_data.items():
                # f.write("\n=============================================\n")
                f.write(f"{section}\n")
                # f.write("=============================================\n")

                if isinstance(content, list):
                    for item in content:
                        f.write(f"{item}\n")
                elif isinstance(content, dict):
                    for key, value in content.items():
                        f.write(f"\n➡ {key}\n")
                        if isinstance(value, list):
                            for d in value:
                                f.write(f"   - {d}\n")
                        else:
                            f.write(f"   {value}\n")
                else:
                    f.write(str(content))
                f.write("\n\n")

    # Close driver
    def close(self):
        self.driver.quit()

    # Run all scrapers
    def run(self):
        self.scrape_all_links()
        self.scrape_courses()
        self.scrape_internship()
        self.scrape_about()
        self.save()
        self.close()

if __name__ == "__main__":
    scraper = SunbeamScraper()
    scraper.run()
    print("Scraping completed successfully — Data saved in TEXT file ")