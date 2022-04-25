# Aave Health Factor Checker

Returns the Aave Health Factor of a given ETH address for a given block or for the latest block if no block is given.
The health factor is returned in decimal format.

## How to Use

You can either:
- Run the `health_checker' executable.
- Download the project folder and run the script via the command line with `$python health_checker.py`

## Requirements
- A valid Ethereum address
- An Infura Project ID
- A block number if you desire historical health factors


## Health Factor
The Aave **Health Factor** of an Ethereum address shows how collateralised all the loans for that wallet are, with respect to the liquidation thresholds of each token being used as collateral. The exact formula can be found [here](https://docs.aave.com/risk/asset-risk/risk-parameters#health-factor).
