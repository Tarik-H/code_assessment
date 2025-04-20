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


if __name__ == "__main__":
    main()
