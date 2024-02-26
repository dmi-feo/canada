import pytest
import aiohttp

from .common import workbook


async def test_create_and_delete_workbook(client, wb_manager):
    wb_title = "my_super_title_for_super_workbook"
    async with workbook(client, title=wb_title) as wb_id:
        wb_obj = await wb_manager.get_workbook(wb_id)
        assert wb_obj.title == wb_title

    with pytest.raises(aiohttp.client_exceptions.ClientResponseError):  # FIXME: normal exceptions
        await wb_manager.get_workbook(wb_id)

