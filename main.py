import os
import time
import subprocess
import logging

from apscheduler.schedulers.blocking import BlockingScheduler
import yaml

logger = logging.getLogger()
logger.setLevel(logging.INFO)
formatter = logging.Formatter("[%(asctime)s] [%(levelname)s] - %(message)s")
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)

with open("/mongob/config.yml", encoding="utf-8") as f:
    config_data = yaml.safe_load(f)
logger.info("Loaded config file: /mongob/config.yml")

host_ip, host_port, db, username, password = config_data["target"].values()
hour, minute = config_data["scheduler"].values()

logger.info(f"Starting with config: host - {host_ip}:{host_port}, db - {db}")

if "TZ" in os.environ:
    tz = os.environ["TZ"]
else:
    tz = "Europe/London"

scheduler = BlockingScheduler(timezone=tz)


def backup():
    logger.info("Starting backup")
    fp = f"/backup/{time.time():.0f}.gz"
    cmd = f"/usr/bin/mongodump --db {db} --gzip --archive={fp} --host {host_ip}:{host_port}"
    if all([username, password]):
        logger.info("Using authentication. authSource=admin")
        cmd += f" --authenticationDatabase admin -u {username} -p {password}"
    subprocess.run(cmd, check=True, shell=True)
    logger.info(f"Backup completed. filename={fp}")


scheduler.add_job(backup, "cron", hour=hour, minute=minute)
scheduler.start()
