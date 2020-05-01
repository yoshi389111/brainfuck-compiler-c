# 簡易的なスタック処理言語風

import bf_core as c

# 数字は以下の2種類
# ・1byte整数(符号なし) {VALUE, 0, 0, 0}
# ・3byte固定小数点小数. {0, 整数部, 小数部, 符号0/1} 符号＋絶対値

# スタックの1要素は4byte固定
ELEMENT_SIZE = 4
# スタックのトップは1要素前
TOP = ELEMENT_SIZE * (-1)
# スタックの2番目は2要素前
SECOND = ELEMENT_SIZE * (-2)
# 現在のスタック位置は空
NOW = 0
# スタックに積んだら1要素後ろに移動
NEXT = ELEMENT_SIZE * (1)

# 1byte整数の配置 { 整数値, 0, 0, 0 }
IDX_BYTE = 0
IDX_DMY1 = 1
IDX_DMY2 = 2
IDX_DMY3 = 3

# 固定小数点小数の配置 { 0, 整数部, 小数部, 符号(0=+/1=-) }
IDX_DMY = 0
IDX_INT = 1
IDX_DEC = 2
IDX_SGN = 3


def push_byte(value: int) -> str:
    "1byteの整数をスタックの先頭に積む"
    value = int(value) & 0xff
    return c.block_of(
        c.init_value(NOW + IDX_BYTE, value & 0xff),
        c.move_ptr(NEXT)
    )


def push_decimal(value: float) -> str:
    "3byteの固定小数点をスタックの先頭に積む"
    (sign, value) = (0, value) if 0 <= value else (1, -value)
    value = int(value * 256) & 0xffff
    return c.block_of(
        c.init_value(NOW + IDX_INT, (value >> 8) & 0xff),
        c.init_value(NOW + IDX_DEC, value & 0xff),
        c.init_value(NOW + IDX_SGN, sign),
        c.move_ptr(NEXT)
    )


def drop() -> str:
    "スタックの先頭を破棄"
    return c.block_of(
        c.clear_pos(TOP + 3),
        c.clear_pos(TOP + 2),
        c.clear_pos(TOP + 1),
        c.clear_pos(TOP + 0),
        c.move_ptr(TOP)
    )


def dup(num: int) -> str:
    "スタックの要素をコピーしてスタック先頭に積む. num=0が先頭をコピー"
    pos = -ELEMENT_SIZE * (num + 1)
    return c.block_of(
        c.copy_data(pos + 0, NOW + 0, NOW + 1),
        c.copy_data(pos + 1, NOW + 1, NOW + 2),
        c.copy_data(pos + 2, NOW + 2, NOW + 3),
        c.copy_data(pos + 3, NOW + 3, NEXT),
        c.move_ptr(NEXT)
    )


def swap(num: int) -> str:
    "スタックの先頭要素と、スタックの該当要素を交換. 1<=numであること"
    pos = -ELEMENT_SIZE * (num + 1)
    work = NOW
    return c.block_of(
        c.swap_data(pos + 0, TOP + 0, work),
        c.swap_data(pos + 1, TOP + 1, work),
        c.swap_data(pos + 2, TOP + 2, work),
        c.swap_data(pos + 3, TOP + 3, work)
    )


def override(num: int) -> str:
    "スタックの先頭要素で、スタックの該当要素を上書き. 1<=numであること."
    pos = -ELEMENT_SIZE * (num + 1)
    return c.block_of(
        c.clear_pos(pos + 3),
        c.move_data(TOP + 3, pos + 3),
        c.clear_pos(pos + 2),
        c.move_data(TOP + 2, pos + 2),
        c.clear_pos(pos + 1),
        c.move_data(TOP + 1, pos + 1),
        c.clear_pos(pos),
        c.move_data(TOP, pos),
        c.move_ptr(TOP)
    )


def put_char() -> str:
    "スタック先頭の1byte(1文字)を出力"
    return c.block_of(
        c.exec_pos(TOP, "."),
        drop()
    )


def loop_of(*statement: str) -> str:
    "TOPの1byte整数分ループする"
    return c.block_of(
        c.for_loop(TOP, c.block_of(*statement)),
        c.move_ptr(TOP)
    )


