# Brainf*ck 用のシミュレータ(インタプリタ 兼 単体テスト用)

import sys
import io
from typing import List


class BfSim:
    """A Brainf*ck Simulator"""

    def __init__(self,
                 source: str = "",
                 size: int = 30000,
                 stdin: io.TextIOBase = None,
                 stdout: io.TextIOBase = None):
        """create instance BfSim"""

        # メモリサイズ
        self.size = size
        # メモリ
        self.memory = [0] * size
        # ソースコード
        self.source = source
        # 次に実行する個所. ソースコードのindex(0～)
        self.index = 0
        # 次に実行する個所. ソースコードの行番号(1～)
        self.linenumber = 1
        # 次に実行する個所. ソースコードの列番号(1～)
        self.columnnumber = 1
        # ポインタ
        self.pointer = 0
        # ブレークポインタ. 止まるべきindexを格納
        self.breakpoints: List[int] = []
        # 命令. 独自拡張の命令を追加可能
        self.instructions = {
            '+': lambda sim: sim._plus(),
            '-': lambda sim: sim._minus(),
            '<': lambda sim: sim._move_backward(),
            '>': lambda sim: sim._move_forward(),
            '[': lambda sim: sim._loop_start(),
            ']': lambda sim: sim._loop_end(),
            ',': lambda sim: sim._get_char(),
            '.': lambda sim: sim._put_char(),
        }
        # 標準入力. 必要なら代わりのTextIOBaseのインスタンスを設定する
        # 例 -> io.StringIO("xxxx")
        self.stdin = sys.stdin if stdin is None else stdin
        # 標準出力. 必要なら代わりのTextIOBaseのインスタンスを設定する
        # 例 -> io.StringIO()
        self.stdout = sys.stdout if stdout is None else stdout

    def set_source(self, source: str):
        """set source code and reset index"""
        self.source = source
        self.index = 0
        self.linenumber = 1
        self.columnnumber = 1

    def reset(self):
        """reset index and memory"""
        self.index = 0
        self.linenumber = 1
        self.columnnumber = 1
        self.memory = [0] * self.size

    def step(self):
        """execute 1 step"""
        if not self.is_stopped():
            ch = self.source[self.index]
            if ch in self.instructions:
                func = self.instructions[ch]
                func(self)
            self._pc_forward()

    def run(self, steps: int) -> int:
        """execute steps"""
        for n in range(steps):
            if self.is_stopped():
                return n
            self.step()
            if self.index in self.breakpoints:
                return n + 1
        return steps

    def is_stopped(self) -> bool:
        return self.index < 0 or len(self.source) <= self.index

    def _plus(self):
        self.memory[self.pointer] += 1
        self.memory[self.pointer] &= 0xff

    def _minus(self):
        self.memory[self.pointer] -= 1
        self.memory[self.pointer] &= 0xff

    def _move_backward(self):
        self.pointer -= 1
        if (self.pointer < 0):
            raise ValueError(f"pointer={self.pointer}")

    def _move_forward(self):
        self.pointer += 1
        if (self.size <= self.pointer):
            raise ValueError(f"pointer={self.pointer}")

    def _loop_start(self):
        if self.memory[self.pointer] == 0:
            self._pc_forward()
            nest = 0
            while nest > 0 or self.source[self.index] != ']':
                if self.source[self.index] == ']':
                    nest -= 1
                if self.source[self.index] == '[':
                    nest += 1
                self._pc_forward()
                if self.is_stopped():
                    break

    def _loop_end(self):
        if self.memory[self.pointer] == 0:
            return
        self._pc_backward()
        nest = 0
        while nest > 0 or self.source[self.index] != '[':
            if self.source[self.index] == ']':
                nest += 1
            if self.source[self.index] == '[':
                nest -= 1
            self._pc_backward()
        self._pc_backward(False)

    def _get_char(self):
        ch = self.stdin.read(1)
        self.memory[self.pointer] = ord(ch)

    def _put_char(self):
        ch = chr(self.memory[self.pointer])
        self.stdout.write(ch)
        self.stdout.flush()

    def _pc_forward(self):
        if not self.is_stopped():
            if self.source[self.index] == '\n':
                self.linenumber += 1
                self.columnnumber = 0
            self.index += 1
            self.columnnumber += 1
        elif self.index == -1:
            self.index = 0
            self.linenumber = 1
            self.columnnumber = 1

    def _pc_backward(self, check: bool = True):
        if 0 < self.index:
            self.index -= 1
            self.columnnumber -= 1
            if self.source[self.index] == '\n':
                self.linenumber -= 1
                pos = self.source.rfind('\n', 0, self.index)
                self.columnnumber = self.index - pos
        elif self.index == 0:
            if check:
                raise RuntimeError("invalid address")
            self.index = -1
            self.linenumber = 0
            self.columnnumber = 0


if __name__ == "__main__":
    argc = len(sys.argv)
    if argc != 2:
        raise RuntimeError("usage: {0} BF_SOURCE".format(sys.argv[0]))
    with open(sys.argv[1], "r") as src_file:
        src = src_file.read()
    sim = BfSim(source=src)
    while not sim.is_stopped():
        rc = sim.run(10000)
