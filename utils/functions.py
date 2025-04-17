from aiogram.fsm.context import FSMContext
from bot.main import db


async def get_user_language(language_code: str):
    supported_languages = {
                           "en": ["English", "en"],
                           "es": ["Español", "es"],
                           "fr": ["Français", "fr"],
                           "de": ["Deutsch", "de"],
                           "uk": ["Українська", "uk"],
                           "zh-cn": ["中文 (简体)", "zh-cn"],
                           "it": ["Italiano", "it"],
                           "ru": ["Русский", "ru"],
                           }

    user_language = supported_languages.get(language_code, ["English", "en"])

    return user_language


async def get_language_from_state(state: FSMContext):
    state_data = await state.get_data()
    language_code = state_data["user_language_code"]

    return language_code


async def update_chosen_focuses(state: FSMContext, chosen_focus: str):
    state_data = await state.get_data()
    chosen_focuses = state_data.get("chosen_focuses", [])
    if chosen_focus in chosen_focuses:
        chosen_focuses.remove(chosen_focus)
    else:
        chosen_focuses.append(chosen_focus)

    await state.update_data(chosen_focuses=chosen_focuses)

async def get_placeholders(goal: str,
                           workout_level: str,
                           focuses: list,
                           warm_up_cool_down: bool,
                           fit_level: str,
                           gender: str):

    fitness_levels = dict(zip(
        ["unfit_and_overweight", "unfit", "moderately_fit", "fit", "very_fit"],
        ["Unfit and significantly overweight", "Unfit", "Moderately fit", "Fit", "Very fit"]
    ))

    genders = dict(zip(
        ["male", "female", "male_or_female"],
        ["Male", "Female", "Male or Female"]
    ))

    warmup_cooldown = dict(zip(
        [True, False],
        ["Include warm-up and cool down exercises", "Do not include warm-up and cool down exercises"]
    ))

    exercise_complexity = dict(zip(
        ["simple", "average", "complex"],
        ["Simple exercises for a beginner", "Exercises of average complexity",
         "Technically complex exercises"]
    ))

    goals = dict(zip(
        ["weight_loss", "building_muscle", "developing_muscle_tone", "cardiovascular_health", "core_strength",
         "strength", "endurance", "improving_flexibility", "improving_mobility", "functional_fitness"],
        ["Weight Loss", "Building Muscle", "Developing Muscle Tone", "Cardiovascular Health",
         "Core Strength", "Strength", "Endurance", "Improving Flexibility",
         "Improving Mobility", "Functional Fitness"]
    ))

    body_parts = dict(zip(
        ["full_body", "abs", "legs", "upper_body", "arms", "lower_body", "back", "glutes", "shoulders", "pecks"],
        ["Full Body", "Abs", "Legs", "Upper Body", "Arms", "Lower Body", "Back", "Glutes", "Shoulders", "Pecks"]
    ))

    equipment = dict(zip(
        ["dumbbells", "resistance_bands", "yoga_mat", "kettlebells", "bench", "fitness_ball", "medicine_ball",
         "trx", "battle_rope", "half_fitness_ball"],
        ["Dumbbells", "Resistance Bands", "Yoga Mat", "Kettlebells", "Bench", "Fitness Ball", "Medicine Ball", "TRX",
         "Battle Rope", "Half Fitness Ball"]
    ))

    pretty_fitness_level = fitness_levels.get(fit_level)
    pretty_goal = goals.get(goal)
    pretty_workout_level = exercise_complexity.get(workout_level)
    pretty_warm_up_cool_down = warmup_cooldown.get(warm_up_cool_down)
    pretty_gender = genders.get(gender)
    pretty_focuses_data = []
    if focuses:
        for focus in focuses:
            pretty_focuses_data.append(body_parts.get(focus))

    pretty_focuses = ", ".join(pretty_focuses_data)
    pretty_data = {"fitness_level": pretty_fitness_level,
                   "goal": pretty_goal,
                   "workout_level": pretty_workout_level,
                   "warmup_cooldown": pretty_warm_up_cool_down,
                   "gender": pretty_gender,
                   "focuses": pretty_focuses}

    return pretty_data

async def update_user_settings(state: FSMContext, user_id: int):
    state_data = await state.get_data()
    update_option = state_data["update_option"]
    update_value = state_data["update_value"]
    if update_option == "warm_up_cool_down":
        mapper = {"include": True,
                  "not_include": False}
        update_value = mapper.get(update_value)
    update_data = {update_option: update_value}

    await db.user_crud.update(id_=user_id, **update_data)
