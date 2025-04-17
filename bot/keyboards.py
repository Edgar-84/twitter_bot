import asyncio

from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from datetime import datetime
import calendar
from db.facade import DB

db = DB()


async def get_languages_kb(update: bool = False):
    languages = {
                 "uk": "🇺🇦",
                 "en": "🇬🇧",
                 "es": "🇪🇸",
                 "fr": "🇫🇷",
                 "de": "🇩🇪",
                 "zh-cn": "🇨🇳",
                 "it": "🇮🇹",
                 }

    buttons = []
    first_row_buttons = [InlineKeyboardButton(text=flag, callback_data=code) for code, flag in languages.items()]
    last_row_button = [InlineKeyboardButton(text='⏩', callback_data='proceed')]
    if update:
        last_row_button = [InlineKeyboardButton(text='⏪', callback_data='back')]

    buttons.append(first_row_buttons)
    buttons.append(last_row_button)

    kb = InlineKeyboardMarkup(inline_keyboard=buttons)

    return kb

async def get_fitness_choices(language_code: str):
    choices = {
    "en": ["Unfit and significantly overweight 🍩", "Unfit 🛋️", "Moderately fit 🚶", "Fit 🏃", "Very fit 🏋️"],
    "es": ["Fuera de forma y con sobrepeso significativo 🍩", "Fuera de forma 🛋️", "Moderadamente en forma 🚶",
           "En forma 🏃", "Muy en forma 🏋️"],
    "fr": ["En mauvaise forme et significativement en surpoids 🍩", "En mauvaise forme 🛋️", "Modérément en forme 🚶",
           "En forme 🏃", "Très en forme 🏋️"],
    "de": ["Unfit und stark übergewichtig 🍩", "Unfit 🛋️", "Mäßig fit 🚶", "Fit 🏃", "Sehr fit 🏋️"],
    "uk": ["Не в формі і значно з надмірною вагою 🍩", "Не в формі 🛋️", "Помірно в формі 🚶", "У формі 🏃",
           "Дуже у формі 🏋️"],
    "zh-cn": ["不健康且严重超重 🍩", "不健康 🛋️", "中等健康水平 🚶", "健康 🏃", "非常健康 🏋️"],
    "it": ["Fuori forma e significativamente in sovrappeso 🍩", "Fuori forma 🛋️", "Moderatamente in forma 🚶",
           "In forma 🏃", "Molto in forma 🏋️"]
    }

    language_texts = choices.get(language_code)
    language_texts.append("⏪")
    callbacks = ["unfit_and_overweight", "unfit", "moderately_fit", "fit", "very_fit", "back"]

    buttons_data = dict(zip(language_texts, callbacks))
    buttons = [[InlineKeyboardButton(text=text, callback_data=callback)] for text, callback in buttons_data.items()]

    kb = InlineKeyboardMarkup(inline_keyboard=buttons)

    return kb

async def get_gender_choices(language_code: str):
    choices = {
    "en": ["Male 👨", "Female 👩", "Male or Female 👨‍👩"],
    "es": ["Masculino 👨", "Femenino 👩", "Masculino o Femenino 👨‍👩"],
    "fr": ["Homme 👨", "Femme 👩", "Homme ou Femme 👨‍👩"],
    "de": ["Männlich 👨", "Weiblich 👩", "Männlich oder Weiblich 👨‍👩"],
    "uk": ["Чоловік 👨", "Жінка 👩", "Чоловік або Жінка 👨‍👩"],
    "zh-cn": ["男性 👨", "女性 👩", "男性或女性 👨‍👩"],
    "it": ["Maschio 👨", "Femmina 👩", "Maschio o Femmina 👨‍👩"]
    }

    language_texts = choices.get(language_code)
    language_texts.append("⏪")
    callbacks = ["male", "female", "male_or_female", "back"]

    buttons_data = dict(zip(language_texts, callbacks))
    buttons = [[InlineKeyboardButton(text=text, callback_data=callback)] for text, callback in buttons_data.items()]

    kb = InlineKeyboardMarkup(inline_keyboard=buttons)

    return kb

