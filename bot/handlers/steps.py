import os
import time
import uuid
from aiogram.types import FSInputFile
import asyncio
import aiohttp
import tiktoken
import bot.texts as texts
import bot.keyboards as keyboards
from aiogram.types import Message, CallbackQuery, Voice
from aiogram.fsm.context import FSMContext
import bot.states as states
from bot.main import gpt, youtube, db, bot, apify_service
from bot.states import TwitterSummaryState
from bot.texts import warm_up_cool_down_message, exercise_text
import bot.filters as filters
from aiogram.dispatcher.router import Router
from utils.functions import get_user_language, get_language_from_state, get_placeholders, update_user_settings
from aiogram.filters.command import Command
import re
from datetime import datetime, timedelta, timezone
from bot.settings import TELEGRAM_CHANNEL_ID, BOT_TOKEN



async def count_tokens(text: str) -> int:
    """Count tokens in text"""
    encoding = tiktoken.get_encoding("cl100k_base")
    tokens = encoding.encode(text)
    return len(tokens)


async def send_telegram_message_to_channel(text: str):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        payload = {
            "chat_id": TELEGRAM_CHANNEL_ID,
            "text": text,
            "parse_mode": "HTML"
        }
        
        async with aiohttp.ClientSession() as session:
            await session.post(url, json=payload, timeout=10)

    except Exception as e:
        print(f"Failed to send message to channel: {e}")


async def process_voice_message(message: Message) -> str:
    voice_file = await message.bot.get_file(message.voice.file_id)
    voice_path = f"voice_messages/{message.voice.file_id}.ogg"
    os.makedirs("voice_messages", exist_ok=True)
    await message.bot.download_file(voice_file.file_path, voice_path)
    print(f"Voice message saved: {voice_path}")
    text = await gpt.transcribe_audio_to_text(voice_path)
    os.remove(voice_path)
    return text

async def get_posts_created_today(posts: list[dict]) -> list[dict]:
    """
    Get X posts created today
    """
    now = datetime.now(tz=timezone.utc)
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)

    filtered_posts_today = [
        post for post in posts
        if isinstance(post, dict)
        and isinstance(post.get("timestamp"), datetime)
        and post["timestamp"] >= today_start
    ]
    return filtered_posts_today


async def get_posts_created_24h_ago(posts: list[dict]) -> list[dict]:
    """
    Get X posts created 24 hours ago
    """
    now = datetime.now(tz=timezone.utc)
    last_24h = now - timedelta(hours=24)

    filtered_posts_24h = [
        post
        for result in posts if result
        for post in result
        if post["timestamp"] >= last_24h
    ]
    return filtered_posts_24h


async def save_posts_to_txt(posts: list[dict]) -> str:
    filename = f"{uuid.uuid4().hex}.txt"
    filepath = f"/tmp/{filename}"

    with open(filepath, "w", encoding="utf-8") as f:
        for i, post in enumerate(posts, start=1):
            f.write(f"Post {i}:\n{post['content']}\n\n")

    return filepath


class UserRegistrationSteps:
    @staticmethod
    async def final_registration_step(message: Message, state: FSMContext):
        user_language_code = message.from_user.language_code

        user_data = {"id": message.from_user.id,
                     "username": message.from_user.username,
                     "first_name": message.from_user.first_name,
                     "last_name": message.from_user.last_name,
                     "chosen_language": user_language_code}

        await db.user_crud.create(**user_data)
        await state.update_data({f"user_{message.from_user.id}": user_data})
        await state.clear()
        await SummaryCreationSteps.get_profile_info_step(message, state)


