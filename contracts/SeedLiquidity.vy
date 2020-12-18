# @version 0.2.8
from vyper.interfaces import ERC20

interface Uniswap:
    # factory
    def getPair(tokenA: address, tokenB: address) -> address: view
    def createPair(tokenA: address, tokenB: address) -> address: nonpayable
    # router
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

router: public(Uniswap)
token_a: public(ERC20)
token_b: public(ERC20)
pair: public(ERC20)
remaining_a: public(uint256)
remaining_b: public(uint256)
balances_a: public(HashMap[address, uint256])
balances_b: public(HashMap[address, uint256])
liquidity: public(uint256)


@external
def __init__(router: address, token_a: address, token_b: address, target_a: uint256, target_b: uint256):
    self.router = Uniswap(router)
    self.token_a = ERC20(token_a)
    self.token_b = ERC20(token_b)
    self.remaining_a = target_a
    self.remaining_b = target_b
    factory: address = self.router.factory()
    pair: address = Uniswap(factory).getPair(token_a, token_b)
    if pair == ZERO_ADDRESS:
        pair = Uniswap(factory).createPair(token_a, token_b)
    self.pair = ERC20(pair)


@external
def deposit(amount_a: uint256, amount_b: uint256):
    assert self.liquidity == 0  # dev: already seeded

    add_a: uint256 = min(amount_a, self.remaining_a)
    self.token_a.transferFrom(msg.sender, self, add_a)
    self.balances_a[msg.sender] += add_a
    self.remaining_a -= add_a

    add_b: uint256 = min(amount_b, self.remaining_b)
    self.token_a.transferFrom(msg.sender, self, add_b)
    self.balances_b[msg.sender] += add_b
    self.remaining_b -= add_b


@external
def provide():
    assert self.liquidity == 0  # dev: already seeded
    assert self.remaining_a == 0  # dev: token a not filled
    assert self.remaining_b == 0  # dev: token b not filled
    
    add_a: uint256 = self.token_a.balanceOf(self)
    add_b: uint256 = self.token_b.balanceOf(self)

    self.token_a.approve(self.router.address, add_a)
    self.token_b.approve(self.router.address, add_b)
    
    self.router.addLiquidity(
        self.token_a.address,
        self.token_b.address,
        add_a,
        add_b,
        add_a,
        add_b,
        self,
        block.timestamp
    )

    self.liquidity = self.pair.balanceOf(self)
    assert self.liquidity > 0  # dev: no liquidity provided
