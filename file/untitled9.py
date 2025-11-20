# from alchemy import Alchemy
# from alchemy.types import AssetTransfersCategory

# # Alchemy configuration
# api_key = "vhfS63Mbxdv6zgIHcrjl5zwvLyAD34B-"  # Replace with your actual Alchemy API key
# alchemy = Alchemy(api_key, network="eth-mainnet")  # Connect to Ethereum mainnet

# # Address to analyze
# to_address = "0x1E6E8695FAb3Eb382534915eA8d7Cc1D1994B152"  # Replace with target address

# # Fetch transactions to analyze
# def fetch_transactions():
#     try:
#         transactions = alchemy.core.get_asset_transfers(
#             from_block="0x0",
#             from_address="0x0000000000000000000000000000000000000000",  # Mint transactions
#             to_address=to_address,
#             exclude_zero_value=True,
#             category=[AssetTransfersCategory.ERC721, AssetTransfersCategory.ERC1155]
#         )
#         return transactions['transfers']
#     except Exception as e:
#         print("Error fetching transactions:", e)
#         return []

# # # Analyze transactions for suspicious activity
# # def analyze_transactions(transactions):
# #     # Placeholder model and thresholds for suspicious behavior
# #     # Use actual ML model here (e.g., pre-trained RandomForest or other classifier)
# #     suspicious_transactions = []
# #     for tx in transactions:
# #         # Example criteria for suspicion (you can customize)
# #         if float(tx['value']) > 1000 or tx['token_type'] in ["ERC721", "ERC1155"]:
# #             suspicious_transactions.append(tx)
# #     return suspicious_transactions

# # Main flow
# transactions = fetch_transactions()
# #suspicious_transactions = analyze_transactions(transactions)
# print(transactions)
# # Output suspicious transactions
# #print("Suspicious Transactions:", suspicious_transactions)
