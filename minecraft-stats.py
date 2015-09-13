#!/usr/bin/python

import time
import vanillabean
import sqlite3


def tps():
    vanillabean.send("/debug start")

    time.sleep(10)

    result = vanillabean.send("/debug stop")
    result = result.split()
    print result

    tps = round(float(result[6].strip("("))/float(result[4]))
    print tps

    conn = sqlite3.connect("/minecraft/barlynaland.db")
    cur = conn.cursor()

    cur.execute("INSERT INTO lag (tps) VALUES (?)", (tps,))

    conn.commit()
    conn.close()


def coords():
    vanillabean.send("/save-all")


coords()
