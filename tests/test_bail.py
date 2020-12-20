import brownie

def test_bail_seed_running(seed, lido, weth, agent, whale, chain):
    lido_amount = seed.target(0)
    weth_amount = seed.target(1)
    
    lido.approve(seed, lido_amount)
    seed.deposit([lido_amount, 0], {'from': agent})

    weth.approve(seed, weth_amount)
    seed.deposit([0, weth_amount], {'from': whale})

    with brownie.reverts():
        seed.bail({'from': agent})
    with brownie.reverts():
        seed.bail({'from': whale})

def test_bail_targets_met_expired(seed, lido, weth, agent, whale, chain):
    lido_amount = seed.target(0)
    weth_amount = seed.target(1)

    lido_before = lido.balanceOf(agent)
    weth_before = weth.balanceOf(whale)
    
    lido.approve(seed, lido_amount)
    seed.deposit([lido_amount, 0], {'from': agent})

    weth.approve(seed, weth_amount)
    seed.deposit([0, weth_amount], {'from': whale})

    chain.sleep(14 * 86400)

    seed.bail({'from': agent})
    assert lido.balanceOf(agent) == lido_before

    seed.bail({'from': whale})
    assert weth.balanceOf(whale) == weth_before

def test_bail_targets_not_met(seed, lido, weth, agent, whale, chain):
    lido_amount = seed.target(0)//2
    weth_amount = seed.target(1)*3//4

    lido_before = lido.balanceOf(agent)
    weth_before = weth.balanceOf(whale)
    
    lido.approve(seed, lido_amount)
    seed.deposit([lido_amount, 0], {'from': agent})

    weth.approve(seed, weth_amount)
    seed.deposit([0, weth_amount], {'from': whale})

    with brownie.reverts():
        seed.provide()

    chain.sleep(14 * 86400)

    seed.bail({'from': agent})
    assert lido.balanceOf(agent) == lido_before

    seed.bail({'from': whale})
    assert weth.balanceOf(whale) == weth_before

def test_bail_targets_met_expired_multi_deposit(seed, lido, weth, agent, whale, chain):
    lido_amount = seed.target(0)
    weth_amount = seed.target(1)

    lido_before = lido.balanceOf(agent)
    weth_before = weth.balanceOf(whale)
    
    lido.approve(seed, lido_amount)
    seed.deposit([lido_amount//2, 0], {'from': agent})
    seed.deposit([lido_amount//2, 0], {'from': agent})

    weth.approve(seed, weth_amount)
    seed.deposit([0, weth_amount//4], {'from': whale})
    seed.deposit([0, weth_amount//4], {'from': whale})
    seed.deposit([0, weth_amount//4], {'from': whale})
    seed.deposit([0, weth_amount//4], {'from': whale})

    chain.sleep(14 * 86400)

    seed.bail({'from': agent})
    assert lido.balanceOf(agent) == lido_before

    seed.bail({'from': whale})
    assert weth.balanceOf(whale) == weth_before