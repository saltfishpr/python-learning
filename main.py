import asyncio
import json
from loguru import logger
from pydantic import BaseModel
from crawl4ai import AsyncWebCrawler, CacheMode
from crawl4ai.extraction_strategy import JsonCssExtractionStrategy


schema = {
    "name": "Novel",
    "baseSelector": ".book-list ul li",
    "fields": [
        {
            "name": "title",
            "type": "text",
            "selector": "h2 a, .name h2",
        },
        {
            "name": "url",
            "type": "attribute",
            "selector": "h2 a, .name",
            "attribute": "href"
        }
    ]
}

strategy = JsonCssExtractionStrategy(schema)


async def main():
    async with AsyncWebCrawler(verbose=True) as crawler:
        result = await crawler.arun(
            url="https://www.qidian.com/rank/",
            extraction_strategy=strategy,
            cache_mode=CacheMode.BYPASS,
        )
                
        if not result.success:
            logger.error(f"Extraction failed: {result.error_message}")
            return
        
        novels = json.loads(result.extracted_content)

            
if __name__ == "__main__":
    asyncio.run(main())
