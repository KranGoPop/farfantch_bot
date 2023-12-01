import aiohttp
import aiomysql
import asyncio
import pymysql
import json
import bs4

max_pages = 20

headers = {
    'Host': 'www.farfetch.com',
    'Cookie': 'BIcookieID=6fbfd5c2-a726-4ca7-8729-6d6df188b352; ckm-ctx-sf=%2Fkz; BISessionId=09d18595-0dfb-d337-1f04-5c2621e02019; ffcp=a.1.0_f.1.0_p.1.0_c.1.0; ub=50CAC614848E6A27CBC86CA9829B46A4; ff_navroot_history=141259; __Host-FF.AppSession=CfDJ8BZV7bSK%2FgVKoJ5%2FtFR15T6JPxPTxquYJkMewNWzAYUoee9GD%2FtM4Tj%2BcXh94Z9Uf9iCO%2B%2FHqq7noyvf%2BB%2BQs1q2pWuu9XYqGdzVc8kNFOvW0LbSlXRhlvR6H8cdluQi68iNOfgZGu5%2BJslBHpjIH7mRtJMkExNJS%2BNHuPT6Qww0; checkoutType2=4; session-1=09d18595-0dfb-d337-1f04-5c2621e02019; ff_newsletter_pv=1; fita.sid.farfetch=614FYqfhTs8CPUrLzo5y1PU5nxod2OEI; _gcl_au=1.1.2122255651.1699216511; rskxRunCookie=0; rCookie=r571ypfnh2snfmoh30918clolxmzl5; _cs_c=0; FPID=FPID2.3.lyIq69k%2BIIPzNjhtIB2fAiohcIUTdA%2FJGmQqqBkQcoQ%3D.1699216512; FPAU=1.1.2122255651.1699216511; __Host-CSRF-TOKEN=CfDJ8BZV7bSK_gVKoJ5_tFR15T4DFijSvznaX6jSZMPR1LaRC__2H5p_LJsXtNzPj3x710pH3mbhnyYGg0jL7fLIevfVFP_oN3ogStdJZ666WPbhRbel-fRcICcAD-n08E5PXUyLVTlamiMbcT8arogG1CQ; FPID=FPID2.2.lyIq69k%2BIIPzNjhtIB2fAiohcIUTdA%2FJGmQqqBkQcoQ%3D.1699216512; FPAU=1.1.2122255651.1699216511; __Host-FF.AppCookie=CfDJ8BZV7bSK_gVKoJ5_tFR15T7OCqjwO8bQ7GOEpBBv6xzZ1GD0uqNu8qrsW7fOnKv4bn13SBRXTk0ecBoWS9qpf_pRWpljGTpP9tDWOs0STB_jnyLxU0Y3uPwc3mWvB5b536ksoZmP70HhfE7_Fq0fJZxhRMz1sEb6pSt7ZBcY6S0ucp8ga4rcOM28JJ5QKBZstsPs9AOdpDCEdVYzkJXUzYdLrHucJZmh8jPK4-cqUJ5cjL_0JczD67vliwQSbl3oQFxTZLM3VLyyf_l4okF3oyLQrEr__o_ZWF5JVwzgmOT8; ABProduct=; ABListing=; ABGeneral=; ABLanding=; ABCheckout=; ABRecommendations=; ABReturns=; ABWishlist=; ExperimentsGeneral=b6cf98.0; _gid=GA1.2.16321806.1701345300; _ga_DSQLKCWFGM=GS1.2.1701345300.1.0.1701345300.60.0.0; FPLC=FppkW1epYxv4Ow%2BNFdH7%2FFmIgUXFMfeJeLkJP%2FcIcbWzZYvRDlWMtVyaXfEv26QoOGC4n8%2F4PWjl7sLwyvkFgZJ3jGEyvyHe8d7rB2Ti%2BTTkh4RgPge41vzYH8a0UA%3D%3D; ExperimentsListing=2548c5.1; g_state={"i_p":1701362698310,"i_l":1}; bm_sz=C0DE826C17C45CF838FD525563DFF987~YAAQJIVlXxppoduLAQAA4CZxIhXzkSHgnbhfBWkscoWg+0ehPR34OsTNfnECprce6E8nxaTDuSEf2nz6q+Ujj5MG5O3yrEmze3ioMzU3w2aTkhQSmgX/lHTXILDlJcxTgNHsoJUXB4v1wIulbp1rmeqsv4TkAhzArnfmfz95R2js5u4uNLySs/YtJs7E4a77fIVcYVF8qZmR8e0qkEvon4i8eGj80ikzSUbykZJuyXHnwFnrLucHwpTmAcZY1YV0jQ88FAa+3giebD6/7ZMbRXds9aFQKSRQNEYJO1dsglRFfykWvw==~4272948~4469814; _abck=9BD79EB77AAF64DC655096070BA57DEF~0~YAAQJIVlX4hroduLAQAA3Pp6IgqeZdt47d3qggmEH0D3gMlyZWIe88WiL5w/gSw0aiA7tMy46QpF9+6ESKtaFvNtUdiTkGVcrIyyFODtDjP3wz953jZeewymLegOHYU1aFz7ENHTSC8NvI7nYh7KxkQe6mEBf86UdnhGb6THM9BCHzucWp/fjBKcTrw3HaKTt9HUN5T1duzPnD8F4QgUpwlz6cZKCyFOhP72VYnS6ARlaQm7mZbh4GkI0o9Egg2KFTBHx+mZIeYx5PjW+5yhe6wiruddqbFapvBgsz5WMjUHF0Nun/THiIXZL+XbtnZP317fxmqwY/LKq0AwlrZAdVWWTLKMalmqq4sYNHRfTUpOeC9WtyBpvphoIZ0Nqk5aJoDR1U0QvLQyVdCz93fF25eHBJ06e4ewFKQ=~-1~-1~-1; bm_mi=0B4B9F29F49F1E005CBD1CB4E6C517B6~YAAQJIVlX2mPoduLAQAALlceIxUCXZbi5gN173Os1EpgXG2hdQGN+0/rDhM9ztu8ZWbzch6jI4vYP59BvMwOV8MxQD0hyKWihoo71Q6LiuZeA5cs6C+yuyyRPKJwmpGAhPRRFREiatKgQ1UD/YaOwodsfVue5zLtKekojIlrIAcdi6hKO/9aQ6RMml/rgX/JqUUyYQT9+9fKGRQiIQUEhUe3nm5rreJR40JTOPnIgv8VHLC23l48mDsEo9XjTnE+yUyCMRvaCtEOuf2DrOSW3542/afxqosJkRPZmOQCsU0SKzTsrF9in4tgFlvG0SE2JIOaT48hmM3NYdlkIUfS4clv93p5VRHukdmPeMcJKldRsfujTA==~1; ak_bmsc=004F46C0336CD1465AC14B129D262F0E~000000000000000000000000000000~YAAQJIVlX3OPoduLAQAAZWYeIxVPApJjIvqvDkORcxqtGmC96zs6UIpSoWIE45P+HMynbK3YJPMnnXOhAbPor1/67nKS5x9LaS6xYtAbCZ8kKK2S+Rs0iGIOs5hIaZSrHyOMuv7QszYXHC5KZziCf12rcDjJ0kcH3a38e+tXUGdks0i9AMafI9zdv0IiDB/WbBrJYImhtFpJkPNFPYbjaVxOfg62ELnEKaJZj+uDA4vYgQsqbkWDmWwxUqyBC4zjvhRZYVoxeB2BuTT6t1d8+F19RsRpCLWtJsp675OCrDagj7txq6UatjPJEbv/mrv4qEEsxo4KvXw5SA97mz7NBbHJDjoYVPugacNsZS7GFmTdUNPCf/RrZ1E/1NNNiYcJM0o5qWKggYoMlHNCNsp3Qo7PwBSha89i8/bnHC07PIRDJB7AonyuB5KOIA3mRVknhO7inYKudNCbjbj3WOM9/880x4gyKbhrZb9V0N4mvbByMCjtkbwHhFKW/p8lXJryQ0H9aF9g0zpS8+P4DzFntaPdgVAE/ZvcvavrFXD5hwn0QfpwAE7UOmYKfzJJXYy1ghpBNOefdDMdcw==; _cs_mk=0.7381555927393946_1701396244055; ftr_blst_1h=1701396246005; _gat_UA-3819811-6=1; __cuid=b8f535ac7f9b438d9ef2f6dc19ae1f6d; AkamaiFeatureToggle=02a57c.1_0357f7.1_04154b.1_050b85.1_0a3efc.1_157b5e.-1_15d9b3.2_1d8e03.1_1fc0ee.-1_20b92f.1_213bb6.-1_247006.-1_26ddb8.1_2ba087.1_34cea2.1_361eee.2_3aa8d2.0_3c8089.2_4247d8.-210644093_425ded.1_45dc7d.1_48259b.1_4b57a6.-1_4d76c8.2_56f7db.-1_5836e0.-1_590a92.1_5a000f.1_5a745a.-1_5dbd1a.1_5edc51.-1959550240_603919.1_613a9b.-416292886_64d19c.1_67486d.-1_677d5c.-1_678f94.0_687752.-1_696e8a.1_6df3b9.-1_6f0973.-1_729a35.1_751ef1.-1_7cf0c5.-1_8c3210.-1_8c4007.-1_931982.1_945679.1_999fce.2_9a710c.1_9ebcf7.1_9f0eda.-1_9fca73.-1_a00510.1148090917_a27c87.-1_a54601.1_a7e49d.-1_aa6446.-1671435226_ac992b.2_ae71cc.-1531679491_b45ee1.1_b833c7.535845473_b8833c.1_b8e9db.-1_b90715.0_bf09c6.1_bf110c.-1_bfc591.1_c06844.-1_c0ba66.-900375819_c2155c.1_c5e8eb.-1_c6215a.-1_ca47d2.-1_cfc1ba.1_d052f2.909416419_d26d24.1_d47781.-1_d59758.1_da4cdf.1_dab09d.632075632_db79f1.0_dd19ed.1_deb641.-1_dec9f3.1_df039e.-1_df93a0.1_e7eec4.1_e89c2a.2_ed07fa.0_ed8d9e.1_f220ef.4_f3db94.1_f5969a.1_f8c66b.1_fb2b96.1_fbf4d6.1_fdbb7a.0_fdd39e.-1; lastRskxRun=1701397031623; _ga_HLS8C90D41=GS1.1.1701396245.11.0.1701397031.0.0.0; _ga=GA1.1.1544398881.1699216512; _ga_CEF7PMN9HX=GS1.1.1701396245.11.1.1701397032.35.0.0; _cs_id=97e15996-2c7b-a337-dd90-453bbc02f276.1699216512.16.1701397032.1701396245.1.1733380512072; _cs_s=5.0.0.1701398832288; __Host-CSRF-REQUEST-TOKEN=CfDJ8BZV7bSK_gVKoJ5_tFR15T5U27hLgHRVzGcu3Bd7uScn6JJIwtmcLvJfNZMotQTQztXBwdRfa6UXqQbsG2z7s_E1pW5zfuBh8hgS3Y2zJwspAXJQbhxaVwR5h8W_zyh7dGPkUH94iUfHGGtdgt8o4cy2iGXjZasvYAo2Dytf_325_dqFTs7Z9qLLUXSmdt2Jrg; bm_sv=D812DAD7753B5AB1A1C85E49946B95D5~YAAQPoVlXxu+9d6LAQAAA28qIxVar3JEINt+cTZdPqMbCWbpcX7BzLD3Rds1yAhgvyGX69MlB4aOaXuPOuP5tJyJNOa1A9Rnmy/8qUnqgNDAgggrpaDWKdpnV7fMRGDt7CYXZx8DADbW5WiboETScskhUxs8COVf28t4TEHNP2bqPB+Em7/1aBCxvgCFnIQtm9EMKXcNcuZttiTnJBg6eeuFA/TtyeFlwkbDL7FkwlbZH4k5II9lptzx6zgfvnAuX9Cf~1; _uetsid=5004c9e08f7711eeba4ee3a2b66e739e; _uetvid=d1c1b0f07c1a11ee9adff563662b3ee2; cto_bundle=qEvViV9McWZWUmlhdTJJRG9uN3glMkJSWWl3TXRUblBSSDJ4Z1MyM0dWSVRFRU9JcHAwUWlrZVlPS1d0NUJEdjJHUFJSQTNXY1olMkJXZFJBMnpGQWhuNGc4cmpsZ2RXdVpYcDQwN1hqa0tLcUc3OUJzZjZLZFNKcTJKdTB6bVBLUUslMkZReGphU05BQTlpc3dRaGdubkpidGxrTHRyTUp1OEphJTJCMXZvZTRoWkNyTHkyZm8wcURVMlpaRldyVmxhN3NicFV3bnRFcGlva3FpQmNxUlg2U1hrdFpCSjNEd0ElM0QlM0Q; forterToken=9e835e583c8f4d6397ff799f26d774f1_1701397031497__UDF43-m4_11ck_; RT="z=1&dm=www.farfetch.com&si=dc0afb07-e9e64f88-a03d-4426bdf6d78b&ss=lplze3ub&sl=5&tt=3zt&obo=4&rl=1&ld=hina&r=cz27kbwn&ul=hinb"', 
    'Cache-Control': 'max-age=0',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
    'Connection': 'close',
    'Sec-Fetch-Site': 'same-origin',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-User': '?1',
    'Sec-Fetch-Dest': 'document',
}

