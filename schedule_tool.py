import argparse
import time
import threading
from threading import Thread

def parse_file(filename):
    """Parse the tasks file and return a dict of tasks"""
    tasks = {}
    with open(filename, "r") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split(',')
            if len(parts) < 2:
                continue
            name = parts[0].strip()
            try:
                duration = float(parts[1].strip())
            except:
                continue
            deps = []
            if len(parts) >= 3:
                dep_str = parts[2].strip()
                if dep_str:
                    deps = [d.strip() for d in dep_str.split(';') if d.strip() != ""]
            tasks[name] = {"duration": duration, "deps": deps}
    return tasks

def validate_tasks(tasks):
    """Check that each dependency in a task exists in the tasks list"""
    valid = True
    names = set(tasks.keys())
    for name, task in tasks.items():
        for dep in task["deps"]:
            if dep not in names:
                print("Error: Task", name, "has undefined dependency", dep)
                valid = False
    return valid

# calculate the total time
def calc_run_time(task, tasks, memo):
    if task in memo:
        return memo[task]
    t_duration = tasks[task]["duration"]
    if not tasks[task]["deps"]:
        memo[task] = t_duration
    else:
        max_dep = 0
        for dep in tasks[task]["deps"]:
            dep_time = calc_run_time(dep, tasks, memo)
            if dep_time > max_dep:
                max_dep = dep_time
        memo[task] = t_duration + max_dep
    return memo[task]

def expected_runtime(tasks):
    """Compute the expected (critical path) runtime."""
    memo = {}
    max_time = 0
    for task in tasks:
        t_time = calc_run_time(task, tasks, memo)
        if t_time > max_time:
            max_time = t_time
    return max_time

#
############## Running tasks
#

def run_tasks(tasks):
    completed = set()
    lock = threading.Lock()
    def run_task(name):
        while True:
            with lock:
                ready = all(dep in completed for dep in tasks[name]["deps"])
            if ready:
                break
            time.sleep(0.1)
        print("Starting", name, "(", tasks[name]["duration"], "sec)")
        time.sleep(tasks[name]["duration"])
        print("Finished", name)
        with lock:
            completed.add(name)

    threads = []
    for task in tasks:
        t = Thread(target=run_task, args=(task,))
        threads.append(t)
        t.start()
    for t in threads:
        t.join()

def main():
    parser = argparse.ArgumentParser(description="Task Scheduler tool")
    parser.add_argument("file", help="task list file path")
    parser.add_argument("--validate", action="store_true", help="Only validate the tasks and show expected runtime")
    parser.add_argument("--run", action="store_true", help="Run the tasks in parallel")
    args = parser.parse_args()

    tasks = parse_file(args.file)
    if not tasks:
        print("No valid tasks found.")
        return

    if not validate_tasks(tasks):
        print("Validation failed. Please fix errors in the task file.")
        return

    exp_time = expected_runtime(tasks)
    print("Expected Total Runtime:", exp_time, "seconds")

    if args.validate and not args.run:
        return

    if args.run:
        start = time.time()
        run_tasks(tasks)
        actual = time.time() - start
        print("Actual Runtime: {:.2f} seconds (Diff: {:.2f} seconds)".format(actual, actual - exp_time))

if __name__ == "__main__":
    main()        