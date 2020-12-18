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

    seed.withdraw({'from': agent})
    assert pair.balanceOf(agent) == seed.liquidity() // 2

    seed.withdraw({'from': whale})
    assert pair.balanceOf(whale) == seed.liquidity() // 2
