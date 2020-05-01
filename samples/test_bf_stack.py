import unittest
import io
import bf_core as c
import bf_stack as s
from bf_sim import BfSim


class TestMandelbrot(unittest.TestCase):

    def getFloat(self, sim: BfSim, pos: int) -> float:
        dmy = sim.memory[pos + s.IDX_DMY]
        if (dmy != 0):
            raise ValueError(f"dmy={dmy}")
        value1 = sim.memory[pos + s.IDX_INT]
        value2 = sim.memory[pos + s.IDX_DEC]
        abs_value = value1 + value2 / 256.0
        sign = sim.memory[pos + s.IDX_SGN]
        if (sign == 0):
            return abs_value
        elif (sign == 1):
            return -abs_value
        else:
            raise ValueError(f"sign={sign}")

    def test_push_decimal_1(self):
        source = s.push_decimal(3.0)
        sim = BfSim(source)
        while not sim.is_stopped():
            sim.run(10000)
        self.assertAlmostEqual(self.getFloat(sim, 0), 3.0)

    def test_push_decimal_2(self):
        source = s.push_decimal(-3.5)
        sim = BfSim(source)
        while not sim.is_stopped():
            sim.run(10000)
        self.assertAlmostEqual(self.getFloat(sim, 0), -3.5)

    def test_add_decimal_1(self):
        source = c.block_of(
            s.push_decimal(3.5),
            s.push_decimal(4.25),
            s.add_decimal()
        )
        sim = BfSim(source)
        while not sim.is_stopped():
            sim.run(10000)
        self.assertAlmostEqual(self.getFloat(sim, 0), 7.75)
        self.assertAlmostEqual(self.getFloat(sim, 4), 0)
        self.assertAlmostEqual(self.getFloat(sim, 8), 0)

    def test_add_decimal_2(self):
        source = c.block_of(
            s.push_decimal(-3.5),
            s.push_decimal(-4.25),
            s.add_decimal()
        )
        sim = BfSim(source)
        while not sim.is_stopped():
            sim.run(10000)
        self.assertAlmostEqual(self.getFloat(sim, 0), -7.75)
        self.assertAlmostEqual(self.getFloat(sim, 4), 0)
        self.assertAlmostEqual(self.getFloat(sim, 8), 0)

    def test_add_decimal_3(self):
        source = c.block_of(
            s.push_decimal(4.5),
            s.push_decimal(-4.25),
            s.add_decimal()
        )
        sim = BfSim(source)
        while not sim.is_stopped():
            sim.run(10000)
        self.assertAlmostEqual(self.getFloat(sim, 0), 0.25)
        self.assertAlmostEqual(self.getFloat(sim, 4), 0)
        self.assertAlmostEqual(self.getFloat(sim, 8), 0)

    def test_dec_both_abs_int_1(self):
        source = c.block_of(
            s.push_decimal(4.5),
            s.push_decimal(3.25),
            s._dec_both_abs_int()
        )
        sim = BfSim(source)
        while not sim.is_stopped():
            sim.run(10000)
        self.assertAlmostEqual(self.getFloat(sim, 0), 1.5)
        self.assertAlmostEqual(self.getFloat(sim, 4), 0.25)

    def test_dec_both_abs_int_2(self):
        source = c.block_of(
            s.push_decimal(3.5),
            s.push_decimal(3.25),
            s._dec_both_abs_int()
        )
        sim = BfSim(source)
        while not sim.is_stopped():
            sim.run(10000)
        self.assertAlmostEqual(self.getFloat(sim, 0), 0.5)
        self.assertAlmostEqual(self.getFloat(sim, 4), 0.25)

    def test_dec_both_abs_int_3(self):
        source = c.block_of(
            s.push_decimal(3.5),
            s.push_decimal(4.25),
            s._dec_both_abs_int()
        )
        sim = BfSim(source)
        while not sim.is_stopped():
            sim.run(10000)
        self.assertAlmostEqual(self.getFloat(sim, 0), 0.5)
        self.assertAlmostEqual(self.getFloat(sim, 4), 1.25)

    def test_dec_both_abs_decimal_1(self):
        source = c.block_of(
            s.push_decimal(0.5),
            s.push_decimal(0.25),
            s._dec_both_abs_decimal()
        )
        sim = BfSim(source)
        while not sim.is_stopped():
            sim.run(10000)
        self.assertAlmostEqual(self.getFloat(sim, 0), 0.25)
        self.assertAlmostEqual(self.getFloat(sim, 4), 0.0)

    def test_dec_both_abs_decimal_2(self):
        source = c.block_of(
            s.push_decimal(0.25),
            s.push_decimal(0.5),
            s._dec_both_abs_decimal()
        )
        sim = BfSim(source)
        while not sim.is_stopped():
            sim.run(10000)
        self.assertAlmostEqual(self.getFloat(sim, 0), 0.0)
        self.assertAlmostEqual(self.getFloat(sim, 4), 0.25)

    def test_dec_both_abs_decimal_3(self):
        source = c.block_of(
            s.push_decimal(0.5),
            s.push_decimal(0.5),
            s._dec_both_abs_decimal()
        )
        sim = BfSim(source)
        while not sim.is_stopped():
            sim.run(10000)
        self.assertAlmostEqual(self.getFloat(sim, 0), 0.0)
        self.assertAlmostEqual(self.getFloat(sim, 4), 0.0)

    def test_if_nz_int_swap_1(self):
        source = c.block_of(
            s.push_decimal(-3.5),
            s.push_decimal(0.25),
            s._if_nz_int_swap()
        )
        sim = BfSim(source)
        while not sim.is_stopped():
            sim.run(10000)
        self.assertAlmostEqual(self.getFloat(sim, 0), 0.25)
        self.assertAlmostEqual(self.getFloat(sim, 4), -3.5)

    def test_if_nz_int_swap_2(self):
        source = c.block_of(
            s.push_decimal(-0.5),
            s.push_decimal(2.25),
            s._if_nz_int_swap()
        )
        sim = BfSim(source)
        while not sim.is_stopped():
            sim.run(10000)
        self.assertAlmostEqual(self.getFloat(sim, 0), -0.5)
        self.assertAlmostEqual(self.getFloat(sim, 4), 2.25)

    def test_if_top_decimal_is_nz_then_override_1(self):
        source = c.block_of(
            s.push_decimal(0.0),
            s.push_decimal(-0.25),
            s._if_top_decimal_is_nz_then_override()
        )
        sim = BfSim(source)
        while not sim.is_stopped():
            sim.run(10000)
        self.assertAlmostEqual(self.getFloat(sim, 0), -0.25)
        self.assertAlmostEqual(self.getFloat(sim, 4), 0.0)

    def test_if_top_decimal_is_nz_then_override_2(self):
        source = c.block_of(
            s.push_decimal(0.5),
            s.push_decimal(0.0),
            s._if_top_decimal_is_nz_then_override()
        )
        sim = BfSim(source)
        while not sim.is_stopped():
            sim.run(10000)
        self.assertAlmostEqual(self.getFloat(sim, 0), 0.5)
        self.assertAlmostEqual(self.getFloat(sim, 4), 0.0)

    def test_top_minus_second_1(self):
        source = c.block_of(
            s.push_decimal(-0.5),
            s.push_decimal(2.25),
            s._top_minus_second()
        )
        sim = BfSim(source)
        while not sim.is_stopped():
            sim.run(10000)
        self.assertAlmostEqual(self.getFloat(sim, 0), 1.75)
        self.assertAlmostEqual(self.getFloat(sim, 4), 0.0)

    def test_add_decimal_4(self):
        source = c.block_of(
            s.push_decimal(3.25),
            s.push_decimal(-4.5),
            s.add_decimal()
        )
        sim = BfSim(source)
        while not sim.is_stopped():
            sim.run(10000)
        self.assertAlmostEqual(self.getFloat(sim, 0), -1.25)
        self.assertAlmostEqual(self.getFloat(sim, 4), 0.0)

    def test_add_decimal_5(self):
        source = c.block_of(
            s.push_decimal(4.5),
            s.push_decimal(-4.5),
            s.add_decimal()
        )
        sim = BfSim(source)
        while not sim.is_stopped():
            sim.run(10000)
        self.assertAlmostEqual(self.getFloat(sim, 0), 0.0)
        self.assertAlmostEqual(self.getFloat(sim, 4), 0.0)

    def test_add_decimal_6(self):
        source = c.block_of(
            s.push_decimal(-4.5),
            s.push_decimal(4.5),
            s.add_decimal()
        )
        sim = BfSim(source)
        while not sim.is_stopped():
            sim.run(10000)
        self.assertAlmostEqual(self.getFloat(sim, 0), 0.0)  # TODO -0.0
        self.assertAlmostEqual(self.getFloat(sim, 4), 0.0)

    def test_sub_decimal_1(self):
        source = c.block_of(
            s.push_decimal(-3.5),
            s.push_decimal(4.25),
            s.sub_decimal()
        )
        sim = BfSim(source)
        while not sim.is_stopped():
            sim.run(10000)
        self.assertAlmostEqual(self.getFloat(sim, 0), -7.75)

    def test_sub_decimal_2(self):
        source = c.block_of(
            s.push_decimal(3.5),
            s.push_decimal(-4.25),
            s.sub_decimal()
        )
        sim = BfSim(source)
        while not sim.is_stopped():
            sim.run(10000)
        self.assertAlmostEqual(self.getFloat(sim, 0), 7.75)

    def test_multi_decimal_abs_1(self):
        source = c.block_of(
            s.push_decimal(2.0),
            s.push_decimal(-4.25),
            s._multi_decimal_abs()
        )
        sim = BfSim(source)
        while not sim.is_stopped():
            sim.run(10000)
        self.assertAlmostEqual(self.getFloat(sim, 0), 2.0)
        self.assertAlmostEqual(self.getFloat(sim, 4), -4.25)
        self.assertAlmostEqual(self.getFloat(sim, 8), 8.5)

    def test_xor_sign_1(self):
        source = c.block_of(
            s.push_decimal(2.0),
            s.push_decimal(-4.25),
            s._xor_sign()
        )
        sim = BfSim(source)
        while not sim.is_stopped():
            sim.run(10000)
        self.assertEqual(sim.memory[8 + s.IDX_DMY], 0)
        self.assertEqual(sim.memory[8 + s.IDX_INT], 0)
        self.assertEqual(sim.memory[8 + s.IDX_DEC], 0)
        self.assertEqual(sim.memory[8 + s.IDX_SGN], 1)
        self.assertEqual(sim.memory[12], 0)

    def test_xor_sign_2(self):
        source = c.block_of(
            s.push_decimal(-2.0),
            s.push_decimal(4.25),
            s._xor_sign()
        )
        sim = BfSim(source)
        while not sim.is_stopped():
            sim.run(10000)
        self.assertEqual(sim.memory[8 + s.IDX_DMY], 0)
        self.assertEqual(sim.memory[8 + s.IDX_INT], 0)
        self.assertEqual(sim.memory[8 + s.IDX_DEC], 0)
        self.assertEqual(sim.memory[8 + s.IDX_SGN], 1)
        self.assertEqual(sim.memory[12], 0)

    def test_xor_sign_3(self):
        source = c.block_of(
            s.push_decimal(-2.0),
            s.push_decimal(-4.25),
            s._xor_sign()
        )
        sim = BfSim(source)
        while not sim.is_stopped():
            sim.run(10000)
        self.assertEqual(sim.memory[8 + s.IDX_DMY], 0)
        self.assertEqual(sim.memory[8 + s.IDX_INT], 0)
        self.assertEqual(sim.memory[8 + s.IDX_DEC], 0)
        self.assertEqual(sim.memory[8 + s.IDX_SGN], 0)
        self.assertEqual(sim.memory[12], 0)

    def test_xor_sign_4(self):
        source = c.block_of(
            s.push_decimal(2.0),
            s.push_decimal(4.25),
            s._xor_sign()
        )
        sim = BfSim(source)
        while not sim.is_stopped():
            sim.run(10000)
        self.assertEqual(sim.memory[8 + s.IDX_DMY], 0)
        self.assertEqual(sim.memory[8 + s.IDX_INT], 0)
        self.assertEqual(sim.memory[8 + s.IDX_DEC], 0)
        self.assertEqual(sim.memory[8 + s.IDX_SGN], 0)
        self.assertEqual(sim.memory[12], 0)

    def test_multi_decimal_1(self):
        source = c.block_of(
            s.push_decimal(2.0),
            s.push_decimal(-4.25),
            s.multi_decimal()
        )
        sim = BfSim(source)
        while not sim.is_stopped():
            sim.run(10000)
        self.assertAlmostEqual(self.getFloat(sim, 0), -8.5)
        self.assertAlmostEqual(self.getFloat(sim, 4), 0.0)
        self.assertAlmostEqual(self.getFloat(sim, 8), 0.0)

    def test_if_lt_decimal_1(self):
        source = c.block_of(
            s.push_decimal(2.0),
            s.push_decimal(4.25),
            s.if_lt_decimal(
                then_statement=s.push_byte(ord('L')) + s.put_char(),
                else_statement=s.push_byte(ord('G')) + s.put_char()
            )
        )
        out = io.StringIO()
        sim = BfSim(source, stdout=out)
        while not sim.is_stopped():
            sim.run(10000)
        self.assertEqual(out.getvalue(), "L")
        self.assertAlmostEqual(self.getFloat(sim, 0), 0.0)
        self.assertAlmostEqual(self.getFloat(sim, 4), 0.0)
        self.assertAlmostEqual(self.getFloat(sim, 8), 0.0)

    def test_if_lt_decimal_2(self):
        source = c.block_of(
            s.push_decimal(4.0),
            s.push_decimal(2.25),
            s.if_lt_decimal(
                then_statement=s.push_byte(ord('L')) + s.put_char(),
                else_statement=s.push_byte(ord('G')) + s.put_char()
            )
        )
        out = io.StringIO()
        sim = BfSim(source, stdout=out)
        while not sim.is_stopped():
            sim.run(10000)
        self.assertEqual(out.getvalue(), "G")
        self.assertAlmostEqual(self.getFloat(sim, 0), 0.0)
        self.assertAlmostEqual(self.getFloat(sim, 4), 0.0)
        self.assertAlmostEqual(self.getFloat(sim, 8), 0.0)

    def test_if_lt_decimal_3(self):
        source = c.block_of(
            s.push_decimal(-4.0),
            s.push_decimal(2.25),
            s.if_lt_decimal(
                then_statement=s.push_byte(ord('L')) + s.put_char(),
                else_statement=s.push_byte(ord('G')) + s.put_char()
            )
        )
        out = io.StringIO()
        sim = BfSim(source, stdout=out)
        while not sim.is_stopped():
            sim.run(10000)
        self.assertEqual(out.getvalue(), "L")
        self.assertAlmostEqual(self.getFloat(sim, 0), 0.0)
        self.assertAlmostEqual(self.getFloat(sim, 4), 0.0)
        self.assertAlmostEqual(self.getFloat(sim, 8), 0.0)

    def test_if_lt_decimal_4(self):
        source = c.block_of(
            s.push_decimal(2.0),
            s.push_decimal(-4.25),
            s.if_lt_decimal(
                then_statement=s.push_byte(ord('L')) + s.put_char(),
                else_statement=s.push_byte(ord('G')) + s.put_char()
            )
        )
        out = io.StringIO()
        sim = BfSim(source, stdout=out)
        while not sim.is_stopped():
            sim.run(10000)
        self.assertEqual(out.getvalue(), "G")
        self.assertAlmostEqual(self.getFloat(sim, 0), 0.0)
        self.assertAlmostEqual(self.getFloat(sim, 4), 0.0)
        self.assertAlmostEqual(self.getFloat(sim, 8), 0.0)

    def test_if_negative_decimal_1(self):
        source = c.block_of(
            s.push_decimal(4.25),
            s.if_negative_decimal(
                then_statement=s.push_byte(ord('N')) + s.put_char(),
                else_statement=s.push_byte(ord('P')) + s.put_char()
            )
        )
        out = io.StringIO()
        sim = BfSim(source, stdout=out)
        while not sim.is_stopped():
            sim.run(10000)
        self.assertEqual(out.getvalue(), "P")
        self.assertAlmostEqual(self.getFloat(sim, 0), 0.0)
        self.assertAlmostEqual(self.getFloat(sim, 4), 0.0)

    def test_if_negative_decimal_2(self):
        source = c.block_of(
            s.push_decimal(-4.25),
            s.if_negative_decimal(
                then_statement=s.push_byte(ord('N')) + s.put_char(),
                else_statement=s.push_byte(ord('P')) + s.put_char()
            )
        )
        out = io.StringIO()
        sim = BfSim(source, stdout=out)
        while not sim.is_stopped():
            sim.run(10000)
        self.assertEqual(out.getvalue(), "N")
        self.assertAlmostEqual(self.getFloat(sim, 0), 0.0)
        self.assertAlmostEqual(self.getFloat(sim, 4), 0.0)

    def test_if_nz_decimal_1(self):
        source = c.block_of(
            s.push_decimal(1.0),
            s.if_nz_decimal(
                then_statement=s.push_byte(ord('N')) + s.put_char(),
                else_statement=s.push_byte(ord('Z')) + s.put_char()
            )
        )
        out = io.StringIO()
        sim = BfSim(source, stdout=out)
        while not sim.is_stopped():
            sim.run(10000)
        self.assertEqual(out.getvalue(), "N")
        self.assertAlmostEqual(self.getFloat(sim, 0), 0.0)
        self.assertAlmostEqual(self.getFloat(sim, 4), 0.0)

    def test_if_nz_decimal_2(self):
        source = c.block_of(
            s.push_decimal(0.5),
            s.if_nz_decimal(
                then_statement=s.push_byte(ord('N')) + s.put_char(),
                else_statement=s.push_byte(ord('Z')) + s.put_char()
            )
        )
        out = io.StringIO()
        sim = BfSim(source, stdout=out)
        while not sim.is_stopped():
            sim.run(10000)
        self.assertEqual(out.getvalue(), "N")
        self.assertAlmostEqual(self.getFloat(sim, 0), 0.0)
        self.assertAlmostEqual(self.getFloat(sim, 4), 0.0)

    def test_if_nz_decimal_3(self):
        source = c.block_of(
            s.push_decimal(0.0),
            s.if_nz_decimal(
                then_statement=s.push_byte(ord('N')) + s.put_char(),
                else_statement=s.push_byte(ord('Z')) + s.put_char()
            )
        )
        out = io.StringIO()
        sim = BfSim(source, stdout=out)
        while not sim.is_stopped():
            sim.run(10000)
        self.assertEqual(out.getvalue(), "Z")
        self.assertAlmostEqual(self.getFloat(sim, 0), 0.0)
        self.assertAlmostEqual(self.getFloat(sim, 4), 0.0)


if __name__ == '__main__':
    unittest.main()
