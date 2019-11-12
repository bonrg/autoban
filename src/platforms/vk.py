import vk_api
import configs
from logging import getLogger
from urllib.parse import urlparse
from multiprocessing import Pool
from vk_api.vk_api import VkApiMethod
from typing import Tuple
from autoban_status import ComplaintStatus
from platforms.abstract_autoban import AbstractAutoban
import re

logger = getLogger('autoban')


class VkAutobanError(Exception):
    pass


class VkBot:

    __slots__ = ['login', 'password', 'cookie_file', 'proxy', 'api']

    def __init__(self, login: str, password: str, proxy: str = None):
        self.login = login
        self.password = password
        self.cookie_file = configs.ABS_BASE_DIR + '/platforms/cookies/vk_' + self.login + '.json'
        if proxy is not None:
            self.proxy = proxy
        self.api = self.get_api_for_methods()

    def get_api_for_methods(self) -> VkApiMethod:
        try:
            vk_session = vk_api.VkApi(self.login, self.password, config_filename=self.cookie_file)
            if hasattr(self, 'proxy'):
                proxies = {
                    'http': self.proxy,
                    'https': self.proxy,
                }
                vk_session.http.proxies = proxies
                vk_session.auth()
                api = vk_session.get_api()
                return api
            else:
                vk_session.auth()
                api = vk_session.get_api()
                return api
        except Exception as e:
            logger.warning(f'Error in: [{self.get_api_for_methods.__name__}] method, Message: {e}')
            raise VkAutobanError('Can not get api methods')


