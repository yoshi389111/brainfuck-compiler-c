# マンデルブロ集合

import bf_core as c
import bf_stack as s


# X軸の範囲
(X_BEGIN, X_END) = (-2.0, 1.0)
# Y軸の範囲
(Y_BEGIN, Y_END) = (-0.9375, 0.9375)

# 繰り返し回数
C_MAX = 26
# 発散するしきい値(2.0 の2乗値)
THRESHOLD2 = 4


def mandelbrot(columns: int, rows: int) -> str:
    # X軸の加算値
    x_step = (X_END - X_BEGIN) / (columns - 1)
    # Y軸の加算値
    y_step = (Y_END - Y_BEGIN) / (rows - 1)

    return c.program_of(

        # #0: y0 = y_begin
        s.push_decimal(Y_BEGIN),

        # #1: y = rows
        s.push_byte(rows),
        s.loop_of(  # for(y)

            # #2: x0 = x_begin
            s.push_decimal(X_BEGIN),

            # #3: x = columns
            s.push_byte(columns),
            s.loop_of(  # for(x)

                s.dup(1),  # #4: cx = x0
                s.dup(4),  # #5: cy = y0
                s.push_decimal(0),  # #6: zx = 0
                s.push_decimal(0),  # #7: zy = 0
                s.push_byte(ord(" ")),  # #8: ch = ' '
                s.push_byte(ord("A") - 1),  # #9: count = 'A'-1

                s.push_byte(C_MAX),  # #10: c = 26
                s.loop_of(  # for(c)

                    # #11: zx2 = zx * zx
                    s.dup(4),
                    s.dup(0),
                    s.multi_decimal(),

                    # #12: zy2 = zy * zy
                    s.dup(4),
                    s.dup(0),
                    s.multi_decimal(),

                    # #13: size2 = zx2 + zy2
                    s.dup(1),
                    s.dup(1),
                    s.add_decimal(),

                    # #14: THRESHOLD2
                    s.push_decimal(THRESHOLD2),
                    # if size2 > 4.0
                    s.if_gt_decimal(
                        then_statement=c.block_of(
                            # 発散

                            # ch = count
                            s.dup(5),  # #15
                            s.override(7),

                            # for_c break
                            s.loop_last(4)
                        ),
                        else_statement=c.block_of(
                            # #15: zx_next = zx2 - zy2 + cx
                            s.dup(3),
                            s.dup(3),
                            s.sub_decimal(),
                            s.dup(11),
                            s.add_decimal(),

                            # #16: zy_next = zx * zy * 2 + cy
                            s.dup(9),
                            s.dup(9),
                            s.multi_decimal(),
                            s.dup(0),
                            s.add_decimal(),
                            s.dup(11),
                            s.add_decimal(),

                            # #17: if zx_next == zx && zy_next == zy
                            s.dup(1),  # zx_next
                            s.dup(11),  # zx
                            s.sub_decimal(),
                            # #17: 0(zx_next == zx) or 1(zx_next != zx)
                            s.if_nz_decimal(
                                s.push_byte(1) + s.swap(1),
                                s.push_byte(0) + s.swap(1)),
                            s.dup(1),  # zy_next
                            s.dup(11),  # zy
                            s.sub_decimal(),
                            # #18: 0(zx_next == zx) or 1(zx_next != zx)
                            s.if_nz_decimal(
                                s.push_byte(1) + s.swap(1),
                                s.push_byte(0) + s.swap(1)),
                            # #17: 0(zx_next == zx && zy_next == zy) or other
                            s.add_byte(),
                            s.if_z(
                                then_statement=c.block_of(
                                    # 収束
                                    s.swap(1),
                                    s.drop(),  # drop zy_next
                                    s.swap(1),
                                    s.drop(),  # drop zx_next
                                    s.loop_last(5)  # last c
                                ),
                                else_statement=c.block_of(
                                    # zx = zx_next
                                    s.swap(1),
                                    s.override(10),

                                    # zy = zy_next
                                    s.swap(1),
                                    s.override(10),

                                    # count += 1
                                    s.dup(6),
                                    s.push_byte(1),
                                    s.add_byte(),
                                    s.override(7)
                                )
                            )
                        )
                    ),
                    s.drop() * 2  # drop zy2, zx2
                ),
                s.drop(),  # drop count
                s.put_char(),  # putchar(ch)
                s.drop() * 4,  # drop zy, zx, cy, cx

                # #4: x0 += x_step
                s.dup(1),
                s.push_decimal(x_step),
                s.add_decimal(),
                s.override(2)
            ),
            # drop x0
            s.drop(),

            # #2: putchar("\n")
            s.push_byte(ord("\n")),
            s.put_char(),

            # #2: y0 += y_step
            s.dup(1),
            s.push_decimal(y_step),
            s.add_decimal(),
            s.override(2)
        )
    )


if __name__ == '__main__':
    program = mandelbrot(128, 40)
    print(program)
