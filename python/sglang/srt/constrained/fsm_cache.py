import threading

from outlines.fsm.fsm import RegexFSM
from outlines.models.transformers import TransformerTokenizer


class FSMCacheEntry:
    def __init__(self):
        self.fsm = None
        self.event = threading.Event()

    def get_fsm(self):
        self.event.wait()
        return self.fsm


class FSMCache:
    def __init__(self, tokenizer):
        self.cache = {}
        self.tokenizer = tokenizer

    def init_fsm_in_background(self, regex, tokenizer_path, tokenizer_args_dict):
        def init_fsm(regex, fsm_cache_entry, tokenizer_path, tokenizer_args_dict):
            outlines_tokenizer = TransformerTokenizer(
                tokenizer_path, **tokenizer_args_dict
            )
            fsm = RegexFSM(regex, outlines_tokenizer)
            fsm_cache_entry.fsm = fsm
            fsm_cache_entry.event.set()

        if regex not in self.cache:
            self.cache[regex] = FSMCacheEntry()
            threading.Thread(
                target=init_fsm,
                args=(
                    regex,
                    self.cache[regex],
                    tokenizer_path,
                    tokenizer_args_dict,
                ),
            ).start()

        return self.cache[regex]