class VkAutoban(AbstractAutoban):

    __slots__ = ['bot', 'api']

    def __init__(self, bot: VkBot):
        self.bot = bot
        self.api = self.bot.api

    def post_complaint(self, owner_id: int, post_id: int) -> ComplaintStatus:
        try:
            result = self.api.wall.reportPost(owner_id=owner_id, post_id=post_id, reason=configs.vk_reason.post_reason_id, comment=configs.vk_reason.comment)
            if result == 1:
                return ComplaintStatus.SUCCESS
        except Exception as e:
            logger.warning(f'Error in: {self.post_complaint.__name__} method, Message: {e}')
            return ComplaintStatus.FAILURE

    def user_complaint(self, user_id: int) -> ComplaintStatus:
        try:
            result = self.api.users.report(user_id=user_id, type=configs.vk_reason.user_reason_type, comment=configs.vk_reason.comment)
            if result == 1:
                return ComplaintStatus.SUCCESS
        except Exception as e:
            logger.warning(f'Error in: {self.user_complaint.__name__} method, Message: {e}')
            return ComplaintStatus.FAILURE

    def video_complaint(self, owner_id: int, video_id: int) -> ComplaintStatus:
        try:
            result = self.api.video.report(owner_id=owner_id, video_id=video_id, reason=configs.vk_reason.video_reason_id, comment=configs.vk_reason.comment)
            if result == 1:
                return ComplaintStatus.SUCCESS
        except Exception as e:
            logger.warning(f'Error in: {self.video_complaint.__name__} method, Message: {e}')
            return ComplaintStatus.FAILURE

    def photo_complaint(self, owner_id: int, photo_id: int) -> ComplaintStatus:
        try:
            result = self.api.photos.report(owner_id=owner_id, photo_id=photo_id, reason=configs.vk_reason.photo_reason_id, comment=configs.vk_reason.comment)
            if result == 1:
                return ComplaintStatus.SUCCESS
        except Exception as e:
            logger.warning(f'Error in: {self.photo_complaint.__name__} method, Message: {e}')
            return ComplaintStatus.FAILURE

    @staticmethod
    def get_vk_objects(url: str) -> str:
        regex_pattern = re.compile(
            r'^public\d+|'
            r'^photo\d+_\d+|^photo-\d+_\d+|^photos\d+|^photos-\d+|'
            r'^video\d+_\d+|^video-\d+_\d+|^videos\d+|^videos-\d+|'
            r'^wall\d+_\d+|^wall-\d+_\d+|'
            r'^search.+|'
            r'^album\d+|^album-\d+|^albums\d+|^albums-\d+|'
            r'^club\d+|'
            r'^audio\d+|^audios\d+|'
            r'\S+z=.+|'
            r'\S+q=.+|'
            r'^doc\d+_\d+|'
            r'^artist',
            re.IGNORECASE
        )
        path = urlparse(url).path.split('/')[1] + urlparse(url).query
        regex = regex_pattern.fullmatch(path)
        if re.match(r'^id\d+', path) or regex is None:
            return 'User'
        elif re.match(r'^wall\d+_\d+|^wall-\d+_\d+|\S+wall\d+_\d+|\S+wall-\d+_\d+|\S+post=\d+_\d+|\S+post=-\d+_\d+', path):
            return 'Post'
        elif re.match(r'^video\d+_\d+|^video-\d+_\d+|\S+video\d+_\d+|\S+video-\d+_\d+', path):
            return 'Video'
        elif re.match(r'^photo\d+_\d+|^photo-\d+_\d+|\S+photo\d+_\d+|\S+photo-\d+_\d+', path):
            return 'Photo'
        else:
            logger.info('No implementation to this object')
            raise VkAutobanError('No implementation to this object')

    def get_user_id(self, url: str) -> int:
        try:
            path = urlparse(url).path.split('/')[1] + urlparse(url).query
            if re.match(r'^id\d+', path):
                user_id = path.split('id')[1]
                return int(user_id)
            else:
                user_id = self.api.users.get(user_ids=path)[0].get('id')
                return int(user_id)
        except Exception as e:
            logger.warning(f'Error in: {self.get_user_id.__name__} method, Message: {e}')

    def get_owner_post_video_photo_ids(self, url: str) -> Tuple[int, int]:
        try:
            path = urlparse(url).path.split('/')[1] + urlparse(url).query
            if re.search(r'wall-\d+_\d+', path):
                owner_id, post_id = re.search(r'wall-\d+_\d+', path).group(0).split(r'wall')[1].split(r'_')
                return int(owner_id), int(post_id)
            elif re.search(r'wall\d+_\d+', path):
                owner_id, post_id = re.search(r'wall\d+_\d+', path).group(0).split(r'wall')[1].split(r'_')
                return int(owner_id), int(post_id)
            elif re.search(r'post=-\d+_\d+', path):
                owner_id, post_id = re.search(r'post=-\d+_\d+', path).group(0).split(r'post=')[1].split(r'_')
                return int(owner_id), int(post_id)
            elif re.search(r'post=\d+_\d+', path):
                owner_id, post_id = re.search(r'post=\d+_\d+', path).group(0).split(r'post=')[1].split(r'_')
                return int(owner_id), int(post_id)
            elif re.search(r'video-\d+_\d+', path):
                owner_id, video_id = re.search(r'video-\d+_\d+', path).group(0).split(r'video')[1].split(r'_')
                return int(owner_id), int(video_id)
            elif re.search(r'video\d+_\d+', path):
                owner_id, video_id = re.search(r'video\d+_\d+', path).group(0).split(r'video')[1].split(r'_')
                return int(owner_id), int(video_id)
            elif re.search(r'photo-\d+_\d+', path):
                owner_id, photo_id = re.search(r'photo-\d+_\d+', path).group(0).split(r'photo')[1].split(r'_')
                return int(owner_id), int(photo_id)
            elif re.search(r'photo\d+_\d+', path):
                owner_id, photo_id = re.search(r'photo\d+_\d+', path).group(0).split(r'photo')[1].split(r'_')
                return int(owner_id), int(photo_id)
        except Exception as e:
            logger.warning(f'Error in: {self.get_owner_post_video_photo_ids.__name__} method, Message: {e}')

    @staticmethod
    def process_complaint(data: tuple) -> ComplaintStatus:
        try:
            url, login, password, vk_object, proxy = data
            bot = VkBot(login, password, proxy)
            autoban = VkAutoban(bot)
            if vk_object == 'Post':
                owner_id, post_id = autoban.get_owner_post_video_photo_ids(url)
                autoban_status = autoban.post_complaint(owner_id, post_id)
                logger.info(f'Platform: VKONTAKTE, Bot: {login}, Complaint Status: {autoban_status}, '
                            f'Object: {vk_object}, Proxy: {proxy}')
            elif vk_object == 'User':
                user_id = autoban.get_user_id(url)
                autoban_status = autoban.user_complaint(user_id)
                logger.info(f'Platform: VKONTAKTE, Bot: {login}, Complaint Status: {autoban_status}, '
                            f'Object: {vk_object}, Proxy: {proxy}')
            elif vk_object == 'Video':
                owner_id, video_id = autoban.get_owner_post_video_photo_ids(url)
                autoban_status = autoban.video_complaint(owner_id, video_id)
                logger.info(f'Platform: VKONTAKTE, Bot: {login}, Complaint Status: {autoban_status}, '
                            f'Object: {vk_object}, Proxy: {proxy}')
            elif vk_object == 'Photo':
                owner_id, photo_id = autoban.get_owner_post_video_photo_ids(url)
                autoban_status = autoban.photo_complaint(owner_id, photo_id)
                logger.info(f'Platform: VKONTAKTE, Bot: {login}, Complaint Status: {autoban_status}, '
                            f'Object: {vk_object}, Proxy: {proxy}')
            else:
                autoban_status = ComplaintStatus.FAILURE
            return autoban_status
        except VkAutobanError as e:
            logger.info(f'Platform: VKONTAKTE, Bot: {data[1]}, Complaint Status: {ComplaintStatus.FAILURE}, '
                        f'Object: {data[3]}, Proxy: {data[4]}')
            logger.warning(e)
            return ComplaintStatus.FAILURE

    @staticmethod
    def make_complaint(url: str, quantity: int) -> tuple:
        if quantity <= len(configs.vk_bots):
            jobs = list()
            vk_object = VkAutoban.get_vk_objects(url)
            _ = list()
            for i in range(quantity):
                items = (url, configs.vk_bots[i][0], configs.vk_bots[i][1], vk_object, configs.proxies[i])
                _.append(items)
            data = tuple(_)
            with Pool(processes=quantity) as pool:
                result = pool.map(VkAutoban.process_complaint, data)
                jobs.append(result)
            return tuple(jobs[0])
        else:
            logger.warning('Not enough Vk bots for complaints')


if __name__ == '__main__':
    quantity = 1
    login = 'login'
    password = 'pass'
    bot = VkBot(login, password)
    autoban = VkAutoban(bot)
    res = autoban.make_complaint('https://vk.com/video-153587180_456240368', quantity)

    print(res)