def loop_last(num: int) -> str:
    "ループを終了できる状態にする. num はループの制御変数の位置. 処理は続行する"
    pos = -ELEMENT_SIZE * (num + 1)
    return c.clear_pos(pos + IDX_BYTE)


def if_nz(then_statement: str, else_statement: str = "") -> str:
    "スタック先頭 1byteが NZ の場合. 終了後スタック先頭は捨てる"
    else_statement = c.delete_useless(else_statement)
    if else_statement != "":
        else_flag = TOP + IDX_DMY1
        return c.block_of(
            c.set_value(else_flag, 1),
            c.if_nz_then(
                TOP + IDX_BYTE,
                c.dec_pos(else_flag) + then_statement),
            c.if_one_then(
                else_flag,
                else_statement),
            c.move_ptr(TOP))
    else:
        return c.block_of(
            c.if_nz_then(
                TOP + IDX_BYTE,
                then_statement),
            c.move_ptr(TOP)
        )


def if_z(then_statement: str, else_statement: str = "") -> str:
    "1byteが Z の場合. 終了後スタック先頭は捨てる"
    return if_nz(else_statement, then_statement)


def if_nz_decimal(then_statement: str, else_statement: str = "") -> str:
    "3byte固定小数点が NZ の場合. 終了後スタック先頭は捨てる"
    nz_flag = TOP + IDX_DMY
    else_flag = TOP + IDX_INT
    then_flag = TOP + IDX_DEC
    return c.block_of(
        c.clear_pos(TOP + IDX_SGN),
        c.if_nz_then(TOP + IDX_DEC, c.inc_pos(nz_flag)),
        c.if_nz_then(TOP + IDX_INT, c.inc_pos(nz_flag)),
        c.inc_pos(else_flag),
        c.if_nz_then(nz_flag, c.dec_pos(else_flag) + c.inc_pos(then_flag)),
        c.if_one_then(then_flag, then_statement),
        c.if_one_then(else_flag, else_statement),
        c.move_ptr(TOP)
    )


def if_z_decimal(then_statement: str, else_statement: str = "") -> str:
    "3byte固定小数点が NZ の場合. 終了後スタック先頭は捨てる"
    return if_nz_decimal(else_statement, then_statement)


def if_negative_decimal(then_statement: str, else_statement: str = "") -> str:
    "3byte固定小数点が負数の場合. 終了後スタック先頭は捨てる"
    # TODO -0.0 対応をしていない
    then_flag = TOP + IDX_DEC
    else_flag = TOP + IDX_INT
    return c.block_of(
        c.clear_pos(then_flag),
        c.set_value(else_flag, 1),
        c.if_nz_then(
            TOP + IDX_SGN,
            c.dec_pos(else_flag) + c.inc_pos(then_flag)),
        c.if_one_then(then_flag, then_statement),
        c.if_one_then(else_flag, else_statement),
        c.move_ptr(TOP))


def add_byte() -> str:
    "1byteの加算"
    return c.block_of(
        c.for_loop(SECOND, c.inc_pos(TOP + IDX_BYTE)),
        override(1)
    )


def _add_abs() -> str:
    "3byte固定小数点の絶対値の加算"
    # SECOND/TOP の符号は同じであることを想定
    return c.block_of(
        c.clear_pos(TOP + IDX_SGN),
        c.for_loop(SECOND + IDX_DEC, c.inc_data_tricky(TOP + IDX_DEC, 2)),
        c.for_loop(SECOND + IDX_INT, c.inc_pos(TOP + IDX_INT)),
        c.override_data(TOP + IDX_DEC, SECOND + IDX_DEC),
        c.override_data(TOP + IDX_INT, SECOND + IDX_INT)
    )


