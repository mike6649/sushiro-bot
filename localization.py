from dataclasses import dataclass


@dataclass
class Messages:
    language_text: str
    welcome: str
    choose_store: str
    store_chosen: str
    ask_queue_number: str
    current_queue_is: str
    store_closed: str
    entered_queue_pls_wait: str
    almost_ready: str

    def display_store_info(self, store_name: str, current_queue: int) -> str:
        return f"{self.store_chosen.format(store_name)}\n" \
                f"{self.current_queue_is.format(current_queue)}"

    def store_chosen_ask_queue_number(self, store_name, current_queue) -> str:
        return f"{self.display_store_info(store_name, current_queue)}\n{self.ask_queue_number}"


EnglishMessages = Messages(
    language_text='English',
    welcome='Welcome',
    choose_store='Please choose a store',
    store_chosen='You have chosen {}.',
    ask_queue_number='What is your queue number?',
    current_queue_is='Currently on queue #{}.',
    store_closed="{} is currently closed.",
    entered_queue_pls_wait="We will let you know when your table #{} is ready!",
    almost_ready="You are almost ready!"
)

ChineseMessages = Messages(
    language_text='中文',
    welcome='你好',
    choose_store='請選擇壽司郎店舖',
    store_chosen='你已選擇壽司郎 {}',
    ask_queue_number='請輸入籌號',
    current_queue_is='現在籌號為 #{}.',
    store_closed='壽司郎 {} 現時暫停營業',
    entered_queue_pls_wait="籌號即將到{}號時會通知你!",
    almost_ready="就黎得喇!"
)

localization = {
    'en': EnglishMessages,
    'zh': ChineseMessages
}

