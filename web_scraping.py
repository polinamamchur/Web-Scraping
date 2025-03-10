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

            # Debugging: Print course link before fetching details
            print(f"Fetching details for: {full_course_link}")

            num_modules, num_topics, course_duration = get_course_details(full_course_link)

            # Ensure keys exist
            unique_courses.append({
                "Course Name": course_name,
                "Course Description": course_description or "Not available",
                "Study Options": study_options or "Not available",
                "Modules": num_modules or "Not found",
                "Topics": num_topics or "Not found",
                "Duration": course_duration.get('Duration', 'Not found')  # Only Duration as plain text
            })
        except Exception as e:
            print(f"Error occurred for {course_name}: {e}")

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


def get_course_details(course_url):
    try:
        response = requests.get(course_url)
        soup = BeautifulSoup(response.text, 'html.parser')

        # Пошук всіх модулів
        modules_list = soup.find('ul', class_='CourseModulesList_modulesList__C86yL')
        modules = modules_list.find_all('li', class_='color-dark-blue') if modules_list else []

        # Підрахунок кількості модулів
        num_modules = len(modules) if modules else "Not found"

        # Підрахунок кількості тем
        num_topics = 0
        for module in modules:
            topic_count_text = module.find('p',
                                           class_='CourseModulesList_topicsCount__H_fv3 typography_textMain__oRJ69')
            if topic_count_text:
                num_topics += int(topic_count_text.text.strip().split(' ')[0])  # Беремо лише число перед словом "тем"

        # Пошук тривалості курсу в елементах "Тривалість"
        duration_section = soup.find_all('div', class_='TableFeedView_rowWithButtons__j6_7p')

        # Ініціалізуємо змінні для тривалості
        full_time_duration = "Not found"
        flex_time_duration = "Not found"

        # Проходимо по знайдених елементах і шукаємо "Тривалість"
        for row in duration_section:
            title = row.find('div', class_='TableFeedView_rowTitle__X_wrw')
            content = row.find('div', class_='TableFeedView_rowContent__Nih2n')

            if title and content:
                title_text = title.text.strip()
                content_text = content.text.strip()

                # Якщо це "Тривалість"
                if "Тривалість" in title_text:
                    # Витягуємо тривалість
                    full_time_duration = content_text

        # Повертаємо знайдені дані
        return num_modules, num_topics, {"Duration": full_time_duration}

    except Exception as e:
        print(f"Error fetching course details: {e}")
        return "Error", "Error", {"Duration": "Error"}


def print_courses(courses_info):
    table = PrettyTable()

    # Додаємо нові поля для відображення
    table.field_names = ["Course Name", "Course Description", "Study Options", "Modules", "Topics", "Duration"]

    # Додаємо інформацію про курси в таблицю
    for course in courses_info:
        table.add_row([
            course['Course Name'],
            course['Course Description'],
            course['Study Options'],
            course['Modules'],
            course['Topics'],
            course['Duration']  # Виводимо Duration без ключа
        ])

    # Виводимо таблицю
    print(table)


def save_to_csv(courses_info, filename='courses_info.csv'):
    # Відкриваємо CSV файл для запису
    with open(filename, 'w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=["Course Name", "Course Description", "Study Options", "Modules", "Topics", "Duration"])
        writer.writeheader()

        for course in courses_info:
            writer.writerow(course)


# Викликаємо основну функцію
courses_info = get_course_info()
print_courses(courses_info)
# save_to_csv(courses_info)  # Якщо потрібно зберегти в CSV
