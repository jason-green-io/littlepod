#!/usr/bin/python3
import gzip
import glob
import collections
import datetime
import os


path = os.path.join(os.environ.get("DATAFOLDER", "/data"), "mc/logs/")

def getActivity(days=14):
    base = datetime.datetime.today()
    date_list = [base - datetime.timedelta(days=x) for x in range(0, days)]
    dateStr_list = [d.strftime("%Y-%m-%d") for d in date_list]
    today = base.strftime("%Y-%m-%d")

    deathVerbs = ["was",
                 "hugged",
                 "walked",
                 "drowned",
                 "experienced",
                 "removed",
                 "blew",
                 "hit",
                 "fell",
                 "went",
                 "burned",
                 "tried",
                 "discovered",
                 "got",
                 "starved",
                 "suffocated",
                 "didn’t",
                 "withered"]

    files = []

    for d in dateStr_list:
        files += glob.glob(path + d + "*")
        
    activity = collections.defaultdict(set)
    deaths = collections.defaultdict(set)
    advancements = collections.defaultdict(set)

    for fStr in files:
        date = fStr.rsplit('/', 1)[-1].split('.')[0].rsplit('-', 1)[0]
        with gzip.open(fStr, 'r') as f:
            file_content = f.readlines()
            for line in file_content:
                lineStr = line.decode('utf-8').strip()
                lineStrSplit = lineStr.split()

                if len(lineStrSplit) >= 5:
                    if "<" not in lineStrSplit[3]:
                        player = lineStrSplit[3].split('[')[0]
                        if lineStrSplit[4] == "logged":
                            #                    print(lineStrSplit)                    

                            activity[player].add(date)
                        elif lineStrSplit[4] in deathVerbs:
                            deaths[player].add(date)
                            # print(lineStrSplit)
                        elif lineStrSplit[4] == "has":
                            advancements[player].add(date)
                            # print(lineStrSplit)
                            pass
                            # print(lineStrSplit)
    sortedActivity = list(activity.items())

    sortedActivity.sort(reverse=True, key=lambda x: len(x[1]))

    activityList = []
    activityList.append("""First `-` is {} showing {} days
`o` logged in, `O` made an advancement, `x` died, `X` died and made an advancement\n""".format(today, days))

    for each in sortedActivity:

        a = ""
        for d in dateStr_list:
            if d in deaths[each[0]] and d in advancements[each[0]]:
                a += "X"
            elif d in advancements[each[0]]:
                a += "O"
            elif d in deaths[each[0]]:
                a += "x"
            elif d in each[1]:
                a += "o"
            else:
                a += '-'
        activityList.append("`|{0}|{1}|`".format(each[0].ljust(16), a.ljust(days)))
    if activityList:    
        return "\n".join(activityList)
    else:
        return "No player activity."

if __name__ == "__main__":
    print(getActivity())
