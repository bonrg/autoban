import logging

import pika
from zayats import RabbitConsumer, RabbitPublisher

from platforms.abstract_autoban import AbstractAutoban
from autoban_status import ComplaintStatus
# from supervisor.worker_supervisor import ReturnStatuses

logger = logging.getLogger('autoban')


class AutobanWorker:

    RABBIT_MAX_PRIORITY = 2

    def __init__(self, pika_params: pika.ConnectionParameters, input_queue: str,
                 platforms: AbstractAutoban):
        self.autoban = platforms
        self.consumer = RabbitConsumer(pika_params,
                                       queue=input_queue,
                                       queue_arguments={'x-max-priority': self.RABBIT_MAX_PRIORITY})
        self.publisher = RabbitPublisher(pika_params)


    def run(self):
        autoban_class = self.autoban.__class__.__name__
        while True:
            task_message = self.consumer.send_ack_and_get_new_msg()
            url = task_message.get('url')
            quantity = task_message.get('quantity')
            try:
                task_message['status'] = self.autoban.make_complaint(url, quantity)
            # except RequesterProxyError as e:
            #     logger.warning(e)
            #     quit(ReturnStatuses.PROXY_ERROR)
            except Exception as e:  # TODO: hotfix
                task_message['status'] = ComplaintStatus.FAILURE
                task_message['_debug'] = '{error_class}({text})'.format(error_class=type(e).__name__, text=str(e))

            self.publisher.publish(queue_name=task_message['output_queue'], data=task_message, declare_queue=True)
            # if self._bot_credentials:
            #     logger.info('Checker: "%s". Status: "%s". Url: "%s". Proxy: "%s". Bot: "%s"',
            #                 checker_class, task_message['status'], url, self._proxy_address, self._bot_credentials)
            # else:
            logger.info(f'Autoban: {autoban_class}. Status: {task_message["status"]}. Url: {url}. Quantity: {quantity}')

