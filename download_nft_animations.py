"""
Download NFT gift Lottie animations from Fragment.com
"""

import asyncio
import aiohttp
import os
import json

# NFT gifts to download
TOP_10_GIFTS = [
    "MightyArm-2995",
    "BondedRing-2469",
    "SignetRing-3380",
    "BlingBinky-255",
    "BlingBinky-8795",
    "CupidCharm-2042",
    "IceCream-227191",
    "TopHat-9438",
    "RecordPlayer-1348",
    "RestlessJar-4793"
]

RANDOM_20_GIFTS = [
    "FaithAmulet-55884",
    "FaithAmulet-55911",
    "FaithAmulet-56038",
    "IceCream-159536",
    "IceCream-159631",
    "IceCream-159732",
    "SnakeBox-9017",
    "DeskCalendar-44858",
    "HomemadeCake-1505",
    "IceCream-159180",
    "IceCream-159284",
    "IceCream-159419",
    "IceCream-158662",
    "IceCream-158559",
    "BDayCandle-230064",
    "SnakeBox-8938",
    "IceCream-158977",
    "IceCream-158877",
    "IceCream-158788",
    "FaithAmulet-55947"
]

# Create output directory
OUTPUT_DIR = "static/animations"
os.makedirs(OUTPUT_DIR, exist_ok=True)

async def download_animation(session, gift_name: str) -> dict:
    """Download a single NFT animation from Fragment.com"""
    # Extract base name (e.g., MightyArm from MightyArm-2995)
    base_name = gift_name.rsplit('-', 1)[0].lower()
    
    url = f"https://nft.fragment.com/gift/{gift_name.lower()}.lottie.json"
    
    try:
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                
                # Save to file
                filename = f"{gift_name}.json"
                filepath = os.path.join(OUTPUT_DIR, filename)
                
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(data, f)
                
                print(f"✅ Downloaded: {gift_name}")
                return {"name": gift_name, "file": filename, "success": True}
            else:
                print(f"❌ Failed ({response.status}): {gift_name}")
                return {"name": gift_name, "success": False, "error": response.status}
    except Exception as e:
        print(f"❌ Error: {gift_name} - {e}")
        return {"name": gift_name, "success": False, "error": str(e)}

async def download_all():
    """Download all NFT animations"""
    all_gifts = TOP_10_GIFTS + RANDOM_20_GIFTS
    
    # Remove duplicates while preserving order
    seen = set()
    unique_gifts = []
    for gift in all_gifts:
        base = gift.rsplit('-', 1)[0]
        if base not in seen:
            seen.add(base)
            unique_gifts.append(gift)
    
    print(f"Downloading {len(unique_gifts)} unique NFT animations...")
    
    async with aiohttp.ClientSession() as session:
        tasks = [download_animation(session, gift) for gift in unique_gifts]
        results = await asyncio.gather(*tasks)
    
    successful = [r for r in results if r.get("success")]
    failed = [r for r in results if not r.get("success")]
    
    print(f"\n✅ Successfully downloaded: {len(successful)}")
    print(f"❌ Failed: {len(failed)}")
    
    # Create manifest file for frontend
    manifest = {
        "top_10": TOP_10_GIFTS,
        "random_20": RANDOM_20_GIFTS,
        "downloaded": [r["name"] for r in successful]
    }
    
    with open(os.path.join(OUTPUT_DIR, "manifest.json"), 'w') as f:
        json.dump(manifest, f, indent=2)
    
    print(f"\nManifest saved to {OUTPUT_DIR}/manifest.json")

if __name__ == "__main__":
    asyncio.run(download_all())
