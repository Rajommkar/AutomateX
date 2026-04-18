from __future__ import annotations

import time
from datetime import datetime


class NativeScheduler:
    """
    A robust, zero-dependency background task scheduler utilizing native Python libraries
    to completely mitigate third-party supply-chain vulnerabilities.
    """

    def __init__(self, logger=None):
        self.jobs = []
        self.logger = logger
        if self.logger:
            self.logger.info("Native Scheduler initialized securely.")

    def every_hour(self, task_func):
        """Schedules a task to run strictly every 3600 seconds."""
        self.jobs.append(
            {
                "task": task_func,
                "interval_seconds": 3600,
                "last_run": datetime.now(),
            }
        )
        if self.logger:
            self.logger.info(f"Registered hourly recurring task: {task_func.__name__}")

    def every_day_at(self, hour: int, minute: int, task_func):
        """Schedules a task to run daily at a specific 24h clock time."""
        self.jobs.append(
            {
                "task": task_func,
                "daily_time": (hour, minute),
                "last_run": None,
            }
        )
        time_str = f"{hour:02d}:{minute:02d}"
        if self.logger:
            self.logger.info(f"Registered daily recurring task: {task_func.__name__} at {time_str}")

    def run_pending(self):
        """Executes any tasks that are chronologically due."""
        now = datetime.now()
        for job in self.jobs:
            if "interval_seconds" in job:
                if (now - job["last_run"]).total_seconds() >= job["interval_seconds"]:
                    self._execute_safe(job["task"])
                    job["last_run"] = now

            elif "daily_time" in job:
                target_hour, target_minute = job["daily_time"]
                
                # Check if it's the right minute
                if now.hour == target_hour and now.minute == target_minute:
                    # Check if it was already run today
                    if not job["last_run"] or job["last_run"].date() < now.date():
                        self._execute_safe(job["task"])
                        job["last_run"] = now

    def _execute_safe(self, task_func):
        """Safely executes the task without crashing the infinite loop."""
        try:
            if self.logger:
                self.logger.info(f"Executing scheduled task: {task_func.__name__}")
            task_func()
        except Exception as error:
            if self.logger:
                self.logger.error(f"Scheduled task {task_func.__name__} failed: {error}")

    def start_blocking_loop(self):
        """Locks the main thread and polls for executions every 1 second."""
        if self.logger:
            self.logger.info("Scheduler blocking loop started. Press Ctrl+C to terminate.")
        try:
            while True:
                self.run_pending()
                time.sleep(1)
        except KeyboardInterrupt:
            if self.logger:
                self.logger.info("Scheduler shutting down gracefully by user interrupt.")
