from datetime import datetime
import time

# Define holidays and non-working days
holidays = [
    (1, 1),  # January 1
    (1, 15), # January 15 (example, typically MLK Day varies)
    (2, 19), # February 19 (example, typically Washington Birthday varies)
    (3, 29), # March 29 (example, Good Friday varies)
    (5, 27), # May 27 (example, Memorial Day varies)
    (6, 19), # June 19 (Juneteenth)
    (9, 2),  # September 2 (example, Labor Day varies)
    (7, 4),  # July 4
    (11, 28),# November 28 (example, Thanksgiving varies)
    (12, 25) # December 25
    ######Weekends######
]

def is_holiday(date):
    return (date.month, date.day) in holidays

def time_range(current_time):
    return current_time < 900 or current_time > 1600

def next_minute():
    now = datetime.now()
    current = now.strftime("%S")
    return 60 - int(current)

def main():
    while True:
        now = datetime.now()
        current_time = int(now.strftime("%H%M"))
        current_date = now.date()

        if is_holiday(now):
            print("Holiday")
        elif time_range(current_time):
            print('Not in time')
        else:
            print("Start")

        # Sleep to prevent excessive CPU usage
        time.sleep(next_minute())  # Check every minute

if __name__ == "__main__":
    main()

