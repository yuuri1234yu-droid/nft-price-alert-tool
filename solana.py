# solana.py --- Solana(Magic Eden) の floor 価格取得

import requests

# Magic Eden のコレクション stats API
# 実際のエンドポイント例: https://api-mainnet.magiceden.dev/v2/collections/{symbol}/stats
API_URL = "https://api-mainnet.magiceden.dev/v2/collections"


def get_floor_price(collection_symbol: str) -> float | None:
    """
    Magic Eden の API からフロア価格を取得して SOL 単位の float で返す。
    失敗したら None を返す。
    """
    url = f"{API_URL}/{collection_symbol}/stats"

    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        data = r.json()

        # Magic Eden の floorPrice は lamports で返ってくる想定（1 SOL = 1e9 lamports）
        floor_lamports = data.get("floorPrice")
        if floor_lamports is None:
            print(f"[Solana] API 応答に floorPrice がありません: {data}")
            return None

        floor_sol = floor_lamports / 1_000_000_000  # lamports → SOL
        return float(floor_sol)

    except Exception as e:
        print(f"[Solana] Magic Eden API error ({collection_symbol}): {e}")
        return None
