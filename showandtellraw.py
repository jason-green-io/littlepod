#!/usr/bin/python3

import re
import json

string ="<green^Welcome to> [_<green^Barlynaland>_|http://barlynaland.greener.ca]<green^!> | {[_<aqua^Discord>_|https://discord.gg/0mYDl0E2UE5Z4xuv]~Slack replacement I think} | {[_<blue^FAQ>_|http://barlynaland.greener.ca/#!new.md]~new player FAQ} | {[<dark_aqua^_contribute_>|http://PayPal.me/greener]~I pay for the server out of pocket.} | [_<yellow^map>_|http://barlynaland.greener.ca/map]"
#print string

def tohtml( string ):
    colorlist = {
"black" : "#000000",
"dark_blue" : "#0000AA",
"dark_green" : "#00AA00",
"dark_aqua" : "#00AAAA",
"dark_red" : "#AA0000",
"dark_purple" : "#AA00AA",
"gold" : "#FFAA00",
"gray" : "#AAAAAA",
"dark_gray" : "#555555",
"blue" : "#5555FF",
"green" : "#55FF55",
"aqua" : "#55FFFF",
"red" : "#FF5555",
"light_purple" : "#FF55FF",
"yellow" : "#FFFF55",
"white" : "#FFFFFF" }

#    print "".join([each.get("text") for each in parse( string)])
    html = []
    for each in parse( string ):
        style = []
        text = each.get("text")
        # print(each)
        if "color" in each:
            style.append( "color: " + colorlist.get(each.get("color")) +";")
        if "bold" in each:
            style.append( "font-weight: bold;")
        if "underlined" in each:
            style.append( "text-decoration: underline;" )
        if "strikethrough" in each:
            style.append( "text-decoration: line-through;" )
        if "italic" in each:
            style.append( "font-style: italic;" )
        if "clickEvent" in each:
            text = '<a style="color: inherit;" target="_blank" href="' + each.get("clickEvent").get("value") + '">' + text + '</a>'

        html.append( '<span style="' + "".join(style) + '">' + text + '</span>' )
#    print html
    return "".join(html)


def tojson( string, noparse="" ):
    jsontext = parse(string)
    if noparse:
        jsontext.append({"text": noparse })
    return json.dumps( jsontext, ensure_ascii=True )


def parse( string ):
    result1 = []
    split = 0

    for charnum in range( len( string ) ):
        if string[ charnum ] == "{":
            result1.append( { "text" : string[ split:charnum  ] } )
            split = charnum
        elif string[ charnum ] == "}":
            hover = string[ split:charnum+1 ].strip("{}").split("~")
            #print string[ split:charnum+1].strip("{}").split("|")
            result1.append( { "text" : hover[0], "hoverEvent" : {"action" : "show_text", "value" : hover[1]  } } )
            split = charnum+1

    result1.append( { "text" : string[ split: ] } )

#    print result1

    result2 = []
    for dict in result1:
        split = 0
        text = dict.get( "text" )
        #print text
        interimresult = []
        for charnum in range( len( text ) ):

            if text[ charnum ] == "[":
                newdict = dict.copy()
                #print text[ split:charnum ]
                newdict.update( { "text" : text[ split:charnum ] } )
                interimresult.append( newdict )
                split = charnum
            elif text[ charnum ] == "]":
                newdict = dict.copy()
                #print text[ split:charnum ]
                link = text[ split:charnum+1 ].strip("[]").split( "|" )
                newdict.update( { "text" : link[0], "clickEvent" : { "action" : "open_url", "value" : link[1] } } )
                interimresult.append( newdict )
                split = charnum+1

        newdict = dict.copy()
        newdict.update( { "text" : text[ split: ] } )
        interimresult.append( newdict )



        result2 += interimresult

#    print result2

    result3 = []
    for dict in result2:
        bold = False
        colorset = False
        underlined = False
        obfuscated = False
        italic = False
        strikethrough = False
        colornum = 0
        color = False
        newtext = ""
        text = dict.get( "text" )
        newdict = dict.copy()

        def genblock():
            block = newdict.copy()
            block.update( { "text" : newtext } )
            if bold:
                block.update( { "bold" : True } )
            if underlined:
                block.update( { "underlined" : True } )
            if obfuscated:
                block.update( { "obfuscated" : True } )
            if strikethrough:
                block.update( { "strikethrough" : True } )
            if italic:
                block.update( { "italic" : True } )
            if color:
                block.update( { "color" : colornum } )
            #print block
            return block
        interimresult = []
        skip = False
        for charnum in range(len( text ) ):
            char = text[charnum ]

            if not skip:
                if char == "*" and not bold:
                    if newtext:
                        interimresult.append( genblock() )
                    bold = True
                    newtext = ""
                elif char == "*" and bold:
                    interimresult.append( genblock() )
                    newtext = ""
                    bold = False

                elif char == "/" and not italic:
                    if newtext:
                        interimresult.append( genblock() )
                    italic = True
                    newtext = ""
                elif char == "/" and italic:
                    interimresult.append( genblock() )
                    newtext = ""
                    italic = False

                elif char == "\\":
                    skip = True
                    continue

                elif char == "@" and not obfuscated:
                    if newtext:
                        interimresult.append( genblock() )
                    obfuscated = True
                    newtext = ""

                elif char == "@" and obfuscated:
                    interimresult.append( genblock() )
                    newtext = ""
                    obfuscated = False
    #           elif char == "-" and not strikethrough:
    #                 if newtext:
    #                     interimresult.append( genblock() )
    #                 strikethrough = True
    #                 newtext = ""
    #             elif char == "-" and strikethrough:
    #                 interimresult.append( genblock() )
    #                 newtext = ""
    #                 strikethrough = False
                elif char == "_" and not underlined and not colorset:
                    if newtext:
                        interimresult.append( genblock() )
                    underlined = True
                    newtext = ""
                elif char == "_" and underlined:
                    interimresult.append( genblock() )
                    newtext = ""
                    underlined = False


                elif char == "<" and not color:
                    if newtext:
                        interimresult.append( genblock() )
                    color = True
                    colorset = True
                    newtext = ""
                elif char == "^" and color:
                    colorset = False
                    colornum = newtext
                    newtext = ""
                elif char == ">" and color:
                    interimresult.append( genblock() )
                    newtext = ""
                    color = False


                else:
                    newtext += char
            else:
                newtext += char
                skip = False
        if newtext:
            interimresult.append ( genblock() )

        result3 += interimresult
#        print result3
    
    return result3


if __name__ == "__main__":

    print(string)
    print(tojson(string, noparse="this is not parsed *-^@"))
    print(tohtml( string ))
