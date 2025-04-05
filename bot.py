from telegram.ext import ApplicationBuilder, MessageHandler, filters, CallbackQueryHandler, CommandHandler

from gpt import *
from util import *

# Bot token for authentication
TOKEN = "7656724252:AAFRRUrK3OIDOEkCZN6iEic7vSPfQUlGQE0"


# This is where we write our main bot code :)

# Command to start the bot
async def start(update, context):
    msg = load_message("main")  # Load the message for the main menu
    await send_photo(update, context, "main")  # Send the image for the main menu
    await send_text(update, context, msg)  # Send the text for the main menu
    await show_main_menu(update, context, {  # Show buttons for the main menu
        "start": "Main Bot Menu",
        "profile": "Generate Tinder Profile 😎",
        "opener": "Message for Dating 🥰",
        "message": "Messaging on Your Behalf 😈",
        "date": "Chat with Celebrities 🔥",
        "gpt": "Ask GPT Chat 🧠",
    })


# Command to start the GPT dialog
async def gpt(update, context):
    dialog.mode = "gpt"  # Set the mode to GPT
    await send_photo(update, context, name="gpt")  # Send the image for GPT
    msg = load_message("gpt")  # Load the message for GPT
    await send_text(update, context, msg)  # Send the text for GPT


# Handle messages during the GPT dialog
async def gpt_dialog(update, context):
    text = update.message.text  # Get the user's message text
    prompt = load_prompt("gpt")  # Load the prompt for GPT
    answer = await chatgpt.send_question(prompt, text)  # Get the answer from GPT
    await send_text(update, context, answer)  # Send the answer back to the user


# Command to start the celebrity "date" dialog
async def date(update, context):
    dialog.mode = "date"  # Set the mode to "date"
    msg = load_message("date")  # Load the message for celebrity selection
    await send_photo(update, context, name="date")  # Send the image for "date"

    # Buttons for selecting a celebrity
    await send_text_buttons(update, context, msg, buttons={
        "date_grande": "Ariana Grande",
        "date_robbie": "Margot Robbie",
        "date_zendaya": "Zendaya",
        "date_gosling": "Ryan Gosling",
        "date_hardy": "Tom Hardy",
    })


# Handle the celebrity selection button click
async def date_button(update, context):
    query = update.callback_query.data  # Get the selected celebrity button data
    await update.callback_query.answer()  # Acknowledge the button click
    await send_photo(update, context, query)  # Send the photo of the selected celebrity
    await send_text(update, context,
                    text="Great choice.🥰 Your task is to invite the person on a date with 5 messages!😎")

    prompt = load_prompt(query)  # Load the prompt for the selected celebrity
    chatgpt.set_prompt(prompt)  # Set the prompt for generating the response


# Handle the dialog for the selected celebrity "date"
async def date_dialog(update, context):
    text = update.message.text  # Get the user's message text
    my_message = await send_text(update, context, text="Typing...")  # Show a typing message
    answer = await chatgpt.add_message(text)  # Send the message to GPT for a response
    await my_message.edit_text(answer)  # Edit the message with GPT's response


# Command to start the message writing process
async def message(update, context):
    dialog.mode = "message"  # Set the mode to "message"
    msg = load_message("message")  # Load the message for message writing
    await send_photo(update, context, name="message")  # Send the image for "message"

    # Buttons for choosing what to do next
    await send_text_buttons(update, context, msg, {
        "message_next": "Write a message",  # Option to write a message
        "message_date": "Invite to a date"  # Option to invite to a date
    })
    dialog.list.clear()  # Clear the dialog list for the new conversation


# Handle the user's message in the message dialog
async def message_dialog(update, context):
    text = update.message.text  # Get the user's message
    dialog.list.append(text)  # Add the message to the conversation history


# Handle button clicks in the message dialog
async def message_button(update, context):
    query = update.callback_query.data  # Get the button data
    await update.callback_query.answer()  # Acknowledge the button click

    prompt = load_prompt(query)  # Load the prompt for the selected option
    user_chat_history = "\n\n".join(dialog.list)  # Join all the conversation messages

    # Show a message indicating that GPT is generating a response
    my_message = await send_text(update, context, "Thinking about response options...")

    answer = await chatgpt.send_question(prompt, user_chat_history)  # Get GPT's response
    await my_message.edit_text(answer)  # Edit the message with GPT's answer