class SummaryCreationSteps:
    @staticmethod
    async def validate_message_content(message: Message, state: FSMContext) -> bool:
        user_id = message.from_user.id
        data = await state.get_data()
        user_info = data.get(f"user_{user_id}", {})
        if not user_info:
            # print(f"Not find user in state in 'get_workout_info_step'")
            user = await db.user_crud.read(id_=user_id)
            user_info = {
                "id": user.id,
                "username": user.username,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "chosen_language": user.chosen_language
            }
            await state.update_data({f"user_{user_id}": user_info})

        language_code = user_info.get("chosen_language", "en")

        # Check requests
        requests_count = await db.user_request_crud.get_requests_count(user_id=user_id)
        print(f"Requests count: {requests_count}")
        if requests_count >= 10:
            message_text = texts.too_many_requests_message.get(language_code)
            await message.answer(text=message_text)
            await state.clear()
            return False

        if message.voice:
            await message.answer(text="Voice messages are not supported")
            await state.clear()
            return False
            # text = await process_voice_message(message)
        else:
            text = message.text.strip()

        # token_count = await count_tokens(text)
        # print(f"Token count: {token_count}, for text: {text}")
        # if token_count > 200:
        #     error_text = texts.too_long_request.get(language_code)
        #     await message.answer(error_text)
        #     await state.clear()
        #     return False

        return text

    @staticmethod
    async def generate_summary(message: Message, state: FSMContext, instruction: str):
        user_id = message.from_user.id
        data = await state.get_data()
        user_info = data.get(f"user_{user_id}")
        language_code = user_info.get("chosen_language", "en")
        print(f"User message: {instruction}")
        MAX_FOLLOWINGS = 100  # Max Followings setting !
        MAX_POSTS = 10  # Max Posts setting !
        MAX_WORKERS = 15 # Max Apify workers for 1 user !
        GET_FOLLOWING_FROM_DB = False

        message_text = texts.generating_summary_text.get(language_code)
        await message.answer(text=message_text)
        await state.set_state(TwitterSummaryState.generating)
        # Save request
        await db.user_request_crud.save_request(user_id=user_id)

        # 1 Get Following profiles for X profile
        # --- Check profile in DB ---
        try:
            profile = await db.profile_crud.get_by_username(instruction)
            print(f"Profile found in DB: {profile}")

        except Exception as e:
            print(f"Failed to get profile from DB: {e}")
            profile = None

        if profile:
            friends_ids = await db.friend_crud.get_friends(profile.id)
            print(f"Friends ids: {friends_ids}")
            if friends_ids:
                start_time = time.perf_counter()
                # Get Profile objects of friends
                following_profiles = []
                for friend_id in friends_ids:
                    friend = await db.profile_crud.get(friend_id)
                    if friend:
                        following_profiles.append({
                            "username": friend.username,
                            "full_name": friend.full_name,
                            "twitter_id": friend.twitter_id
                        })
                duration = time.perf_counter() - start_time
                print(f"Get following profiles from DB: {duration:.2f}s")
                GET_FOLLOWING_FROM_DB = True

            else:
                # No friends saved, need to scrape
                print(f"No friends saved for user: {instruction}, need to scrape")
                following_profiles = await apify_service.run_get_x_followings_actor(x_profile_name=instruction, max_items=MAX_FOLLOWINGS)
        
        else:
            print(f"Profile not found in DB: {instruction}, need to scrape")
            following_profiles = await apify_service.run_get_x_followings_actor(x_profile_name=instruction, max_items=MAX_FOLLOWINGS)

        print(f"Following profiles len: {len(following_profiles)}")
        if len(following_profiles) == 0:
            await message.answer(text=f"No following profiles found for user: {instruction}")
            last_message = texts.finish_message.get(language_code)
            await message.answer(text=last_message)
            await state.set_state(TwitterSummaryState.selecting_profile)
            return

        else:
            # TODO save to DB following profiles
            if GET_FOLLOWING_FROM_DB is False:
                try:
                    print(f"Try to save following profiles to DB")
                    start_time = time.perf_counter()

                    # Save X profile separately, if it doesn't exist
                    profile = await db.profile_crud.get_by_username(instruction)
                    if not profile:
                        profile = await db.profile_crud.create(username=instruction, twitter_id=0)  # can be updated later

                    # Prepare list of all friends for bulk saving
                    all_profiles = following_profiles + [{
                        "username": instruction,
                        "full_name": None,
                        "twitter_id": profile.twitter_id
                    }]

                    friends_profile_ids = await db.profile_crud.bulk_save_profiles(all_profiles)
                    
                    duration = time.perf_counter() - start_time
                    print(f"Saved following profiles to DB: {duration:.2f}s")

                    await db.friend_crud.add_friends(profile.id, friends_profile_ids)

                except Exception as e:
                    print(f"Failed to save following profiles to DB: {e}")

            # Get information about posts (max workers 125!)
            semaphore = asyncio.Semaphore(MAX_WORKERS)

            async def limited_run(profile_username: str, max_items: int):
                """
                For limited run scraping posts
                """
                async with semaphore:
                    return await apify_service.run_get_x_posts(
                        x_profile_name=profile_username,
                        max_items=max_items
                    )
            
            tasks = [limited_run(profile["username"], MAX_POSTS) for profile in following_profiles]
            print(f"Prepare tasks count: {len(tasks)}, start searching posts ...")
            results_nested = await asyncio.gather(*tasks)
            posts = [post for result in results_nested if result for post in result]
            print(f"Find posts after scraping len: {len(posts)}")
    
            print(f"First post:\n{posts[0]}\n")
            print(f"Last post:\n{posts[-1]}\n")

            filtered_posts_today = await get_posts_created_today(posts)
            print(f"Filtered posts (today) len: {len(filtered_posts_today)}")
            # filtered_posts_24h_ago = await get_posts_created_24h_ago(posts)
            # print(f"Filtered posts (24h ago) len: {len(filtered_posts_24h_ago)}")

            # TODO save to DB posts
            if filtered_posts_today:
                filepath = await save_posts_to_txt(filtered_posts_today)
                file = FSInputFile(filepath)
                await message.answer_document(file, caption="All posts for today 📄")

            else:
                await message.answer("No posts found for today 😕")
            
            # for numb_post, post in enumerate(filtered_posts_today, start=1):
                
            #     post_content = f"Post {numb_post}:\n{post['content']}"
            #     print(f"Answer for client: {post_content}")
            #     await message.answer(text=post_content)
            

        last_message = texts.finish_message.get(language_code)
        await message.answer(text=last_message)
        await state.set_state(TwitterSummaryState.selecting_profile)

    @staticmethod
    async def get_profile_info_step(message: Message, state: FSMContext):
        user_id = message.from_user.id
        data = await state.get_data()
        user_info = data.get(f"user_{user_id}")
        if not user_info:
            print(f"Not find user in state in 'get_workout_info_step'")
            user = await db.user_crud.read(id_=user_id)
            user_info = {
                "id": user.id,
                "username": user.username,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "chosen_language": user.chosen_language
            }
            await state.update_data({f"user_{user_id}": user_info})

        language_code = user_info.get("chosen_language", "en")
        message_text = texts.start_messages.get(language_code)
        await message.answer(text=message_text)
        await state.set_state(TwitterSummaryState.selecting_profile)
