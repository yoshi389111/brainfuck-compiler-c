# 簡易的なスタック処理言語として実装

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


def push_byte(value: int) -> str:
    "1byteの整数をスタックの先頭に積む"
    value = int(value) & 0xff
    return c.block_of(
        c.init_value(NOW, value & 0xff),
        c.move_ptr(NEXT)
    )


def push_decimal(value: float) -> str:
    "3byteの固定小数点をスタックの先頭に積む"
    (sign, value) = (0, value) if 0 <= value else (1, -value)
    value = int(value * 256) & 0xffff
    return c.block_of(
        c.init_value(NOW + 1, (value >> 8) & 0xff),
        c.init_value(NOW + 2, value & 0xff),
        c.init_value(NOW + 3, sign),
        c.move_ptr(NEXT)
    )


def drop() -> str:
    "スタックの先頭を破棄"
    return c.block_of(
        c.clear_pos(TOP + 3),
        c.clear_pos(TOP + 2),
        c.clear_pos(TOP + 1),
        c.clear_pos(TOP),
        c.move_ptr(TOP)
    )


def drop_byte() -> str:
    "スタックの先頭を破棄"
    return c.block_of(
        c.clear_pos(TOP),
        c.move_ptr(TOP)
    )


def drop_decimal() -> str:
    "スタックの先頭を破棄"
    return c.block_of(
        c.clear_pos(TOP + 3),
        c.clear_pos(TOP + 2),
        c.clear_pos(TOP + 1),
        c.move_ptr(TOP)
    )


def dup(num: int) -> str:
    "スタックの要素をコピーしてスタック先頭に積む. num=0が先頭をコピー"
    pos = -ELEMENT_SIZE * (num + 1)
    return c.block_of(
        c.copy_data(pos, NOW, NOW + 1),
        c.copy_data(pos + 1, NOW + 1, NOW + 2),
        c.copy_data(pos + 2, NOW + 2, NOW + 3),
        c.copy_data(pos + 3, NOW + 3, NEXT),
        c.move_ptr(NEXT)
    )


def swap(num: int) -> str:
    "スタックの先頭要素と、スタックの該当要素を交換. 1<=numであること"
    pos = -ELEMENT_SIZE * (num + 1)
    return c.block_of(
        c.swap_data(pos, TOP, NOW),
        c.swap_data(pos + 1, TOP + 1, NOW),
        c.swap_data(pos + 2, TOP + 2, NOW),
        c.swap_data(pos + 3, TOP + 3, NOW)
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
        drop())


def loop_of(*statement: str) -> str:
    "TOPの1byte整数分ループする"
    return c.block_of(
        c.for_loop(TOP, c.block_of(*statement)),
        c.move_ptr(TOP))


def loop_last(num: int) -> str:
    "ループを終了できる状態にする. num はループの制御変数の位置. 処理は続行する"
    pos = -ELEMENT_SIZE * (num + 1)
    return c.clear_pos(pos)


def if_nz(then_statement: str, else_statement: str = "") -> str:
    "スタック先頭 1byteが NZ の場合. 終了後スタック先頭は捨てる"
    else_statement = c.delete_useless(else_statement)
    if else_statement != "":
        return c.block_of(
            c.set_value(TOP + 1, 1),
            c.if_nz_then(TOP, c.dec_pos(TOP + 1) + then_statement),
            c.if_one_then(TOP + 1, else_statement),
            c.move_ptr(TOP)
        )
    else:
        return c.block_of(
            c.if_nz_then(TOP, then_statement),
            c.move_ptr(TOP)
        )


def if_z(then_statement: str, else_statement: str = "") -> str:
    "1byteが Z の場合. 終了後スタック先頭は捨てる"
    return if_nz(else_statement, then_statement)


