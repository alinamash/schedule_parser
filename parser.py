import requests
from bs4 import BeautifulSoup
import datetime

months = {
    'января': 1, 'февраля': 2, 'марта': 3, 'апреля': 4,
    'мая': 5, 'июня': 6, 'июля': 7, 'августа': 8,
    'сентября': 9, 'октября': 10, 'ноября': 11, 'декабря': 12
}
days_of_week = ['Понедельник', 'Вторник','Среда','Четверг','Пятница','Суббота']
group_id = "14717" 
dont_attend = ['История России', 'Основы российской государственности', 'Физическая культура и спорт']


def get_events_for_week(week_number):
    events = []
    url = f"https://dek2026.kspu.ru/table/group/14717/year/2026/week/{week_number}"
    
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'lxml')
    table = soup.find('table', class_='MsoTableGrid')
    
    if not table:
        print(f"Неделя {week_number}: таблица не найдена.")
        return []

    rows = table.find_all('tr')
    current_day = ""

    for row in rows:
        # ... (весь твой код парсинга строк, начиная с cells = row.find_all('td'))
        # ... (не забудь внутри этой функции добавлять события в локальный events)
        
        cells = row.find_all('td')
        if len(cells) == 2:
            time_text = cells[0].get_text(strip=True)
            lesson_text = cells[1].get_text(separator='\n', strip=True)

            parts = [p for p in lesson_text.split('\n') if p.strip()]
            if any(day in lesson_text for day in days_of_week):
                current_day = lesson_text
            elif time_text and lesson_text and parts:

                # дата
                date_str = current_day.split(', ')[1]
                day_str, month_name, year_str = date_str.split(' ')
                day = int(day_str)
                month = months[month_name.lower()]
                year = int(year_str)
                dt_date = datetime.date(year, month, day)

                # время
                time_str = time_text[1:]
                start_str, end_str = time_str.split('-')
                start_time = datetime.datetime.strptime(start_str, "%H:%M").time()
                end_time = datetime.datetime.strptime(end_str, "%H:%M").time()
                start_dt = datetime.datetime.combine(dt_date, start_time)
                end_dt = datetime.datetime.combine(dt_date, end_time)

                # данные пары
                lesson_name = parts[0] if len(parts) > 0 else "Без названия"

                if lesson_name.strip() in dont_attend:
                    continue
                
                lesson_type = parts[1] if len(parts) > 1 else ""
                lesson_type_only = lesson_type.split(',')[0]
                summary_text = f"{lesson_type_only}: {lesson_name}" if lesson_type else lesson_name
                room = parts[2] if len(parts) > 2 else ""
                teacher = parts[3] if len(parts) > 3 else ""
    
                # формирование события для ics
                dtstart_str = start_dt.strftime('%Y%m%dT%H%M%S')
                dtend_str = end_dt.strftime('%Y%m%dT%H%M%S')

                uid = f"{dtstart_str}-{group_id}@kspu.ru"
                description = f"Преподаватель: {teacher}"
                event = f"""BEGIN:VEVENT
UID:{uid}
DTSTAMP:{datetime.datetime.now().strftime('%Y%m%dT%H%M%SZ')}
DTSTART:{dtstart_str}
DTEND:{dtend_str}
SUMMARY:{summary_text}
LOCATION:{room}
DESCRIPTION:{description}
END:VEVENT"""

                events.append(event)

                # Для проверки в консоли
                print(f"[{current_day}] {time_text[1:]}")
                print(f"   Предмет: {lesson_name}")
                print(f"   Тип: {lesson_type} | Ауд: {room} | Препод: {teacher}")
                print("-" * 30)

    return events

today = datetime.date.today()
current_week = today.isocalendar()[1]

all_events = []
# Парсим текущую неделю
all_events.extend(get_events_for_week(current_week))
# Парсим следующую неделю
all_events.extend(get_events_for_week(current_week + 1))

calendar_header = """BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//KSPU Schedule//RU
CALSCALE:GREGORIAN
METHOD:PUBLISH
"""
calendar_footer = "END:VCALENDAR"

full_calendar = calendar_header + "\n".join(all_events) + "\n" + calendar_footer

with open('schedule.ics', 'w', encoding='utf-8') as f:
    f.write(full_calendar)

print(f"\nГотово! Создан файл schedule.ics с {len(all_events)} событиями.")