# -*- coding: utf-8 -*-

import os
import time
import tempfile
import datetime

from threading import Thread


class CacheControl:

    def __init__(self):
        self.execute = True
        self.files = {}
        self.__tmp_dir__ = None
        self.__active_thread = None

    @property
    def tmp_dir(self):
        if self.__tmp_dir__ is None:
            self.__tmp_dir__ = tempfile.mkdtemp()
        elif not os.path.isdir(self.__tmp_dir__):
            self.__tmp_dir__ = tempfile.mkdtemp()
            self.files.clear() 
        return self.__tmp_dir__

    def clear(self):
        try:
            import shutil
            shutil.rmtree(self.tmp_dir, True)
            self.files.clear()
            self.__tmp_dir__ = None
        except:
            pass

    def __del__(self):
        self.clear()

    def _start_thread(self):
        if self.__active_thread is None or not self.__active_thread.is_alive():
            self.__active_thread = Thread(target=self.__check_cache, daemon=True)
            self.__active_thread.start()

    def add_file(self, filename, timeout):
        if os.path.isabs(filename):
            if os.path.dirname(filename) == self.tmp_dir:
                fname = os.path.basename(filename)
                fpath = filename
            else:
                raise Exception('O arquivo não pertence ao diretório de controle da cache!')
        else:
            fname = filename
            fpath = os.path.join(self.tmp_dir, fname)
        if os.path.isfile(fpath):
            self.files[fname] = {'path': fpath, 'start': datetime.datetime.now(), 'timeout': datetime.timedelta(seconds=timeout)}
            self._start_thread()
        else:
            raise Exception('{} não é um arquivo existente.'.format(filename))

    def remove_file(self, filename):
        fname = os.path.basename(filename)
        del self.files[fname]

    def __check_cache(self):
        while True:
            if len(self.files) == 0:
                break
            _now = datetime.datetime.now()
            for fkey in list(self.files.keys()):
                fobj = self.files[fkey]
                try:
                    if _now - fobj['start'] > fobj['timeout']:
                        try:
                            os.unlink(fobj['path'])
                            del self.files[fkey]
                        except Exception as e:
                            pass
                except Exception as e:
                    pass
            time.sleep(1)
        self.__active_thread = None