# bfコマンドマクロの基本命令

import math
import re


def delete_useless(statement: str) -> str:
    """
    無駄な移動/計算を相殺、削除

    >>> delete_useless("+++--<<>>>")
    '+>'
    >>> delete_useless("---++>><<<")
    '-<'
    >>> delete_useless(">++++[-][-]")
    '>[-]'
    >>> delete_useless(">--[-]++[-]")
    '>[-]'
    """
    while True:
        if "<>" in statement:
            # 無駄な移動の相殺・その１
            statement = statement.replace("<>", "")
            continue
        if "><" in statement:
            # 無駄な移動の相殺・その２
            statement = statement.replace("><", "")
            continue
        if "+-" in statement:
            # 無駄な加減算の相殺・その１
            statement = statement.replace("+-", "")
            continue
        if "-+" in statement:
            # 無駄な加減算の相殺・その２
            statement = statement.replace("-+", "")
            continue
        if "+[-]" in statement or "-[-]" in statement:
            # ゼロクリアの前の加減算の削除
            statement = re.sub(r'[-+]+\[-\]', "[-]", statement)
            continue
        if "[-][-]" in statement:
            # 複数回のゼロクリアを１回に
            statement = statement.replace("[-][-]", "[-]")
            continue
        break
    return statement


def delete_useless_all(statement: str) -> str:
    """
    無駄な移動/計算を相殺、削除。最後の無駄な処理も削除する

    >>> delete_useless_all("[+>-<]>++++[-][-]")
    '[+>-<]'
    >>> delete_useless_all("[-<+>][-]>>++")
    '[-<+>]'
    >>> delete_useless_all("[-<+>][-]<<--")
    '[-<+>]'
    """
    statement = delete_useless(statement)
    while statement:
        if statement[-1] in "-+><":
            # 末尾の "+" "-" ">" "<" は削除
            statement = re.sub(r'[-+><]+$', "", statement)
            continue
        if statement.endswith("[-]"):
            # 末尾の "[-]" は削除
            statement = re.sub(r'\[-\]$', "", statement)
            continue
        break
    return statement


def block_of(*statements: str) -> str:
    """
    複数の命令をまとめる

    >>> block_of("[", "-", "]")
    '[-]'
    """
    return delete_useless("".join(statements))


def program_of(*statements: str) -> str:
    source = delete_useless_all("".join(statements))
    source = re.sub(r'(.{1,72})', "\\1\n", source)
    return source


def move_ptr(pos: int) -> str:
    """
    ポインターを移動

    >>> move_ptr(0)
    ''
    >>> move_ptr(2)
    '>>'
    >>> move_ptr(-3)
    '<<<'
    """
    return ">" * pos if 0 <= pos else "<" * (-pos)


def exec_pos(pos: int, statement: str) -> str:
    """
    指定位置で処理を実行

    >>> exec_pos(3, "+")
    '>>>+<<<'
    >>> exec_pos(3, "<+>")
    '>>+<<'
    """
    return block_of(
        move_ptr(pos),
        statement,
        move_ptr(-pos)
    )


def inc_pos(pos: int) -> str:
    """
    指定位置をインクリメント

    >>> inc_pos(2)
    '>>+<<'
    """
    return exec_pos(pos, "+")


def dec_pos(pos: int) -> str:
    """
    指定位置をデクリメント

    >>> dec_pos(3)
    '>>>-<<<'
    """
    return exec_pos(pos, "-")


def clear_pos(pos: int) -> str:
    """
    指定位置をクリア

    >>> clear_pos(3)
    '>>>[-]<<<'
    """
    return exec_pos(pos, "[-]")


def set_value(pos: int, value: int) -> str:
    """
    指定の値を設定

    >>> set_value(2, 3)
    '>>[-]+++<<'
    >>> set_value(2, -1)
    '>>[-]-<<'
    """
    (op, value) = ("+", value) if 0 < value else ("-", -value)
    return block_of(
        clear_pos(pos),
        exec_pos(pos, op * value)
    )


def while_loop(pos: int, *statements: str) -> str:
    """
    whileループ.

    >>> while_loop(3, ">>+<<")
    '>>>[<+>]<<<'
    """
    return block_of(
        exec_pos(pos, "["),
        block_of(*statements),
        exec_pos(pos, "]")
    )


def for_loop(pos: int, *statements: str) -> str:
    """
    繰り返し. 破壊版

    >>> for_loop(3, "+")
    '>>>[-<<<+>>>]<<<'
    """
    return block_of(
        exec_pos(pos, "[-"),
        block_of(*statements),
        exec_pos(pos, "]")
    )


def for_safe(pos: int, work1: int, statement: str) -> str:
    """
    繰り返し. 非破壊版(ただしループ中にposを参照更新してはダメ)

    >>> for_safe(3, 4, "+")
    '>>>[->+<<<<+>>>]>[-<+>]<<<<'
    """
    return block_of(
        for_loop(pos, inc_pos(work1), statement),
        move_data(work1, pos)
    )


def move_data(source: int, destination: int) -> str:
    "1byteの移動/あるいは加算."
    return for_loop(source, inc_pos(destination))


def copy_data(source: int, destination: int, work1: int) -> str:
    "1byteのコピー."
    return block_of(
        clear_pos(destination),
        for_safe(source, work1, inc_pos(destination))
    )


def override_data(source: int, destination: int) -> str:
    "1byteの移動."
    return block_of(
        clear_pos(destination),
        move_data(source, destination)
    )