# Command to start generating a Tinder profile
async def profile(update, context):
    dialog.mode = "profile"  # Set the mode to "profile"
    msg = load_message("profile")  # Load the message for profile generation
    await send_photo(update, context, "profile")  # Send the image for "profile"
    await send_text(update, context, msg)  # Send the text for profile generation

    dialog.user.clear()  # Clear the user data
    dialog.counter = 0  # Reset the question counter
    await send_text(update, context, "How old are you?")  # Ask for the user's age


# Handle the profile creation dialog
async def profile_dialog(update, context):
    text = update.message.text  # Get the user's response
    dialog.counter += 1  # Increment the question counter

    # Collect user's data step by step
    if dialog.counter == 1:
        dialog.user["age"] = text
        await send_text(update, context, "What is your occupation?")
    if dialog.counter == 2:
        dialog.user["occupation"] = text
        await send_text(update, context, "What are your hobbies?")
    if dialog.counter == 3:
        dialog.user["hobby"] = text
        await send_text(update, context, "What do you dislike in people?")
    if dialog.counter == 4:
        dialog.user["annoys"] = text
        await send_text(update, context, "What is your goal in dating?")
    if dialog.counter == 5:
        dialog.user["goals"] = text

        # Generate the profile using GPT
        prompt = load_prompt("profile")
        user_info = dialog_user_info_to_str(dialog.user)

        # Show a message indicating GPT is generating the profile
        my_message = await send_text(update, context, "ChatGPT is loading your profile, please wait a moment!")
        answer = await chatgpt.send_question(prompt, user_info)  # Get the generated profile from GPT
        await my_message.edit_text(answer)  # Edit the message with GPT's result


# Command to start generating a message opener
async def opener(update, context):
    dialog.mode = "opener"  # Set the mode to "opener"
    msg = load_message("opener")  # Load the message for opener generation
    await send_photo(update, context, "opener")  # Send the image for "opener"
    await send_text(update, context, msg)  # Send the text for opener generation

    dialog.user.clear()  # Clear the user data
    dialog.counter = 0  # Reset the question counter
    await send_text(update, context, "Partner's name?")  # Ask for the partner's name


# Handle the opener dialog
async def opener_dialog(update, context):
    text = update.message.text  # Get the user's response
    dialog.counter += 1  # Increment the question counter

    # Collect user's data for the opener
    if dialog.counter == 1:
        dialog.user["name"] = text
        await send_text(update, context, "How old are they?")
    if dialog.counter == 2:
        dialog.user["age"] = text
        await send_text(update, context, "How attractive are they on a scale of 1-10?")
    if dialog.counter == 3:
        dialog.user["handsome"] = text
        await send_text(update, context, "What is their profession?")
    if dialog.counter == 4:
        dialog.user["occupation"] = text
        await send_text(update, context, "What is your goal in dating?")
    if dialog.counter == 5:
        dialog.user["goals"] = text

        # Generate the opener using GPT
        prompt = load_prompt("opener")
        user_info = dialog_user_info_to_str(dialog.user)

        # Show a message indicating GPT is generating the opener
        my_message = await send_text(update, context, "ChatGPT is loading your opener, please wait a moment!")
        answer = await chatgpt.send_question(prompt, user_info)  # Get the generated opener from GPT
        await my_message.edit_text(answer)  # Edit the message with GPT's result


# Handle different dialog modes
async def hello(update, context):
    if dialog.mode == "gpt":
        await gpt_dialog(update, context)
    elif dialog.mode == "date":
        await date_dialog(update, context)
    elif dialog.mode == "message":
        await message_dialog(update, context)
    elif dialog.mode == "profile":
        await profile_dialog(update, context)
    elif dialog.mode == "opener":
        await opener_dialog(update, context)


# Initialize dialog object
dialog = Dialog()
dialog.mode = None
dialog.list = []
dialog.user = {}
dialog.counter = 0

# Initialize the ChatGPT service with the API key
chatgpt = ChatGptService(
    token="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")

# Build the application and add handlers
app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("gpt", gpt))
app.add_handler(CommandHandler("date", date))
app.add_handler(CommandHandler("message", message))
app.add_handler(CommandHandler("profile", profile))
app.add_handler(CommandHandler("opener", opener))

# Add message and callback query handlers
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, hello))
app.add_handler(CallbackQueryHandler(date_button, pattern="^date_.*"))
app.add_handler(CallbackQueryHandler(message_button, pattern="^message_.*"))

# Run the bot using polling
app.run_polling()
