from langchain_core.tools import tool, Tool
from langchain_community.tools import (
    DuckDuckGoSearchResults,
    WikipediaQueryRun,
    YouTubeSearchTool,
)
from langchain_community.utilities import (
    DuckDuckGoSearchAPIWrapper,
    WikipediaAPIWrapper,
)
from langchain_community.tools.wikidata.tool import WikidataAPIWrapper, WikidataQueryRun
from langchain_community.tools.yahoo_finance_news import YahooFinanceNewsTool


def get_news_search_tool(region="in-en"):
    news_search_tool_wrapper = DuckDuckGoSearchAPIWrapper(
        region=region,
        time="d",
        max_results=5,
    )
    news_search_tool = Tool(
        name="latest_news_search",
        description="Useful for searching latest news articles.",
        func=DuckDuckGoSearchResults(
            api_wrapper=news_search_tool_wrapper,
            source="news",
        ).run,
    )
    return news_search_tool


def get_web_search_tool():
    news_search_tool = Tool(
        name="web_search",
        description="Useful for searching the web.",
        func=DuckDuckGoSearchResults().run,
    )
    return news_search_tool


wikipedia_tool = Tool(
    name="wikipedia_search",
    description="Useful for searching on Wikipedia.",
    func=WikipediaQueryRun(api_wrapper=WikipediaAPIWrapper()).run,
)


wikidata_tool = Tool(
    name="wikidata_search",
    description="Useful for searching on Wikidata.",
    func=WikidataQueryRun(api_wrapper=WikidataAPIWrapper()).run,
)


youtube_search_tool = Tool(
    name="youtube_search",
    description="Useful for searching on youtube.",
    func=YouTubeSearchTool().run,
)
