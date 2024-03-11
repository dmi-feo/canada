async def test_create_and_delete_entry(wb_client):
    entry_name, entry_scope, entry_type = "test_entry", "megachart", "sometype"
    entry_data = {"hello": "there"}
    async with wb_client.workbook_ctx() as wb_id:
        async with wb_client.entry_ctx(
            name=entry_name,
            workbook_id=wb_id,
            scope=entry_scope,
            type=entry_type,
            data=entry_data,
        ) as entry_id:
            entry = await wb_client.get_entry(entry_id)

            assert entry["key"] == entry_name
            assert entry["scope"] == entry_scope
            assert entry["type"] == entry_type
            assert entry["data"] == entry_data


async def test_get_workbook_entries(wb_client):
    entries = [
        {
            "name": "entry_10",
            "scope": "scope_1",
            "type": "sometype",
            "data": {},
        },
        {
            "name": "entry_11",
            "scope": "scope_1",
            "type": "sometype",
            "data": {},
        },
        {
            "name": "entry_20",
            "scope": "scope_2",
            "type": "sometype",
            "data": {},
        },
    ]

    async with wb_client.workbook_ctx() as wb_id:
        async with (
            wb_client.entry_ctx(workbook_id=wb_id, **entries[0]) as eid0,
            wb_client.entry_ctx(workbook_id=wb_id, **entries[1]) as eid1,
            wb_client.entry_ctx(workbook_id=wb_id, **entries[2]) as eid2,
        ):
            wb_all_entries = await wb_client.get_workbook_entries(workbook_id=wb_id)
            assert len(wb_all_entries["entries"]) == len(entries)
            assert len(set(item["scope"] for item in wb_all_entries["entries"])) == 2

            wb_entries_scope_1 = await wb_client.get_workbook_entries(workbook_id=wb_id, scope="scope_1")
            assert len(wb_entries_scope_1["entries"]) == 2
            assert set(item["entryId"] for item in wb_entries_scope_1["entries"]) == {
                eid0,
                eid1,
            }

            wb_entries_scope_2 = await wb_client.get_workbook_entries(workbook_id=wb_id, scope="scope_2")
            assert len(wb_entries_scope_2["entries"]) == 1
            assert wb_entries_scope_2["entries"][0]["entryId"] == eid2
