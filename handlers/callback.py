from aiogram.utils import callback_data as cb_data

# === Создание фабрики колбэков ===
button_callback = cb_data.CallbackData('button', 'action', 'extra_param')
