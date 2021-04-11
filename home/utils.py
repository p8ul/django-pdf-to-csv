from collections import defaultdict
import pdfplumber
import pprint


def search_line(data, search_text):
    for line in data.split('\n'):
        if not line:
            continue
        if search_text in line:
            return line


def is_header(text: str):
    return text.isupper()


def is_course(text: str):
    return '(' and ')' in text


def has_course(text: str):
    return '←' in text or '()' in text


def get_course(text: str):
    course = text.split("^(?=.*?\d)\d*[(]?\d*$", 1)[0]
    code, title = course.split('-', 1)

    title, hours = title.split('(')
    return {'title': title, 'code': code, 'hours': hours}


def get_courses(text: str):
    main_course, conditional_course = text.split(')', 1)
    return {'course': get_course(main_course), 'conditional': conditional_course}


def process_text(data_text):
    data = defaultdict(list)

    pp = pprint.PrettyPrinter()
    with pdfplumber.open("output.pdf") as pdf:
        pages = pdf.pages
        index = 0
        for page in pages:
            for item in page.dedupe_chars().extract_tables()[0]:
                if item[0]:
                    line = str(item[0]).encode("utf-8").decode()
                    if is_header(line.strip()):
                        index += 1
                    data[index].append(line)

        courses = []
        and_separator = '--- And ---'
        for i in range(2, len(data.keys()) - 1):
            for text in data[i]:
                if has_course(text):
                    if and_separator in text:
                        for text_sep in text.split(and_separator):
                            courses.append(get_courses(text_sep))
                    else:
                        courses.append(get_courses(text))

                    continue
    academic_year = search_line(data.get(0)[0], 'Academic Year').replace('Effective during the ', '').replace(
        'Academic Year', '')

    to_from = data.get(0)[1].split('From:')
    college_to = to_from[0].replace('To:', '')
    college_from = to_from[1]

    return {
        'academic_year': academic_year,
        'college_to': college_to,
        'college_from': college_from,
        'degree': data.get(0)[2],
        'courses': courses
    }


csv_headers = ['Academic year', 'Degree title', 'From college', 'To college', 'Course title', 'Course code',
               'Course hours',
               'Conditional courses title', 'required']
