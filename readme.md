# Seed liquidity

A contract to pool funds which are then used to boostrap a new Uniswap liquidity pair.

## Specification
1. A new `SeedLiquidity` contract is deployed for non-existent or non-liquid Uniswap pair. The initial price is specified using `target` amounts.
2. Users `deposit` tokens into the contract until both targets are reached.
3. A user calls `provide` to supply liquidity to Uniswap.
4. Users can `claim` their pro-rata share of the LP received LP token.
5. If the target amounts are not raised or the liquidity is not provided before expiry, users can `bail` their deposits and the contract becomes void.

## Interface

### `__init__(address,address[2],uint256[2],uint256)`
Set up a new seed liquidity contract
- `router` UniswapRouter address, e.g. 0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D
- `tokens` Tokens which comprise a pair
- `target` Amounts of tokens to provide, also determines the initial price
- `duration` Duration in seconds over which the contract accepts deposits

### `deposit(uint256[2])`
A user must have approved the contract to spend both tokens. The token amounts are clamped to not exceed their targets. This function only works up to the moment when liquidity is provided or the contract has expired, whichever comes first.
- `amounts` Token amounts to deposit
### `provide()`
This function can only be called once and before the contract has expired. Requires the target to be reached for both tokens. Requires the pool to have no liquidity in it.
### `claim()`
Can be called after liquidity is provided. The token amount is distributed pro-rata to the contribution.
### `bail()`
Can be called after expiry given no liquidity has been provided.
