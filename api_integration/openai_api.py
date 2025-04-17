import asyncio
import re
from openai import OpenAI
import logging
import json


class ChatGPT:
    def __init__(self, api_key, assistant_id=None):
        self.api_key = api_key
        self.assistant_id = assistant_id
        self.client = OpenAI(api_key=self.api_key)
        self.assistant = self.client.beta.assistants.retrieve(assistant_id=self.assistant_id)


    async def generate_workout(self, prompt: str):
        thread_id = await self.__create_thread()
        response_from_openai = await self.__send_prompt(prompt=prompt, thread_id=thread_id)

        return response_from_openai

    async def transcribe_audio_to_text(self, audio_file_path: str) -> str:
        with open(audio_file_path, "rb") as audio_file:
            transcription = self.client.audio.transcriptions.create(
                model="whisper-1", 
                file=audio_file
            )
        print(f"Text for file: {audio_file_path} is:\n{transcription.text}")
        return transcription.text

    async def __create_thread(self):
        thread = self.client.beta.threads.create()

        thread_id = thread.id

        return thread_id

    async def __send_prompt(self, prompt: str, thread_id: str):
        self.client.beta.threads.messages.create(
            thread_id=thread_id,
            role="user",
            content=prompt,
        )
        run = self.client.beta.threads.runs.create_and_poll(
            thread_id=thread_id,
            assistant_id=self.assistant.id
        )

        if run.status == "completed":
            messages = self.client.beta.threads.messages.list(thread_id=thread_id)

            for message in messages:
                for component in message.content:
                    if component.type == "text" and message.role == "assistant":
                        response_json = json.loads(component.text.value)
                        # print(response_json)
                        return response_json
        else:
            logging.info("Run did not complete successfully.")