def if_nz_decimal(then_statement: str, else_statement: str = "") -> str:
    "3byte固定小数点が NZ の場合. 終了後スタック先頭は捨てる"
    return c.block_of(
        c.if_nz_then(TOP + 1, c.inc_pos(TOP)),
        c.if_nz_then(TOP + 2, c.inc_pos(TOP)),
        c.inc_pos(TOP + 1),
        c.if_nz_then(TOP, c.dec_pos(TOP + 1) + c.inc_pos(TOP + 2)),
        c.if_one_then(TOP + 2, then_statement),
        c.if_one_then(TOP + 1, else_statement),
        c.clear_pos(TOP + 3),
        c.move_ptr(TOP)
    )


def if_z_decimal(then_statement: str, else_statement: str = "") -> str:
    "3byte固定小数点が NZ の場合. 終了後スタック先頭は捨てる"
    return if_nz_decimal(else_statement, then_statement)


def if_negative_decimal(then_statement: str, else_statement: str = "") -> str:
    "3byte固定小数点が負数の場合. 終了後スタック先頭は捨てる"
    return c.block_of(
        c.clear_pos(TOP + 1),
        c.clear_pos(TOP + 2),  # TODO -0.0 対応をしていない
        c.inc_pos(TOP + 1),
        c.if_nz_then(TOP + 3, c.dec_pos(TOP + 1) + c.inc_pos(TOP + 2)),
        c.if_one_then(TOP + 2, then_statement),
        c.if_one_then(TOP + 1, else_statement),
        c.move_ptr(TOP)
    )


def add_byte() -> str:
    "1byteの加算"
    return c.block_of(
        c.for_loop(SECOND, c.inc_pos(TOP)),
        override(1)
    )


def _add_abs() -> str:
    "3byte固定小数点の絶対値の加算"
    # SECOND/TOP の符号は同じであることを想定
    return c.block_of(
        c.clear_pos(TOP + 3),  # TOP 側の符号を削除
        c.for_loop(SECOND + 2, c.inc_data_tricky(TOP + 2, 2)),
        c.for_loop(SECOND + 1, c.inc_pos(TOP + 1)),
        c.clear_pos(SECOND + 2),
        c.move_data(TOP + 2, SECOND + 2),
        c.clear_pos(SECOND + 1),
        c.move_data(TOP + 1, SECOND + 1)
    )


def _dec_both_abs_int() -> str:
    "整数部を片方が0になるまで両方をデクリメント"
    return c.block_of(
        c.copy_data(SECOND + 1, NOW, NOW + 1),
        c.for_loop(NOW, c.block_of(
            c.if_z_tricky(
                TOP + 1,
                ELEMENT_SIZE,
                ELEMENT_SIZE,
                then_statement=loop_last(NOW),
                else_statement=c.dec_pos(SECOND + 1) + c.dec_pos(TOP + 1)
            )
        ))
    )


def _dec_both_abs_decimal() -> str:
    "小数部を片方が0になるまで両方をデクリメント"
    return c.block_of(
        c.copy_data(SECOND + 2, NOW, NOW + 1),
        c.for_loop(NOW, c.block_of(
            c.if_z_tricky(
                TOP + 2,
                ELEMENT_SIZE,
                ELEMENT_SIZE,
                then_statement=loop_last(NOW),
                else_statement=c.dec_pos(SECOND + 2) + c.dec_pos(TOP + 2)
            )
        ))
    )


def _if_nz_int_swap() -> str:
    "SECOND+1が0以外なら、TOP/SECONDをひっくり返す"
    return c.if_nz_tricky(
        SECOND + 1, ELEMENT_SIZE * 2, ELEMENT_SIZE * 2,
        then_statement=c.block_of(
            c.swap_data(SECOND + 1, TOP + 1, NOW),
            c.swap_data(SECOND + 2, TOP + 2, NOW),
            c.swap_data(SECOND + 3, TOP + 3, NOW)
        ))


