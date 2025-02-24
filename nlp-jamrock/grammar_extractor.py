import asyncio
from crawl4ai import *
from bs4 import BeautifulSoup
from datasets import Dataset
from datasets import load_dataset
from tabulate import tabulate  # For nice table formatting
import pandas as pd


config = CrawlerRunConfig(
        #    cache_mode=CacheMode.ENABLED  # Use cache if available
)

proverbs = []
# Create lists for jamaican and english texts
jamaican_texts = []
english_texts = []

async def main():
    async with AsyncWebCrawler() as crawler:
        results = await crawler.arun_many(
            urls=["https://opengrammar.github.io/jam/glossary/","https://opengrammar.github.io/jam/" , "https://opengrammar.github.io/jam/gazetteer/"],
            config=config
        )
    
    for url in results:
        soup = BeautifulSoup(url.cleaned_html, 'html.parser')
        for p in soup.find_all('p'):
            strong = p.find('strong')
            em = p.find('em')
            if strong and em:
                jamaican = strong.text.strip()
                english = em.text.strip()
                proverbs.append((jamaican, english))
                jamaican_texts.append(jamaican)
                english_texts.append(english_texts)


    # Create DataFrame
    df = pd.DataFrame(proverbs, columns=['Jamaican', 'English'])

    # Create and print table
    headers = ["Jamaican", "English"]

    table = tabulate(proverbs, headers=headers, tablefmt="grid")

    # load Dataset from Pandas Dataframe
    dataset = Dataset.from_pandas(df)

    dataset.push_to_hub("gearV9/patois_proverbs")

if __name__ == "__main__":
    asyncio.run(main())
