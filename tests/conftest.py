import pytest


@pytest.fixture(scope="function", autouse=True)
def shared_setup(fn_isolation):
    pass


@pytest.fixture
def agent(accounts):
    return accounts.at("0x3e40D73EB977Dc6a537aF587D48316feE66E9C8c", force=True)


@pytest.fixture
def lido(interface, agent):
    return interface.ERC20("0x5A98FcBEA516Cf06857215779Fd812CA3beF1B32", owner=agent)


@pytest.fixture
def whale(accounts):
    return accounts.at("0x2F0b23f53734252Bda2277357e97e1517d6B042A", force=True)


@pytest.fixture
def weth(interface, whale):
    return interface.ERC20("0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2", owner=whale)


@pytest.fixture
def uniswap(interface):
    return interface.UniswapRouter("0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D")


@pytest.fixture
def seed(SeedLiquidity, uniswap, lido, weth, accounts):
    return SeedLiquidity.deploy(
        uniswap,
        [lido, weth],
        ["10000000 ether", "150 ether"],
        14 * 86400,
        0,
        {"from": accounts[0]},
    )
