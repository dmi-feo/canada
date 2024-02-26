import pytest


async def test_create_and_delete_workbook(wb_client):
    wb_title = "my_super_title_for_super_workbook"
    async with wb_client.workbook_ctx(title=wb_title) as wb_id:
        workbook = await wb_client.get_workbook(wb_id)
        assert workbook["title"] == wb_title

    with pytest.raises(Exception):  # FIXME: normal exceptions
        await wb_client.get_workbook(wb_id)
