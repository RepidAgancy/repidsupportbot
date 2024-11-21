import asyncio
import os

from aiogram import Bot, Dispatcher, types,F
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from dotenv import load_dotenv, find_dotenv
from aiogram.fsm.state import State, StatesGroup

load_dotenv(find_dotenv())
# Replace 'YOUR_BOT_TOKEN' with your bot's token from @BotFather

# Initialize bot and dispatcher
bot = Bot(token=os.getenv('BOT_TOKEN'))
dp = Dispatcher()

# Complaint states
class ComplaintStates(StatesGroup):
    complaint = State()
    phone = State()
    name = State()

    # Texts for prompts
    texts = {
        'ComplaintStates:complaint': 'Nima muamongiz bor batafsil yozing:',
        'ComplaintStates:phone': 'Aloqa uchun telefon raqamingizni kirirting:',
        'ComplaintStates:name': "To'liq ismingiz kiriting:",
    }

keyboard_phone = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text='Telefon raqam ☎️', request_contact=True)],
        ],resize_keyboard=True,
    input_field_placeholder="Sizning telefon raqamingiz"
    )


# Complaint start
@dp.message(Command("start"))
async def start_complaint(message: types.Message, state: FSMContext):
    await message.answer(
        ComplaintStates.texts['ComplaintStates:complaint'],

    )
    await state.set_state(ComplaintStates.complaint)

# Cancel process
@dp.message(StateFilter("*"), Command('cancel'))
async def cancel_complaint(message: types.Message, state: FSMContext):
    current_state = await state.get_state()

    if current_state is None:
        return

    await state.clear()
    await message.answer("Complaint process has been canceled.", )

# Back command
@dp.message(StateFilter("*"),Command('back'))
async def back_complaint(message: types.Message, state: FSMContext):
    current_state = await state.get_state()

    if current_state == ComplaintStates.complaint:
        await message.answer("Siz birinchi qadamdasiz orqaga o'ta olmaysiz!!!")
        return

    previous = None
    for step in ComplaintStates.__all_states__:
        if step.state == current_state:
            await state.set_state(previous)
            await message.answer(
                ComplaintStates.texts[previous.state],
            )
            return
        previous = step


# Complaint input
@dp.message(ComplaintStates.complaint, F.text)
async def handle_complaint(message: types.Message, state: FSMContext):
    await state.update_data(complaint=message.text)
    await message.answer(
        ComplaintStates.texts['ComplaintStates:phone'],
        reply_markup=keyboard_phone
    )
    await state.set_state(ComplaintStates.phone)

# Phone input
@dp.message(ComplaintStates.phone)
async def handle_phone(message: types.Message, state: FSMContext):
    await state.update_data(phone=message.contact.phone_number)
    await message.answer(
        ComplaintStates.texts['ComplaintStates:name'],
    )
    await state.set_state(ComplaintStates.name)

# Name input
@dp.message(ComplaintStates.name, F.text)
async def handle_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    data = await state.get_data()

    # Sending complaint to admin (replace with specific admin ID)
    admin_id = 5714872865
    await bot.send_message(
        admin_id,
        f"📩 Yangi Ariza:\n\n"
        f"✉ Ariza matini: {data['complaint']}\n"
        f"📞 Telefon raqam: {data['phone']}\n"
        f"👤 Ism Familiyasi: {data['name']}"
    )

    # Notify the user
    await message.answer(
        "Rahmat, murojat uchun siz bilan 24 soat ichida bog'lanishadi"
    )
    await state.clear()



# Run bot
async def main():  # No external routers
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
