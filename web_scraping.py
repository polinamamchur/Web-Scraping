import requests
from bs4 import BeautifulSoup
from prettytable import PrettyTable
import csv


def get_course_info():
    base_url = "https://mate.academy/"
    response = requests.get(base_url)
    soup = BeautifulSoup(response.text, 'html.parser')

    courses = soup.find_all('div', class_='DropdownProfessionsItem_item__BRxO2')
    unique_courses = []

    for course in courses:
        try:
            course_name = course.find('span', class_='ButtonBody_buttonText__34ExO').text.strip()
            course_link = course.find('a', href=True)['href']
            full_course_link = f"https://mate.academy{course_link}"

            course_description = get_course_description(full_course_link)
            study_options = get_study_options(full_course_link)

            unique_courses.append({
                "Course Name": course_name,
                "Course Description": course_description,
                "Study Options": study_options
            })
        except Exception as e:
            print(f"Error occurred: {e}")

    return unique_courses


def get_course_description(course_url):
    try:
        response = requests.get(course_url)
        soup = BeautifulSoup(response.text, 'html.parser')

        description = soup.find('pre', class_='typography_landingTextMain__Rc8BD SalarySection_aboutProfession__1VFHK')

        if description:
            return description.text.strip()
        else:
            return "Description not found"
    except Exception as e:
        print(f"Error fetching course description: {e}")
        return "Error fetching description"


def get_study_options(course_url):
    try:
        response = requests.get(course_url)
        soup = BeautifulSoup(response.text, 'html.parser')

        study_options = []

        full_time_option = soup.find('a', string="Навчатися повний день")
        if full_time_option:
            study_options.append("Навчатися повний день")

        flex_time_option = soup.find('a', string="Навчатися у вільний час")
        if flex_time_option:
            study_options.append("Навчатися у вільний час")

        if not study_options:
            return "No study options available"

        return ", ".join(study_options)
    except Exception as e:
        print(f"Error fetching study options: {e}")
        return "Error fetching study options"


def print_courses(courses_info):
    table = PrettyTable()

    table.field_names = ["Course Name", "Course Description", "Study Options"]

    # Додаємо інформацію про курси в таблицю
    for course in courses_info:
        table.add_row([
            course['Course Name'],
            course['Course Description'],
            course['Study Options']
        ])

    # Виводимо таблицю
    print(table)


def save_to_csv(courses_info, filename='courses_info.csv'):
    # Відкриваємо CSV файл для запису
    with open(filename, 'w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=["Course Name", "Course Description", "Study Options"])
        writer.writeheader()

        for course in courses_info:
            writer.writerow(course)


courses_info = get_course_info()
print_courses(courses_info)
save_to_csv(courses_info)
