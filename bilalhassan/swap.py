"""
Interacting with the Raydium protocol
"""

import asyncio
import aiohttp
import base58
import base64
from solders.transaction import Transaction
from solana.rpc.async_api import AsyncClient
from solana.rpc import types
from solders.pubkey import Pubkey
from solders.keypair import Keypair
from spl.token.constants import TOKEN_PROGRAM_ID
from typing import Optional, List, Dict, Any

import os
from dotenv import load_dotenv

load_dotenv('secrets.env')

RPC_ENDPOINT = os.getenv('RPC_ENDPOINT')
SECRET_KEY = list(map(int, os.getenv('SECRET_KEY').split(",")))

OUTPUT_MINT = os.getenv('OUTPUT_MINT')
INPUT_MINT = os.getenv('INPUT_MINT')
BASE_HOST = os.getenv('BASE_HOST')
SWAP_HOST = os.getenv('SWAP_HOST')
PRIORITY_FEE = os.getenv('PRIORITY_FEE')
PUBLIC_KEY = os.getenv('PUBLIC_KEY')

AMOUNT = 10
SLIPPAGE = 0.5

class RaydiumSwap:
  """
    Attributes:
        owner (Keypair): The owner of the swap.
        sol_client (AsyncClient): The Solana client used for the swap.

    Methods:
        fetch_token_account_data: Fetches the token account data for the owner.
    """
    
  def __init__(self, sol_client: AsyncClient):
    self.owner = Keypair.from_bytes(bytearray(SECRET_KEY))
    self.sol_client = sol_client
    
    self.NATIVE_MINT = 'So11111111111111111111111111111111111111112'

  async def fetch_token_account_data(self):
    response = await self.sol_client.get_token_accounts_by_owner(self.owner.pubkey(), types.TokenAccountOpts(program_id=TOKEN_PROGRAM_ID))
    print(response)
    print(self.owner.pubkey())
    return response

  async def get_priority_fee(self):
    """
    Get transcaction fee from api
    ***NOT_WORKING***
    """

    async with aiohttp.ClientSession() as session:
      async with session.get(f"{PRIORITY_FEE}") as response:
          final_response = await response.json()
          print(final_response)
          return final_response
      
  async def compute_swap(self):
    """Compute swap parameters"""
    params = {
        "inputMint": INPUT_MINT,
        "outputMint": OUTPUT_MINT,
        "amount": str(AMOUNT),
        "slippageBps": int(SLIPPAGE * 100)
    }
    async with aiohttp.ClientSession() as session:
      async with session.get(
        f"{SWAP_HOST}/compute/swap-base-in",
        params = params
      ) as response:
        final_response = await response.json()
        print(final_response)
        return final_response
  
  async def get_swap_transactions(self, swap_response: Dict[str, Any], 
                                  priority_fee: Dict[str, Any],
                                  input_token_acc: Optional[str], 
                                  output_token_acc: Optional[str],
                                  is_input_sol: bool, 
                                  is_output_sol: bool) -> Dict[str, Any]:
    """Get swap transactions from API"""
    payload = {
      "computeUnitPriceMicroLamports": str(priority_fee["data"]["default"]["h"]),
      "swapResponse": swap_response,
      "wallet": str(self.owner.public_key()),
      "wrapSol": is_input_sol,
      "unwrapSol": is_output_sol,
      "inputAccount": None if is_input_sol else input_token_acc,
      "outputAccount": None if is_output_sol else output_token_acc
    }
    
    async with aiohttp.ClientSession() as session:
      async with session.post(
          f"{SWAP_HOST}/transaction/swap-base-in",
          json=payload
      ) as response:
          final_response = await response.json()
          print(final_response)
          return final_response
      
  async def process_transaction(self, tx_data: str) -> str:
    """Process and send a single transaction"""
    tx_buffer = base64.b64decode(tx_data)
    transaction = Transaction.from_bytes(tx_buffer)
    recent_blockhash = await self.sol_client.get_latest_blockhash()
    transaction.message.recent_blockhash = recent_blockhash.value.blockhash
    
    # Sign transaction
    transaction.sign([self.owner])
    tx_id = await self.sol_client.send_transaction(
      transaction,
      opts={"skip_preflight": True}
    )
    
    # Confirm transaction
    await self.sol_client.confirm_transaction(
      tx_id,
      commitment="confirmed"
    )
    
    return tx_id.value
  
  async def api_swap(self):
    """Main swap function"""
    # Configuration
    input_mint = self.NATIVE_MINT
    output_mint = "4k3Dyjzvzp8eMZWUXbBCjEvwSkkk59S5iCNLY3QrkX6R"  # RAY
    amount = 100
    slippage = 0.5  # 0.5%
    
    # Check if input/output is SOL
    is_input_sol = input_mint == self.NATIVE_MINT
    is_output_sol = output_mint == self.NATIVE_MINT
    
    # Fetch token accounts
    token_accounts_data = await self.fetch_token_account_data()
    input_token_acc = next(
        (acc["publicKey"] for acc in token_accounts_data.value
          if acc["mint"] == input_mint), 
        None
    )
    output_token_acc = next(
        (acc["publicKey"] for acc in token_accounts_data.value
          if acc["mint"] == output_mint), 
        None
    )
    
    if not input_token_acc and not is_input_sol:
        raise ValueError("Do not have input token account")
        
    # Get priority fee
    priority_fee = await self.get_priority_fee()
    
    # Compute swap
    swap_response = await self.compute_swap()
    
    # Get swap transactions
    try:
      swap_transactions = await self.get_swap_transactions(
          swap_response, priority_fee, input_token_acc, output_token_acc,
          is_input_sol, is_output_sol
      )
    
      # Process transactions
      for idx, tx_data in enumerate(swap_transactions["data"], 1):
          try:
              tx_id = await self.process_transaction(tx_data["transaction"])
              print(f"Transaction {idx} confirmed, txId: {tx_id}")
          except Exception as e:
              print(f"Transaction {idx} failed: {str(e)}")
    except Exception as e:
       print('unable to fetch priority fees and preceeding values smthng to do with ', e.__str__())

async def main():
  sol_client = AsyncClient(RPC_ENDPOINT)
  account = (await sol_client.get_account_info(Pubkey.from_string(PUBLIC_KEY)))
  print(account)
  
  swap = RaydiumSwap(sol_client)
  # await swap.fetch_token_account_data()
  await swap.get_priority_fee()
  # await swap.fetch_token_account_data()
  # await swap.api_swap()

  await sol_client.close()

asyncio.run(main())
