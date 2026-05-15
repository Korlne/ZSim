# import pytest
# import pandas as pd
# from zsim.sim_progress.Buff import Buff
# from zsim.define import JUDGE_FILE_PATH, EXIST_FILE_PATH
#
# EXIST_FILE = pd.read_csv(EXIST_FILE_PATH, index_col="BuffName")
# JUDGE_FILE = pd.read_csv(JUDGE_FILE_PATH, index_col="BuffName")
#
#
# @pytest.fixture(
#     params=[
#         "NonExistentBuff",  # 仅测试非法输入
#     ]
# )
# def invalid_buff_index(request):
#     return request.param
#
#
# @pytest.fixture(
#     params=[
#         "Buff-武器-精1街头巨星-终结技增伤",  # 仅测试合法输入
#     ]
# )
# def valid_buff_index(request):
#     return request.param
#
#
# @pytest.fixture(
#     params=[
#         "Buff-武器-精1街头巨星-终结技增伤",  # 仅测试合法输入
#     ]
# )
# def complex_buff_index(request):
#     """待测试的复杂Buff名"""
#     return request.param
#
#
# @pytest.fixture
# def buff(valid_buff_index):
#     dict_1 = EXIST_FILE.loc[valid_buff_index].to_dict()
#     if "BuffName" not in dict_1:
#         dict_1["BuffName"] = valid_buff_index
#     dict_2 = JUDGE_FILE.loc[valid_buff_index].to_dict()
#     return Buff(dict_1, dict_2)
#
#
# class TestBuff:
#     def test_invalid_buff(self, invalid_buff_index):
#         """测试非法不存在的Buff名能否抛出异常"""
#         with pytest.raises(KeyError):
#             EXIST_FILE.loc[invalid_buff_index]
#
#     def test_valid_buff(self, buff, valid_buff_index):
#         """测试合法的Buff名能否让Buff类实例化成功"""
#         assert buff.ft.index == valid_buff_index
#
#     def test_xjudge_init(self, buff):
#         if buff.ft.simple_judge_logic:
#             assert buff.logic.xjudge is None
#         else:
#             assert buff.logic.xjudge is not None
#
#     def test_xjudge_judge(self, xjudge_buff, test_node):
#         pass
