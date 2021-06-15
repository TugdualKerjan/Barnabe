# -*- coding: utf-8 -*-

import vlc
import pafy
import telegram
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, InlineQueryResultVideo, InputTextMessageContent, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, MessageHandler, Updater, Filters, CallbackQueryHandler, InlineQueryHandler, ChosenInlineResultHandler
from telegram.error import NetworkError, Unauthorized
from youtubesearchpython import VideosSearch
from dotenv import dotenv_values

config = dotenv_values(".env")

token = config["SECRET"]

updater = Updater(token=token, use_context=True)

# Create a vlc instance
player = vlc.Instance()

# Create a media_list to give to the media_list_player
media_list = player.media_list_new()
media_list_player = player.media_list_player_new()
# Add the media_list to the media_list_player
media_list_player.set_media_list(media_list)

# Set fullscreen
media_list_player.get_media_player().set_fullscreen(True)

print('Hit me up with songs')

# Track the songs to be played
list_of_songs = []

# When a song is finished take it off the media_list and the songs to be tracked


def songFinished(self):
    None
    # list_of_songs.pop(0)
    # media_list.remove_index(0)

group_id = -1001159998304

events = media_list_player.event_manager()
events.event_attach(vlc.EventType.MediaListPlayerNextItemSet, songFinished)


def receive_link(update, context):
    text_message = update.message.text
    # Check if link is a youtube link
    if text_message.startswith(('https://www.youtube.com/watch?v=', 'https://youtu.be/', 'https://m.youtube.com')):
        play_link(text_message, context)
    else:
        context.bot.send_message(chat_id=group_id,
                                 text="""Not a valid youtube link!""")


def play_link(link, context):
    # Get the best video quality url
    video = pafy.new(link)
    video = video.getbest()
    media_list.add_media(video.url)

    # Track the song
    list_of_songs.append(video.title)

    # Send the list of songs to be played back
    context.bot.send_message(chat_id=group_id,
                             text="Merci cheri! Current list of songs: \n\n" +
                             "\n".join(list_of_songs))
    # If is the first song then play the media (Stops when the list ends (i.e. gets to 0)))
    if not media_list_player.get_media_player().is_playing():
        print("Not playing")
        media_list_player.play_item_at_index(len(list_of_songs)-1)


def main():
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(CommandHandler('next', nextSong))
    dispatcher.add_handler(CommandHandler('prev', prevSong))
    dispatcher.add_handler(CommandHandler('pause', pauseSong))
    dispatcher.add_handler(CommandHandler('play', playSong))
    dispatcher.add_handler(CommandHandler('add', receive_link))
    dispatcher.add_handler(InlineQueryHandler(inline_handling))
    dispatcher.add_handler(ChosenInlineResultHandler(on_result_chosen))
    dispatcher.add_handler(CallbackQueryHandler(callback_handler))
    # Maybe display images at one point?
    # dispatcher.add_handler(MessageHandler(Filters.photo, receive_images))
    # dispatcher.add_handler(MessageHandler(Filters.text, receive_link))

    updater.start_polling()


def callback_handler(update, context):
    data = update.callback_query.data
    if data == "next":
        nextSong(update, context)

    if data == "prev":
        prevSong(update, context)

    if data == "pausePlay":
        playPauseSong(update, context)

    if data == "increaseVol":
        increaseVol(update, context)

    if data == "lowerVol":
        lowerVol(update, context)

    context.bot.answerCallbackQuery(
        callback_query_id=update.callback_query.id, text="OK FINE!")


def on_result_chosen(update, context):
    # print(update.to_dict())
    play_link("https://www.youtube.com/watch?v=" +
              update.chosen_inline_result.result_id, context)


def nextSong(update, context):
    media_list_player.next()


def prevSong(update, context):
    media_list_player.previous()


def pauseSong(update, context):
    media_list_player.pause()


def lowerVol(update, context):
    player = media_list_player.get_media_player()
    player.audio_set_volume(max(player.audio_get_volume()-10, 0))


def increaseVol(update, context):
    player = media_list_player.get_media_player()
    player.audio_set_volume(min(player.audio_get_volume()+10, 100))


def playSong(update, context):
    media_list_player.play()


def playPauseSong(update, context):
    if media_list_player.is_playing():
        pauseSong(update, context)
    else:
        playSong(update, context)


reply_keyboard = InlineKeyboardMarkup([
    [InlineKeyboardButton("◀️", None, "prev"),
     InlineKeyboardButton("⏯️", None, "pausePlay"),
     InlineKeyboardButton("▶️", None, "next")],
    [InlineKeyboardButton("🔉", None, "lowerVol"),
     InlineKeyboardButton("🔊", None, "increaseVol")]])


def inline_handling(update, context):
    query = update.inline_query.query
    if not query:
        return

    results = VideosSearch(query, limit=4).result()

    inline_options = []
    for result in results['result']:
        inline_options.append(
            InlineQueryResultVideo(
                id=result['id'],
                video_url=result['link'],
                title=result['title'],
                mime_type="video/mp4",
                thumb_url=result['thumbnails'][0]['url'],
                input_message_content=InputTextMessageContent(
                    "Putain BarnaB, joue moi du '%s'" % result['title']),
                reply_markup=reply_keyboard
            )
        )
    context.bot.answer_inline_query(update.inline_query.id, inline_options)


def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text="ID IS : %s Hey! Send me a youtube link and come faire la teuf a sysmic!\n The available commands are: /next, /prev, /play, /pause" % str(update.effective_chat.id))


if __name__ == '__main__':
    main()

# def receive_images(update, context):
#     user_id=int(update.message.from_user['id'])
#     username=update.message.from_user['username']

#     # decode_img = cv2.imdecode(np.frombuffer(BytesIO(context.bot.getFile(update.message.photo[-1].file_id).download_as_bytearray()).getbuffer(), np.uint8), -1)
#     # context.bot.sendMessage(update.effective_chat.id, "Preparing scissors and glue...")
#     # context.bot.send_photo(740175095, update.message.photo[-1].file_id)

#     # for subimage in predict(decode_img):
#     #     subimage = resize(subimage)
#     #     buffer = cv2.imencode(".png", subimage)[1].tobytes()
#     #     try:
#     #         context.bot.add_sticker_to_set(user_id, name="pepites_de_%s_by_SmartCutterBot" % username, emojis="🧮", png_sticker=buffer)
#     #     except:
#     #         context.bot.createNewStickerSet(user_id, name="pepites_de_%s_by_SmartCutterBot" % username, title="PepitesDe%sSticker" % username, png_sticker=buffer, emojis="🙂")
#     #     context.bot.sendSticker(update.effective_chat.id, buffer)
#     # context.bot.sendMessage(update.effective_chat.id, "Get your stickers at t.me/addstickers/pepites_de_%s_by_SmartCutterBot" % username)
