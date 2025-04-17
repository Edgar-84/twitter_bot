import time
import asyncio
from typing import Tuple
from datetime import datetime

from apify_client import ApifyClientAsync


class ApifyService:
    ACTOR_PROFILE_X_ID = "apidojo/twitter-user-scraper"
    ACTOR_POSTS_X_ID = "apidojo/twitter-scraper-lite"

    def __init__(self, apify_key: str):
        self.__apify_key = apify_key
        self.apify_client = ApifyClientAsync(self.__apify_key)

    async def run_get_x_posts(
            self,
            x_profile_name: str,
            max_items: int = 20,
            start_date: datetime = None,
            end_date: datetime = None
        ) -> list[dict]:
        """
        Get information about posts for selected X profile
        """
        try:
            start_str = start_date.strftime('%Y-%m-%d') if start_date else datetime.now().strftime('%Y-%m-%d')
            end_str = end_date.strftime('%Y-%m-%d') if end_date else datetime.now().strftime('%Y-%m-%d')

            run_input = {
                "end": end_str,
                "maxItems": max_items,
                "sort": "Latest",
                "start": start_str,
                "startUrls": [
                    f"https://x.com/{x_profile_name}"
                ]
            }

            # Start an Actor and wait for it to finish.
            actor_client = self.apify_client.actor(self.ACTOR_POSTS_X_ID)
            call_result = await actor_client.call(run_input=run_input)

            if call_result is None:
                print(f'Actor [{self.ACTOR_POSTS_X_ID}] run failed.')
                return []

            # Fetch results from the Actor run's default dataset.
            dataset_client = self.apify_client.dataset(call_result['defaultDatasetId'])
            list_items_result = await dataset_client.list_items()
            # print(f"Type DATASET: {type(list_items_result)}")
            # print(f'Dataset: {list_items_result}')
            posts = list_items_result.items
            if len(posts) == 1:
                if posts[0].get("noResults") is True:
                    print(f"No posts found for {x_profile_name}: {posts[0]}")
                    return []
            
            results = []
            for post in posts:
                # print(f"🔹 Post:\n{post}")
                results.append({
                    "content": post["text"],
                    "url": post["url"],
                    "timestamp": datetime.strptime(post["createdAt"], '%a %b %d %H:%M:%S %z %Y')
                })

            return results
        
        except Exception as ex:
            print(f"Critical mistake during work with 'run_get_x_posts': {ex}")
            return []


    async def run_get_x_followings_actor(self, x_profile_name: str, max_items: int = 20) -> list[dict]:
        """
        Get information about followings for selected X profile
        """
        
        try:
            run_input = {
                "customMapFunction": "(object) => { return {...object} }",
                "getFollowers": False,
                "getFollowing": True,
                "getRetweeters": False,
                "includeUnavailableUsers": False,
                "maxItems": max_items,
                "twitterHandles": [
                    x_profile_name,
                ]
            }

            # Start an Actor and wait for it to finish.
            actor_client = self.apify_client.actor(self.ACTOR_PROFILE_X_ID)
            call_result = await actor_client.call(run_input=run_input)

            if call_result is None:
                print(f'Actor [{self.ACTOR_PROFILE_X_ID}] run failed.')
                return []
            
            # Fetch results from the Actor run's default dataset.
            dataset_client = self.apify_client.dataset(call_result['defaultDatasetId'])
            list_items_result = await dataset_client.list_items()
            # print(f"Type DATASET: {type(list_items_result)}")
            # print(f'Dataset: {list_items_result}')
            followings = list_items_result.items
            if followings[0].get("noResults") is True:
                print(f"No followingss found for {x_profile_name}: {followings[0]}")
                return []

            results = []
            for following in followings:
                # print(f"🔹 Following:\n{following}")
                results.append({
                    "username": following["userName"],
                    "full_name": following["name"],
                    "twitter_id": following["id"]
                })

            return results
        
        except Exception as ex:
            print(f"Critical mistake during work with 'run_get_x_followings_actor': {ex}")
            return []


# For tests

async def run_profile_task(profile_name: str, service: ApifyService) -> Tuple[str, float]:
    start = time.perf_counter()
    
    result = await service.run_get_x_posts(x_profile_name=profile_name, max_items=20)
    duration = time.perf_counter() - start
    print(f"[{profile_name}] Completed in {duration:.2f} seconds")
    return result, duration


async def run_followings_task(profile_name: str, service: ApifyService) -> Tuple[str, float]:
    start = time.perf_counter()
    
    result = await service.run_get_x_followings_actor(x_profile_name=profile_name, max_items=50)
    duration = time.perf_counter() - start
    print(f"[{profile_name}] Completed in {duration:.2f} seconds")
    return result, duration


async def main():
    api_key = ""
    overall_start = time.perf_counter()
    service = ApifyService(apify_key=api_key)

    profiles = ["elonmusk"]
    # # For check Posts
    # tasks = [run_profile_task(profile, service) for profile in profiles]

    # For check Followings
    tasks = [run_followings_task(profile, service) for profile in profiles]

    results = await asyncio.gather(*tasks)

    overall_duration = time.perf_counter() - overall_start

    print("\n=== Results ===")
    for profile, (result, duration) in zip(profiles, results):
        print(f"{profile}: duration = {duration:.2f}s, result = {result}")

    print(f"\nTotal time for all tasks: {overall_duration:.2f} seconds")

if __name__ == "__main__":
    asyncio.run(main())
