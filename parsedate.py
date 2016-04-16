import re
import time
import dateutil.parser as dparser


def parsedate(datestr):
    dateint = 0
    try:
        #del all chinese characters
        pubtimetxt2 = re.sub(ur'[\u4e00-\u9fff]+', ' ', datestr)
        pubtimetxt2 = re.sub(ur'[\ufe30-\uffa0]+', ' ', pubtimetxt2)
        pos_year = re.search(r'201\d\D', pubtimetxt2).regs[0][0]
        pos_time = pos_year + len("yyyy-mm-dd")
        match_hhmmss = re.search(r'\D\d\d:\d\d:\d\d',pubtimetxt2)
        match_hhmm = re.search(r'\D\d\d:\d\d',pubtimetxt2)
        if (match_hhmmss):
            pos_time = match_hhmmss.regs[0][1]
        elif (match_hhmm):
            pos_time = match_hhmm.regs[0][1]
        pubtimetxt2 = pubtimetxt2[pos_year:pos_time]
        pubtime = dparser.parse(pubtimetxt2, fuzzy=True)  #.strftime('%Y%m%d%H%M%S')
        dateint = int(time.mktime(pubtime.timetuple()))

    except:
        dateint = 0
        pass
    return dateint