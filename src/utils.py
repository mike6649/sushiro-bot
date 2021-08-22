import re
import requests
import uuid
from cachetools import cached, TTLCache
from typing import Dict, List, Tuple, Union

import logging
# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

base_url = "https://sushipass.sushiro.com.hk/api/1.1"
group_info_url = "/remote/groupqueues?storeid={}"
queue_info_url = "/remote/storequeue?storeid={}"
all_stores_url = "/info/storelist?latitude={}&longitude={}&numresults=100&guid={}"


class SushiroUtils:
    @staticmethod
    def _get_response_json(url: str):
        return requests.get(f"{base_url}{url}").json()

    @staticmethod
    @cached(cache=TTLCache(ttl=60, maxsize=1000))
    def get_queue_info(store_id: Union[int, str]) -> List:
        response = SushiroUtils._get_response_json(queue_info_url.format(store_id))
        if not response:
            return []
        return [re.split('-', s)[0] for s in response]

    @staticmethod
    @cached(cache=TTLCache(ttl=600, maxsize=1000))
    def get_all_stores_info() -> Dict:
        lat = 22.307338
        long = 114.171603

        response = SushiroUtils._get_response_json(all_stores_url.format(lat, long, str(uuid.uuid4())))
        store_dict = {}
        for r in response:
            store_dict[str(r['id'])] = dict(
                name=r['name'],
                lat=r['latitude'],
                long=r['longitude']
            )
        return store_dict

