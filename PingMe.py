#! /usr/bin/env python3

import telebot
import argparse
import os
import subprocess
import time
import datetime

# Checks environment variable to require or not arguments
isTokenSet = False if 'PING_ME_TOKEN' not in os.environ else True
isUserIdSet = False if 'TELEGRAM_ID' not in os.environ else True

ap = argparse.ArgumentParser(description='Pings you when process is finish')
ap.add_argument("-t", "--token", required=not isTokenSet,
                help="provides bot token, or you could set environment variable PING_ME_TOKEN")
ap.add_argument("-i", "--user_id", required=not isUserIdSet,
                help="provides telegram user id, or you could set environment variable TELEGRAM_ID")
ap.add_argument('--print_stdout', action="store_true", help="prints stdout to provided telegram user. Please notice,"
                                                            " buffer will be lost in case of interruption")
ap.add_argument('--print_stderr', action="store_true", help="prints stderr to provided telegram user. Please notice,"
                                                            " buffer will be lost in case of interruption")
ap.add_argument('command', nargs='+', help="command that will be executed")
args = vars(ap.parse_args())

TOKEN = args['token'] if args['token'] is not None else os.environ['PING_ME_TOKEN']
TELEGRAM_ID = args['user_id'] if args['user_id'] is not None else os.environ['TELEGRAM_ID']
COMMAND_TO_RUN = args['command']
IS_PRINT_STDOUT = args['print_stdout']
IS_PRINT_STDERR = args['print_stderr']

# Bot initialization
bot = telebot.TeleBot(TOKEN)


def prepare_time_string(time_begin, time_end):
    return f"Time spent: `{str(datetime.timedelta(seconds=time_end - time_begin))}`\n"


def concatenate_args(arguments):
    return " ".join(arguments)


def prepare_return_code_string(return_code):
    return "Finished with exit code: `" + str(return_code) + "`\n"


def prepare_output(return_process):
    result = ""
    if IS_PRINT_STDOUT:
        result += f"stdout: ```{return_process.stdout}```\n"
    if IS_PRINT_STDERR:
        result += f"stderr: ```{return_process.stderr}```\n"
    return result


start_time = int()
try:
    bot.send_message(TELEGRAM_ID, "Execute: `" + concatenate_args(COMMAND_TO_RUN) + "`", parse_mode="markdown")
    start_time = time.time()
    return_answer = subprocess.run(COMMAND_TO_RUN, stdout=subprocess.PIPE if IS_PRINT_STDOUT else None,
                                   stderr=subprocess.PIPE if IS_PRINT_STDERR else None, universal_newlines=True)
    bot.send_message(TELEGRAM_ID, "Executed command: `" + concatenate_args(return_answer.args) + "`\n" +
                     prepare_return_code_string(return_answer.returncode) + prepare_time_string(start_time, time.time())
                     + prepare_output(return_answer), parse_mode="markdown")
except FileNotFoundError as e:
    print(e)
    bot.send_message(TELEGRAM_ID, "Execution failed: `" + str(e) + "`", parse_mode="markdown")
except telebot.apihelper.ApiException as e:
    print(e)
except KeyboardInterrupt as e:
    print(e)
    bot.send_message(TELEGRAM_ID, "Interrupted by user: `" + concatenate_args(COMMAND_TO_RUN) + "`\n" +
                     prepare_time_string(start_time, time.time()), parse_mode="markdown")


