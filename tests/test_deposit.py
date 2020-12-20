import pytest
import brownie


# SeedLiquidity contract
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


def test_lido_not_approved(seed, lido, agent):
    lido_amount = "1 ether"

    with brownie.reverts():
        seed.deposit(
            [lido_amount, 0],
            {'from': agent},
        )

    assert lido.balanceOf(seed) == 0
    assert seed.balances(agent, 0) == 0
    assert seed.totals(0) == 0


def test_lido_approved(seed, lido, agent):
    lido_amount = "1 ether"

    lido.approve(seed, lido_amount, {'from': agent})
    seed.deposit(
        [lido_amount, 0],
        {'from': agent},
    )

    assert lido.balanceOf(seed) == lido_amount
    assert seed.balances(agent, 0) == lido_amount
    assert seed.totals(0) == lido_amount

    lido_amount = "2 ether"

    lido.approve(seed, lido_amount, {'from': agent})
    seed.deposit(
        [lido_amount, 0],
        {'from': agent},
    )

    lido_amount = "3 ether"
    assert lido.balanceOf(seed) == lido_amount
    assert seed.balances(agent, 0) == lido_amount
    assert seed.totals(0) == lido_amount


def test_weth_not_approved(seed, weth, whale):
    weth_amount = "1 ether"

    with brownie.reverts():
        seed.deposit(
            [0, weth_amount],
            {'from': whale},
        )

    assert weth.balanceOf(seed) == 0
    assert seed.balances(whale, 1) == 0
    assert seed.totals(1) == 0


def test_weth_approved(seed, weth, whale):
    weth_amount = "1 ether"

    weth.approve(seed, weth_amount, {'from': whale})
    seed.deposit(
        [0, weth_amount],
        {'from': whale},
    )

    assert weth.balanceOf(seed) == weth_amount
    assert seed.balances(whale, 1) == weth_amount
    assert seed.totals(1) == weth_amount

    weth_amount = "2 ether"

    weth.approve(seed, weth_amount, {'from': whale})
    seed.deposit(
        [0, weth_amount],
        {'from': whale},
    )

    weth_amount = "3 ether"

    assert weth.balanceOf(seed) == weth_amount
    assert seed.balances(whale, 1) == weth_amount
    assert seed.totals(1) == weth_amount


def test_both_approved(seed, lido, weth, agent, whale):
    lido_amount = "1 ether"
    weth_amount = "1 ether"

    lido.transfer(whale, lido_amount, {'from': agent})
    lido.approve(seed, lido_amount, {'from': whale})
    weth.approve(seed, weth_amount, {'from': whale})
    seed.deposit(
        [lido_amount, weth_amount],
        {'from': whale},
    )

    assert lido.balanceOf(seed) == lido_amount
    assert seed.balances(whale, 0) == lido_amount
    assert seed.totals(0) == lido_amount
    assert weth.balanceOf(seed) == weth_amount
    assert seed.balances(whale, 1) == weth_amount
    assert seed.totals(1) == weth_amount

    lido_amount = "2 ether"
    weth_amount = "2 ether"

    lido.transfer(whale, lido_amount, {'from': agent})
    lido.approve(seed, lido_amount, {'from': whale})
    weth.approve(seed, weth_amount, {'from': whale})
    seed.deposit(
        [lido_amount, weth_amount],
        {'from': whale},
    )

    lido_amount = "3 ether"
    weth_amount = "3 ether"

    assert lido.balanceOf(seed) == lido_amount
    assert seed.balances(whale, 0) == lido_amount
    assert seed.totals(0) == lido_amount
    assert weth.balanceOf(seed) == weth_amount
    assert seed.balances(whale, 1) == weth_amount
    assert seed.totals(1) == weth_amount


def test_lido_expired(seed, lido, agent, chain):
    lido_amount = "1 ether"

    lido.approve(seed, lido_amount, {'from': agent})
    chain.sleep(14 * 86400)
    with brownie.reverts():
        seed.deposit(
            [lido_amount, 0],
            {'from': agent},
        )

    assert lido.balanceOf(seed) == 0
    assert seed.balances(agent, 0) == 0
    assert seed.totals(0) == 0