async def get_warm_up_cool_down_choices(language_code: str):
    choices = {
    "en": ["Include warm-up and cool down exercises ✅",
           "Do not include warm-up and cool down exercises ❌"],
    "es": ["Incluir ejercicios de calentamiento y enfriamiento ✅",
           "No incluir ejercicios de calentamiento y enfriamiento ❌"],
    "fr": ["Inclure des exercices de réchauffement et de récupération ✅",
           "Ne pas inclure des exercices de réchauffement et de récupération ❌"],
    "de": ["Aufwärm- und Abkühlübungen einbeziehen ✅",
           "Keine Aufwärm- und Abkühlübungen einbeziehen ❌"],
    "uk": ["Включити вправи на розігрів та охолодження ✅",
           "Не включати вправи на розігрів та охолодження ❌"],
    "zh-cn": ["包括热身和冷却运动 ✅",
              "不包括热身和冷却运动 ❌"],
    "it": ["Includere esercizi di riscaldamento e raffreddamento ✅",
           "Non includere esercizi di riscaldamento e raffreddamento ❌"]
    }

    language_texts = choices.get(language_code)
    language_texts.append("⏪")
    callbacks = ["include", "not_include", "back"]

    buttons_data = dict(zip(language_texts, callbacks))
    buttons = [[InlineKeyboardButton(text=text, callback_data=callback)] for text, callback in buttons_data.items()]

    kb = InlineKeyboardMarkup(inline_keyboard=buttons)

    return kb

async def get_confirm_health_state_kb():
    buttons = []

    back_confirm_buttons = [InlineKeyboardButton(text="⏪", callback_data="back"),
                            InlineKeyboardButton(text="✅", callback_data="confirm")]

    buttons.append(back_confirm_buttons)

    kb = InlineKeyboardMarkup(inline_keyboard=buttons)

    return kb

async def get_cancel_kb():
    buttons = [[InlineKeyboardButton(text="❌", callback_data="cancel")]]

    kb = InlineKeyboardMarkup(inline_keyboard=buttons)

    return kb

async def get_workout_level_kb(language_code: str):
    choices = {
    "en": ["Simple exercises for a beginner 🧘",
           "Exercises of average complexity 🏃‍♂️",
           "Technically complex exercises 🏋️‍♀️"],
    "es": ["Ejercicios sencillos para principiantes 🧘",
           "Ejercicios de complejidad media 🏃‍♂️",
           "Ejercicios técnicamente complejos 🏋️‍♀️"],
    "fr": ["Exercices simples pour débutants 🧘",
           "Exercices de complexité moyenne 🏃‍♂️",
           "Exercices techniquement complexes 🏋️‍♀️"],
    "de": ["Einfache Übungen für Anfänger 🧘",
           "Übungen mittlerer Komplexität 🏃‍♂️",
           "Technisch komplexe Übungen 🏋️‍♀️"],
    "uk": ["Прості вправи для початківців 🧘",
           "Вправи середньої складності 🏃‍♂️",
           "Технічно складні вправи 🏋️‍♀️"],
    "zh-cn": ["初学者简单锻炼 🧘",
              "中等复杂度的锻炼 🏃‍♂️",
              "技术复杂的锻炼 🏋️‍♀️"],
    "it": ["Esercizi semplici per principianti 🧘",
           "Esercizi di difficoltà media 🏃‍♂️",
           "Esercizi tecnicamente complessi 🏋️‍♀️"]
    }

    language_texts = choices.get(language_code)
    callbacks = ["simple", "average", "complex"]

    buttons_data = dict(zip(language_texts, callbacks))
    buttons = [[InlineKeyboardButton(text=text, callback_data=callback)] for text, callback in buttons_data.items()]
    cancel_back_button = [InlineKeyboardButton(text="⏪", callback_data="back")]

    buttons.append(cancel_back_button)
    kb = InlineKeyboardMarkup(inline_keyboard=buttons)

    return kb