def _if_top_decimal_is_nz_then_override() -> str:
    "TOP+2がNZなら、TOPをSECONDに移動"
    return c.if_z_tricky(
        TOP + 2,
        ELEMENT_SIZE,
        ELEMENT_SIZE,
        then_statement=c.clear_pos(TOP + 3),
        else_statement=c.block_of(
            c.swap_data(TOP + 3, SECOND + 3, NOW),
            c.swap_data(TOP + 2, SECOND + 2, NOW)
        ))


def _top_minus_second() -> str:
    "SECOND+2分、TOPから削除して、SECONDの位置に移動"
    return c.block_of(
        # 符号を退避
        c.clear_pos(SECOND + 3),
        c.move_data(TOP + 3, SECOND + 3),
        # SECOND+2の分だけデクリメント
        c.for_loop(SECOND + 2, c.dec_data_tricky(TOP + 2, 2)),
        # 結果を SECONDに移動
        c.clear_pos(SECOND + 2),
        c.move_data(TOP + 2, SECOND + 2),
        c.move_data(TOP + 1, SECOND + 1)
    )


def _sub_abs() -> str:
    "3byte固定小数点の絶対値の減算"
    # どちらかが0になるまでdecする. 残ったほうが答え(符号も含め)
    return c.block_of(
        # 整数部を片方が0になるまで両方をデクリメント
        _dec_both_abs_int(),
        # SECOND+1が0以外なら、TOP/SECONDをひっくり返す
        _if_nz_int_swap(),
        c.if_nz_tricky(
            TOP + 1, ELEMENT_SIZE, ELEMENT_SIZE,
            then_statement=_top_minus_second(),
            else_statement=c.block_of(
                # TOP+1もSECOND+1も0の場合
                _dec_both_abs_decimal(),
                _if_top_decimal_is_nz_then_override()
            ))
    )


def add_decimal() -> str:
    # 符号が同じなら、絶対値の加算
    # 符号が異なるなら、絶対値の減算
    return c.block_of(
        c.for_safe(SECOND + 3, SECOND, c.inc_pos(TOP)),
        c.for_safe(TOP + 3, SECOND, c.dec_pos(TOP)),
        c.inc_pos(SECOND),
        c.if_nz_then(TOP, c.dec_pos(SECOND) + _sub_abs()),
        c.if_nz_then(SECOND, _add_abs()),
        drop()
    )


def sub_decimal() -> str:
    # 符号を反転して加算(A-B => A+(-B))
    return c.block_of(
        c.inc_pos(NOW),
        c.if_one_then(TOP + 3, c.dec_pos(NOW)),
        c.if_one_then(NOW, c.inc_pos(TOP + 3)),
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
    IDX_A1 = SECOND + 1
    IDX_A2 = SECOND + 2
    IDX_B1 = TOP + 1
    IDX_B2 = TOP + 2
    IDX_R1 = NOW + 1
    IDX_R2 = NOW + 2
    IDX_R3 = NOW + 3

    # 繰り上がり処理の関係で、上の桁から計算する
    return c.block_of(
        c.multi_data_tricky(IDX_A1, IDX_B1, IDX_R1, 1),  # AxC (1byte 分)
        c.multi_data_tricky(IDX_A1, IDX_B2, IDX_R2, 2),  # AxD (繰り上げ含め2byte)
        c.multi_data_tricky(IDX_A2, IDX_B1, IDX_R2, 2),  # BxC (繰り上げ含め2byte)
        c.multi_data_tricky(IDX_A2, IDX_B2, IDX_R3, 3),  # BxD (繰り上げ含め3byte)
        c.clear_pos(IDX_R3),  # R3 は繰り上げ分のみが必要なのでクリア
    )


def _xor_sign() -> str:
    # 符号は同じなら＋、異なるならマイナス
    IDX_AS = SECOND + 3
    IDX_BS = TOP + 3
    IDX_RS = NOW + 3
    return c.block_of(
        c.for_loop(IDX_AS, c.inc_pos(IDX_RS + 1)),
        c.for_loop(IDX_BS, c.dec_pos(IDX_RS + 1)),
        c.if_nz_then(IDX_RS + 1, c.inc_pos(IDX_RS))
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
