import logging

import pika
from zayats import RabbitPublisher, RabbitConsumer

import configs
from dispenser.dispenser import Dispenser, PlatformWorkerQueues, InvalidTask


logger = logging.getLogger('autoban')


class DispenserWorker:

    RABBIT_MAX_PRIORITY = 2

    def __init__(self, pika_params: pika.ConnectionParameters, input_queue: str):
        self.dispenser = Dispenser()
        self.consumer = RabbitConsumer(pika_params, queue=input_queue)
        self.transit_publisher = RabbitPublisher(pika_params)

        for name in PlatformWorkerQueues:
            worker_queue = name.value
            self.transit_publisher.pika_channel.queue_declare(queue=worker_queue,
                                                              durable=True,
                                                              arguments={'x-max-priority': self.RABBIT_MAX_PRIORITY})

    def process_queues(self):
        while True:
            task_message = self.consumer.send_ack_and_get_new_msg()
            try:
                output_platform_queue, data = self.dispenser.get_worker_info(task_message)
            except InvalidTask:
                continue  # handled in dispenser

            self.transit_publisher.publish(
                queue_name=output_platform_queue,
                data=data,
                declare_queue=False,
            )
            logger.info('Published to: "%s". Priority: %s. Task: %s.', output_platform_queue, task_message)


if __name__ == '__main__':
    dispenser_worker = DispenserWorker(input_queue=configs.INPUT_QUEUE, pika_params=configs.RABBIT_PIKA_PARAMS)
    dispenser_worker.process_queues()
