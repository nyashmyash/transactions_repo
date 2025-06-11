import datetime
def get_week_start_end_date(date):
    weekday = date.weekday()

    # Calculate the start date (Monday)
    start_date = date - datetime.timedelta(days=weekday)

    # Calculate the end date (Sunday)
    end_date = start_date + datetime.timedelta(days=6)

    return start_date, end_date