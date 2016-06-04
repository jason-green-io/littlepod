#!/bin/bash


# contentduration tweetsduration "title"

sleep 10

echo 3
echo -e \
"/title greener_ca reset\n/title greener_ca title {\"text\": \"3\"}" \
> /minecraft/vanillabean

sleep 1

echo 2
echo -e \
"/title greener_ca title {\"text\": \"2\"}" \
> /minecraft/vanillabean

sleep 1

echo 1
echo -e \
"/title greener_ca title {\"text\": \"1\"}" \
> /minecraft/vanillabean

sleep 8

echo "$1 minute(s)"

echo -e \
"/title greener_ca subtitle {\"text\": \"$3\", \"color\": \"gold\"}\n/title greener_ca title {\"text\": \"Barlynaland\", \"color\": \"gold\"}" \
> /minecraft/vanillabean

sleep $(( $1 * 60  ))
if [[ "$2" > 0 ]]; then
	echo tweets!

        echo -e \
	"/title greener_ca title {\"text\": \"tweets\", \"color\": \"gold\"}" \
> /minecraft/vanillabean

	sleep $(( $2 * 60 ))
fi
echo -e \
"/title greener_ca title {\"text\": \"wrap it up\", \"color\": \"gold\"}" \
> /minecraft/vanillabean

echo wrap it up

sleep 60

echo -e \
"/title greener_ca times 20 160 20\n/title greener_ca subtitle {\"text\": \"see you next time!\", \"color\": \"gold\"}\n/title greener_ca title {\"text\": \"Barlynaland\", \"color\": \"gold\"}" \
> /minecraft/vanillabean

sleep 12

echo -e \
"/title greener_ca title {\"text\": \"done\"}" \
> /minecraft/vanillabean