def swap_data(target1: int, target2: int, work1: int) -> str:
    "1byte同士の値の入れ替え"
    return block_of(
        move_data(target1, work1),
        move_data(target2, target1),
        move_data(work1, target2)
    )


def _init_value_sub(value: int) -> str:
    "初回の値設定. 隣以降はワークに使ってよい前提"
    (op1, op2) = ("+", "-")
    if value < 0:
        value = -value
        (op1, op2) = ("-", "+")
    if value < 16:
        return op1 * value
    len0 = value
    str0 = op1 * value
    xmin = int(math.sqrt(value))
    xmax = int(math.ceil(value / 2.0))
    for x in range(xmin, xmax + 1):
        strx = _init_value_sub(x)
        lenx = len(strx)
        # len0 = x * y1 + c1 の形に分割
        y1 = value // x
        c1 = value % x
        len1 = lenx + y1 + c1 + 7
        if len1 < len0:
            len0 = len1
            str0 = ">" + strx + "[<" + op1 * y1 + ">-]<" + op1 * c1
        if c1 != 0:
            # len0 = x * y2 - c1 の形に分割
            y2 = y1 + 1
            c2 = x - c1
            len2 = lenx + y2 + c2 + 7
            if len2 < len0:
                len0 = len2
                str0 = ">" + strx + "[<" + op1 * y2 + ">-]<" + op2 * c2
    return str0


def init_value(pos: int, value: int) -> str:
    """
    初回の値設定.

    隣以降はワークに使ってよい前提. 初期化順に注意
    """
    return delete_useless(exec_pos(pos, _init_value_sub(value)))


def if_nz_then(pos: int, then_statement: str) -> str:
    "if_nz の破壊版. thenのみの簡易版"
    return while_loop(
        pos,
        clear_pos(pos),
        then_statement
    )


def if_one_then(pos: int, then_statement: str) -> str:
    "posの位置が 1 か 0 のどちらが前提. 1 の場合に処理する (破壊版)."
    return while_loop(
        pos,
        dec_pos(pos),
        then_statement
    )


def if_nz_tricky(
        pos: int,
        n: int,
        m: int,
        then_statement: str,
        else_statement: str = "") -> str:
    """
    if_nz の非破壊版. ちょっとトリッキー

    前提条件
      *(ptr + pos + n) == 0
      *(ptr + pos + m) == 0
      *(ptr + pos + n + m) == 0
    ※ n == m でもOK
    """
    return block_of(
        move_ptr(pos),
        inc_pos(n),  # pos+n = else用フラグ
        "[",  # NZ の場合
        dec_pos(n),  # else用フラグをクリア
        exec_pos(-pos, then_statement),
        move_ptr(m),  # NZ は pos+m / Z は pos のまま
        "c]",
        move_ptr(n),  # NZ は pos+n+m / Z は pos+n
        "[-",  # Z の場合
        exec_pos(-pos - n, else_statement),
        move_ptr(m),  # NZ は pos+n+m のまま / Z も pos+n+m に移動
        "c]",
        move_ptr(-pos - n - m)
    )


def if_z_tricky(
        pos: int,
        n: int,
        m: int,
        then_statement: str,
        else_statement: str = "") -> str:
    """
    if_z の非破壊版. ちょっとトリッキー

    前提条件
      *(ptr + pos + n) == 0
      *(ptr + pos + m) == 0
      *(ptr + pos + n + m) == 0
    ※ n == m でもOK
    """
    return if_nz_tricky(pos, n, m, else_statement, then_statement)


def inc_data_tricky(pos: int, digit: int) -> str:
    """
    繰り上がりありのインクリメント. ちょっとトリッキー

    前提条件
      *(ptr + pos + 1) == 0
      *(ptr + pos + 2) == 0
    """

    if 1 < digit:
        # 繰り上がり必要
        return block_of(
            inc_pos(pos),
            if_z_tricky(pos, 1, 1,
                        inc_data_tricky(pos - 1, digit - 1))
        )
    else:
        # 繰り上がり不要
        return inc_pos(pos)


def dec_data_tricky(pos: int, digit: int) -> str:
    """
    繰り下がりありのデクリメント. ちょっとトリッキー

    前提条件
      *(ptr + pos + 1) == 0
      *(ptr + pos + 2) == 0
    """
    if 1 < digit:
        return block_of(
            if_z_tricky(pos, 1, 1,
                        dec_data_tricky(pos - 1, digit - 1)),
            dec_pos(pos)
        )
    else:
        return dec_pos(pos)


def add_data_tricky(source: int, pos: int, work: int, digit: int) -> str:
    """
    1byte加算. pos += source. 繰り上がりあり. 非破壊版. ちょっとトリッキー

    前提条件
      *(ptr + pos + 1) == 0
      *(ptr + pos + 2) == 0
    """
    return for_safe(source, work, inc_data_tricky(pos, digit))


def multi_data_tricky(
        source1: int,
        source2: int,
        pos: int,
        digit: int) -> str:
    """
    1byte乗算. pos = source1 * source2. 繰り上がりあり. 非破壊版. ちょっとトリッキー

    前提条件
      *(ptr + pos + 1) == 0
      *(ptr + pos + 2) == 0
      *(ptr + pos + 3) == 0
      *(ptr + pos + 4) == 0
    """
    return for_safe(
        source1,
        pos + 3,
        add_data_tricky(source2, pos, pos + 4, digit)
    )
