import os
from wine_analysis_hplc_uv.my_sheetsinterface import gspread_methods as g_methods


def test_key():
    assert os.environ.get("TEST_SAMPLETRACKER_KEY")


def test_sample_tracker_sh(sheet):
    assert sheet


def test_service_account(service_account):
    assert service_account


def test_sheet_list(sample_tracker_sh):
    sheet_list = g_methods.get_sheet_list(sample_tracker_sh)
    assert sheet_list


def test_sheet_title_in_sheet_list(sheet_title: str, sheet_list: list):
    assert sheet_title in sheet_list
