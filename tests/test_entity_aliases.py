import pytest


@pytest.mark.skip("check that `bar` not found when exceptions are shiny enough")
async def test_get_by_alias(wb_client):
    await wb_client.get_collection("foo")


@pytest.mark.skip("check that `bar` not found when exceptions are shiny enough")
async def test_create_entry_in_wb_with_alias(wb_client):
    async with wb_client.entry_ctx(
            "some_workbook",
            workbook_id="foo",
            scope="scope", type="type", data={}
    ):
        pass
