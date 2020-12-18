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
ratio: public(uint256)
balanceOf: public(HashMap[address, uint256])
liquidity: public(uint256)

@external
def __init__(router: address, token_a: address, token_b: address, ratio: uint256):
    self.router = Uniswap(router)
    self.token_a = ERC20(token_a)
    self.token_b = ERC20(token_b)
    self.ratio = ratio
    factory: address = self.router.factory()
    pair: address = Uniswap(factory).getPair(token_a, token_b)
    if pair == ZERO_ADDRESS:
        pair = Uniswap(factory).createPair(token_a, token_b)
    self.pair = ERC20(pair)
