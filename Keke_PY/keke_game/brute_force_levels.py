import multiprocessing
import time
from concurrent.futures import Executor
from typing import Tuple, Union, List, Dict, Iterable

from Keke_PY.keke_game.keke import make_level, parse_map, GameState
from Keke_PY.keke_game.gui import play_level, inputs_from_keyboard, yield_solution_delayed
from Keke_PY.keke_game.simulation import load_level_set
from Keke_PY.search_agents.BFS import BFS


max_forward_model_calls: int = 2000 * 200

def brute_force_level(
    level_and_solution: Tuple[str, str]
) -> Tuple[str, str, int]:
    start_state: GameState = make_level(parse_map(level_and_solution[0]))
    agent: BFS = BFS()
    solution: Tuple[Union[List[str], None], int] = agent.search(
        start_state,
        max_forward_model_calls,
        None,
        False
    )
    res: str = '----' if solution[0] is None else ''.join(action[0] for action in solution[0])
    print(level_and_solution[0].replace('\\','\\\\').replace('\n', '\\n'), level_and_solution[1], res, solution[1])
    return level_and_solution[0], res, solution[1]


def measure_time() -> Iterable[None]:
    start = time.time()
    yield None
    end = time.time()
    print("The time of execution is:", (end - start), "s")

if __name__ == "__main__":
    for _ in measure_time():
        if False:
            test: str = "__________\n_.Rrbll.f_\n_L18.lll._\n_.5..ll.r_\n_..r.ll.1_\n_..r.ll.l_\n_.F..ll.B_\n_B19.ll.1_\n_r3r....2_\n__________ ddddlruuldrdlulluuddrrurrrruru LDURRRRR 502"
            level, prev_solution, new_solution, count = test.split(' ')
            yield_solution_delayed(prev_solution)
            play_level(level, yield_solution_delayed(prev_solution, 1.0))
            play_level(level, yield_solution_delayed(new_solution, 1.0))
            play_level(level, inputs_from_keyboard())
        else:
            levels_with_solutions: List[Tuple[str, str]] = [
                *[(level["ascii"], level["solution"]) for level in
                  load_level_set("./json_levels/train_LEVELS.json")["levels"]],
                *[(level["ascii"], level["solution"]) for level in
                  load_level_set("./json_levels/test_LEVELS.json")["levels"]],
            ]
            executor: Executor = multiprocessing.Pool(20)
            simulation_results: List[Tuple[str, str, int]] = list(executor.map(
                brute_force_level, levels_with_solutions
            ))









