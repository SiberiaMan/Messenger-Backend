from collections import deque
from typing import Optional, Tuple
from pytz import timezone
from datetime import datetime


def find_user_config(user_id: str) -> Optional[Tuple[bool, str]]:
    if not user_id:
        return None
    with open('user_configs.txt', 'r') as fd:
        while True:
            s = fd.readline()
            if not s:
                break
            s = s.split()
            find_user = s[0]
            if find_user == user_id:
                return (True, s[1])
    return (False, '')


def personal_answer(config: str) -> str:
    user_timezone = timezone(config)
    local_timezone = timezone('Europe/Moscow')
    user_offset = user_timezone.utcoffset(datetime.now())
    user_seconds = user_offset.seconds
    if user_offset.days < 0:
        user_seconds = - 24 * 3600 + user_offset.seconds
    local_offset = local_timezone.utcoffset(datetime.now())
    diff = (user_seconds - local_offset.seconds) // 3600
    user_hour = (datetime.now().hour + diff) % 24
    if 0 <= user_hour < 4:
        return "Good night!"
    if 4 <= user_hour < 12:
        return "Good morning!"
    if 12 <= user_hour < 17:
        return "Good afternoon!"
    return "Good evening!"


class CacheMessage:
    def __init__(self, text, message_id):
        self.message_id = message_id
        self.text = text

    def get_id(self):
        return self.message_id

    def get_message(self):
        return self.text


class Chat:
    def __init__(self):
        self.size = 10
        self.messages = deque()

    def add_message(self, message: CacheMessage):
        if len(self.messages) < self.size:
            self.messages.append(message)
        else:
            self.messages.popleft()
            self.messages.append(message)

    def length_chat(self):
        return len(self.messages)

    def get_head(self):
        return self.messages[0].get_id()

    def get_tail(self):
        last_idx = self.length_chat() - 1
        return self.messages[last_idx].get_id()

    def get_distance(self, cursor):
        idx = 0
        for i in range(self.length_chat()):
            if self.messages[i].get_id() == cursor:
                idx = i
                break
        distance = self.length_chat() - idx
        return idx, distance

    def get_message(self, idx):
        return self.messages[idx].get_message()

    def get_id(self, idx):
        try:
            return self.messages[idx].get_id()
        except IndexError:
            return None


class ApiCache:
    def __init__(self):
        self._cache = {}

    def get_messages(self, chat_id: str,
                     limit: int,
                     cursor: int,
                     is_working_db: bool,
                     login: Optional[str] = None):
        s = "Sorry, we have technical works, but we will finish soon :)"
        messages = deque()
        if self.get_chat(chat_id):
            chat = self.get_chat(chat_id)
            head_chat = chat.get_head()
            tail_chat = chat.get_tail()
            idx, distance = chat.get_distance(cursor)
            if head_chat <= cursor <= tail_chat:
                prev_cursor = cursor
                for i in range(min(limit, distance)):
                    prev_cursor = chat.get_id(idx)
                    messages.appendleft(chat.get_message(idx))
                    idx += 1
                next_cursor = chat.get_id(idx)
                cursor = next_cursor if next_cursor else prev_cursor
        config_is_find = find_user_config(login) # TODO
        if config_is_find and config_is_find[0] and not is_working_db:
            user_answer = personal_answer(config_is_find[1])
            messages.appendleft(f'{user_answer} {s}')
        elif not is_working_db:
            messages.appendleft(s)
        return messages, cursor

    def get_chat(self, chat_id: str):
        return self._cache.get(chat_id)

    def update_cache(self, chat_id: str, message: str, message_id: int):
        if not self._cache.get(chat_id):
            self._cache[chat_id] = Chat()
        new_message = CacheMessage(message, message_id)
        self._cache[chat_id].add_message(new_message)

# if __name__ == '__main__':
#     my_cache = ApiCache()
#     msg = CacheMessage(23, 32)
#     my_cache.update_cache('5', 'hello', 23)
#     my_cache.update_cache('5', 'lol', 35)
#     my_cache.update_cache('5', 'heeeeeed', 54)
#     msgs, cursor = my_cache.get_messages('5', 10, , False, '4')
#     print(list(msgs), cursor)
