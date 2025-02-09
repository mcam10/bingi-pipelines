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

async def main():
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(
            url="https://opengrammar.github.io/jam/",
            config=config
        )

    soup = BeautifulSoup(result.cleaned_html, 'html.parser')

    # Find all paragraphs that contain both strong and em tags
    proverbs = []
    # Create lists for jamaican and english texts
    jamaican_texts = []
    english_texts = []

    for p in soup.find_all('p'):
        strong = p.find('strong')
        em = p.find('em')
        if strong and em:  # Only process paragraphs that have both tags
            jamaican = strong.text.strip()
            english = em.text.strip()
            proverbs.append((jamaican, english))

            ## Building for lata DF pandas or HG
            jamaican_texts.append(jamaican)
            english_texts.append(english_texts)

    
    # Create DataFrame
    df = pd.DataFrame(proverbs, columns=['Jamaican', 'English'])
    
    # Create and print table
    headers = ["Jamaican", "English"]

    table = tabulate(proverbs, headers=headers, tablefmt="grid")

    # load Dataset from Pandas Dataframe
    dataset = Dataset.from_pandas(df)

    print(dataset)


if __name__ == "__main__":
    asyncio.run(main())
