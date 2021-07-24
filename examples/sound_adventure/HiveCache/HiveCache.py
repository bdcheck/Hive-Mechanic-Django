from collections import defaultdict
from typing import ClassVar
import os.path
import requests
import tempfile
import mimetypes
import shutil
import os
import pygame


class HiveCache(object):
    __main_cache__:ClassVar = None

    @staticmethod
    def get_main_cache():
        if not HiveCache.__main_cache__:
            HiveCache.__main_cache__ = HiveCache()
        return HiveCache.__main_cache__

    def __init__(self):
        self.__cache = {}

    def check_if_exists(self, key):
        if key in self.__cache:
            return True
        return False

    def get_value(self, key) -> (str, None):
        if not self.check_if_exists(key) or self.__cache[key] is None:
            c_type = mimetypes.guess_type(key)
            ext = mimetypes.guess_extension(c_type[0])
            file = tempfile.NamedTemporaryFile(suffix=ext,delete=False)
            cat_type = str(c_type[0]).split("/")[0]
            data = {"filename": file.name, "type": cat_type, "optional": None}
            r = requests.get(key,stream=True)
            if r.status_code == 200:
                r.raw.decode_content = True
                shutil.copyfileobj(r.raw, file)
                self.__cache[key] = data
            else:
                self.__cache[key] = data
                self.__remove_file(key)
                self.__cache[key] = None

        return self.__cache[key]

    def get_file_name(self, key):
        item = self.get_value(key)
        return item.name

    def get_type_for_key(self, key)->str:
        data = self.__cache[key]
        return data["type"]

    def remove_from_cache(self, key):
        self.__remove_file(key)
        del(self.__cache[key])

    def add_option_value_to_key(self, key, optional_data):
        if self.check_if_exists(key):
            data = self.__cache[key]
            data["optional"]= optional_data
            self.__cache[key] = data

    def get_optional_value(self, key)->any:
        data = self.get_value(key)
        if data and data["optional"]:
            return data["optional"]
        return None

    def clear(self):
        for key in self.__cache.keys():
            self.__remove_file(key)
        self.__cache.clear()

    def __remove_file(self,key):
        data = self.__cache[key]
        file = data["filename"]
        os.remove(file)


class PygameSoundCache(HiveCache):
    __sound_cache__:ClassVar = None

    @staticmethod
    def get_main_cache():
        if not PygameSoundCache.__sound_cache__:
            PygameSoundCache.__sound_cache__ = PygameSoundCache()
        return PygameSoundCache.__sound_cache__

    def get_value(self, key) -> (str, None):
        val = super().get_value(key)
        if not val["optional"]:
            sound = pygame.mixer.Sound(val["filename"])
            self.add_option_value_to_key(key, sound)
        return val

    def play(self, key):
        sound = self.get_optional_value(key)
        sound.play()

    def stop(self,key):
        sound = self.get_optional_value(key)
        sound.stop()