async def get_workout_goal_kb(language_code: str):
    choices = {
    "en": [
        "Weight Loss 🏃‍♂️",
        "Building Muscle 💪",
        "Developing Muscle Tone 🏃‍♀️",
        "Cardiovascular Health ❤️",
        "Core Strength 🧘",
        "Strength 🏋️",
        "Endurance 🚴‍♂️",
        "Improving Flexibility 🤸‍♂️",
        "Improving Mobility 🚶‍♂️",
        "Functional Fitness ⚙️"
    ],
    "es": [
        "Pérdida de peso 🏃‍♂️",
        "Desarrollar músculo 💪",
        "Desarrollar tono muscular 🏃‍♀️",
        "Salud cardiovascular ❤️",
        "Fuerza del núcleo 🧘",
        "Fuerza 🏋️",
        "Resistencia 🚴‍♂️",
        "Mejorar flexibilidad 🤸‍♂️",
        "Mejorar movilidad 🚶‍♂️",
        "Fitness funcional ⚙️"
    ],
    "fr": [
        "Perte de poids 🏃‍♂️",
        "Renforcement musculaire 💪",
        "Développement du tonus musculaire 🏃‍♀️",
        "Santé cardiovasculaire ❤️",
        "Force du tronc 🧘",
        "Force 🏋️",
        "Endurance 🚴‍♂️",
        "Amélioration de la flexibilité 🤸‍♂️",
        "Amélioration de la mobilité 🚶‍♂️",
        "Fitness fonctionnel ⚙️"
    ],
    "de": [
        "Gewichtsverlust 🏃‍♂️",
        "Muskelaufbau 💪",
        "Muskeltonus entwickeln 🏃‍♀️",
        "Herz-Kreislauf-Gesundheit ❤️",
        "Rumpfstärke 🧘",
        "Stärke 🏋️",
        "Ausdauer 🚴‍♂️",
        "Flexibilität verbessern 🤸‍♂️",
        "Mobilität verbessern 🚶‍♂️",
        "Funktionelles Fitness ⚙️"
    ],
    "uk": [
        "Втрата ваги 🏃‍♂️",
        "Нарощування м'язів 💪",
        "Розвиток м'язового тонусу 🏃‍♀️",
        "Серцево-судинне здоров'я ❤️",
        "Сила кору 🧘",
        "Сила 🏋️",
        "Витривалість 🚴‍♂️",
        "Покращення гнучкості 🤸‍♂️",
        "Покращення мобільності 🚶‍♂️",
        "Функціональний фітнес ⚙️"
    ],
    "zh-cn": [
        "减肥 🏃‍♂️",
        "增肌 💪",
        "发展肌肉线条 🏃‍♀️",
        "心血管健康 ❤️",
        "核心力量 🧘",
        "力量 🏋️",
        "耐力 🚴‍♂️",
        "提高柔韧性 🤸‍♂️",
        "提高灵活性 🚶‍♂️",
        "功能性健身 ⚙️"
    ],
    "it": [
        "Perdita di peso 🏃‍♂️",
        "Costruzione muscolare 💪",
        "Sviluppo del tono muscolare 🏃‍♀️",
        "Salute cardiovascolare ❤️",
        "Forza del core 🧘",
        "Forza 🏋️",
        "Resistenza 🚴‍♂️",
        "Migliorare la flessibilità 🤸‍♂️",
        "Migliorare la mobilità 🚶‍♂️",
        "Fitness funzionale ⚙️"
    ]
    }

    language_texts = choices.get(language_code)
    callbacks = ["weight_loss", "building_muscle", "developing_muscle_tone", "cardiovascular_health", "core_strength",
                "strength", "endurance", "improving_flexibility", "improving_mobility", "functional_fitness"]

    buttons_data = dict(zip(language_texts, callbacks))
    buttons = [[InlineKeyboardButton(text=text, callback_data=callback)] for text, callback in buttons_data.items()]
    cancel_back_button = [InlineKeyboardButton(text="⏪", callback_data="back")]

    buttons.append(cancel_back_button)
    kb = InlineKeyboardMarkup(inline_keyboard=buttons)

    return kb