download_counter = 0

async def connect_to_db():
    i = 0

    # for i in range(10):
    while True:
        i += 1

        try:
            conn = await aiomysql.connect(
                host='db',
                user='db_user',
                password='1234',
                db='farfetch',
                loop=asyncio.get_event_loop()
            )
        except pymysql.err.OperationalError:
            print(f"STEALER: Trying to connect to MySQL ... ({i} try)")
            await asyncio.sleep(5)
        else:
            return conn

    print("STEALER: Filed to connect to MySQL")
    return False

async def fetch_data(cur, page):
    global download_counter
    url = f"https://www.farfetch.com/kz/shopping/men/trainers-2/items.aspx?page={page}&view=96&sort=3&scale=282"

    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            html = await response.text()

            soup = bs4.BeautifulSoup(html, 'html.parser')
            data = soup.css.select('.ltr-113ivyq>[type="application/ld+json"]')

            if len(data) > 0:
                data = json.loads(data[0].contents[0])
                data = data['itemListElement']
            else:
                data = False
    
    if data != False:
        download_counter += 1

        print()

        data = [(item["brand"]["name"] + ' ' + item["name"], item["name"], int(item["offers"]["price"]), item["brand"]["name"], item["image"][0]) for item in data]
        await cur.executemany("INSERT INTO supplies(`search`, `name`, `price`, `brand`, `image`) VALUES(%s, %s, %s, %s, %s)", data)

        print(f"STEALER: Page {download_counter} of {max_pages} Downloaded;")
    else:
        print()
        print(htlm[:2000])
        print("SETALER: Some Error occured while downloading contents!!!!!!")


async def main():
    conn = await connect_to_db()

    if conn == False:
        return

    print('STEALER: Connect with DB has established')

    cur = await conn.cursor(aiomysql.DictCursor)

    with open('status.json', 'r') as fd:
        is_reload = json.loads(fd.read())['reload']

    if is_reload:
        await cur.execute("DELETE FROM supplies")
        with open('status.json', 'w') as fd:
            fd.write(json.dumps({"reload": False}))

    for i in range(1, max_pages):
        await fetch_data(cur, i)
        await asyncio.sleep(4)

    print("\nSTAELER: All pages has downloaded!")

    await conn.commit()

    await cur.close()
    conn.close()


asyncio.run(main())