def test_weth_expired(seed, weth, whale, chain):
    weth_amount = "1 ether"

    weth.approve(seed, weth_amount, {'from': whale})
    chain.sleep(14 * 86400)
    with brownie.reverts():
        seed.deposit(
            [0, weth_amount],
            {'from': whale},
        )

    assert weth.balanceOf(seed) == 0
    assert seed.balances(whale, 1) == 0
    assert seed.totals(1) == 0


def test_both_expired(seed, lido, weth, agent, whale, chain):
    lido_amount = "1 ether"
    weth_amount = "1 ether"

    lido.transfer(whale, lido_amount, {'from': agent})
    lido.approve(seed, lido_amount, {'from': whale})
    weth.approve(seed, weth_amount, {'from': whale})
    chain.sleep(14 * 86400)
    with brownie.reverts():
        seed.deposit(
            [lido_amount, weth_amount],
            {'from': whale},
        )

    assert lido.balanceOf(seed) == 0
    assert seed.balances(whale, 0) == 0
    assert seed.totals(0) == 0
    assert weth.balanceOf(seed) == 0
    assert seed.balances(whale, 1) == 0
    assert seed.totals(1) == 0


def test_lido_exceeds_target(seed, lido, agent, chain):
    target_amount = "10 ether"
    balance_amount = "4 ether"
    lido_amount = "7 ether"

    lido.approve(seed, lido_amount, {'from': agent})
    seed.deposit(
        [lido_amount, 0],
        {'from': agent},
    )

    assert lido.balanceOf(seed) == lido_amount
    assert seed.balances(agent, 0) == lido_amount
    assert seed.totals(0) == lido_amount

    lido.approve(seed, lido_amount, {'from': agent})
    seed.deposit(
        [lido_amount, 0],
        {'from': agent},
    )

    assert lido.balanceOf(seed) == target_amount
    assert seed.balances(agent, 0) == target_amount
    assert seed.totals(0) == target_amount
    assert lido.allowance(agent, seed) == balance_amount


def test_weth_exceeds_target(seed, weth, whale, chain):
    target_amount = "10 ether"
    balance_amount = "4 ether"
    weth_amount = "7 ether"

    weth.approve(seed, weth_amount, {'from': whale})
    seed.deposit(
        [0, weth_amount],
        {'from': whale},
    )

    assert weth.balanceOf(seed) == weth_amount
    assert seed.balances(whale, 1) == weth_amount
    assert seed.totals(1) == weth_amount

    weth.approve(seed, weth_amount, {'from': whale})
    seed.deposit(
        [0, weth_amount],
        {'from': whale},
    )

    assert weth.balanceOf(seed) == target_amount
    assert seed.balances(whale, 1) == target_amount
    assert seed.totals(1) == target_amount
    assert weth.allowance(whale, seed) == balance_amount


def test_both_exceeds_target(seed, lido, weth, agent, whale, chain):
    target_amount = "10 ether"
    balance_amount = "4 ether"
    lido_amount = "7 ether"
    weth_amount = "7 ether"

    lido.transfer(whale, lido_amount, {'from': agent})
    lido.approve(seed, lido_amount, {'from': whale})
    weth.approve(seed, weth_amount, {'from': whale})
    seed.deposit(
        [lido_amount, weth_amount],
        {'from': whale},
    )

    assert lido.balanceOf(seed) == lido_amount
    assert seed.balances(whale, 0) == lido_amount
    assert seed.totals(0) == lido_amount
    assert weth.balanceOf(seed) == weth_amount
    assert seed.balances(whale, 1) == weth_amount
    assert seed.totals(1) == weth_amount

    lido.transfer(whale, lido_amount, {'from': agent})
    lido.approve(seed, lido_amount, {'from': whale})
    weth.approve(seed, weth_amount, {'from': whale})
    seed.deposit(
        [lido_amount, weth_amount],
        {'from': whale},
    )

    assert lido.balanceOf(seed) == target_amount
    assert seed.balances(whale, 0) == target_amount
    assert seed.totals(0) == target_amount
    assert weth.balanceOf(seed) == target_amount
    assert seed.balances(whale, 1) == target_amount
    assert seed.totals(1) == target_amount
    assert lido.allowance(whale, seed) == balance_amount
    assert weth.allowance(whale, seed) == balance_amount
