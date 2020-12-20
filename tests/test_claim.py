import brownie

def test_claim_seed_expired(seed, lido, weth, agent, whale, chain):

    lido_amount = seed.target(0)
    weth_amount = seed.target(1)
    
    lido_before = lido.balanceOf(agent)
    weth_seed_before = weth.balanceOf(seed)
    
    lido.approve(seed, lido_amount)
    seed.deposit([lido_amount, 0], {'from': agent})

    lido_after = lido.balanceOf(agent)

    assert lido_amount == lido_before - lido_after
    assert lido.balanceOf(seed) == lido_amount
    assert weth.balanceOf(seed) == weth_seed_before
    assert seed.balances(agent, 0) == lido_amount
    assert seed.balances(agent, 1) == 0
    assert seed.totals(0) == lido_amount
    assert seed.totals(1) == 0

    weth_before = weth.balanceOf(whale)

    weth.approve(seed, weth_amount)
    seed.deposit([0, weth_amount], {'from': whale})

    weth_after = weth.balanceOf(whale)

    assert weth_amount == weth_before - weth_after
    assert weth.balanceOf(seed) == weth_amount
    assert seed.balances(whale, 1) == weth_amount
    assert seed.balances(whale, 0) == 0
    assert seed.totals(1) == weth_amount

    chain.sleep(14 * 86400)

    with brownie.reverts():
        seed.claim()
    with brownie.reverts():
        seed.provide()
    with brownie.reverts():
        seed.claim()

def test_claim_target_not_met(seed, lido, weth, agent, whale, chain):

    lido_amount = seed.target(0)//2
    weth_amount = seed.target(1)*3//4
    
    lido.approve(seed, lido_amount)
    seed.deposit([lido_amount, 0], {'from': agent})

    weth.approve(seed, weth_amount)
    seed.deposit([0, weth_amount], {'from': whale})

    with brownie.reverts():
        seed.claim()
    with brownie.reverts():
        seed.provide()
    with brownie.reverts():
        seed.claim()

def test_claim_targets_met_not_provided(seed, lido, weth, agent, whale, chain):

    lido_amount = seed.target(0)
    weth_amount = seed.target(1)
    
    lido.approve(seed, lido_amount)
    seed.deposit([lido_amount, 0], {'from': agent})

    weth.approve(seed, weth_amount)
    seed.deposit([0, weth_amount], {'from': whale})

    with brownie.reverts():
        seed.claim()

def test_claim_targets_met_provided_locked(seed_with_waitime, lido, weth, agent, whale, chain):

    lido_amount = seed_with_waitime.target(0)
    weth_amount = seed_with_waitime.target(1)
    
    lido.approve(seed_with_waitime, lido_amount)
    seed_with_waitime.deposit([lido_amount, 0], {'from': agent})

    weth.approve(seed_with_waitime, weth_amount)
    seed_with_waitime.deposit([0, weth_amount], {'from': whale})

    seed_with_waitime.provide()
    with brownie.reverts():
        seed_with_waitime.claim()

def test_claim_targets_met_provided_unlocked_distribute(seed_with_waitime, lido, weth, agent, whale, interface, chain):
    pair = interface.ERC20(seed_with_waitime.pair())
    lido_amount = seed_with_waitime.target(0)
    weth_amount = seed_with_waitime.target(1)
    
    lido.approve(seed_with_waitime, lido_amount)
    seed_with_waitime.deposit([lido_amount, 0], {'from': agent})

    weth.approve(seed_with_waitime, weth_amount)
    seed_with_waitime.deposit([0, weth_amount], {'from': whale})

    seed_with_waitime.provide()

    chain.sleep(100)

    seed_with_waitime.claim({"from": agent})
    assert pair.balanceOf(agent) == seed_with_waitime.liquidity() // 2

    seed_with_waitime.claim({"from": whale})
    assert pair.balanceOf(whale) == seed_with_waitime.liquidity() // 2