async def get_workout_focus_kb(language_code: str, state: FSMContext):
    state_data = await state.get_data()
    chosen_focuses = state_data.get("chosen_focuses", [])

    choices = {
               "en": ["Full Body", "Abs", "Legs", "Upper Body", "Arms", "Lower Body", "Back", "Glutes", "Shoulders",
                      "Pecks"],
               "es": ["Cuerpo completo", "Abdominales", "Piernas", "Parte superior", "Brazos", "Parte inferior",
                      "Espalda", "Glúteos", "Hombros", "Pectorales"],
               "fr": ["Corps entier", "Abdos", "Jambes", "Haut du corps", "Bras", "Bas du corps", "Dos", "Fessiers",
                      "Épaules", "Pectoraux"],
               "de": ["Ganzer Körper", "Bauch", "Beine", "Oberkörper", "Arme", "Unterkörper", "Rücken", "Gesäß",
                      "Schultern", "Brustmuskeln"],
               "uk": ["Все тіло", "Прес", "Ноги", "Верхня частина тіла", "Руки", "Нижня частина тіла", "Спина",
                      "Сідниці", "Плечі", "Грудні м’язи"],
               "zh-cn": ["全身", "腹肌", "腿", "上身", "手臂", "下半身", "背部", "臀部", "肩膀", "胸肌"],
               "it": ["Tutto il corpo", "Addominali", "Gambe", "Parte superiore", "Braccia", "Parte inferiore",
                      "Schiena", "Glutei", "Spalle", "Pettorali"]
               }

    language_texts = choices.get(language_code)
    callbacks = ["full_body", "abs", "legs", "upper_body", "arms", "lower_body", "back", "glutes", "shoulders", "pecks"]

    buttons_data = dict(zip(language_texts, callbacks))
    clear_buttons = []
    for text, callback in buttons_data.items():
        if callback in chosen_focuses:
            text += " ✅"
        button = InlineKeyboardButton(text=text, callback_data=callback)
        clear_buttons.append(button)
    buttons = [clear_buttons[i:i + 2] for i in range(0, len(clear_buttons), 2)]

    last_row_buttons = [InlineKeyboardButton(text="⏪", callback_data="back_"),
                        InlineKeyboardButton(text="⏩", callback_data="proceed")]

    buttons.append(last_row_buttons)

    kb = InlineKeyboardMarkup(inline_keyboard=buttons)

    return kb

async def get_workout_equipment_kb(language_code):
    choices = {
               "en": ["Dumbbells", "Resistance Bands", "Yoga Mat", "Kettlebells", "Bench", "Fitness Ball",
                      "Medicine Ball", "TRX", "Battle Rope", "Half Fitness Ball"],
               "es": ["Mancuernas", "Bandas de resistencia", "Esterilla de yoga", "Pesas rusas", "Banco",
                      "Pelota de fitness", "Balón medicinal", "TRX", "Cuerda de batalla", "Media pelota de fitness"],
               "fr": ["Haltères", "Bandes de résistance", "Tapis de yoga", "Kettlebells", "Banc", "Balle de fitness",
                      "Médecine-ball", "TRX", "Corde de combat", "Demi-balle de fitness"],
               "de": ["Hanteln", "Widerstandsbänder", "Yogamatte", "Kettlebells", "Bank", "Fitnessball", "Medizinball",
                      "TRX", "Battle Rope", "Halber Fitnessball"],
               "uk": ["Гантелі", "Еспандери", "Килимок для йоги", "Гирі", "Лава", "Фітнес-м'яч", "Медичний м'яч",
                      "TRX", "Бойова мотузка", "Напівсфера для фітнесу"],
               "zh-cn": ["哑铃", "弹力带", "瑜伽垫", "壶铃", "健身椅", "健身球", "医学球", "TRX", "战绳", "半健身球"],
               "it": ["Manubri", "Bande elastiche", "Tappetino yoga", "Kettlebell", "Panchina", "Palla fitness",
                      "Palla medica", "TRX", "Corda da combattimento", "Mezza palla fitness"]
               }

    language_texts = choices.get(language_code)
    callbacks = ["dumbbells", "resistance_bands", "yoga_mat", "kettlebells", "bench", "fitness_ball", "medicine_ball",
                 "trx", "battle_rope", "half_fitness_ball"]

    buttons_data = dict(zip(language_texts, callbacks))
    buttons = [[InlineKeyboardButton(text=text, callback_data=callback)] for text, callback in buttons_data.items()]
    cancel_back_button = [InlineKeyboardButton(text="⏪", callback_data="back")]

    buttons.append(cancel_back_button)
    kb = InlineKeyboardMarkup(inline_keyboard=buttons)

    return kb

