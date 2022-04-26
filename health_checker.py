from web3 import Web3
from functools import wraps
import json
import traceback
from typing import Union
from requests.exceptions import HTTPError

class AaveHealthFactor:
    '''
    Contains functions to access the "Lending Pool" contract of the Aave DAO
    and return the Health factor of a given account.

    Resources
    ---------
    Aave Deployed Contracts: https://docs.aave.com/developers/v/2.0/deployed-contracts/deployed-contracts
    Lending Pool functions: https://docs.aave.com/developers/v/2.0/the-core-protocol/lendingpool
    '''

    def __init__(self):
        self.blockchain_name = 'ethereum'
        self.blockchain_net = 'mainnet'
        self.lending_pool_abi_filename = 'lending_pool_abi.json'
        self.lending_pool_address = '0x7d2768dE32b0b80b7a3454c06BdAc94A69DDc7A9'
        self.infura_nodes = ['https://mainnet.infura.io/v3', 'wss://mainnet.infura.io/ws/v3']
        ## Constants
        self.max_sol_hex = '0xffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff'


    def connect(self, infura_id: str = None):
        ''' Return a web3 session object or False if a faulty Infura ID is provided. '''
        print('Attempting to connect to Ethereum node.')
        for node in self.infura_nodes:
            endpoint = Web3.HTTPProvider(f'{node}/{infura_id}')
            w3 = Web3(endpoint)
            is_connected = w3.isConnected()
            if is_connected is True:
                return w3
        print('Connection failed.')
        return False


    def get_lending_pool_abi(self):
        ## Try to Get ABI from Etherscan
        # Hmm... this is on the farthest backburner for web3.py (https://github.com/ethereum/web3.py/issues/1711)
        # Could build a web scarper for Etherscan in the future.

        ## Load Saved ABI
        self.lending_pool_abi_filename
        try:
            with open(self.lending_pool_abi_filename) as json_file:
                abi = json.load(json_file)
        except FileNotFoundError:
            print('Please move the executable to the same folder as the `lending_pool_abi.json` file.')
            if self.exe:
                input('Press enter to exit the program.')
        return abi


    def get_health_factor_at_block(self, borrower_address: str, block_number: int):
        # For the latest value, you can also use self.lending_pool_contract.functions.getUserAccountData(borrower_address).call()
        (
            totalCollateralETH, totalDebtETH, availableBorrowsETH,
            currentLiquidationThreshold, ltv, health_factor
        ) = self.lending_pool_contract.caller(block_identifier=block_number).getUserAccountData(borrower_address)
        return health_factor


    def exe_wait(function):
        '''
        A decorator that catches and print an exception and pauses for the user to see,
        before ending the execution and closing the program.
        '''
        @wraps(function)
        def exe_wait_wrapper(self, *args, **kwargs):
            try:
                return function(self, *args, **kwargs)
            except Exception:
                traceback.print_exc()
                input('Press enter to exit the program.')
        return exe_wait_wrapper

    @exe_wait
    def run(self, borrower_address: str = None, infura_id: str = None, block_number: Union[int, None] = None, exe: bool = False):
        ''' Cleans Inputs, queries the Health Factor, and handing query exceptions. '''
        self.exe = exe
        ## Clean Inputs - Borrower Address
        while True:
            if infura_id is None:
                infura_id = input('Please provide an "infura_id" below... \n')
            self.w3 = self.connect(infura_id=infura_id)
            if self.w3 is not False:
                print("Connected to Infura's Ethereum Node")
                break
            else:
                infura_id = input('The "infura_id" provided is faulty. Please provide a working Infura Project ID address below... \n')

        ## Clean Inputs - Borrower Address
        while True:
            if self.w3.isAddress(borrower_address) is True:
                borrower_address = Web3.toChecksumAddress(borrower_address)
                break
            if borrower_address is None:
                borrower_address = input('Please provide a "borrower_address" below... \n')
            else:
                borrower_address = input('The "borrower_address" provided is not an Ethereum address. Please provide an Ethereum address below... \n')

        ## Clean Inputs - Block Number
        while True:
            if block_number is not None:
                break
            response = input('Please enter a block number, or press enter to return the health factor of the latest block. \n')
            if response == '':
                block_number = Web3.eth.get_block('latest')
                break
            try:
                block_number = int(response)
                break
            except ValueError:
                print('An integer value or no value must be given.')

        ## Get Aave Lending Pool Contract
        lending_pool_abi = self.get_lending_pool_abi()
        self.lending_pool_contract = self.w3.eth.contract(address=self.lending_pool_address, abi=lending_pool_abi)

        ## Get Health Factor for Address
        try:
            health_factor = self.get_health_factor_at_block(borrower_address, block_number)
        except HTTPError:
            print('Sorry, the Ethereum node provided does not allow historical access to a block that far back.')
            if self.exe:
                input('Press enter to exit the program.')
            return

        ## Return Health Factor to User
        if Web3.toHex(health_factor) == self.max_sol_hex:
            print(f'The address "{borrower_address}" has no outstanding borrow position on Aave.\n')
        else:
            print(f'Health factor is {health_factor}: \n - for address {borrower_address} \n - at block {block_number}')
        if self.exe:
            input('Press enter to exit the program.')
        return health_factor



if __name__ == '__main__':
    infura_id = None
    borrower_address = None
    block_number = None
    AaveHealthFactor().run(
        infura_id=infura_id,
        borrower_address=borrower_address,
        block_number=block_number
    )
