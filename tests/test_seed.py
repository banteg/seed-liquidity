def test_seed(seed, lido, weth, agent, whale, interface):
    pair = interface.ERC20(seed.pair())
    lido_amount = seed.target(0)
    weth_amount = seed.target(1)
    
    lido.approve(seed, lido_amount)
    weth.approve(seed, weth_amount)
    
    seed.deposit([lido_amount, 0], {'from': agent})
    assert lido.balanceOf(seed) == lido_amount
    assert seed.balances(agent, 0) == lido_amount
    assert seed.totals(0) == lido_amount
    
    seed.deposit([0, weth_amount], {'from': whale})
    assert weth.balanceOf(seed) == weth_amount
    assert seed.balances(whale, 1) == weth_amount
    assert seed.totals(1) == weth_amount

    seed.provide()
    assert seed.liquidity() > 0
    assert pair.balanceOf(seed) == seed.liquidity()
    assert pair.balanceOf(seed) + 1000 == pair.totalSupply()

    seed.claim({'from': agent})
    assert pair.balanceOf(agent) == seed.liquidity() // 2

    seed.claim({'from': whale})
    assert pair.balanceOf(whale) == seed.liquidity() // 2


def test_bail(seed, lido, weth, agent, whale, chain):
    lido_before = lido.balanceOf(agent)
    weth_before = weth.balanceOf(whale)
    lido_amount = seed.target(0)
    weth_amount = seed.target(1)
    
    lido.approve(seed, lido_amount)
    seed.deposit([lido_amount, 0], {'from': agent})
    assert lido.balanceOf(agent) == lido_before - lido_amount
    
    weth.approve(seed, weth_amount)
    seed.deposit([0, weth_amount], {'from': whale})
    assert weth.balanceOf(whale) == weth_before - weth_amount
    
    chain.sleep(14 * 86400)
    
    seed.bail({'from': agent})
    assert lido.balanceOf(agent) == lido_before

    seed.bail({'from': whale})
    assert weth.balanceOf(whale) == weth_before
