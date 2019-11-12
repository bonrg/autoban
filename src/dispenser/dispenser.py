from enum import Enum
from typing import Tuple, Optional
from urllib.parse import urlparse

from autoban_status import ComplaintStatus
from utils import domain_parser


class DispenserError(Exception):
    pass


class InvalidTask(DispenserError):
    pass


class InvalidUrl(DispenserError):
    pass


class InvalidPriority(InvalidTask):
    pass


class InavalidQuantity(DispenserError):
    pass


class PlatformWorkerQueues(Enum):
    VK = 'vk_autoban'
    INSTAGRAM = 'instagram_autoban'
    YOUTUBE = 'youtube_autoban'
    FACEBOOK = 'facebook_autoban'


class MsgPriorities:
    LOW = 1
    HIGH = 2


class Dispenser:

    STATUS_RESULT_FIELD = 'status'
    DEBUG_MSG_RESULT_FIELD = 'debug'

    queue_map = {
        'vk.com': PlatformWorkerQueues.VK.value,
        'm.vk.com': PlatformWorkerQueues.VK,
        'youtube.com': PlatformWorkerQueues.YOUTUBE.value,
        'youtu.be': PlatformWorkerQueues.YOUTUBE.value,
        'instagram.com': PlatformWorkerQueues.INSTAGRAM.value,
        'facebook.com': PlatformWorkerQueues.FACEBOOK.value,
        'web.facebook.com': PlatformWorkerQueues.FACEBOOK.value,
        'm.facebook.com': PlatformWorkerQueues.FACEBOOK.value,

    }

    web_protocols = (
        'http',
        'https',
        'ftp',
    )

    def get_worker_info(self, task: dict) -> Tuple[str, dict]:
        """
            {
                "task_id": int,
                "url": str,
                "priority": str,
                "output_queue": str,
                "quantity": int,
            }
        """
        try:
            return self._get_worker_info(task)
        except InvalidTask as e:
            raise e

        except InvalidUrl as e:
            error_status = ComplaintStatus.FAILURE
            debug_msg = 'Invalid URL (%s)' % e

        except Exception as e:
            error_status = ComplaintStatus.FAILURE
            debug_msg = 'Dispenser error: %s(%s)' % (type(e).__name__, e)

        if 'output_queue' not in task:
            raise InvalidTask

        task[self.STATUS_RESULT_FIELD] = error_status
        task[self.DEBUG_MSG_RESULT_FIELD] = debug_msg

        # в случае ошибки, или некорректной ссылки, отправляем результат проверки сразу
        msg_data = task
        worker_queue_name = task['output_queue']
        return worker_queue_name, msg_data

    def _get_worker_info(self, task: dict) -> Tuple[str, dict]:

        output_queue = task.get('output_queue')
        self._check_output_queue_is_valid(output_queue)

        url = task.get('url')
        self._check_url_is_valid(url)

        quantity = task.get('quantity')
        self.check_quantity_is_valid(quantity)

        try:
            hostname = domain_parser.parse_domain(url)
        except domain_parser.InvalidUrl:
            raise InvalidUrl('domain parsing error')
        worker_queue_name = self._get_platform_worker_name(hostname)

        return worker_queue_name, task

    def _check_url_is_valid(self, url: str) -> None:
        if not url or not isinstance(url, str):
            raise InvalidUrl('url is not string or empty')
        base_url = urlparse(url).scheme
        if base_url not in self.web_protocols:
            raise InvalidUrl('This is not valid url')

    @staticmethod
    def _check_output_queue_is_valid(output_queue: str) -> None:
        if not output_queue:
            raise InvalidTask('There is no output_queue provided')

    @classmethod
    def _get_platform_worker_name(cls, hostname: str):
        queue_name = cls.queue_map.get(hostname, None)
        return queue_name

    @staticmethod
    def check_quantity_is_valid(quantity: int) -> None:
        if quantity not in (5, 10, 20, 30, 40) and not isinstance(quantity, int):
            raise InavalidQuantity('The number of complaints is not available')
