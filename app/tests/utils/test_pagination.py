import pytest

from app.utils.pagination import get_skip_value, pagination


@pytest.mark.parametrize(
    "page, limit, expected_skip",
    [
        (1, 10, 0),
        (2, 10, 10),
        (3, 15, 30),
    ],
)
def test_get_skip_value(page, limit, expected_skip):
    assert get_skip_value(page, limit) == expected_skip


@pytest.mark.asyncio
async def test_pagination_from_total_items():
    paginate = await pagination(25, limit=10, page=2)

    assert paginate.total == 25
    assert paginate.per_page == 10
    assert paginate.current_page == 2
    assert paginate.last_page == 3


@pytest.mark.asyncio
async def test_pagination_raises_with_invalid_limit():
    with pytest.raises(ValueError):
        await pagination(25, limit=0, page=1)
