import os

clear = lambda: os.system("cls")


def get_time(seconds):
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    return "{:.0f} h {:.0f} m {:.2f} s".format(hours, minutes, seconds) if hours > 0 else "{:.0f} m {:.2f} s".format(minutes, seconds) if minutes > 0 else "{:.2f} s".format(seconds)
