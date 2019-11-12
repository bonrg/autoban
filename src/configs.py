from collections import namedtuple
import logging.config
import os
from pathlib import Path
from selenium.webdriver.chrome.options import Options
import pika

DEBUG = True if os.environ.setdefault('DEBUG', '').lower() == 'true' else False
BASE_DIR = 'src'
ABS_BASE_DIR = str([p for p in Path(__file__).absolute().parents if p.name == BASE_DIR][0])

INPUT_QUEUE = 'input_autoban'
# RabbitMQ
# ----------------------------------------------------------------------------------------------------------------------
RABBITMQ_HOST = os.environ.setdefault('RABBITMQ_HOST', '0.0.0.0')
RABBITMQ_PORT = os.environ.setdefault('RABBITMQ_PORT', '2055')
RABBITMQ_USER = os.environ.setdefault('RABBITMQ_DEFAULT_USER', 'rabbit')
RABBITMQ_PASS = os.environ.setdefault('RABBITMQ_DEFAULT_PASS', '123')

RABBIT_PIKA_PARAMS = pika.ConnectionParameters(
    host=RABBITMQ_HOST, port=RABBITMQ_PORT, heartbeat=0,
    credentials=pika.credentials.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS)
)


WEBDRIVER_PATH = ABS_BASE_DIR + '/platforms/utils/chromedriver/chromedriver_74'
# YOUTUBE_AUTH_URL = 'https://www.youtube.com/'
# YOUTUBE_REPORT_ABUSE_URL = 'https://www.youtube.com/reportabuse'
# INSTAGRAM_AUTH_URL = 'https://www.instagram.com/accounts/login/?source=auth_switcher'
# FACEBOOK_AUTH_URL = 'https://www.facebook.com/'

chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument("--disable-notifications")
chrome_options.add_argument('--window-size=1920,1080')
chrome_options.add_argument('--lang=ru')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--test-type')
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument('--no-first-run')
chrome_options.add_argument('--no-default-browser-check')
chrome_options.add_argument('--ignore-certificate-errors')
chrome_options.add_argument('--start-maximized')
chrome_options.add_argument('--disable-dev-shm-usage')  # essential options for use in docker containers
prefs = {"profile.managed_default_content_settings.images": 2}
chrome_options.add_experimental_option("prefs", prefs)

# Logging
# ----------------------------------------------------------------------------------------------------------------------
LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {'autoban': {'format': '[%(levelname)s] [%(asctime)s] [%(module)s:%(lineno)d] [V2.0] %(message)s',
                            'datefmt': '%d/%m/%Y %H:%M:%S'}},
    'handlers': {
        'console': {'level': 'DEBUG', 'class': 'logging.StreamHandler', 'formatter': 'autoban'},
    },
    'loggers': {
        'RabbitConsumer': {'handlers': ['console'], 'propagate': False, 'level': 'INFO'},
        'RabbitPublisher': {'handlers': ['console'], 'propagate': False, 'level': 'INFO'},
        'autoban': {'handlers': ['console'], 'propagate': False, 'level': 'INFO'},
    }
}
logging.config.dictConfig(LOGGING)

# Platform selector elements
# ----------------------------------------------------------------------------------------------------------------------

# Vk Complaint reasons
# ----------------------------------------------------------------------------------------------------------------------

VkComplaint = namedtuple('Vk',
                         'post_reason_id user_reason_type video_reason_id photo_reason_id comment')

vk_reason = VkComplaint(
    post_reason_id=2,  # экстремизм
    user_reason_type='insult',  # оскорбительное поведение
    video_reason_id=2,  # экстремизм
    photo_reason_id=2,  # экстремизм
    comment='Материалы радикального характера'
)

# Platform bots = 40 bots in every platforms
# ----------------------------------------------------------------------------------------------------------------------

vk_bots = (
    ('your_login', 'your_password'),

)

#  Proxies list
# ----------------------------------------------------------------------------------------------------------------------
proxies = (
    'http://95.95.95.95:10000',
    'your_proxy_list'
)
