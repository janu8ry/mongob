import os
import sys
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

try:
    host_ip = config_data["target"]["host"]
    host_port = config_data["target"]["port"]
    db = config_data["target"]["database"]
    username = config_data["target"]["username"]
    password = config_data["target"]["password"]
    hour = config_data["scheduler"]["hour"]
    minute = config_data["scheduler"]["minute"]
except KeyError as e:
    logger.error(f"Missing parameter in config file: {e}")
    logger.info("Shutting down...")
    sys.exit(1)

do_test = True
if "test" in config_data["scheduler"]:
    do_test = config_data["scheduler"]["test"]
    if not isinstance(do_test, bool):
        logger.error(f"Incorrect value at scheduler.test: {do_test}")
        logger.info("Shutting down...")
        sys.exit(1)

logger.info(f"Starting with config: host - {host_ip}:{host_port}, db - {db}, testrun = {do_test}")

if "TZ" in os.environ:
    tz = os.environ["TZ"]
else:
    tz = "Europe/London"


def run_command(fp):
    cmd = f"/usr/bin/mongodump --db {db} --gzip --archive={fp} --host {host_ip}:{host_port}"
    if all([username, password]):
        logger.info("Using authentication. authSource=admin")
        cmd += f" --authenticationDatabase admin -u {username} -p {password}"
    try:
        subprocess.run(cmd, check=True, shell=True)
    except subprocess.CalledProcessError:
        logger.error(f"Cannot connect to db {host_ip}:{host_port}")
        logger.info("Shutting down...")
        sys.exit(1)


if do_test:
    logger.info("Trying test run.")
    test_fp = "test.gz"
    run_command(test_fp)
    if os.path.isfile(test_fp):
        os.remove(test_fp)
    logger.info("Test run finished successfully.")

scheduler = BlockingScheduler(timezone=tz)


def backup():
    logger.info("Starting backup")
    fp = f"/backup/{time.time():.0f}.gz"
    run_command(fp)
    logger.info(f"Backup completed. filename={fp}")


try:
    scheduler.add_job(backup, "cron", hour=hour, minute=minute)
except ValueError as e:
    logger.error(e)
    logger.info("Shutting down...")
    sys.exit(1)

scheduler.start()