"""

___________\n_rg9SkofVr_\n_GF.6WOV0A_\n_Fw0.3o6AB_\n_A5W..5A2l_\n_.WO5KlF.1_\n_441934sR2_\n_vF38vVb.k_\n_W4bAS.K1K_\n_kO9.W..21_\n_0Ba4o3.L2_\n_w9G.SG99v_\n_g9Br5Kkbk_\n_.l7RRG6r3_\n_LFffV..Gv_\n_ga8.ro1wr_\n_VWV7R..3._\n___________ uuuuuuuuuuuddddddddl R 4
__________\n_........_\n_....V12._\n_........_\n_...v...._\n_F.v.v..._\n_1..v...._\n_3......._\n_....f..._\n__________ ddr DDD 24
__________\n_B12.F13._\n_........_\n_...sss.._\n_.b.sfs.._\n_...s...._\n_...s...._\n_........_\n_........_\n__________ dddrrruuu RRR 29
__________\n_s..S..a._\n_k.o....l_\n_.g....b._\n_L.g..b.w_\n_g.s..fs._\n_....B..l_\n_b...1r.._\n_G13.2b.._\n__________ uu UU 5
________\n_rrrrrr_\n_rrrrrr_\n_rrbrrr_\n_rr.rRr_\n_r..B12_\n_r.3.6._\n________ DDLDRRLLL DDLDRRLLL 20
____________\n_v......V12_\n_...f.....F_\n_.R.....b.1_\n_B12......3_\n_...S.S14.._\n____________ LLLLU DRRR 79
__________\n_b....Vwv_\n_.....1ww_\n_.....3.._\n_........_\n_........_\n_.....BW._\n_.....11._\n_.....26._\n__________ dddddddrrrrrr DDDDDDDRRRRRU 161
____________\n_B12......S_\n_Br.......1_\n_R..f.....F_\n_.........1_\n_G1.......3_\n_1.....s.f._\n_.0.3.sbs.F_\n_g.....s..g_\n_gg..13..gg_\n_ggg....ggg_\n____________ L U 1
____________\n_G13wwwwK14_\n_w.o.okofow_\n_wo.o.o.o.w_\n_wko.o.o.ow_\n_wggggggggw_\n_w.o.o.o.ow_\n_wo.o.o.okw_\n_w.o.o.o.ow_\n_wo.obo.o.w_\n_K17wwwwB12_\n____________ uuuu UUUU 91
__________\n_S13....._\n_.......f_\n_...r...3_\n_........_\n_........_\n_F14..R12_\n_........_\n_......s._\n__________ rddddrrd DDDDDRRR 144
__________\n_glF13S12_\n_gksgggVV_\n_ggrrrrV2_\n_vggkgkVr_\n_vvgvvvVr_\n_vvvvvlVl_\n_vvvvvlVl_\n_vvvvl.fl_\n__________ rrrdddddrd DDDDDDRRRR 110
__________\n_f.k.k.kk_\n_.B12F13._\n_k......k_\n_...b...._\n_k......k_\n_........_\n_k......k_\n_.K14K17._\n__________ llluuu LLULUU 1171
__________\n_.Rrbll.f_\n_L18.lll._\n_.5..ll.r_\n_..r.ll.1_\n_..r.ll.l_\n_.F..ll.B_\n_B19.ll.1_\n_r3r....2_\n__________ ddddlruuldrdlulluuddrrurrrruru LDURRRRR 502
__________\n_bB1...2._\n_..fR1SF._\n_1...31s._\n_3.r..2.1_\n__________ RUULLLDURRRDLRLD URULULLURL 911
__________\n_........_\n_...bV12._\n_........_\n_........_\n_.B13...._\n_........_\n_........_\n_...vv..._\n__________ rururuululllu UURUUULLU 1501
_________\n_.....B8_\n_......._\n_...R..._\n_..o1..._\n_......._\n_....B.._\n_......._\n_....rs._\n_..1SF.._\n_fB31s.._\n_F112o.._\n_......._\n_________ URULLULLLDDD DLUURRD 941
________\n_......_\n_......_\n_......_\n_......_\n_......_\n_......_\n_..B..._\n_..1..._\n_..2F13_\n_..b..._\n_......_\n_......_\n_f.F15._\n_......_\n_......_\n________ DDDLL DDDLL 154
__________\n_A.2...bg_\n_1.G.3.a._\n_wwg1W16._\n_..12B12b_\n_........_\n_........_\n_........_\n_........_\n__________ druddddllllulu DLUDRRU 1153
______\n_K.2._\n_kSF._\n_bB1._\n_..fR_\n_1..._\n_3.r._\n_251O_\n_s.31_\n_o..2_\n______ RRUUULUULURL RRUUULUULURL 1812
__________\n_...V13.._\n_v......._\n_........_\n_......b._\n_....B12._\n_........_\n_..V15..._\n_........_\n__________ ullllluuldrdddrdduuuull RDLLDDDLLLUU 3181
__________\n_b..lsllf_\n_...lslll_\n_.S.lslll_\n_L18lslll_\n_.6.ls..._\n_F......._\n_1......._\n_3.B12..._\n__________ rrdduullrrdddurllrrrrrruu DDRDRDLRR 1244
____________\n_F13wwwwK14_\n_w.o.okofow_\n_wo.o.o.o.w_\n_wko.o.o.ow_\n_wo.o.o.o.w_\n_w.o.o.o.ow_\n_wo.o.o.okw_\n_w.o.o.o.ow_\n_wo.obo.o.w_\n_K17wwwwB12_\n____________ uuldrrssruuurruluu UUUUUUURRR 2249

"""