import os

import configs
from platforms.vk import VkAutoban, VkBot
from dispenser.dispenser import PlatformWorkerQueues
from workers.autoban_worker import AutobanWorker


if __name__ == '__main__':
    # WORKER_PROXY = os.environ.setdefault('WORKER_PROXY', None) or None
    WORKER_BOT_LOGIN = ''
    WORKER_BOT_PASSWORD = ''
    if not WORKER_BOT_LOGIN and WORKER_BOT_PASSWORD:
        raise Exception('No bot arguments are passed')
    bot = VkBot(login=WORKER_BOT_LOGIN, password=WORKER_BOT_PASSWORD)
    vk = VkAutoban(bot)
    autoban_worker = AutobanWorker(
        input_queue=PlatformWorkerQueues.VK.value,
        pika_params=configs.RABBIT_PIKA_PARAMS,
        platforms=vk
                                   )
    autoban_worker.run()
