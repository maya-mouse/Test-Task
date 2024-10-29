
import requests
import os
import pandas as pd

OS_API_KEY = os.getenv("OS_API_KEY")

query = {
    "queries": {
        "q1": {"schema": "Organization", "properties": {"name": ["cryptex"], "topics" : ["sanction"]}}
    }
}

headers = {
    "Authorization": OS_API_KEY,
}
########################################### finding sanctioned crypto exchanges

response = requests.post("https://api.opensanctions.org/match/default?limit=200", headers=headers, json=query)
response.raise_for_status()

results = []
for result in response.json()["responses"]["q1"]["results"]:
        sanctions_str = ', '.join(result["datasets"])
        results.append(
            {
                "id": result["id"],
                "caption": result["caption"],
                "sanctions": sanctions_str
            }
        )


q1_df = pd.DataFrame(results)

q1_df.to_excel('sanctioned_crypto_exchanges.xlsx', index=False)

########################################### finding crypto wallets

exchange_data = pd.read_excel("sanctioned_crypto_exchanges.xlsx")
wallet_results = []

for index, row in exchange_data.iterrows():

    caption = row['caption']
    id = row['id']

    response = requests.get(f"https://api.opensanctions.org/search/default?limit=400&q={id}", headers=headers)
    response.raise_for_status()

    results = response.json().get('results', [])

    for entity in results:
            if entity.get('schema') == 'CryptoWallet':
                sanctions_str = ', '.join(entity['datasets'])
                publicKey_str = ', '.join(entity['properties'].get('publicKey'))
                wallet_info = {
                    "exchange id": id,
                    "exchange caption": caption,
                    "publicKey": publicKey_str,
                    "sanctions": sanctions_str
                }

                wallet_results.append(wallet_info)


wallets_df = pd.DataFrame(wallet_results)
wallets_df.to_excel("sanctioned_crypto_wallets.xlsx", index=False)

