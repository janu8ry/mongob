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

test = config_data["testmode"]
dbdata = config_data["mongo"]["test" if test else "main"]
username = None
if "username_file" in dbdata:
    with open(dbdata["username_file"]) as f:
        username = f.read()
password = None
if "password_file" in dbdata:
    with open(dbdata["password_file"]) as f:
        password = f.read()

try:
    host_ip = dbdata["host"]
    host_port = dbdata["port"]
    db = dbdata["db"]
    hour = config_data["mongo"]["scheduler"]["hour"]
    minute = config_data["mongo"]["scheduler"]["minute"]
except KeyError as e:
    logger.error(f"Missing parameter in config file: {e}")
    logger.info("Shutting down...")
    sys.exit(1)

try:
    if not username:
        username = dbdata["username"]
    if not password:
        password = dbdata["password"]
except KeyError:
    try:
        username = os.environ["MONGOB_USERNAME"]
        password = os.environ["MONGOB_PASSWORD"]
    except KeyError:
        username = None
        password = None

logger.info(f"Starting with config: host - {host_ip}:{host_port}, db - {db}")

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