async def get_update_kb(language_code: str):
    choices = {
               "en": ["Language", "Fitness Level", "Workout Level", "Sex", "Warmup and Cooldown"],
               "es": ["Idioma", "Nivel de condición física", "Nivel de entrenamiento", "Sexo", "Calentamiento y Enfriamiento"],
               "fr": ["Langue", "Niveau de forme physique", "Niveau d'entraînement", "Sexe", "Échauffement et Récupération"],
               "de": ["Sprache", "Fitnesslevel", "Workout Level", "Geschlecht", "Aufwärmen und Abkühlen"],
               "uk": ["Мова", "Рівень фізичної підготовки", "Рівень тренування", "Стать", "Розминка та Завершення"],
               "zh-cn": ["语言", "健身水平", "锻炼级别", "性别", "热身和冷却"],
               "it": ["Lingua", "Livello di forma fisica", "Livello di allenamento", "Sesso", "Riscaldamento e Defaticamento"]
               }

    language_texts = choices.get(language_code)
    callbacks = ["chosen_language", "fitness_level", "workout_level", "gender", "warm_up_cool_down"]

    buttons_data = dict(zip(language_texts, callbacks))
    clear_buttons = [InlineKeyboardButton(text=text, callback_data=callback) for text, callback in buttons_data.items()]
    buttons = [clear_buttons[i:i + 2] for i in range(0, len(clear_buttons), 2)]
    cancel_button = [InlineKeyboardButton(text="❌", callback_data="cancel")]

    buttons.append(cancel_button)
    kb = InlineKeyboardMarkup(inline_keyboard=buttons)

    return kb

async def get_proceed_to_workout_kb(language_code: str, focus_step: bool = False, equipment_step: bool = False):
    choices = {
    "en": ["Workout Now", "Choose Focus", "Choose Equipment"],
    "es": ["Comienza El Entrenamiento Ahora", "Elige El Enfoque Del Entrenamiento", 
           "Elige El Equipo"],
    "fr": ["Commencez L'Entraînement Maintenant", "Choisissez Le Focus De L'Entraînement", 
           "Choisissez L'Équipement"],
    "de": ["Jetzt Mit Dem Training Beginnen", "Fokus Des Trainings Auswählen", 
           "Wählen Sie Die Ausrüstung"],
    "uk": ["Розпочати Тренування Зараз", "Обрати Фокус Тренування", 
           "Обрати Обладнання"],
    "zh-cn": ["立即开始锻炼", "选择锻炼重点", "选择设备"],
    "it": ["Inizia L'Allenamento Ora", "Scegli Il Focus Dell'Allenamento", 
           "Scegli L'Attrezzatura"]
    }


    callbacks = ["proceed_to_workout", "workout_focus", "equipment"]

    language_texts = choices.get(language_code)
    buttons_data = dict(zip(callbacks, language_texts))

    if focus_step:
        del buttons_data["equipment"]
    else:
        del buttons_data["workout_focus"]

    buttons = []
    first_row_buttons = [InlineKeyboardButton(text=text, callback_data=callback) for callback, text in buttons_data.items()]


    buttons.append(first_row_buttons)

    kb = InlineKeyboardMarkup(inline_keyboard=buttons)

    return kb

