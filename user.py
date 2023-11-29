class User:
    user_id: int
    name: str
    total_hours: int
    date_of_finish: str
    hours_remaining: int
    hours_per_day: int
    corrected_date: str
    registration_date: str

    def set_all_fields(self, user_id: int, name: str, total_hours: int, date_of_finish: str,
                       hours_remaining: int, hours_per_day: int, corrected_date: str, registration_date: str):
        self.user_id = user_id
        self.name = name
        self.total_hours = total_hours
        self.date_of_finish = date_of_finish
        self.hours_remaining = hours_remaining
        self.hours_per_day = hours_per_day
        self.corrected_date = corrected_date
        self.registration_date = registration_date


    def __str__(self):
        return (
            f"User ID: {self.user_id}\n"
            f"Name: {self.name}\n"
            f"Total Hours: {self.total_hours}\n"
            f"Date of Finish: {self.date_of_finish}\n"
            f"Hours Remaining: {self.hours_remaining}\n"
            f"Hours Per Day: {self.hours_per_day}\n"
            f"Corrected Date: {self.corrected_date}"
        )
