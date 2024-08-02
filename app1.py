import time
def background_task(n):
    """ Function that returns len(n) and simulates a delay """
    delay = 2
    print(f"Task running with argument {n}")
    time.sleep(delay)
    print(f"Task completed with argument {n}")
    return len(n)
