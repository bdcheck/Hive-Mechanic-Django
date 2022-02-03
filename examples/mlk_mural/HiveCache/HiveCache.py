import json
from typing import ClassVar
import os.path
import requests
import tempfile
import mimetypes
import shutil
import os
import pygame
import validators

class HiveCache(object):
    """Class that caches URLs, keys are based on input strings that are URLs"""
    __main_cache__: ClassVar = None

    @staticmethod
    def get_main_cache():
        """Singleton method for creating a main cache
        :return: Main HiveCache repository
        """
        if not HiveCache.__main_cache__:
            HiveCache.__main_cache__ = HiveCache()
        return HiveCache.__main_cache__

    @staticmethod
    def get_type(key) -> str:
        """
        returns the mimetype category for an url
        :param key:
        :return: minetype category
        """
        c_type = mimetypes.guess_type(key)
        cat_type = str(c_type[0]).split("/")[0]
        return cat_type

    def __init__(self, name="main"):
        self.__cache = {}
        self.__name = name
        self.check_and_read_cache_list()

    def check_file_exists(self, file, ending=None):
        dir = tempfile.gettempdir()
        new_file = dir + "/" + file
        if ending:
            new_file += ending
        if os.path.exists(new_file):
            return new_file
        return False

    def check_and_read_cache_list(self):
        """
        checks to see if it exists and if it exists reads it in
        """
        name = self.check_file_exists(self.__name, ".cache")
        if name:
            with open(name) as fp:
                self.__cache = json.load(fp)

            self.cleanup_cache_list()

    def cleanup_cache_list(self):
        """
        Goes through cache list and determines if files exist
        :return:
        """
        list_to_delete = []
        for key in self.__cache:
            data = self.__cache[key]
            filename = data["filename"]
            if not os.path.exists(filename):
                list_to_delete.append(key)
        for key in list_to_delete:
            del self.__cache[key]


    def write_cache_list(self):
        """
        Writes cache list to a file
        :return:
        """
        dir = tempfile.gettempdir()
        file = dir + "/"+self.__name + ".cache"
        with open(file,"w") as fp:
            dump = {key: self.get_all_fields_but_optional(value) for key, value in self.__cache.items()}
            json.dump(dump, fp)

    def get_all_fields_but_optional(self, entry):
        return {key: value for key, value in entry.items() if key != "optional"}

    def check_if_exists(self, key: str):
        """Determines if a url is already in the system
        :param key: URL
        """
        if key in self.__cache:
            return True
        return False

    def get_value(self, key: str) -> (dict, None):
        """Returns the raw data structure for the cache, if the url is not in the cache is will download and add a new entry
        if URL is unavailable None is returned.
        Raises Validation error if url is not a valid URL
        :param key: URL
        :return: Data structure or None if key does not exist
        """
        validators.url(key)
        if not self.check_if_exists(key) or self.__cache[key] is None:
            c_type = mimetypes.guess_type(key)
            ext = mimetypes.guess_extension(c_type[0])
            file = tempfile.NamedTemporaryFile(suffix=ext, delete=False)
            cat_type = str(c_type[0]).split("/")[0]
            data = {"filename": file.name, "type": cat_type, "optional": None}
            r = requests.get(key, stream=True)
            if r.status_code == 200:
                r.raw.decode_content = True
                shutil.copyfileobj(r.raw, file)
                self.__cache[key] = data
                self.write_cache_list()
            else:
                self.__cache[key] = data
                self.__remove_file(key)
                self.__cache[key] = None

        return self.__cache[key]

    def get_file_name(self, key: str):
        """
        :param key:
        :return: path for cached file
        """
        item = self.get_value(key)
        return item.name

    def get_type_for_key(self, key: str)->str:
        """
        Get the type from key
        :param key: strURL
        :return: str type from mimetype
        """
        data = self.__cache[key]
        return data["type"]

    def remove_from_cache(self, key: str):
        """
        Remove a cached entry
        :param key: URL
        """
        self.__remove_file(key)
        del(self.__cache[key])

    def add_optional_value_to_key(self, key: str, optional_data):
        """
        Structure for holding user define structures, primarily used for sound and image pointers used in pygame
        :param key: URL
        :param optional_data: Data to be stored
        :return:
        """
        if self.check_if_exists(key):
            data = self.__cache[key]
            data["optional"] = optional_data
            self.__cache[key] = data

    def get_optional_value(self, key: str):
        """
        Retrieve optional data from the cache
        :param key: URL
        :return:
        """
        data = self.get_value(key)
        if data and data["optional"]:
            return data["optional"]
        return None

    def clear(self):
        """
        Clears out entire cache and remove all local files
        """
        for key in self.__cache.keys():
            self.__remove_file(key)
        self.__cache.clear()

    def __remove_file(self, key: str):
        """
        Removes a cached file from system
        :param key: URL str
        """
        data = self.__cache[key]
        file = data["filename"]
        os.remove(file)


class PygameSoundCache(HiveCache):
    """Pygame Sound specific instance of HiveCache"""
    __sound_cache__: ClassVar = None

    @staticmethod
    def get_sound_cache():
        """
        Singleton for sound cache
        :return: PygameSoundCache instance
        """
        if not PygameSoundCache.__sound_cache__:
            PygameSoundCache.__sound_cache__ = PygameSoundCache()
        return PygameSoundCache.__sound_cache__

    def __init__(self):
        super().__init__("sound")

    def get_value(self, key: str) -> (dict, None):
        """

        :param key: URL str
        :return: dictionary of cache or None if doesn't exist
        """
        val = super().get_value(key)
        if val and not val.get("optional"):
            sound = pygame.mixer.Sound(val["filename"])
            self.add_optional_value_to_key(key, sound)
        return val

    def get_optional_value(self, key: str)->(pygame.mixer.Sound,None):
        """
        Returns cached sound
        :param key: URL str
        :return: pygame.mixer.Sound or None if cache url cannot be found
        """
        data = self.get_value(key)
        if data and data.get("optional"):
            return data["optional"]
        return None

    def play(self, key: str):
        """
        Plays sound from URL, caches if doesn't exist
        :param key: URL str
        :return:
        """
        sound = self.get_optional_value(key)
        sound.play()

    def stop(self, key: str):
        """
        Stop playing sound for URL
        :param key: str URL
        :return:
        """
        sound = self.get_optional_value(key)
        sound.stop()


class PygameImageCache(HiveCache):
    """Pygame Sound specific instance of HiveCache"""
    __surface_cache__: ClassVar = None

    @staticmethod
    def get_image_cache():
        """
        Singleton for sound cache
        :return: PygameImageCache instance
        """
        if not PygameImageCache.__surface_cache__:
            PygameImageCache.__surface_cache__ = PygameImageCache()
        return PygameImageCache.__surface_cache__

    def __init__(self):
        super().__init__("images")

    def get_value(self, key: str) -> (dict, None):
        """
        :param key: URL str
        :return: dictionary of cache or None if doesn't exist
        """
        val = super().get_value(key)
        if val and not val.get('optional'):
            image = pygame.image.load(val["filename"])
            self.add_optional_value_to_key(key, image)
        return val

    def get_optional_value(self, key: str)->(pygame.surface,None):
        """
        Returns cached sound
        :param key: URL str
        :return: pygame.surface or None if cache url cannot be found
        """
        data = self.get_value(key)
        if data and data.get("optional"):
            return data["optional"]
        return None

    def get_image(self, key) -> (pygame.surface, None):
        return self.get_optional_value(key)



