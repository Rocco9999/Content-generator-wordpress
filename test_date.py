from datetime import date, timedelta, datetime
from random import choices, randint
import random

# Ottenere la data e ora attuale
current_datetime = datetime.now()

K = 14
# Primo range: dal momento attuale alle 20:00 dello stesso giorno
end_time_first_range = datetime(current_datetime.year, current_datetime.month, current_datetime.day, 20, 0)
first_range = [current_datetime + timedelta(minutes=randint(0, int((end_time_first_range - current_datetime).total_seconds() / 60))) for _ in range(K)]

# Secondo range: dal giorno successivo alle 06:00 alle 20:00 dello stesso giorno
next_day = current_datetime + timedelta(days=1)
start_time_second_range = datetime(next_day.year, next_day.month, next_day.day, 6, 0)
end_time_second_range = datetime(next_day.year, next_day.month, next_day.day, 20, 0)
second_range = [start_time_second_range + timedelta(minutes=randint(0, int((end_time_second_range - start_time_second_range).total_seconds() / 60))) for _ in range(K)]


combined_range = first_range + second_range
selected_dates = random.sample(combined_range, K)

# Formattazione nel formato desiderato
selected_dates_formatted = [date.strftime('%Y-%m-%dT%H:%M:%S') for date in selected_dates]


# Stampa
print("Primo range:", selected_dates_formatted[12])