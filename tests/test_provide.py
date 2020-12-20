import pytest
import brownie


@pytest.fixture
def seed(SeedLiquidity, uniswap, lido, weth, accounts):
    return SeedLiquidity.deploy(
        uniswap,
        [lido, weth],
        ["10 ether", "10 ether"],
        14 * 86400,
        0,
        {"from": accounts[0]},
    )


def test_both_unfilled(seed, lido, weth, agent, whale, interface):
    pair = interface.ERC20(seed.pair())
    lido_amount = "9 ether"
    weth_amount = "9 ether"

    lido.approve(seed, lido_amount, {'from': agent})
    seed.deposit(
        [lido_amount, 0],
        {'from': agent},
    )
    weth.approve(seed, weth_amount, {'from': whale})
    seed.deposit(
        [0, weth_amount],
        {'from': whale},
    )

    assert lido.balanceOf(seed) == lido_amount
    assert seed.balances(agent, 0) == lido_amount
    assert seed.totals(0) == lido_amount
    assert weth.balanceOf(seed) == weth_amount
    assert seed.balances(whale, 1) == weth_amount
    assert seed.totals(1) == weth_amount

    with brownie.reverts():
        seed.provide()

    assert seed.liquidity() == 0
    assert pair.balanceOf(seed) == 0
    assert pair.totalSupply() == 0


def test_lido_unfilled(seed, lido, weth, agent, whale, interface):
    pair = interface.ERC20(seed.pair())
    lido_amount = "9 ether"
    weth_amount = "10 ether"

    lido.approve(seed, lido_amount, {'from': agent})
    seed.deposit(
        [lido_amount, 0],
        {'from': agent},
    )
    weth.approve(seed, weth_amount, {'from': whale})
    seed.deposit(
        [0, weth_amount],
        {'from': whale},
    )

    assert lido.balanceOf(seed) == lido_amount
    assert seed.balances(agent, 0) == lido_amount
    assert seed.totals(0) == lido_amount
    assert weth.balanceOf(seed) == weth_amount
    assert seed.balances(whale, 1) == weth_amount
    assert seed.totals(1) == weth_amount

    with brownie.reverts():
        seed.provide()

    assert seed.liquidity() == 0
    assert pair.balanceOf(seed) == 0
    assert pair.totalSupply() == 0


def test_weth_unfilled(seed, lido, weth, agent, whale, interface):
    pair = interface.ERC20(seed.pair())
    lido_amount = "10 ether"
    weth_amount = "9 ether"

    lido.approve(seed, lido_amount, {'from': agent})
    seed.deposit(
        [lido_amount, 0],
        {'from': agent},
    )
    weth.approve(seed, weth_amount, {'from': whale})
    seed.deposit(
        [0, weth_amount],
        {'from': whale},
    )

    assert lido.balanceOf(seed) == lido_amount
    assert seed.balances(agent, 0) == lido_amount
    assert seed.totals(0) == lido_amount
    assert weth.balanceOf(seed) == weth_amount
    assert seed.balances(whale, 1) == weth_amount
    assert seed.totals(1) == weth_amount

    with brownie.reverts():
        seed.provide()

    assert seed.liquidity() == 0
    assert pair.balanceOf(seed) == 0
    assert pair.totalSupply() == 0


def test_filled(seed, lido, weth, agent, whale, interface):
    pair = interface.ERC20(seed.pair())
    lido_amount = "10 ether"
    weth_amount = "10 ether"

    lido.approve(seed, lido_amount, {'from': agent})
    seed.deposit(
        [lido_amount, 0],
        {'from': agent},
    )
    weth.approve(seed, weth_amount, {'from': whale})
    seed.deposit(
        [0, weth_amount],
        {'from': whale},
    )

    assert lido.balanceOf(seed) == lido_amount
    assert seed.balances(agent, 0) == lido_amount
    assert seed.totals(0) == lido_amount
    assert weth.balanceOf(seed) == weth_amount
    assert seed.balances(whale, 1) == weth_amount
    assert seed.totals(1) == weth_amount

    seed.provide()

    assert seed.liquidity() > 0
    assert pair.balanceOf(seed) == seed.liquidity()
    assert pair.balanceOf(seed) == pair.totalSupply() - 1000  # 1000 LP tokens burned

    # Check revert on second time
    with brownie.reverts():
        seed.provide()


def test_existing(seed, lido, weth, agent, whale, interface, uniswap, chain):
    pair = interface.ERC20(seed.pair())

    # Prefund pool
    lido_amount = "1 ether"
    weth_amount = "1 ether"
    lido.transfer(whale, lido_amount, {'from': agent})
    lido.approve(uniswap, lido_amount, {'from': whale})
    weth.approve(uniswap, weth_amount, {'from': whale})
    uniswap.addLiquidity(
        lido,
        weth,
        lido_amount,
        weth_amount,
        lido_amount,
        weth_amount,
        whale,
        chain.time(),
        {'from': whale},
    )

    assert seed.liquidity() == 0
    assert pair.balanceOf(seed) == 0
    assert pair.balanceOf(whale) > 0
    assert pair.totalSupply() > 0

    # Try to seed
    lido_amount = "10 ether"
    weth_amount = "10 ether"

    lido.approve(seed, lido_amount, {'from': agent})
    seed.deposit(
        [lido_amount, 0],
        {'from': agent},
    )
    weth.approve(seed, weth_amount, {'from': whale})
    seed.deposit(
        [0, weth_amount],
        {'from': whale},
    )

    assert lido.balanceOf(seed) == lido_amount
    assert seed.balances(agent, 0) == lido_amount
    assert seed.totals(0) == lido_amount
    assert weth.balanceOf(seed) == weth_amount
    assert seed.balances(whale, 1) == weth_amount
    assert seed.totals(1) == weth_amount

    with brownie.reverts():
        seed.provide()

    assert seed.liquidity() == 0
    assert pair.balanceOf(seed) == 0
    assert pair.totalSupply() > 0


def test_expired(seed, lido, weth, agent, whale, interface, chain):
    pair = interface.ERC20(seed.pair())
    lido_amount = "10 ether"
    weth_amount = "10 ether"

    lido.approve(seed, lido_amount, {'from': agent})
    seed.deposit(
        [lido_amount, 0],
        {'from': agent},
    )
    weth.approve(seed, weth_amount, {'from': whale})
    seed.deposit(
        [0, weth_amount],
        {'from': whale},
    )

    assert lido.balanceOf(seed) == lido_amount
    assert seed.balances(agent, 0) == lido_amount
    assert seed.totals(0) == lido_amount
    assert weth.balanceOf(seed) == weth_amount
    assert seed.balances(whale, 1) == weth_amount
    assert seed.totals(1) == weth_amount

    chain.sleep(14 * 86400)
    with brownie.reverts():
        seed.provide()

    assert seed.liquidity() == 0
    assert pair.balanceOf(seed) == 0
    assert pair.totalSupply() == 0
