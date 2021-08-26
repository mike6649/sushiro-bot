from dataclasses import dataclass


@dataclass
class Messages:
    language_text: str
    welcome: str
    goodbye: str
    choose_language: str
    choose_store: str
    store_chosen: str
    ask_queue_number: str
    current_queue_is: str
    store_closed: str
    this_store_closed_no_more_msgs: str
    entered_queue_pls_wait: str
    bad_queue_input: str
    almost_ready: str
    still_have_n_tables: str
    help_msg: str
    about: str = "Find my source code on [GitHub](https://github.com/mike6649/sushiro-bot)\\!\n" \
                 "sushiro\\_hk\\_bot is created by [banhooves](https://t.me/banhooves)\n" \
                 "I am not affiliated with Sushiro HK"

    def display_store_info(self, store_name: str, current_queue: str) -> str:
        return f"{self.store_chosen.format(store_name)}\n" \
                f"{self.current_queue_is.format(current_queue)}"

    def store_chosen_ask_queue_number(self, store_name, current_queue) -> str:
        return f"{self.display_store_info(store_name, current_queue)}\n{self.ask_queue_number}"

    def almost_ready_queue_now(self, current_queue, tables_left) -> str:
        return f"{self.still_have_n_tables.format(tables_left)}\n{self.current_queue_is.format(current_queue)}"

    def final_call_queue_now(self, current_queue) -> str:
        return f"{self.almost_ready}\n{self.current_queue_is.format(current_queue)}"


EnglishMessages = Messages(
    language_text='English',
    welcome='Hello! I am Sushiro Bot. Enter /cancel to stop talking to me.',
    goodbye='Until next time!',
    choose_language='Please choose a language',
    choose_store='Please choose a store',
    store_chosen='You have chosen *{}*\\.',
    ask_queue_number='What is your queue number?',
    current_queue_is='Currently on queue {}',
    store_closed="Sorry, *{}* is currently closed\\. Try again later",
    this_store_closed_no_more_msgs="Sorry, this store is currently closed. I will stop sending you notifications",
    entered_queue_pls_wait="We will let you know when table {} is almost ready!",
    bad_queue_input="Sorry, please enter a valid number",
    almost_ready="Your table is almost ready\\!",
    still_have_n_tables="Still *{}* tables to go\\!",
    help_msg="/start - Start talking to me\n"
             "/cancel - Stop talking to me\n"
             "/about - About me\n"
             "/help - Display this help message"

)

ChineseMessages = Messages(
    language_text='中文',
    welcome='你好！我是 Sushiro Bot. 你隨時可以輸入 /cancel 終止對話',
    goodbye='下次見！',
    choose_language='請選擇語言',
    choose_store='請選擇壽司郎店舖',
    store_chosen='你已選擇壽司郎 *{}*',
    ask_queue_number='請輸入你的籌號，我會幫你記下',
    current_queue_is='現在籌號為 *{}*',
    store_closed='唔好意思, 壽司郎 *{}* 現時暫停營業，請稍後再嘗試',
    this_store_closed_no_more_msgs="唔好意思， 這間壽司郎店舖已暫停營業，你不會再接收籌號通知",
    entered_queue_pls_wait="籌號即將到{}號時會通知你！",
    bad_queue_input="唔好意思，請輸入阿拉伯數字",
    almost_ready="就黎得喇！",
    still_have_n_tables='仲有 *{}*張籌！',
    help_msg="/start - 開始對話\n"
             "/cancel - 終止對話\n"
             "/about - 關於我\n"
             "/help - 顯示這訊息"
)

localization = {
    'en': EnglishMessages,
    'zh': ChineseMessages
}

