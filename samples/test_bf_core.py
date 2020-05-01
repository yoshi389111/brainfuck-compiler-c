# bfコマンドマクロの基本命令のテスト

import unittest
import bf_core as c
from bf_sim import BfSim


class TestBfCore(unittest.TestCase):

    def test_move_data_1(self):
        source = c.move_data(1, 2)
        sim = BfSim(source)
        sim.memory[1] = 3
        sim.run(10000)
        self.assertEqual(sim.memory[1], 0)
        self.assertEqual(sim.memory[2], 3)

    def test_move_data_2(self):
        source = c.move_data(1, 2)
        sim = BfSim(source)
        sim.memory[1] = 3
        sim.memory[2] = 4
        sim.run(10000)
        self.assertEqual(sim.memory[1], 0)
        self.assertEqual(sim.memory[2], 7)

    def test_override_data_1(self):
        source = c.override_data(1, 2)
        sim = BfSim(source)
        sim.memory[1] = 3
        sim.memory[2] = 4
        sim.run(10000)
        self.assertEqual(sim.memory[1], 0)
        self.assertEqual(sim.memory[2], 3)

    def test_copy_data_1(self):
        source = c.copy_data(1, 2, 3)
        sim = BfSim(source)
        sim.memory[1] = 3
        sim.memory[2] = 4
        sim.run(10000)
        self.assertEqual(sim.memory[1], 3)
        self.assertEqual(sim.memory[2], 3)

    def test_swap_data_1(self):
        source = c.swap_data(1, 2, 3)
        sim = BfSim(source)
        sim.memory[1] = 3
        sim.memory[2] = 4
        sim.run(10000)
        self.assertEqual(sim.memory[1], 4)
        self.assertEqual(sim.memory[2], 3)

    def test_init_value_1(self):
        source = c.init_value(1, 5)
        sim = BfSim(source)
        sim.run(10000)
        self.assertEqual(sim.memory[1], 5)

    def test_init_value_2(self):
        source = c.init_value(1, 120)
        sim = BfSim(source)
        sim.run(10000)
        self.assertEqual(sim.memory[1], 120)

    def test_init_value_3(self):
        source = c.init_value(1, 255)
        sim = BfSim(source)
        sim.run(10000)
        self.assertEqual(sim.memory[1], 255)

    def test_if_nz_then_1(self):
        source = c.if_nz_then(1, c.inc_pos(3))
        sim = BfSim(source)
        sim.memory[1] = 3
        sim.run(10000)
        self.assertEqual(sim.memory[1], 0)
        self.assertEqual(sim.memory[3], 1)

    def test_if_nz_then_2(self):
        source = c.if_nz_then(1, c.inc_pos(3))
        sim = BfSim(source)
        sim.memory[1] = 0
        sim.run(10000)
        self.assertEqual(sim.memory[1], 0)
        self.assertEqual(sim.memory[3], 0)

    def test_if_one_then_1(self):
        source = c.if_one_then(1, c.inc_pos(3))
        sim = BfSim(source)
        sim.memory[1] = 1
        sim.run(10000)
        self.assertEqual(sim.memory[1], 0)
        self.assertEqual(sim.memory[3], 1)

    def test_if_one_then_2(self):
        source = c.if_one_then(1, c.inc_pos(3))
        sim = BfSim(source)
        sim.memory[1] = 0
        sim.run(10000)
        self.assertEqual(sim.memory[1], 0)
        self.assertEqual(sim.memory[3], 0)

    def test_if_nz_tricky_1(self):
        source = c.if_nz_tricky(1, 1, 1, c.inc_pos(5), c.inc_pos(6))
        sim = BfSim(source)
        sim.memory[1] = 3
        sim.run(10000)
        self.assertEqual(sim.memory[1], 3)
        self.assertEqual(sim.memory[5], 1)
        self.assertEqual(sim.memory[6], 0)

    def test_if_nz_tricky_2(self):
        source = c.if_nz_tricky(1, 1, 1, c.inc_pos(5), c.inc_pos(6))
        sim = BfSim(source)
        sim.memory[1] = 0
        sim.run(10000)
        self.assertEqual(sim.memory[1], 0)
        self.assertEqual(sim.memory[5], 0)
        self.assertEqual(sim.memory[6], 1)

    def test_if_z_tricky_1(self):
        source = c.if_z_tricky(1, 1, 1, c.inc_pos(5), c.inc_pos(6))
        sim = BfSim(source)
        sim.memory[1] = 3
        sim.run(10000)
        self.assertEqual(sim.memory[1], 3)
        self.assertEqual(sim.memory[5], 0)
        self.assertEqual(sim.memory[6], 1)

    def test_if_z_tricky_2(self):
        source = c.if_z_tricky(1, 1, 1, c.inc_pos(5), c.inc_pos(6))
        sim = BfSim(source)
        sim.memory[1] = 0
        sim.run(10000)
        self.assertEqual(sim.memory[1], 0)
        self.assertEqual(sim.memory[5], 1)
        self.assertEqual(sim.memory[6], 0)

    def test_inc_data_tricky_1(self):
        source = c.inc_data_tricky(3, 1)
        sim = BfSim(source)
        sim.memory[3] = 0
        sim.run(10000)
        self.assertEqual(sim.memory[1], 0)
        self.assertEqual(sim.memory[2], 0)
        self.assertEqual(sim.memory[3], 1)

    def test_inc_data_tricky_2(self):
        source = c.inc_data_tricky(3, 1)
        sim = BfSim(source)
        sim.memory[3] = 10
        sim.run(10000)
        self.assertEqual(sim.memory[1], 0)
        self.assertEqual(sim.memory[2], 0)
        self.assertEqual(sim.memory[3], 11)

    def test_inc_data_tricky_3(self):
        source = c.inc_data_tricky(3, 1)
        sim = BfSim(source)
        sim.memory[3] = 255
        sim.run(10000)
        self.assertEqual(sim.memory[1], 0)
        self.assertEqual(sim.memory[2], 0)
        self.assertEqual(sim.memory[3], 0)

    def test_inc_data_tricky_4(self):
        source = c.inc_data_tricky(3, 2)
        sim = BfSim(source)
        sim.memory[3] = 255
        sim.run(10000)
        self.assertEqual(sim.memory[1], 0)
        self.assertEqual(sim.memory[2], 1)
        self.assertEqual(sim.memory[3], 0)

    def test_inc_data_tricky_5(self):
        source = c.inc_data_tricky(3, 3)
        sim = BfSim(source)
        sim.memory[2] = 255
        sim.memory[3] = 255
        sim.run(10000)
        self.assertEqual(sim.memory[1], 1)
        self.assertEqual(sim.memory[2], 0)
        self.assertEqual(sim.memory[3], 0)

    def test_dec_data_tricky_1(self):
        source = c.dec_data_tricky(3, 1)
        sim = BfSim(source)
        sim.memory[3] = 0
        sim.run(10000)
        self.assertEqual(sim.memory[1], 0)
        self.assertEqual(sim.memory[2], 0)
        self.assertEqual(sim.memory[3], 255)

    def test_dec_data_tricky_2(self):
        source = c.dec_data_tricky(3, 1)
        sim = BfSim(source)
        sim.memory[3] = 10
        sim.run(10000)
        self.assertEqual(sim.memory[1], 0)
        self.assertEqual(sim.memory[2], 0)
        self.assertEqual(sim.memory[3], 9)

    def test_dec_data_tricky_3(self):
        source = c.dec_data_tricky(3, 1)
        sim = BfSim(source)
        sim.memory[2] = 1
        sim.memory[3] = 0
        sim.run(10000)
        self.assertEqual(sim.memory[1], 0)
        self.assertEqual(sim.memory[2], 1)
        self.assertEqual(sim.memory[3], 255)

    def test_dec_data_tricky_4(self):
        source = c.dec_data_tricky(3, 2)
        sim = BfSim(source)
        sim.memory[2] = 1
        sim.memory[3] = 0
        sim.run(10000)
        self.assertEqual(sim.memory[1], 0)
        self.assertEqual(sim.memory[2], 0)
        self.assertEqual(sim.memory[3], 255)

    def test_dec_data_tricky_5(self):
        source = c.dec_data_tricky(3, 3)
        sim = BfSim(source)
        sim.memory[1] = 1
        sim.memory[2] = 0
        sim.memory[3] = 0
        sim.run(10000)
        self.assertEqual(sim.memory[1], 0)
        self.assertEqual(sim.memory[2], 255)
        self.assertEqual(sim.memory[3], 255)

    def test_add_data_tricky_1(self):
        source = c.add_data_tricky(source=2, pos=4, work=7, digit=2)
        sim = BfSim(source)
        sim.memory[2] = 129
        sim.memory[3] = 5
        sim.memory[4] = 129
        sim.run(10000)
        self.assertEqual(sim.memory[2], 129)
        self.assertEqual(sim.memory[3], 6)
        self.assertEqual(sim.memory[4], 2)

    def test_multi_data_tricky_1(self):
        source = c.multi_data_tricky(
            source1=1, source2=3, pos=5, digit=2)
        sim = BfSim(source)
        sim.memory[1] = 100
        sim.memory[3] = 100
        sim.memory[4] = 0
        sim.memory[5] = 0
        while not sim.is_stopped():
            sim.run(10000)
        self.assertEqual(sim.memory[4], 39)
        self.assertEqual(sim.memory[5], 16)


if __name__ == '__main__':
    unittest.main()
