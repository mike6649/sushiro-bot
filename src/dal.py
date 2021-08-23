from abc import ABC, abstractmethod
from telegram.ext import CallbackContext


class SushiroDalInterface(ABC):

    @staticmethod
    @abstractmethod
    def save_language(username: str, language: str, obj): pass

    @staticmethod
    @abstractmethod
    def get_language(username: str, obj): pass

    @staticmethod
    @abstractmethod
    def save_queue_number(username: str, queue_number: int, obj): pass

    @staticmethod
    @abstractmethod
    def get_queue_number(username: str, obj): pass

    @staticmethod
    @abstractmethod
    def save_store_id(username: str, store_id: str, obj): pass

    @staticmethod
    @abstractmethod
    def get_store_id(username: str, obj): pass

    @staticmethod
    @abstractmethod
    def save_chat_id(username: str, chat_id: int, obj): pass

    @staticmethod
    @abstractmethod
    def get_chat_id(username: str, obj): pass


class ContextDal(SushiroDalInterface):

    @staticmethod
    def save_language(username: str, language: str, context: CallbackContext):
        context.user_data['language'] = language

    @staticmethod
    def get_language(username: str, context: CallbackContext):
        return context.user_data.get('language', 'zh')

    @staticmethod
    def save_queue_number(username: str, queue_number: int, context: CallbackContext):
        context.user_data['queue_number'] = queue_number

    @staticmethod
    def get_queue_number(username: str, context: CallbackContext):
        return context.user_data.get('queue_number')

    @staticmethod
    def save_store_id(username: str, store_id: str, context: CallbackContext):
        context.user_data['store_id'] = store_id

    @staticmethod
    def get_store_id(username: str, context: CallbackContext):
        return context.user_data.get('store_id')

    @staticmethod
    def save_chat_id(username: str, chat_id: int, context: CallbackContext):
        context.user_data['chat_id'] = chat_id

    @staticmethod
    def get_chat_id(username: str, context: CallbackContext):
        return context.user_data.get('chat_id')
