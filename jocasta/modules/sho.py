import os
import time
import requests
from requests.exceptions import ProxyError

from jocasta.modules.filters.checker_defs import gate_error, save_live
from jocasta.services.antispam_dec import get_spam_dec
from jocasta.services.language import get_strings_dec
from jocasta.services.gate_on_off import gate_info_dec
from jocasta.dec import register
from jocasta.services.red import aioredis
from jocasta.services.mongo import adb
from jocasta.utlis.send_log import send_logs, send_logs_doc
from jocasta.modules.filters.bin_info import get_bin_info
from jocasta.modules.filters.get_card_details import get_cards

from .func.sho import *
from .func.rand_user import random_user_api, PROXIES




@register(cmds="sho", is_text=True)
@gate_info_dec('sho')
@get_strings_dec("card_check")
@get_spam_dec()
async def sho(message, gate_info, user_info,start_time, lang):
    try:
        await message.answer_chat_action('typing')
        msg = await message.reply(lang['start_msg'].format(gate_name=gate_info['name'], name=message.from_user.first_name, id=message.from_user.id,role=user_info['role']), disable_web_page_preview=True)
        data = await get_cards(message.reply_to_message.text if message.reply_to_message is not None else message.text,message.from_user.id)
        assert isinstance(data, tuple), data
        cc, mes, ano, cvv = data
        lista = cc + '|' + mes + '|' + ano + '|' + cvv 
        bin_info = await get_bin_info(cc[:6],message.from_user.id)
        await msg.edit_text(lang['card_msg'].format(card=lista, name=message.from_user.first_name, id=message.from_user.id,
                                    bin_bank=bin_info['bank_name'], gate_name=gate_info['name'],
                                    elapsed=round(time.time() - start_time), bin_country=bin_info['country'],
                                    flag=bin_info['flag'], vendor=bin_info['vendor'], level=bin_info['level'],
                                    type=bin_info['type'], role=user_info['role']), disable_web_page_preview=True)
        browser = requests.Session()
        
        a = sho_one(browser)
        assert a, lang['first_error']
        b = sho_two(browser,a)
        assert b, lang['second_error']
        random_user = random_user_api().get_random_user_info()
        authenticity_token = random_user_api.get_random_string(86)
        await msg.edit_text(lang['half_msg'].format(card=lista, name=message.from_user.first_name, id=message.from_user.id,
                                    bin_bank=bin_info['bank_name'], gate_name=gate_info['name'],
                                    elapsed=round(time.time() - start_time), bin_country=bin_info['country'],
                                    flag=bin_info['flag'], vendor=bin_info['vendor'], level=bin_info['level'],
                                    type=bin_info['type'], role=user_info['role']), disable_web_page_preview=True)
        c = sho_three(browser, authenticity_token)
        assert c, lang['third_error']
        d = sho_four(browser, cc, mes, ano, cvv, random_user)
        assert d, lang['fourth_error']
        await msg.edit_text(lang['half_half_msg'].format(card=lista, name=message.from_user.first_name, id=message.from_user.id,
                                    bin_bank=bin_info['bank_name'], gate_name=gate_info['name'],
                                    elapsed=round(time.time() - start_time), bin_country=bin_info['country'],
                                    flag=bin_info['flag'], vendor=bin_info['vendor'], level=bin_info['level'],
                                    type=bin_info['type'], role=user_info['role']), disable_web_page_preview=True)
        c = sho_three(browser, authenticity_token)
        e = sho_last(browser, c, authenticity_token, d)
        r_text, r_logo, r_respo = get_response_sho_br(e)
        if 'Charged $30' in r_text:
            await send_logs(lista + ' ' + gate_info['name'])
            save_live(lista + ' ' + gate_info['name'])
            if user_info['save-ccs']:
                await adb.users.update_one({'_id': message.from_user.id}, {'$addToSet': {'cards': lista + ' ' + gate_info['name']}})
        elif 'Error' in r_respo:
            await send_logs("Error in {} Gateway. uploading file....".format(gate_info['name']))
            gate_error(e, gate_info['name'])
            if os.path.exists(f'text_files/{gate_info["name"]}.txt'):
                await send_logs_doc(f'text_files/{gate_info["name"]}.txt')
        await msg.edit_text(lang['last_msg'].format(card=lista, name=message.from_user.first_name, id=message.from_user.id,
                                    bin_bank=bin_info['bank_name'], gate_name=gate_info['name'],
                                    elapsed=round(time.time() - start_time), bin_country=bin_info['country'],
                                    flag=bin_info['flag'], vendor=bin_info['vendor'], level=bin_info['level'],
                                    type=bin_info['type'], role=user_info['role'],r_respo = r_respo,r_text=r_text,r_logo = r_logo
                                    ), disable_web_page_preview=True)
        await aioredis.set(f"spam_{message.from_user.id}", time.time())
    except AssertionError as aserr:
        await msg.edit_text(aserr)
    except ConnectionError: 
        await msg.edit_text(lang['proxy_dead'])
    except ProxyError: 
        await msg.edit_text(lang['proxy_dead'])
    except Exception as e:
        await send_logs(e)