def _dec_both_abs_int() -> str:
    "整数部を片方が0になるまで両方をデクリメント"
    count = NOW
    work1 = NOW + 1
    return c.block_of(
        c.copy_data(SECOND + IDX_INT, count, work1),
        c.for_loop(
            count,
            c.if_z_tricky(
                TOP + IDX_INT,
                ELEMENT_SIZE,  # work2 = NOW + IDX_INT
                ELEMENT_SIZE,  # work3 = NEXT + IDX_INT
                then_statement=loop_last(count),
                else_statement=c.block_of(
                    c.dec_pos(SECOND + IDX_INT),
                    c.dec_pos(TOP + IDX_INT)
                )
            )
        )
    )


def _dec_both_abs_decimal() -> str:
    "小数部を片方が0になるまで両方をデクリメント"
    count = NOW
    work1 = NOW + 1
    return c.block_of(
        c.copy_data(SECOND + 2, count, work1),
        c.for_loop(count, c.block_of(
            c.if_z_tricky(
                TOP + IDX_DEC,
                ELEMENT_SIZE,  # work2 = NOW + IDX_DEC
                ELEMENT_SIZE,  # work3 = NEXT + IDX_DEC
                then_statement=loop_last(count),
                else_statement=c.block_of(
                    c.dec_pos(SECOND + IDX_DEC),
                    c.dec_pos(TOP + IDX_DEC)
                )
            )
        ))
    )


def _if_nz_int_swap() -> str:
    "SECONDの整数部が0以外なら、TOP/SECONDをひっくり返す"
    work = NOW
    return c.if_nz_tricky(
        SECOND + IDX_INT,
        ELEMENT_SIZE * 2,  # work2 = NOW + IDX_INT
        ELEMENT_SIZE * 2,  # work3 = NEXT + NEXT + IDX_INT
        then_statement=c.block_of(
            c.swap_data(SECOND + IDX_INT, TOP + IDX_INT, work),
            c.swap_data(SECOND + IDX_DEC, TOP + IDX_DEC, work),
            c.swap_data(SECOND + IDX_SGN, TOP + IDX_SGN, work)
        )
    )


def _if_top_decimal_is_nz_then_override() -> str:
    "TOPの小数部が0以外なら、TOPをSECONDに移動"
    return c.if_z_tricky(
        TOP + IDX_DEC,
        ELEMENT_SIZE,  # work1 = NOW + IDX_DEC
        ELEMENT_SIZE,  # work2 = NEXT + IDX_DEC
        then_statement=c.clear_pos(TOP + IDX_SGN),
        else_statement=c.block_of(
            c.override_data(TOP + IDX_SGN, SECOND + IDX_SGN),
            c.move_data(TOP + IDX_DEC, SECOND + IDX_DEC)
        )
    )


def _top_minus_second() -> str:
    "SECOND+2分、TOPから削除して、SECONDの位置に移動"
    return c.block_of(
        # 符号を移動(tricky対策で、先に移動)
        c.override_data(TOP + IDX_SGN, SECOND + IDX_SGN),
        # SECONDの小数部だけデクリメント
        c.for_loop(
            SECOND + IDX_DEC,
            c.dec_data_tricky(TOP + IDX_DEC, 2)),
        # 結果を SECONDに移動
        c.move_data(TOP + IDX_DEC, SECOND + IDX_DEC),
        c.move_data(TOP + IDX_INT, SECOND + IDX_INT)
        # TODO -0.0 を 0.0 に変換すべき？
    )


def _sub_abs() -> str:
    "3byte固定小数点の絶対値の減算"
    # どちらかが0になるまでdecする. 残ったほうが答え(符号も含め)
    return c.block_of(
        # 整数部を片方が0になるまで両方をデクリメント
        _dec_both_abs_int(),
        # SECONDの整数部が0以外なら、TOP/SECONDをひっくり返す
        _if_nz_int_swap(),
        c.if_nz_tricky(
            TOP + IDX_INT,
            ELEMENT_SIZE,  # work1 = NEXT + IDX_INT
            ELEMENT_SIZE,  # work2 = NEXT + NEXT + IDX_INT
            then_statement=_top_minus_second(),
            else_statement=c.block_of(
                # TOP/SECONDの両方とも整数部が0の場合
                _dec_both_abs_decimal(),
                _if_top_decimal_is_nz_then_override()
            )
        )
    )


