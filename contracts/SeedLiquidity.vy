# @version 0.2.8
from vyper.interfaces import ERC20

interface Factory:
    def getPair(tokenA: address, tokenB: address) -> address: view
    def createPair(tokenA: address, tokenB: address) -> address: nonpayable


interface Router:
    def factory() -> address: view
    def addLiquidity(
        tokenA: address,
        tokenB: address,
        amountADesired: uint256,
        amountBDesired: uint256,
        amountAMin: uint256,
        amountBMin: uint256,
        to: address,
        deadline: uint256
    ) -> (uint256, uint256, uint256): nonpayable


router: public(Router)
tokens: public(address[2])
target: public(uint256[2])
pair: public(ERC20)
balances: public(HashMap[address, HashMap[uint256, uint256]])  # address -> index -> balance
totals: public(HashMap[uint256, uint256])  # index -> balance
liquidity: public(uint256)
expiry: public(uint256)


@external
def __init__(router: address, tokens: address[2], target: uint256[2], duration: uint256):
    self.router = Router(router)
    self.tokens = tokens
    self.target = target
    factory: address = self.router.factory()
    pair: address = Factory(factory).getPair(tokens[0], tokens[1])
    if pair == ZERO_ADDRESS:
        pair = Factory(factory).createPair(tokens[0], tokens[1])
    self.pair = ERC20(pair)
    self.expiry = block.timestamp + duration
    assert self.pair.totalSupply() == 0  # dev: pair already liquid


@external
def deposit(amounts: uint256[2]):
    assert self.liquidity == 0  # dev: liquidity already seeded
    assert block.timestamp < self.expiry  # dev: contract has expired
    amount: uint256 = 0
    for i in range(2):
        amount = min(amounts[i], self.target[i] - self.totals[i])
        assert ERC20(self.tokens[i]).transferFrom(msg.sender, self, amount)
        self.balances[msg.sender][i] += amount
        self.totals[i] += amount


@external
def provide():
    assert self.liquidity == 0  # dev: liquidity already seeded
    assert block.timestamp < self.expiry  # dev: contract has expired
    assert self.pair.totalSupply() == 0  # dev: cannot seed a liquid pair
    amount: uint256 = 0
    for i in range(2):
        assert self.totals[i] == self.target[i]  # dev: target not reached
        assert ERC20(self.tokens[i]).approve(self.router.address, self.totals[i])
    
    self.router.addLiquidity(
        self.tokens[0],
        self.tokens[1],
        self.totals[0],
        self.totals[1],
        self.totals[0],  # don't allow slippage
        self.totals[1],
        self,
        block.timestamp
    )

    self.liquidity = self.pair.balanceOf(self)
    assert self.liquidity > 0  # dev: no liquidity provided


@external
def claim():
    assert self.liquidity != 0  # dev: liquidity not seeded
    amount: uint256 = 0
    for i in range(2):
        amount += self.balances[msg.sender][i] * self.liquidity / self.totals[i] / 2
        self.balances[msg.sender][i] = 0
    assert self.pair.transfer(msg.sender, amount)


@external
def bail():
    assert self.liquidity == 0  # dev: liquidity already seeded, use `claim()`
    assert block.timestamp >= self.expiry  # dev: contract not expired
    amount: uint256 = 0
    for i in range(2):
        amount = self.balances[msg.sender][i]
        self.balances[msg.sender][i] = 0
        ERC20(self.tokens[i]).transfer(msg.sender, amount)