def add_decimal() -> str:
    "固定小数点小数の加算"
    # 符号が同じなら、絶対値の加算
    # 符号が異なるなら、絶対値の減算
    work = SECOND + IDX_DMY
    diff_work = TOP + IDX_DMY
    same_flag = SECOND + IDX_DMY
    return c.block_of(
        c.for_safe(SECOND + IDX_SGN, work, c.inc_pos(diff_work)),
        c.for_safe(TOP + IDX_SGN, work, c.dec_pos(diff_work)),
        c.inc_pos(same_flag),
        c.if_nz_then(diff_work, c.dec_pos(same_flag) + _sub_abs()),
        c.if_nz_then(same_flag, _add_abs()),
        drop()
    )


def sub_decimal() -> str:
    "固定小数点小数の減算"
    # 符号を反転して加算(A-B => A+(-B))
    plus_flag = NOW + IDX_DMY
    return c.block_of(
        c.inc_pos(plus_flag),
        c.if_one_then(TOP + IDX_SGN, c.dec_pos(plus_flag)),
        c.if_one_then(plus_flag, c.inc_pos(TOP + IDX_SGN)),
        add_decimal()
    )


def _multi_decimal_abs() -> str:
    "3byte固定小数点の絶対値の乗算"
    # 整数部と小数部は筆算と同様に、byte単位で計算する
    # TODO カラツバ法を使う？
    #             A1. A2
    #           x B1. B2
    # ---------------------
    #               .A1xB2 A2xB2
    #       +  A1xB1.A2xB1
    # ----------------------
    #            R1 .  R2    R3
    #          <---------> 必要な範囲
    idx_a1 = SECOND + IDX_INT
    idx_a2 = SECOND + IDX_DEC
    idx_b1 = TOP + IDX_INT
    idx_b2 = TOP + IDX_DEC
    idx_r1 = NOW + IDX_INT
    idx_r2 = NOW + IDX_DEC
    idx_r3 = NOW + IDX_DEC + 1

    # 繰り上がり処理の関係で、上の桁から計算する
    return c.block_of(
        c.multi_data_tricky(idx_a1, idx_b1, idx_r1, 1),  # AxC (1byte 分)
        c.multi_data_tricky(idx_a1, idx_b2, idx_r2, 2),  # AxD (繰り上げ含め2byte)
        c.multi_data_tricky(idx_a2, idx_b1, idx_r2, 2),  # BxC (繰り上げ含め2byte)
        c.multi_data_tricky(idx_a2, idx_b2, idx_r3, 3),  # BxD (繰り上げ含め3byte)
        c.clear_pos(idx_r3),  # R3 は繰り上げ分のみが必要なのでクリア
    )


def _xor_sign() -> str:
    # 符号は同じなら＋、異なるならマイナス
    idx_as = SECOND + IDX_SGN
    idx_bs = TOP + IDX_SGN
    idx_rs = NOW + IDX_SGN
    sign_work = NEXT
    return c.block_of(
        c.for_loop(idx_as, c.inc_pos(sign_work)),
        c.for_loop(idx_bs, c.dec_pos(sign_work)),
        c.if_nz_then(sign_work, c.inc_pos(idx_rs))
    )


def multi_decimal() -> str:
    "3byte固定小数点の乗算"
    # A * B => R
    return c.block_of(
        _multi_decimal_abs(),  # R の絶対値を求める
        _xor_sign(),  # R の符号を求める
        c.move_ptr(NEXT),  # スタックの状態は {A, B, R}
        override(2),  # R を A の位置に上書き
        drop()  # B を削除
    )


def if_lt_decimal(then_statement: str, else_statement: str = "") -> str:
    return c.block_of(
        swap(1),  # {A, B} -> {B, A} の順にする. then/else実行時のスタック数を変えないため
        dup(1),  # {B, A, B}
        sub_decimal(),  # {B, R (= A - B)}
        # R が負数なら A < B
        if_negative_decimal(then_statement, else_statement),
        drop()  # drop B
    )


def if_ge_decimal(then_statement: str, else_statement: str = "") -> str:
    return if_lt_decimal(else_statement, then_statement)
